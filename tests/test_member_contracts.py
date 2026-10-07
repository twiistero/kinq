"""Isolated ownership, handoff, persistence and signature checks; no real email."""
import base64
import time
import unittest
from unittest.mock import patch

import httpx
from fastapi import FastAPI, HTTPException, Request
from sqlalchemy import String, Integer, select
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from tests.test_contracts import draft
from backend.app import contracts as service, member_contracts as copies


class IsolatedMember(service.ContractBase):
    __tablename__ = "isolated_contract_test_members"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="active")


class MemberContractTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool)
        service.ContractBase.metadata.create_all(self.engine)
        self.sessions=sessionmaker(self.engine)
        with self.sessions() as db:
            db.add_all([IsolatedMember(id=i,email=f"person{i}@example.test",status="active") for i in [1,2,3]])
            db.commit()
        def member(request:Request):
            value=request.headers.get("x-isolated-member")
            if not value: raise HTTPException(401,"Session requise")
            with self.sessions() as db: return db.get(IsolatedMember,int(value))
        app=FastAPI()
        service.install_contract_routes(app,self.sessions,on_signed=lambda db,c:copies.archive_known_members(db,c,IsolatedMember))
        copies.install_member_contract_routes(app,self.sessions,member,IsolatedMember)
        self.client=httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url=service.PUBLIC_ORIGIN,headers={"Origin":service.PUBLIC_ORIGIN})
        self.mail=[]
        async def send(email,*args,**kwargs):self.mail.append((email,kwargs))
        self.patcher=patch.object(service,"send_contract_email",send);self.patcher.start()

    async def asyncTearDown(self):
        self.patcher.stop();await self.client.aclose();self.engine.dispose()

    def owner(self,value):return {"x-isolated-member":str(value)}

    async def test_print_is_encrypted_persistent_deduplicated_and_owner_only(self):
        response=await self.client.post('/api/member/contracts/print',json={"document":draft()},headers=self.owner(1))
        self.assertEqual(response.status_code,201);copy_id=response.json()['id']
        same=await self.client.post('/api/member/contracts/print',json={"document":draft()},headers=self.owner(1))
        self.assertEqual(copy_id,same.json()['id'])
        for suffix in ['', '/pdf']:
            self.assertEqual((await self.client.get('/api/member/contracts/'+copy_id+suffix,headers=self.owner(2))).status_code,404)
        self.assertEqual((await self.client.get('/api/member/contracts')).status_code,401)
        pdf=await self.client.get('/api/member/contracts/'+copy_id+'/pdf',headers=self.owner(1))
        self.assertTrue(pdf.content.startswith(b'%PDF'));self.assertIn('no-store',pdf.headers['Cache-Control'])
        with self.sessions() as db:
            row=db.get(copies.SavedContract,copy_id)
            self.assertNotIn('Premier pseudo',row.content);self.assertNotIn('%PDF',row.pdf)
        await self.client.delete('/api/member/contracts/'+copy_id,headers=self.owner(1))
        self.assertEqual((await self.client.get('/api/member/contracts',headers=self.owner(1))).json(),[])
        restored=await self.client.post('/api/member/contracts/print',json={"document":draft()},headers=self.owner(1))
        self.assertEqual(restored.json()['id'],copy_id)
        self.assertTrue((await self.client.get('/api/member/contracts/'+copy_id+'/pdf',headers=self.owner(1))).content.startswith(b'%PDF'))

    async def test_handoff_survives_login_is_one_time_and_expires(self):
        response=await self.client.post('/api/contracts/account-draft',json={"document":draft()})
        self.assertEqual(response.status_code,201);token=response.json()['token']
        body={"draftToken":token}
        self.assertEqual((await self.client.post('/api/member/contracts/claim',json=body)).status_code,401)
        first=await self.client.post('/api/member/contracts/claim',json=body,headers=self.owner(1))
        self.assertEqual(first.status_code,200)
        self.assertEqual((await self.client.post('/api/member/contracts/claim',json=body,headers=self.owner(2))).status_code,404)
        token=(await self.client.post('/api/contracts/account-draft',json={"document":draft()})).json()['token']
        with self.sessions() as db:
            row=db.get(copies.AccountDraft,service.digest(token));row.expires_at=1;db.commit()
        self.assertEqual((await self.client.post('/api/member/contracts/claim',json={"draftToken":token},headers=self.owner(1))).status_code,404)

    async def test_two_account_signatures_archive_identical_pdf_and_keep_after_link_expiry(self):
        response=await self.client.post('/api/contracts',json={"document":draft(),"emailA":"person1@example.test","emailB":"person2@example.test","processing":True})
        contract_id=response.json()['id']
        self.assertEqual(len((await self.client.get('/api/member/contracts',headers=self.owner(1))).json()),1)
        self.assertEqual((await self.client.get('/api/member/contracts/'+contract_id,headers=self.owner(3))).status_code,404)
        for owner in [1,2]:
            value=(await self.client.get('/api/member/contracts/'+contract_id,headers=self.owner(owner))).json()
            response=await self.client.post('/api/member/contracts/'+contract_id+'/sign',headers=self.owner(owner),json={
                "name":value['document']['nameA' if owner==1 else 'nameB'],"contentHash":value['contentHash'],"accepted":True})
            self.assertEqual(response.status_code,200,response.text)
        lists=[(await self.client.get('/api/member/contracts',headers=self.owner(i))).json() for i in [1,2]]
        self.assertTrue(all(len(rows)==1 and rows[0]['status']=='signed' for rows in lists))
        completed=(await self.client.get('/api/member/contracts/'+contract_id,headers=self.owner(1))).json()
        self.assertEqual(completed['id'],lists[0][0]['id'])
        pdfs=[(await self.client.get('/api/member/contracts/'+rows[0]['id']+'/pdf',headers=self.owner(i+1))).content for i,rows in enumerate(lists)]
        self.assertEqual(pdfs[0],pdfs[1]);self.assertEqual(len(self.mail),2)
        self.assertTrue(all(message[1]['pdf']==pdfs[0] for message in self.mail))
        with self.sessions() as db:
            db.get(service.Contract,contract_id).expires_at=1;db.commit();service.cleanup(db)
        self.assertEqual((await self.client.get('/api/member/contracts/'+lists[0][0]['id']+'/pdf',headers=self.owner(1))).content,pdfs[0])
        await self.client.delete('/api/member/contracts/'+lists[0][0]['id'],headers=self.owner(1))
        self.assertEqual(len((await self.client.get('/api/member/contracts',headers=self.owner(2))).json()),1)

    async def test_expired_or_wrong_signer_access_cannot_claim(self):
        for body in [{"contractId":"missing","access":"wrong"},{"draftToken":"wrong"},{"draftToken":"wrong","contractId":"missing","access":"wrong"}]:
            response=await self.client.post('/api/member/contracts/claim',json=body,headers=self.owner(3))
            self.assertIn(response.status_code,[404,422])
        self.assertEqual((await self.client.get('/api/member/contracts',headers=self.owner(3))).json(),[])
