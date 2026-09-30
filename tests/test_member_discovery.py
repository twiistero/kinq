"""Regression tests only: isolated SQLite; never a product/demo data source."""
import os
import unittest
os.environ['DATABASE_URL'] = 'sqlite://'
os.environ['KINQ_SESSION_SECRET'] = 'isolated-unit-test-secret-not-for-runtime'
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.main import (Base, Member, MemberProfile, MemberSignal, DemoProfile,
    SignalEdit, public_profiles, get_member_signals, set_member_signal)

class MemberDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite://')
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.member = Member(email='unit@example.test')
        self.db.add(self.member); self.db.flush()
        self.db.add(MemberProfile(member_id=self.member.id, code='KQ-UNIT', data={'pseudo':'Unit','age':'32','city':'Paris','hideCity':True}))
        self.db.add(DemoProfile(id='alex', data={'id':'alex','name':'Legacy fixture'}))
        self.db.add(MemberSignal(member_id=self.member.id, target_id='alex', kind='pin'))
        self.db.commit()
    def tearDown(self):
        self.db.close(); self.engine.dispose()
    def test_only_persisted_members_are_discoverable(self):
        result = public_profiles(self.member, self.db)
        self.assertEqual([p['id'] for p in result], [f'member-{self.member.id}'])
        self.assertEqual(result[0]['city'], '')
        self.assertEqual(get_member_signals(self.member, self.db), {'pins':[], 'hooks':[]})
    def test_legacy_fixture_cannot_receive_a_signal(self):
        with self.assertRaises(HTTPException) as raised:
            set_member_signal(SignalEdit(kind='hook', target_id='alex', active=True), self.member, self.db)
        self.assertEqual(raised.exception.status_code, 400)

class ConfiguredLoginTests(MemberDiscoveryTests):
    def test_configured_code_uses_normal_challenge_and_session(self):
        import asyncio
        from unittest.mock import patch
        from starlette.requests import Request
        from backend.app.main import (MemberLoginCode, MemberCode, CodeRequest, CodeVerify,
            code_digest, request_member_code, verify_member_code, PUBLIC_ORIGIN)
        self.db.add(MemberLoginCode(member_id=self.member.id, digest=code_digest(self.member.email, '123456')))
        self.db.commit()
        request = Request({'type':'http', 'headers':[(b'origin', PUBLIC_ORIGIN.encode())], 'session':{}})
        with patch('backend.app.main.httpx.AsyncClient', side_effect=AssertionError('No email for a configured credential')):
            result = asyncio.run(request_member_code(CodeRequest(email=self.member.email, purpose='login'), request, self.db))
        self.assertEqual(result['delivery'], 'configured_code')
        with self.assertRaises(HTTPException):
            verify_member_code(CodeVerify(email=self.member.email, code='000000'), request, self.db)
        self.assertEqual(self.db.get(MemberCode, self.member.email).attempts, 1)
        result = verify_member_code(CodeVerify(email=self.member.email, code='123456'), request, self.db)
        self.assertEqual(result['id'], self.member.id)
        self.assertEqual(request.session['member_id'], self.member.id)
        self.assertTrue(request.session['member_csrf'])
        self.assertIsNone(self.db.get(MemberCode, self.member.email))
        with self.assertRaises(HTTPException):
            verify_member_code(CodeVerify(email=self.member.email, code='123456'), request, self.db)
        # A fresh challenge allows the same provisioned account to log in again.
        asyncio.run(request_member_code(CodeRequest(email=self.member.email, purpose='login'), request, self.db))
        self.assertTrue(verify_member_code(CodeVerify(email=self.member.email, code='123456'), request, self.db)['ok'])

    def test_other_account_does_not_accept_the_configured_code(self):
        import asyncio
        from unittest.mock import patch
        from starlette.requests import Request
        from backend.app.main import CodeRequest, CodeVerify, request_member_code, verify_member_code, PUBLIC_ORIGIN
        request = Request({'type':'http', 'headers':[(b'origin', PUBLIC_ORIGIN.encode())], 'session':{}})
        with patch.dict(os.environ, {'KINQ_RESEND_API_KEY':''}):
            with self.assertRaises(HTTPException) as raised:
                asyncio.run(request_member_code(CodeRequest(email=self.member.email, purpose='login'), request, self.db))
            self.assertEqual(raised.exception.status_code, 503)
        with self.assertRaises(HTTPException):
            verify_member_code(CodeVerify(email=self.member.email, code='123456'), request, self.db)
        self.assertNotIn('member_id', request.session)

if __name__ == '__main__': unittest.main()
