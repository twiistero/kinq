"""Provision the owner-authorized QA member, using the normal member/profile tables.

Run inside the API container: python < ensure_test_member.py
Idempotent: preserves an existing profile, permissions and account status.
Provisions only the owner-requested login code digest; no session or consent fabrication.
"""
import json
import secrets
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.main import Member, MemberProfile, MemberLoginCode, ProfileEdit, engine, effective_member_status, code_digest

EMAIL = "test@kinq-app.com"
# Explicit owner instruction; this credential belongs only to this member.
CODE = "123456"
with Session(engine) as db:
    member = db.scalar(select(Member).where(Member.email == EMAIL))
    if member is None:
        member = Member(email=EMAIL, name="Test KINQ")
        db.add(member)
        db.flush()
    if effective_member_status(member) != "active":
        raise RuntimeError("Existing test member is not active; do not bypass moderation")
    profile = db.get(MemberProfile, member.id)
    if profile is None:
        data = ProfileEdit(data={
            "pseudo": "Test KINQ", "age": "32", "city": "Paris",
            "bio": "Compte de test officiel KINQ pour vérifier le site et l’app iOS. Ce compte ne recherche pas de rencontres.",
            "style": ["Leather"], "practice": [],
            "kinkPreferences": {"version": 1, "items": [{"id": "leather", "role": "wear"}], "combinations": []},
            "wishes": "Vérifier les parcours, les préférences et leur sauvegarde.",
            "limits": "Compte réservé aux tests techniques.",
            "discreet": True, "hideCity": True, "hideLimits": True, "invisible": False,
        }).model_dump()["data"]
        profile = MemberProfile(member_id=member.id, code="KQ-" + secrets.token_hex(4).upper(), data=data)
        db.add(profile)
    credential = db.get(MemberLoginCode, member.id)
    if credential is None:
        db.add(MemberLoginCode(member_id=member.id, digest=code_digest(EMAIL, CODE)))
    elif credential.digest != code_digest(EMAIL, CODE):
        raise RuntimeError("Existing credential differs; do not silently reset it")
    db.commit()
    print(json.dumps({"email": member.email, "member_id": member.id, "status": member.status,
                      "profile_code": profile.code, "pseudo": profile.data.get("pseudo"),
                      "database": engine.dialect.name}, ensure_ascii=False))
