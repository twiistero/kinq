"""Isolated account erasure and email verification; never use production members."""
import os
import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
os.environ['DATABASE_URL'] = 'sqlite://'
os.environ['KINQ_SESSION_SECRET'] = 'isolated-account-test-secret-not-for-runtime'
from fastapi import HTTPException
from sqlalchemy import create_engine, event, select, func
from sqlalchemy.orm import Session
from backend.app.main import (Base, Member, MemberProfile, MemberLoginCode, MemberCode,
    MemberConsent, MemberActivity, MemberLocation, MemberSignal, MemberMessage,
    MemberNotification, Photo, PrivatePhoto, PhotoAccessRequest, Article, Comment,
    erase_member, close_member_account, verify_email_change, EmailChange, code_digest)

class MemberAccountTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite://')
        @event.listens_for(self.engine, 'connect')
        def foreign_keys(connection, _): connection.execute('PRAGMA foreign_keys=ON')
        Base.metadata.create_all(self.engine); self.db = Session(self.engine)
        self.members = [Member(email=f'account-{n}@example.test', name=f'Unit {n}') for n in range(3)]
        self.db.add_all(self.members); self.db.flush()
        self.a, self.b, self.c = self.members
        now = datetime.now(timezone.utc)
        for member in self.members:
            self.db.add_all([
                MemberProfile(member_id=member.id, code=f'KQ-U{member.id}', data={'pseudo': 'Unit'}),
                MemberConsent(member_id=member.id, accepted_at=now, version='unit'),
                MemberActivity(member_id=member.id, seen_at=now),
                MemberLocation(member_id=member.id, latitude=0, longitude=0, accuracy=10, updated_at=now),
                MemberLoginCode(member_id=member.id, digest='unit'),
                MemberCode(email=member.email, purpose='login', digest='unit', expires_at=now+timedelta(minutes=10), sent_at=now),
                Photo(id=f'photo-{member.id}', member_id=member.id, mime='image/jpeg', data=b'unit', status='approved')])
        self.db.flush()
        self.db.add(PrivatePhoto(photo_id=f'photo-{self.a.id}'))
        self.db.add(MemberCode(email='new-address@example.test', member_id=self.a.id, purpose='change', digest='unit', expires_at=now+timedelta(minutes=10), sent_at=now))
        for sender, recipient in ((self.a,self.b),(self.b,self.a),(self.b,self.c)):
            key=f'{sender.id}-{recipient.id}'
            self.db.add_all([
                MemberMessage(id='message-'+key, sender_id=sender.id, recipient_id=recipient.id, body='isolated', nonce=key, created_at=now),
                MemberSignal(member_id=sender.id, target_id=f'member-{recipient.id}', kind='hook'),
                MemberSignal(member_id=sender.id, target_id=f'member-{recipient.id}', kind='pin'),
                MemberNotification(id='notice-'+key, actor_id=sender.id, recipient_id=recipient.id, kind='message', event_key=key, created_at=now),
                PhotoAccessRequest(id='access-'+key, owner_id=recipient.id, requester_id=sender.id)])
        article=Article(slug='unit', title='Unit'); self.db.add(article); self.db.flush()
        for member in (self.a,self.b): self.db.add(Comment(article_id=article.id, member_id=member.id, body='isolated'))
        self.db.commit()
    def tearDown(self): self.db.close(); self.engine.dispose()
    def count(self, model): return self.db.scalar(select(func.count()).select_from(model))
    def test_confirmed_erasure_removes_content_in_both_directions_and_preserves_other_pairs(self):
        request=SimpleNamespace(session={'member_id':self.a.id, 'csrf':'unit'})
        self.assertEqual(close_member_account(request, self.a, self.db), {'ok':True})
        self.assertEqual(request.session, {})
        self.db.expire_all()
        for model in (MemberProfile,MemberConsent,MemberActivity,MemberLocation,MemberLoginCode):
            self.assertIsNone(self.db.get(model,self.a.id)); self.assertIsNotNone(self.db.get(model,self.b.id))
        self.assertEqual(self.count(MemberCode),2)
        self.assertEqual(self.count(MemberSignal),2)
        for model in (MemberMessage,MemberNotification,PhotoAccessRequest,Comment): self.assertEqual(self.count(model),1)
        self.assertEqual(self.count(Photo),2); self.assertEqual(self.count(PrivatePhoto),0)
        message=self.db.scalar(select(MemberMessage))
        self.assertEqual((message.sender_id,message.recipient_id),(self.b.id,self.c.id))
        deleted=self.db.get(Member,self.a.id)
        self.assertEqual(deleted.email,f'deleted-{deleted.id}@invalid.local')
        self.assertEqual(deleted.name,''); self.assertEqual(deleted.status,'deleted')
    def test_erasure_is_one_transaction_and_can_be_rolled_back(self):
        erase_member(self.db,self.a); self.db.flush(); self.db.rollback(); self.db.expire_all()
        self.assertEqual(self.a.status,'active'); self.assertEqual(self.count(MemberMessage),3)
        self.assertEqual(self.count(Photo),3); self.assertEqual(self.count(PrivatePhoto),1)
        self.assertIsNotNone(self.db.get(MemberProfile,self.a.id))
    def challenge(self):
        value=self.db.get(MemberCode,'new-address@example.test')
        value.digest=code_digest(value.email,'654321'); self.db.commit(); return value
    def test_email_requires_the_bound_valid_code_and_consumes_it_after_persistence(self):
        challenge=self.challenge(); old=self.a.email
        with self.assertRaises(HTTPException): verify_email_change(EmailChange(email=challenge.email,code='654321'),self.b,self.db)
        with self.assertRaises(HTTPException): verify_email_change(EmailChange(email=challenge.email,code='123456'),self.a,self.db)
        self.db.expire_all(); self.assertEqual(self.a.email,old)
        self.assertEqual(verify_email_change(EmailChange(email=challenge.email,code='654321'),self.a,self.db), {'ok':True})
        self.db.expire_all(); self.assertEqual(self.a.email,'new-address@example.test')
        self.assertIsNone(self.db.get(MemberCode,'new-address@example.test'))
        with self.assertRaises(HTTPException): verify_email_change(EmailChange(email=self.a.email,code='654321'),self.a,self.db)
    def test_email_attempt_limit_preserves_the_original_address(self):
        challenge=self.challenge(); old=self.a.email
        for _ in range(5):
            with self.assertRaises(HTTPException): verify_email_change(EmailChange(email=challenge.email,code='000000'),self.a,self.db)
        with self.assertRaises(HTTPException): verify_email_change(EmailChange(email=challenge.email,code='654321'),self.a,self.db)
        self.db.expire_all(); self.assertEqual(self.a.email,old)

if __name__ == '__main__': unittest.main()
