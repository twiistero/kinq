"""Private-photo consent and visibility, isolated SQLite only."""
import os
import unittest
import uuid
from types import SimpleNamespace
os.environ['DATABASE_URL'] = 'sqlite://'
os.environ['KINQ_SESSION_SECRET'] = 'isolated-unit-test-secret-not-for-runtime'
from fastapi import HTTPException
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from backend.app.main import (Base, Member, MemberProfile, Photo, PrivatePhoto, PhotoAccessRequest, MemberNotification,
    PhotoAccessDecision, get_photo_access, request_photo_access, received_photo_requests, decide_photo_access,
    private_photo, public_photo, public_profiles, member_notifications)

class PhotoAccessTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite://')
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.owner = Member(email='unit-owner@example.test')
        self.viewer = Member(email='unit-viewer@example.test')
        self.other = Member(email='unit-other@example.test')
        self.db.add_all([self.owner, self.viewer, self.other]); self.db.flush()
        for member in (self.owner, self.viewer, self.other):
            self.db.add(MemberProfile(member_id=member.id, code='KQ-TEST' + str(member.id), data={'pseudo':'Test', 'age':'32'}))
        self.public = Photo(id=str(uuid.uuid4()), member_id=self.owner.id, mime='image/png', data=b'public', status='approved')
        self.private = Photo(id=str(uuid.uuid4()), member_id=self.owner.id, mime='image/png', data=b'private', status='approved')
        self.db.add_all([self.public, self.private]); self.db.flush()
        self.db.add(PrivatePhoto(photo_id=self.private.id)); self.db.commit()
    def tearDown(self):
        self.db.close(); self.engine.dispose()
    def assertDenied(self, action):
        with self.assertRaises(HTTPException) as failure: action()
        self.assertEqual(failure.exception.status_code, 404)
    def request(self): return request_photo_access(self.owner.id, self.viewer, self.db)
    def decide(self, result, status, member=None):
        return decide_photo_access(uuid.UUID(result['id']), PhotoAccessDecision(status=status), member or self.owner, self.db)
    def test_private_photo_never_leaks_via_public_routes_or_notification_portraits(self):
        profile = next(p for p in public_profiles(self.viewer, self.db) if p['id'] == f'member-{self.owner.id}')
        self.assertEqual(profile['photos'], ['/api/photos/' + self.public.id])
        self.assertEqual(public_photo(self.public.id, SimpleNamespace(session={}), self.db).body, b'public')
        self.assertDenied(lambda: public_photo(self.private.id, SimpleNamespace(session={}), self.db))
        result = self.request(); self.decide(result, 'accepted')
        notice = member_notifications(self.viewer, self.db)['items'][0]
        self.assertEqual(notice['photo'], '/api/photos/' + self.public.id)
    def test_request_is_persisted_and_idempotent_then_owner_can_accept_and_revoke(self):
        self.assertEqual(get_photo_access(self.owner.id, self.viewer, self.db)['status'], 'none')
        result = self.request()
        self.assertEqual(self.request()['id'], result['id'])
        self.db.expire_all()
        self.assertEqual(get_photo_access(self.owner.id, self.viewer, self.db)['status'], 'pending')
        self.assertEqual(self.db.scalar(select(func.count()).select_from(PhotoAccessRequest)), 1)
        self.assertEqual(self.db.scalar(select(func.count()).select_from(MemberNotification)), 1)
        self.assertDenied(lambda: private_photo(self.private.id, self.viewer, self.db))
        self.assertDenied(lambda: self.decide(result, 'accepted', self.other))
        self.decide(result, 'accepted')
        access = get_photo_access(self.owner.id, self.viewer, self.db)
        self.assertEqual(access['photos'], ['/api/member/private-photos/' + self.private.id])
        response = private_photo(self.private.id, self.viewer, self.db)
        self.assertEqual(response.body, b'private'); self.assertIn('no-store', response.headers['cache-control'])
        self.assertDenied(lambda: private_photo(self.private.id, self.other, self.db))
        self.decide(result, 'declined')
        self.assertEqual(get_photo_access(self.owner.id, self.viewer, self.db)['photos'], [])
        self.assertDenied(lambda: private_photo(self.private.id, self.viewer, self.db))
        self.assertEqual(self.request()['status'], 'declined', 'Repeated taps cannot bypass a refusal')
    def test_no_self_request_invisible_owner_or_unapproved_photo(self):
        self.assertDenied(lambda: request_photo_access(self.owner.id, self.owner, self.db))
        result = self.request(); self.decide(result, 'accepted')
        self.private.status = 'pending'; self.db.commit()
        self.assertEqual(get_photo_access(self.owner.id, self.viewer, self.db)['photos'], [])
        self.assertDenied(lambda: private_photo(self.private.id, self.viewer, self.db))
        profile = self.db.get(MemberProfile, self.owner.id); profile.data = {**profile.data, 'invisible': True}; self.db.commit()
        self.assertDenied(lambda: get_photo_access(self.owner.id, self.viewer, self.db))
        self.assertDenied(lambda: private_photo(self.private.id, self.owner, self.db))
    def test_request_notification_identifies_discreet_sender_without_exposing_photo(self):
        profile = self.db.get(MemberProfile, self.viewer.id); profile.data = {**profile.data, 'discreet': True}; self.db.commit()
        self.request()
        notice = member_notifications(self.owner, self.db)['items'][0]
        self.assertEqual(notice['actorID'], f'member-{self.viewer.id}'); self.assertIsNone(notice['photo'])
        self.assertEqual(received_photo_requests(self.other, self.db), [])
        self.assertEqual(len(received_photo_requests(self.owner, self.db)), 1)
    def test_grant_stops_working_when_owner_is_banned(self):
        result = self.request(); self.decide(result, 'accepted')
        self.owner.status = 'banned'; self.db.commit()
        self.assertDenied(lambda: private_photo(self.private.id, self.viewer, self.db))

if __name__ == '__main__': unittest.main()
