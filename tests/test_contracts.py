"""Isolated agreement API checks. No runtime profile and no real email transmission."""
import copy
import os
import time
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit, parse_qs

os.environ.setdefault("KINQ_SESSION_SECRET","isolated-contract-secret-not-for-runtime")
from fastapi import FastAPI, HTTPException
import httpx
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.app import contracts as service


def draft(model="bdsm"):
    spec=service.MODELS[model]
    return dict(version=service.CATALOGUE["version"],model=model,nameA="Premier pseudo",nameB="Second pseudo",
        roleA=spec["roles"][0],roleB=spec["roles"][1],start="2026-10-06",end="2026-10-20",duration="Deux semaines",
        fields={field["id"]:field["default"] for field in [*service.CATALOGUE["common"],*spec["fields"]]})


class ContractTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool)
        service.ContractBase.metadata.create_all(self.engine)
        self.sessions=sessionmaker(self.engine)
        app=FastAPI();service.install_contract_routes(app,self.sessions)
        self.client=httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url=service.PUBLIC_ORIGIN,
            headers={"Origin":service.PUBLIC_ORIGIN})
        self.emails=[];self.fail_receipt=False
        async def send(email,subject,title,message,**kwargs):
            if kwargs.get("pdf") and self.fail_receipt and email=="second@example.test":
                raise HTTPException(502,"Isolated provider failure")
            self.emails.append((email,kwargs))
        self.patcher=patch.object(service,"send_contract_email",send);self.patcher.start()

    async def asyncTearDown(self):
        self.patcher.stop();await self.client.aclose();self.engine.dispose()

    async def create(self,document=None):
        response=await self.client.post("/api/contracts",json={"document":document or draft(),
            "emailA":"first@example.test","emailB":"second@example.test","processing":True})
        self.assertEqual(response.status_code,201,response.text)
        result=response.json();self.contract_id=result["id"];return result["invitation"]

    def headers(self,token,verified=False):
        return {"Authorization":"Bearer "+token,**({"X-Contract-Access":"verified"} if verified else {})}

    async def verify(self,token,email):
        base=f"/api/contracts/{self.contract_id}"
        response=await self.client.post(base+"/code",headers=self.headers(token),json={"email":email})
        self.assertEqual(response.status_code,200,response.text)
        code=self.emails[-1][1]["code"]
        response=await self.client.post(base+"/verify",headers=self.headers(token),json={"code":code,"processing":True})
        self.assertEqual(response.status_code,200,response.text)
        return response.json()

    async def both(self):
        owner=await self.verify(await self.create(),"first@example.test")
        token=parse_qs(urlsplit(owner["partnerLink"]).fragment)["invitation"][0]
        partner=await self.verify(token,"second@example.test")
        return owner,partner

    async def sign(self,person,name=None,content_hash=None):
        return await self.client.post(f"/api/contracts/{self.contract_id}/sign",headers=self.headers(person["access"]),
            json={"name":name or person["document"]["nameA" if person["slot"]==0 else "nameB"],
                "contentHash":content_hash or person["contentHash"],"accepted":True})

    async def test_private_payload_is_encrypted_and_hidden_before_verification(self):
        token=await self.create();response=await self.client.get(f"/api/contracts/{self.contract_id}",headers=self.headers(token))
        self.assertNotIn("document",response.json());self.assertNotIn("email",response.text)
        self.assertIn("no-store",response.headers["Cache-Control"])
        with self.sessions() as db:
            row=db.get(service.Contract,self.contract_id)
            self.assertNotIn("Premier pseudo",row.content)
            signer=db.scalar(select(service.Signer).where(service.Signer.slot==0))
            self.assertNotIn("first@example.test",signer.email)
        verified=await self.verify(token,"first@example.test")
        self.assertNotIn("first@example.test",str(verified));self.assertNotIn("second@example.test",str(verified))

    async def test_wrong_email_and_origin_cannot_send_or_create(self):
        token=await self.create()
        response=await self.client.post(f"/api/contracts/{self.contract_id}/code",headers=self.headers(token),json={"email":"other@example.test"})
        self.assertEqual(response.status_code,400);self.assertEqual(self.emails,[])
        response=await self.client.post("/api/contracts",headers={"Origin":"https://other.example"},json={"document":draft(),"emailA":"first@example.test","emailB":"second@example.test","processing":True})
        self.assertEqual(response.status_code,403)

    async def test_code_is_one_time_and_five_attempt_limited(self):
        token=await self.create();base=f"/api/contracts/{self.contract_id}"
        await self.client.post(base+"/code",headers=self.headers(token),json={"email":"first@example.test"})
        correct=self.emails[-1][1]["code"]
        for _ in range(5):
            response=await self.client.post(base+"/verify",headers=self.headers(token),json={"code":"111111" if correct!="111111" else "222222","processing":True})
            self.assertEqual(response.status_code,400)
        response=await self.client.post(base+"/verify",headers=self.headers(token),json={"code":correct,"processing":True})
        self.assertEqual(response.status_code,400)
        with self.sessions() as db:
            signer=db.scalar(select(service.Signer).where(service.Signer.slot==0));signer.code_sent_at=0;db.commit()
        verified=await self.verify(token,"first@example.test")
        response=await self.client.post(base+"/verify",headers=self.headers(token),json={"code":self.emails[-1][1]["code"],"processing":True})
        self.assertEqual(response.status_code,400)
        response=await self.client.get(base,headers=self.headers(token,True));self.assertEqual(response.status_code,401)

    async def test_two_signatures_freeze_one_pdf_and_send_separate_identical_copies(self):
        owner,partner=await self.both()
        response=await self.sign(owner);self.assertEqual(response.status_code,200);self.assertEqual(response.json()["status"],"pending")
        response=await self.client.get(f"/api/contracts/{self.contract_id}/pdf",headers=self.headers(owner["access"]))
        self.assertEqual(response.status_code,409)
        response=await self.sign(partner);self.assertEqual(response.status_code,200);self.assertEqual(response.json()["status"],"completed")
        receipts=[item for item in self.emails if "pdf" in item[1]]
        self.assertEqual(len(receipts),2);self.assertEqual(receipts[0][1]["pdf"],receipts[1][1]["pdf"])
        self.assertTrue(receipts[0][1]["pdf"].startswith(b"%PDF"))
        stamps=response.json()["signatures"];self.assertEqual([s["name"] for s in stamps],["Premier pseudo","Second pseudo"])
        response=await self.sign(partner);self.assertEqual(response.status_code,200)
        self.assertEqual(len([item for item in self.emails if "pdf" in item[1]]),2)
        response=await self.client.get(f"/api/contracts/{self.contract_id}/pdf",headers=self.headers(owner["access"]))
        self.assertEqual(response.content,receipts[0][1]["pdf"])

    async def test_resends_are_limited_per_recipient_across_invitations(self):
        token=await self.create();base=f"/api/contracts/{self.contract_id}"
        now=int(time.time())
        for attempt in range(5):
            with patch.object(service.time,"time",return_value=now+attempt*61):
                response=await self.client.post(base+"/code",headers=self.headers(token),json={"email":"first@example.test"})
            self.assertEqual(response.status_code,200,response.text)
        with patch.object(service.time,"time",return_value=now+400):
            second_token=await self.create()
            response=await self.client.post(f"/api/contracts/{self.contract_id}/code",headers=self.headers(second_token),json={"email":"first@example.test"})
        self.assertEqual(response.status_code,429)
        self.assertEqual(len(self.emails),5)

    async def test_wrong_name_or_version_cannot_sign(self):
        owner,partner=await self.both()
        self.assertEqual((await self.sign(owner,"Second pseudo")).status_code,409)
        self.assertEqual((await self.sign(owner,content_hash="0"*64)).status_code,409)

    async def test_receipt_failure_preserves_signatures_and_retries_only_unsent_copy(self):
        owner,partner=await self.both();self.fail_receipt=True
        await self.sign(owner);response=await self.sign(partner)
        self.assertEqual(response.status_code,200);self.assertEqual(response.json()["delivery"],"pending")
        with self.sessions() as db:
            signer=db.scalar(select(service.Signer).where(service.Signer.slot==1));signer.delivery_next=0;db.commit()
            self.fail_receipt=False;await service.deliver(db,db.get(service.Contract,self.contract_id))
        receipts=[item for item in self.emails if "pdf" in item[1]]
        self.assertEqual([item[0] for item in receipts],["first@example.test","second@example.test"])

    async def test_withdrawal_revokes_both_links_and_removes_document(self):
        owner,partner=await self.both()
        response=await self.client.post(f"/api/contracts/{self.contract_id}/withdraw",headers=self.headers(partner["access"]))
        self.assertEqual(response.status_code,200)
        response=await self.client.get(f"/api/contracts/{self.contract_id}",headers=self.headers(owner["access"],True));self.assertEqual(response.status_code,404)
        with self.sessions() as db:
            row=db.get(service.Contract,self.contract_id);self.assertEqual(service.decrypt(row.content),{});self.assertIsNone(row.pdf)

    async def test_expiry_and_cleanup_remove_private_rows(self):
        token=await self.create()
        with self.sessions() as db:
            row=db.get(service.Contract,self.contract_id);row.expires_at=int(time.time())-1;db.commit()
        response=await self.client.get(f"/api/contracts/{self.contract_id}",headers=self.headers(token));self.assertEqual(response.status_code,404)
        with self.sessions() as db:
            service.cleanup(db);self.assertIsNone(db.get(service.Contract,self.contract_id));self.assertEqual(list(db.scalars(select(service.Signer))),[])

    async def test_schema_rejects_modified_model_extra_clauses_and_inverted_dates(self):
        for mutate in [lambda d:d.update(version="unknown"),lambda d:d["fields"].update(fake="fake"),lambda d:d.update(end="2026-10-01")]:
            value=draft();mutate(value)
            response=await self.client.post("/api/contracts",json={"document":value,"emailA":"first@example.test","emailB":"second@example.test","processing":True})
            self.assertEqual(response.status_code,422)


if __name__=="__main__":unittest.main()
