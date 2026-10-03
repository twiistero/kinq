"""Isolated auth/email checks. No runtime account and no real email delivery."""
import json
import base64
from pathlib import Path
import os
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("KINQ_SESSION_SECRET", "isolated-email-test-secret-not-for-runtime")

import httpx
from fastapi import HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from backend.app import mailer, main


class MemberAuthEmailTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        main.Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.member = main.Member(email="login@example.test")
        self.db.add(self.member)
        self.db.commit()
        self.request = SimpleNamespace(headers={"origin": main.PUBLIC_ORIGIN}, session={})
        self.payloads = []
        self.env = patch.dict(os.environ, {"KINQ_RESEND_API_KEY": "isolated-unit-key",
            "KINQ_RESEND_FROM": "KINQ <verified@example.test>"})
        self.env.start()
        self.client_class = httpx.AsyncClient
        self.use_transport(self.accept)

    def tearDown(self):
        self.transport_patch.stop()
        self.env.stop()
        self.db.close()
        self.engine.dispose()

    def accept(self, request):
        self.assertEqual(str(request.url), "https://api.resend.com/emails")
        self.assertEqual(request.headers["authorization"], "Bearer isolated-unit-key")
        self.payloads.append(json.loads(request.content))
        return httpx.Response(200, json={"id": "isolated-unit-message"})

    def use_transport(self, handler):
        if hasattr(self, "transport_patch"):
            self.transport_patch.stop()
        self.transport_patch = patch.object(mailer.httpx, "AsyncClient",
            side_effect=lambda **kwargs: self.client_class(transport=httpx.MockTransport(handler), **kwargs))
        self.transport_patch.start()

    async def request_code(self, email=None, purpose="login", **agreements):
        return await main.request_member_code(main.CodeRequest(email=email or self.member.email,
            purpose=purpose, **agreements), self.request, self.db)

    def sent_code(self):
        return self.payloads[-1]["text"].split("Ton code KINQ : ")[1].split("\n")[0]

    async def test_login_uses_branded_resend_and_consumes_normal_challenge(self):
        self.assertEqual(await self.request_code(), {"ok": True, "delivery": "email"})
        payload = self.payloads[0]
        self.assertEqual(payload["from"], "Kinq Team <verified@example.test>")
        self.assertEqual(payload["to"], [self.member.email])
        self.assertIn("connexion", payload["subject"])
        self.assertIn("#b2ff1a", payload["html"])
        self.assertIn("#171916", payload["html"])
        self.assertIn('src="cid:kinq-logo"', payload["html"])
        attachment = payload["attachments"][0]
        self.assertEqual(attachment["content_id"], "kinq-logo")
        self.assertEqual(attachment["filename"], "kinq-logo.png")
        self.assertEqual(base64.b64decode(attachment["content"]),
                         (Path(mailer.__file__).parent / "templates/kinq-logo.png").read_bytes())
        code = self.sent_code()
        self.assertIn(code, payload["html"])
        challenge = self.db.get(main.MemberCode, self.member.email)
        self.assertEqual(challenge.digest, main.code_digest(self.member.email, code))
        self.assertNotEqual(challenge.digest, code)
        self.assertAlmostEqual((challenge.expires_at - challenge.sent_at).total_seconds(), 600)
        result = main.verify_member_code(main.CodeVerify(email=self.member.email, code=code), self.request, self.db)
        self.assertEqual(result["id"], self.member.id)
        self.assertEqual(self.request.session["member_id"], self.member.id)
        self.assertTrue(self.request.session["member_csrf"])
        self.assertIsNone(self.db.get(main.MemberCode, self.member.email))
        with self.assertRaises(HTTPException):
            main.verify_member_code(main.CodeVerify(email=self.member.email, code=code), self.request, self.db)

    async def test_signup_without_existing_member_is_verified_before_creation(self):
        email = "new@example.test"
        self.assertEqual(await self.request_code(email, "signup", adult=True, terms=True, charter=True),
            {"ok": True, "delivery": "email"})
        self.assertIsNone(self.db.scalar(select(main.Member).where(main.Member.email == email)))
        self.assertIn("créer ton compte", self.payloads[0]["subject"])
        result = main.verify_member_code(main.CodeVerify(email=email, code=self.sent_code()), self.request, self.db)
        created = self.db.get(main.Member, result["id"])
        self.assertEqual(created.email, email)
        self.assertIsNotNone(self.db.get(main.MemberConsent, created.id))

    async def test_signup_requires_all_three_agreements_before_sending(self):
        for missing in ("adult", "terms", "charter"):
            agreements = {key: key != missing for key in ("adult", "terms", "charter")}
            with self.assertRaises(HTTPException) as error:
                await self.request_code("new@example.test", "signup", **agreements)
            self.assertEqual(error.exception.status_code, 400)
        self.assertEqual(self.payloads, [])

    async def test_ineligible_requests_remain_neutral_without_delivery(self):
        self.assertEqual(await self.request_code("absent@example.test"), {"ok": True})
        self.assertEqual(await self.request_code(purpose="signup", adult=True, terms=True, charter=True), {"ok": True})
        self.member.status = "banned"
        self.db.commit()
        self.assertEqual(await self.request_code(), {"ok": True})
        self.assertEqual(self.payloads, [])

    async def test_provisioned_credential_uses_normal_session_without_any_email(self):
        code = "234567"  # Isolated test credential; never provisioned in a runtime.
        self.db.add(main.MemberLoginCode(member_id=self.member.id,
            digest=main.code_digest(self.member.email, code)))
        self.db.commit()
        with patch.dict(os.environ, {"KINQ_RESEND_API_KEY": ""}):
            self.assertEqual(await self.request_code(), {"ok": True, "delivery": "configured_code"})
        self.assertEqual(self.payloads, [])
        main.verify_member_code(main.CodeVerify(email=self.member.email, code=code), self.request, self.db)
        self.assertEqual(self.request.session["member_id"], self.member.id)

    async def test_missing_key_creates_no_challenge(self):
        with patch.dict(os.environ, {"KINQ_RESEND_API_KEY": ""}):
            with self.assertRaises(HTTPException) as error:
                await self.request_code()
        self.assertEqual(error.exception.status_code, 503)
        self.assertIsNone(self.db.get(main.MemberCode, self.member.email))

    async def test_provider_rejections_do_not_create_challenge_or_leak_details(self):
        for status, data in ((403, {"message": "private-provider-diagnostic"}), (429, {}),
                             (200, {}), (200, [])):
            self.use_transport(lambda request: httpx.Response(status, json=data))
            with self.assertRaises(HTTPException) as error:
                await self.request_code()
            self.assertEqual(error.exception.status_code, 502)
            self.assertNotIn("private-provider-diagnostic", error.exception.detail)
            self.assertIsNone(self.db.get(main.MemberCode, self.member.email))

    async def test_network_timeout_keeps_previous_challenge_usable(self):
        await self.request_code()
        previous = self.db.get(main.MemberCode, self.member.email)
        old_digest = previous.digest
        previous.sent_at = datetime.now(timezone.utc) - timedelta(seconds=61)
        self.db.commit()
        def timeout(request):
            raise httpx.ReadTimeout("isolated", request=request)
        self.use_transport(timeout)
        with self.assertRaises(HTTPException) as error:
            await self.request_code()
        self.assertEqual(error.exception.status_code, 502)
        self.db.expire_all()
        self.assertEqual(self.db.get(main.MemberCode, self.member.email).digest, old_digest)

    async def test_resend_throttle_preserves_code_and_does_not_send_twice(self):
        await self.request_code()
        with self.assertRaises(HTTPException) as error:
            await self.request_code()
        self.assertEqual(error.exception.status_code, 429)
        self.assertEqual(len(self.payloads), 1)

    async def test_expiry_and_five_attempt_limit_still_apply(self):
        await self.request_code()
        valid = self.sent_code()
        wrong = "111111" if valid != "111111" else "222222"
        for _ in range(5):
            with self.assertRaises(HTTPException):
                main.verify_member_code(main.CodeVerify(email=self.member.email, code=wrong), self.request, self.db)
        with self.assertRaises(HTTPException):
            main.verify_member_code(main.CodeVerify(email=self.member.email, code=valid), self.request, self.db)
        challenge = self.db.get(main.MemberCode, self.member.email)
        challenge.attempts = 0
        challenge.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        self.db.commit()
        with self.assertRaises(HTTPException):
            main.verify_member_code(main.CodeVerify(email=self.member.email, code=valid), self.request, self.db)

    async def test_email_change_reuses_branding_and_binds_to_member(self):
        email = "changed@example.test"
        await main.request_email_change(main.EmailChange(email=email), self.member, self.db)
        self.assertEqual(self.payloads[0]["from"], "Kinq Team <verified@example.test>")
        self.assertIn("nouvelle adresse", self.payloads[0]["subject"])
        challenge = self.db.get(main.MemberCode, email)
        self.assertEqual(challenge.member_id, self.member.id)
        self.assertEqual(challenge.purpose, "change")
        main.verify_email_change(main.EmailChange(email=email, code=self.sent_code()), self.member, self.db)
        self.db.expire_all()
        self.assertEqual(self.member.email, email)

    def test_sender_uses_requested_name_for_existing_and_plain_mailbox_config(self):
        for configured in ("Legacy name <verified@example.test>", "verified@example.test", ""):
            with patch.dict(os.environ, {"KINQ_RESEND_FROM": configured}):
                expected = "verified@example.test" if configured else "connexion@kinq-app.com"
                self.assertEqual(mailer.resend_sender(), f"Kinq Team <{expected}>")
        with patch.dict(os.environ, {"KINQ_RESEND_FROM": "invalid"}):
            with self.assertRaises(HTTPException): mailer.resend_sender()

    def test_template_rejects_non_code_content(self):
        with self.assertRaises(ValueError): mailer.code_email("<script>", "login")
        with self.assertRaises(ValueError): mailer.code_email("000000", "unknown")


if __name__ == "__main__":
    unittest.main()
