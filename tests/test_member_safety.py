"""Privacy and moderation boundaries in isolated SQL, never against production."""
import os, unittest, uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
os.environ['DATABASE_URL']='sqlite://'
os.environ['KINQ_SESSION_SECRET']='isolated-safety-test-secret-not-for-runtime'
from fastapi import HTTPException
from sqlalchemy import create_engine, event, select, func
from sqlalchemy.orm import Session
from backend.app import main as api

class MemberSafetyTests(unittest.TestCase):
 def setUp(self):
  self.engine=create_engine('sqlite://')
  @event.listens_for(self.engine,'connect')
  def fk(connection,_): connection.execute('PRAGMA foreign_keys=ON')
  api.Base.metadata.create_all(self.engine);self.db=Session(self.engine)
  self.a,self.b,self.c=[api.Member(email=f'safety-{n}@example.test') for n in range(3)]
  self.db.add_all((self.a,self.b,self.c));self.db.flush();now=datetime.now(timezone.utc)
  for m in (self.a,self.b,self.c):
   self.db.add(api.MemberProfile(member_id=m.id,code=f'KQ-SAFE{m.id}',data={'pseudo':'Isolated','age':'32','city':'Paris'}))
  self.db.flush()
  for sender,target in ((self.a,self.b),(self.b,self.a),(self.b,self.c)):
   key=f'{sender.id}-{target.id}'
   self.db.add_all([api.MemberMessage(id='msg'+key,sender_id=sender.id,recipient_id=target.id,body='isolated',nonce=key,created_at=now),
    api.MemberSignal(member_id=sender.id,target_id=f'member-{target.id}',kind='pin'),
    api.MemberNotification(id='notice'+key,actor_id=sender.id,recipient_id=target.id,kind='message',event_key=key,created_at=now),
    api.PhotoAccessRequest(id='grant'+key,owner_id=target.id,requester_id=sender.id,status='accepted')])
  self.db.add_all([api.Photo(id='public',member_id=self.b.id,mime='image/png',data=b'unit',status='approved'),api.Photo(id='private',member_id=self.b.id,mime='image/png',data=b'unit',status='approved')]);self.db.flush()
  self.db.add(api.PrivatePhoto(photo_id='private'));self.db.commit()
 def tearDown(self):self.db.close();self.engine.dispose()
 def count(self,model):return self.db.scalar(select(func.count()).select_from(model))
 def denied(self,fn,status=404):
  with self.assertRaises(HTTPException) as error:fn()
  self.assertEqual(error.exception.status_code,status)
 def test_block_is_reciprocal_and_prevents_contacts_known_ids_and_photo_grants(self):
  self.assertEqual(api.block_member(self.b.id,self.a,self.db),{'ok':True})
  api.block_member(self.b.id,self.a,self.db);self.assertEqual(self.count(api.MemberBlock),1)
  for first,second in ((self.a,self.b),(self.b,self.a)):
   self.assertNotIn(f'member-{second.id}',[p['id'] for p in api.public_profiles(first,self.db)])
   self.assertNotIn(f'member-{second.id}',[p['id'] for p in api.conversations(first,self.db)])
   self.denied(lambda:api.messages(second.id,first,self.db))
   self.denied(lambda:api.send_message(second.id,api.MessageEdit(body='blocked',nonce=uuid.uuid4()),first,self.db))
   self.denied(lambda:api.set_member_signal(api.SignalEdit(kind='hook',target_id=f'member-{second.id}',active=True),first,self.db))
   self.denied(lambda:api.request_photo_access(second.id,first,self.db))
   self.denied(lambda:api.visit_member_profile(second.id,first,self.db))
  self.denied(lambda:api.private_photo('private',self.a,self.db))
  self.denied(lambda:api.public_photo('public',SimpleNamespace(session={'member_id':self.a.id}),self.db))
  self.assertEqual(api.public_photo('public',SimpleNamespace(session={'member_id':self.c.id}),self.db).body,b'unit')
  self.assertEqual(api.get_member_signals(self.a,self.db),{'pins':[],'hooks':[]})
  self.assertEqual(api.member_notifications(self.a,self.db)['unreadCount'],0)
  self.assertEqual(self.count(api.PhotoAccessRequest),1);self.assertEqual(self.count(api.MemberMessage),3)
  self.assertIn(f'member-{self.c.id}',[p['id'] for p in api.conversations(self.b,self.db)])
 def test_unblock_is_owned_and_does_not_restore_revoked_grants_or_signals(self):
  api.block_member(self.b.id,self.a,self.db);api.block_member(self.a.id,self.b,self.db)
  api.unblock_member(self.b.id,self.c,self.db);self.assertEqual(self.count(api.MemberBlock),2)
  api.unblock_member(self.b.id,self.a,self.db);self.denied(lambda:api.messages(self.b.id,self.a,self.db))
  self.assertEqual(api.member_blocks(self.b,self.db),[{'id':f'member-{self.a.id}','name':'Isolated'}])
  api.unblock_member(self.a.id,self.b,self.db)
  self.assertEqual(len(api.messages(self.b.id,self.a,self.db)),2)
  self.denied(lambda:api.private_photo('private',self.a,self.db))
  self.assertEqual(api.get_member_signals(self.a,self.db)['pins'],[])
 def test_signalement_is_persisted_idempotent_validated_and_inaccessible_after_block(self):
  body=api.ReportEdit(reason='harassment',detail='isolated unit report',nonce=uuid.uuid4())
  self.assertEqual(api.report_member(self.b.id,body,self.a,self.db),{'ok':True,'status':'pending'})
  api.report_member(self.b.id,body,self.a,self.db);self.assertEqual(self.count(api.MemberReport),1)
  self.denied(lambda:api.report_member(self.c.id,body,self.a,self.db),409)
  self.denied(lambda:api.report_member(self.b.id,api.ReportEdit(reason='other',nonce=uuid.uuid4()),self.a,self.db),400)
  self.denied(lambda:api.report_member(self.a.id,body,self.a,self.db))
  self.assertEqual(len(api.member_report_queue(None,self.db)),1)
  self.assertEqual(api.member_notifications(self.b,self.db)['unreadCount'],1) # Existing message only; no report notification.
  api.block_member(self.b.id,self.a,self.db);self.denied(lambda:api.report_member(self.b.id,body,self.a,self.db))
 def test_presence_uses_real_timestamp_and_hides_discreet_and_unknown_members(self):
  profile=self.db.get(api.MemberProfile,self.b.id)
  self.assertIsNone(api.profile_projection(profile,self.b,self.db,self.a)['lastSeenAt'])
  stamp=datetime.now(timezone.utc)-timedelta(minutes=12)
  self.db.add(api.MemberActivity(member_id=self.b.id,seen_at=stamp));self.db.commit()
  result=api.profile_projection(profile,self.b,self.db,self.a)
  self.assertFalse(result['online']);self.assertEqual(result['lastSeenAt'],stamp.isoformat(timespec='seconds'))
  profile.data=dict(profile.data,discreet=True);self.db.commit()
  result=api.profile_projection(profile,self.b,self.db,self.a)
  self.assertIsNone(result['lastSeenAt']);self.assertFalse(result['online'])
 def test_erasure_removes_blocks_and_reports_without_deleting_unrelated_pairs(self):
  api.block_member(self.b.id,self.a,self.db)
  api.report_member(self.c.id,api.ReportEdit(reason='spam',nonce=uuid.uuid4()),self.b,self.db)
  api.report_member(self.c.id,api.ReportEdit(reason='spam',nonce=uuid.uuid4()),self.a,self.db)
  api.erase_member(self.db,self.a);self.db.commit()
  self.assertEqual(self.count(api.MemberBlock),0);self.assertEqual(self.count(api.MemberReport),1)
  self.assertEqual(self.db.scalar(select(api.MemberReport)).reporter_id,self.b.id)

if __name__=='__main__':unittest.main()
