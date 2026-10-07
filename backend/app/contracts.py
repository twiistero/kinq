"""Private two-person agreements: immutable version, email verification, independent receipts."""
import asyncio
import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import time
import uuid
from datetime import date, datetime, timezone

from cryptography.fernet import Fernet
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint, delete, func, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .contracts_pdf import CATALOGUE, MODELS, render_pdf
from .mailer import send_contract_email

PUBLIC_ORIGIN = os.environ.get("KINQ_PUBLIC_ORIGIN", "http://127.0.0.1:4173").rstrip("/")
SECRET = os.environ.get("KINQ_SESSION_SECRET", "")
FERNET = Fernet(base64.urlsafe_b64encode(hashlib.sha256(("kinq-contracts-v1:"+SECRET).encode()).digest()))


class ContractBase(DeclarativeBase):
    pass


class Contract(ContractBase):
    __tablename__ = "private_contracts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[int] = mapped_column(Integer)
    expires_at: Mapped[int] = mapped_column(Integer, index=True)
    source_hash: Mapped[str] = mapped_column(String(64), index=True)
    pdf: Mapped[str | None] = mapped_column(Text, nullable=True)


class Signer(ContractBase):
    __tablename__ = "private_contract_signers"
    __table_args__ = (UniqueConstraint("contract_id", "slot"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    contract_id: Mapped[str] = mapped_column(ForeignKey("private_contracts.id", ondelete="CASCADE"), index=True)
    slot: Mapped[int] = mapped_column(Integer)
    email: Mapped[str] = mapped_column(Text)
    email_hash: Mapped[str] = mapped_column(String(64), index=True)
    invite_hash: Mapped[str] = mapped_column(String(64), unique=True)
    access_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    access_expires: Mapped[int] = mapped_column(Integer, default=0)
    code_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    code_expires: Mapped[int] = mapped_column(Integer, default=0)
    code_sent_at: Mapped[int] = mapped_column(Integer, default=0)
    code_attempts: Mapped[int] = mapped_column(Integer, default=0)
    signed_at: Mapped[int] = mapped_column(Integer, default=0)
    signature: Mapped[str | None] = mapped_column(Text, nullable=True)
    delivery: Mapped[str] = mapped_column(String(16), default="pending")
    delivery_attempts: Mapped[int] = mapped_column(Integer, default=0)
    delivery_next: Mapped[int] = mapped_column(Integer, default=0)


class CodeDispatch(ContractBase):
    __tablename__ = "private_contract_code_dispatches"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email_hash: Mapped[str] = mapped_column(String(64), index=True)
    requested_at: Mapped[int] = mapped_column(Integer, index=True)


def digest(value):
    return hmac.new(SECRET.encode(),value.encode(),hashlib.sha256).hexdigest()


def encrypt(value):
    return FERNET.encrypt(json.dumps(value,ensure_ascii=False,sort_keys=True).encode()).decode()


def decrypt(value):
    return json.loads(FERNET.decrypt(value.encode()))


def iso(value):
    return datetime.fromtimestamp(value,timezone.utc).isoformat()


class Draft(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: str = Field(max_length=20)
    model: str = Field(max_length=40)
    nameA: str = Field(max_length=80)
    nameB: str = Field(max_length=80)
    roleA: str = Field(max_length=80)
    roleB: str = Field(max_length=80)
    start: str = Field(default="",max_length=10)
    end: str = Field(default="",max_length=10)
    duration: str = Field(max_length=240)
    fields: dict[str,str]

    @model_validator(mode="after")
    def validate_document(self):
        if self.version != CATALOGUE["version"] or self.model not in MODELS:
            raise ValueError("Modèle de contrat indisponible ; recharge la page.")
        keys = {f["id"] for f in [*CATALOGUE["common"],*MODELS[self.model]["fields"]]}
        if set(self.fields) != keys or any(len(value)>2000 for value in self.fields.values()):
            raise ValueError("Rubriques de contrat invalides.")
        for value in [self.nameA,self.nameB,self.roleA,self.roleB,self.duration,*self.fields.values()]:
            if any(ord(char)<32 and char not in "\n\t" for char in value):
                raise ValueError("Un champ contient un caractère non pris en charge.")
        if self.start: date.fromisoformat(self.start)
        if self.end: date.fromisoformat(self.end)
        if self.start and self.end and self.end<self.start:
            raise ValueError("La fin doit suivre le début.")
        return self


class NewContract(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document: Draft
    emailA: str = Field(max_length=255)
    emailB: str = Field(max_length=255)
    processing: bool


class CodeRequest(BaseModel):
    email: str = Field(max_length=255)


class CodeVerify(BaseModel):
    code: str = Field(pattern=r"^[0-9]{6}$")
    processing: bool


class SignRequest(BaseModel):
    name: str = Field(min_length=1,max_length=80)
    contentHash: str = Field(min_length=64,max_length=64)
    accepted: bool


def cleanup(db):
    expired = select(Contract.id).where(Contract.expires_at<=int(time.time()))
    db.execute(delete(Signer).where(Signer.contract_id.in_(expired)))
    db.execute(delete(Contract).where(Contract.expires_at<=int(time.time())))
    db.execute(delete(CodeDispatch).where(CodeDispatch.requested_at<=int(time.time())-3600))
    from .member_contracts import cleanup_drafts
    cleanup_drafts(db)
    db.commit()


def reference(contract):
    return "KQ-"+contract.id[:8].upper()


def get_contract(db, contract_id, request, access=False, lock=False):
    token = request.headers.get("authorization", "").removeprefix("Bearer ")
    if not 20<=len(token)<=100: raise HTTPException(404,"Lien indisponible ou expiré.")
    query=select(Contract).where(Contract.id==contract_id)
    contract=db.scalar(query.with_for_update() if lock else query)
    if not contract or contract.expires_at<=int(time.time()) or contract.status=="withdrawn":
        raise HTTPException(404,"Lien indisponible ou expiré.")
    field=Signer.access_hash if access else Signer.invite_hash
    signer=db.scalar(select(Signer).where(Signer.contract_id==contract_id,field==digest(token)))
    if not signer or (access and signer.access_expires<=int(time.time())):
        raise HTTPException(401,"Vérifie ton adresse e-mail pour accéder au contrat.")
    return contract,signer


def projection(db,contract,signer):
    stored=decrypt(contract.content)
    signers=list(db.scalars(select(Signer).where(Signer.contract_id==contract.id).order_by(Signer.slot)))
    return {"id":contract.id,"reference":reference(contract),"status":contract.status,"document":stored["document"],
        "contentHash":contract.content_hash,"slot":signer.slot,"expiresAt":iso(contract.expires_at),
        "partnerLink":f'{PUBLIC_ORIGIN}/contrats/signature/{contract.id}#invitation={stored["partnerToken"]}' if signer.slot==0 else None,
        "signatures":[{"name":decrypt(s.signature),"signedAt":iso(s.signed_at)} if s.signed_at else None for s in signers],
        "delivery":signer.delivery if contract.status=="completed" else None}


async def deliver(db,contract):
    if contract.status!="completed": return
    for signer in db.scalars(select(Signer).where(Signer.contract_id==contract.id).order_by(Signer.slot)):
        if signer.delivery=="sent" or signer.delivery_attempts>=6 or signer.delivery_next>int(time.time()): continue
        signer.delivery_attempts+=1
        # Persist retry timing before transmission; providers also deduplicate retries.
        signer.delivery_next=int(time.time())+min(3600,60*2**signer.delivery_attempts)
        db.commit()
        try:
            await send_contract_email(decrypt(signer.email),"Ta copie de l’accord Kinq", "Votre accord est signé.",
                "Les deux signatures ont été enregistrées. Tu trouveras ta copie du document en pièce jointe. Garde-la dans un espace privé.",
                pdf=base64.b64decode(decrypt(contract.pdf)),filename=f'accord-kinq-{reference(contract)}.pdf',
                idempotency=f'contract-copy-{contract.id}-{signer.slot}')
            signer.delivery="sent"
        except HTTPException:
            signer.delivery="failed" if signer.delivery_attempts>=6 else "pending"
        db.commit()


def apply_signature(db, contract, signer, body):
    stored=decrypt(contract.content);name=stored["document"]["nameA" if signer.slot==0 else "nameB"].strip()
    if not body.accepted or body.name.strip()!=name or body.contentHash!=contract.content_hash:
        raise HTTPException(409,"Relis cette version et signe avec le nom ou pseudo prévu.")
    if not signer.signed_at:
        signer.signed_at=int(time.time());signer.signature=encrypt(name);db.flush()
    signers=list(db.scalars(select(Signer).where(Signer.contract_id==contract.id).order_by(Signer.slot)))
    if all(s.signed_at for s in signers) and contract.status!="completed":
        stamps=[{"name":decrypt(s.signature),"signedAt":iso(s.signed_at)} for s in signers]
        pdf=render_pdf(stored["document"],stamps,reference(contract))
        contract.pdf=encrypt(base64.b64encode(pdf).decode());contract.status="completed"
        contract.expires_at=int(time.time())+30*86400


def install_contract_routes(app,session_factory,on_signed=None):
    router=APIRouter(prefix="/api/contracts")

    def db_session():
        with session_factory() as db: yield db

    def same_origin(request:Request):
        if request.method!="GET" and request.headers.get("origin")!=PUBLIC_ORIGIN:
            raise HTTPException(403,"Requête non autorisée.")

    @router.post("",status_code=201,dependencies=[Depends(same_origin)])
    def create(body:NewContract,request:Request,db=Depends(db_session)):
        cleanup(db)
        if not body.processing or not body.document.nameA.strip() or not body.document.nameB.strip():
            raise HTTPException(422,"Les deux noms ou pseudos et l’accord de stockage sont requis.")
        emails=[body.emailA.strip().lower(),body.emailB.strip().lower()]
        if emails[0]==emails[1] or any(not re.fullmatch(r"[^@\s<>]+@[^@\s<>]+\.[^@\s<>]+",email) for email in emails):
            raise HTTPException(422,"Deux adresses e-mail distinctes et valides sont requises.")
        source=digest(request.headers.get("x-forwarded-for",request.client.host if request.client else "unknown").split(",")[0])
        recent=db.scalar(select(func.count()).select_from(Contract).where(Contract.source_hash==source,Contract.created_at>int(time.time())-3600))
        if recent>=10: raise HTTPException(429,"Trop de créations. Réessaie dans une heure.")
        tokens=[secrets.token_urlsafe(32),secrets.token_urlsafe(32)]
        document=body.document.model_dump()
        canonical=json.dumps(document,sort_keys=True,ensure_ascii=False,separators=(",",":"))
        contract=Contract(id=str(uuid.uuid4()),content=encrypt({"document":document,"partnerToken":tokens[1]}),
            content_hash=hashlib.sha256(canonical.encode()).hexdigest(),created_at=int(time.time()),
            expires_at=int(time.time())+14*86400,source_hash=source,status="pending")
        db.add(contract);db.flush()
        for slot,email in enumerate(emails):
            db.add(Signer(id=str(uuid.uuid4()),contract_id=contract.id,slot=slot,email=encrypt(email),email_hash=digest("email:"+email),invite_hash=digest(tokens[slot])))
        db.commit()
        return {"id":contract.id,"reference":reference(contract),"invitation":tokens[0]}

    @router.get("/{contract_id}")
    def read(contract_id:str,request:Request,db=Depends(db_session)):
        mode=request.headers.get("x-contract-access") == "verified"
        contract,signer=get_contract(db,contract_id,request,access=mode)
        if not mode: return {"reference":reference(contract),"needsVerification":True,"slot":signer.slot}
        return projection(db,contract,signer)

    @router.post("/{contract_id}/code",dependencies=[Depends(same_origin)])
    async def request_code(contract_id:str,body:CodeRequest,request:Request,db=Depends(db_session)):
        contract,signer=get_contract(db,contract_id,request,lock=True)
        if body.email.strip().lower()!=decrypt(signer.email): raise HTTPException(400,"Adresse incorrecte pour ce lien.")
        now=int(time.time())
        if db.get_bind().dialect.name=="postgresql":
            # Serialize the recipient quota even for simultaneous requests on distinct contracts.
            key=int(signer.email_hash[:16],16)-(1<<63)
            db.execute(text("SELECT pg_advisory_xact_lock(:key)"),{"key":key})
        # Count requests across contracts for the same recipient, not just this invitation.
        recent=db.scalar(select(func.count()).select_from(CodeDispatch).where(CodeDispatch.email_hash==signer.email_hash,CodeDispatch.requested_at>now-3600))
        if signer.code_sent_at>now-60 or recent>=5: raise HTTPException(429,"Patiente avant de demander un nouveau code.")
        code=f"{secrets.randbelow(1000000):06d}"
        # Reserve the window before transmission so parallel requests cannot generate floods.
        signer.code_sent_at=now;signer.code_hash=None;signer.code_expires=0
        db.add(CodeDispatch(id=str(uuid.uuid4()),email_hash=signer.email_hash,requested_at=now));db.commit()
        try:
            await send_contract_email(decrypt(signer.email),"Ton code pour l’accord Kinq", "Vérifie ton adresse.",
                "Ce code permet d’accéder à ton accord privé Kinq. Il est valable 10 minutes et ne doit pas être partagé.",code=code)
        except HTTPException:
            signer.code_sent_at=now;db.commit();raise
        signer.code_hash=digest(f'{signer.id}:{code}');signer.code_expires=now+600;signer.code_attempts=0;db.commit()
        return {"ok":True}

    @router.post("/{contract_id}/verify",dependencies=[Depends(same_origin)])
    def verify(contract_id:str,body:CodeVerify,request:Request,db=Depends(db_session)):
        contract,signer=get_contract(db,contract_id,request,lock=True)
        if not body.processing: raise HTTPException(422,"Ton accord de stockage et d’envoi est requis.")
        if not signer.code_hash or signer.code_expires<=int(time.time()) or signer.code_attempts>=5:
            raise HTTPException(400,"Code indisponible ou expiré. Demande un nouveau code.")
        signer.code_attempts+=1
        if not hmac.compare_digest(signer.code_hash,digest(f'{signer.id}:{body.code}')):
            db.commit();raise HTTPException(400,"Code incorrect.")
        token=secrets.token_urlsafe(32);signer.access_hash=digest(token);signer.access_expires=int(time.time())+7200
        signer.code_hash=None;signer.code_expires=0;db.commit()
        return {"access":token,**projection(db,contract,signer)}

    @router.post("/{contract_id}/sign",dependencies=[Depends(same_origin)])
    async def sign(contract_id:str,body:SignRequest,request:Request,db=Depends(db_session)):
        contract,signer=get_contract(db,contract_id,request,access=True,lock=True)
        apply_signature(db, contract, signer, body)
        if on_signed: on_signed(db, contract)
        db.commit()
        await deliver(db,contract)
        return projection(db,contract,signer)

    @router.get("/{contract_id}/pdf")
    def pdf(contract_id:str,request:Request,db=Depends(db_session)):
        contract,signer=get_contract(db,contract_id,request,access=True)
        if contract.status!="completed": raise HTTPException(409,"Le PDF signé sera disponible après les deux signatures.")
        return Response(base64.b64decode(decrypt(contract.pdf)),media_type="application/pdf",headers={
            "Content-Disposition":f'attachment; filename="accord-kinq-{reference(contract)}.pdf"',"Cache-Control":"private, no-store","X-Robots-Tag":"noindex, nofollow"})

    @router.post("/{contract_id}/withdraw",dependencies=[Depends(same_origin)])
    def withdraw(contract_id:str,request:Request,db=Depends(db_session)):
        contract,signer=get_contract(db,contract_id,request,access=True,lock=True)
        from .member_contracts import remove_agreement_copies
        remove_agreement_copies(db, contract.id)
        contract.status="withdrawn";contract.content=encrypt({});contract.pdf=None
        for s in db.scalars(select(Signer).where(Signer.contract_id==contract.id)):
            s.email=encrypt("");s.signature=None;s.access_hash=None;s.invite_hash=digest(secrets.token_urlsafe(32))
        db.commit();return {"ok":True}

    app.include_router(router)

    @app.middleware("http")
    async def private_headers(request,call_next):
        response=await call_next(request)
        if request.url.path.startswith("/api/contracts"):
            response.headers["Cache-Control"]="private, no-store"
            response.headers["X-Robots-Tag"]="noindex, nofollow"
        return response

    async def worker():
        while True:
            try:
                with session_factory() as db:
                    cleanup(db)
                    candidates=list(db.scalars(select(Contract).join(Signer).where(Contract.status=="completed",Signer.delivery!="sent",Signer.delivery_attempts<6,Signer.delivery_next<=int(time.time())).distinct().limit(20)))
                    for contract in candidates: await deliver(db,contract)
            except Exception:
                # No document, token, recipient or credential may enter application logs.
                pass
            await asyncio.sleep(60)

    task=None
    async def start():
        nonlocal task
        task=asyncio.create_task(worker())
    async def stop():
        if task: task.cancel()
    app.add_event_handler("startup",start);app.add_event_handler("shutdown",stop)
