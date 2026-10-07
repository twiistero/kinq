"""Member-owned copies. Only the authenticated owner can read or remove a copy."""
import base64
import hashlib
import json
import secrets
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Boolean, Integer, String, Text, UniqueConstraint, delete, select, text
from sqlalchemy.orm import Mapped, mapped_column

from . import contracts as service
from .contracts_pdf import MODELS, render_pdf, sections


class SavedContract(service.ContractBase):
    __tablename__ = "member_contract_copies"
    __table_args__ = (UniqueConstraint("member_id", "source_key"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    member_id: Mapped[int] = mapped_column(Integer, index=True)
    source_key: Mapped[str] = mapped_column(String(80))
    content: Mapped[str] = mapped_column(Text)
    pdf: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[int] = mapped_column(Integer)
    removed: Mapped[bool] = mapped_column(Boolean, default=False)


class AccountDraft(service.ContractBase):
    __tablename__ = "contract_account_drafts"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    source_hash: Mapped[str] = mapped_column(String(64), index=True)
    created_at: Mapped[int] = mapped_column(Integer)
    expires_at: Mapped[int] = mapped_column(Integer, index=True)


class SavePrint(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document: service.Draft


class ClaimCopy(BaseModel):
    model_config = ConfigDict(extra="forbid")
    draftToken: str = Field(default="", max_length=100)
    contractId: str = Field(default="", max_length=36)
    access: str = Field(default="", max_length=100)


def cleanup_drafts(db):
    db.execute(delete(AccountDraft).where(AccountDraft.expires_at <= int(time.time())))


def erase_copies(db, member_id):
    db.execute(delete(SavedContract).where(SavedContract.member_id == member_id))


def remove_agreement_copies(db, contract_id):
    db.execute(delete(SavedContract).where(SavedContract.source_key == "signed:" + contract_id))


def save_copy(db, member_id, source_key, content, pdf, restore=False):
    # Serialize duplicate saves without replacing a previously removed copy.
    if db.get_bind().dialect.name == "postgresql":
        key = int(service.digest(f"copy:{member_id}:{source_key}")[:16], 16) - (1 << 63)
        db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": key})
    row = db.scalar(select(SavedContract).where(SavedContract.member_id == member_id, SavedContract.source_key == source_key))
    if row:
        if restore and row.removed:
            row.removed = False
            row.content = service.encrypt(content)
            row.pdf = service.encrypt(base64.b64encode(pdf).decode())
        return row
    row = SavedContract(id=str(uuid.uuid4()), member_id=member_id, source_key=source_key,
        content=service.encrypt(content), pdf=service.encrypt(base64.b64encode(pdf).decode()),
        created_at=int(time.time()), removed=False)
    db.add(row)
    db.flush()
    return row


def frozen_content(db, contract, signer):
    value = service.projection(db, contract, signer)
    return {"document": value["document"], "signatures": value["signatures"],
        "reference": value["reference"], "status": "signed", "slot": signer.slot,
        "contentHash": value["contentHash"]}


def archive_known_members(db, contract, member_class):
    if contract.status != "completed":
        return
    for signer in db.scalars(select(service.Signer).where(service.Signer.contract_id == contract.id)):
        member = db.scalar(select(member_class).where(member_class.email == service.decrypt(signer.email), member_class.status == "active"))
        if member:
            save_copy(db, member.id, "signed:" + contract.id, frozen_content(db, contract, signer),
                base64.b64decode(service.decrypt(contract.pdf)))


def print_copy(db, member_id, document):
    canonical = json.dumps(document, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    key = "print:" + hashlib.sha256(canonical.encode()).hexdigest()
    existing = db.scalar(select(SavedContract).where(SavedContract.member_id == member_id, SavedContract.source_key == key))
    if existing and not existing.removed:
        return existing
    if existing and existing.removed:
        # A new explicit save may restore this member's own printable copy.
        existing.removed = False
        existing.content = service.encrypt({"document": document, "signatures": [None, None], "status": "print"})
        existing.pdf = service.encrypt(base64.b64encode(render_pdf(document)).decode())
        return existing
    return save_copy(db, member_id, key, {"document": document, "signatures": [None, None], "status": "print"}, render_pdf(document))


def copy_summary(row):
    content = service.decrypt(row.content)
    doc = content["document"]
    return {"id": row.id, "title": MODELS[doc["model"]]["title"], "model": doc["model"],
        "status": content["status"], "names": [doc["nameA"], doc["nameB"]],
        "createdAt": service.iso(row.created_at), "signatureCount": sum(bool(s) for s in content["signatures"])}


def install_member_contract_routes(app, session_factory, current_member, member_class):
    router = APIRouter(prefix="/api/member/contracts")

    def db_session():
        with session_factory() as db:
            yield db

    def agreement(db, contract_id, member, lock=False):
        query = select(service.Contract).where(service.Contract.id == contract_id)
        contract = db.scalar(query.with_for_update() if lock else query)
        signer = db.scalar(select(service.Signer).where(service.Signer.contract_id == contract_id,
            service.Signer.email_hash == service.digest("email:" + member.email.lower())))
        if not contract or not signer or contract.status == "withdrawn" or contract.expires_at <= int(time.time()):
            raise HTTPException(404, "Contrat indisponible.")
        return contract, signer

    def own_copy(db, copy_id, member):
        row = db.scalar(select(SavedContract).where(SavedContract.id == copy_id,
            SavedContract.member_id == member.id, SavedContract.removed == False))
        if not row:
            raise HTTPException(404, "Contrat indisponible.")
        return row

    @app.post("/api/contracts/account-draft", status_code=201)
    def prepare_account_draft(body: SavePrint, request: Request, db=Depends(db_session)):
        if request.headers.get("origin") != service.PUBLIC_ORIGIN:
            raise HTTPException(403, "Requête non autorisée.")
        cleanup_drafts(db)
        source = service.digest(request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown").split(",")[0])
        if len(list(db.scalars(select(AccountDraft.token_hash).where(AccountDraft.source_hash == source, AccountDraft.created_at > int(time.time()) - 3600)))) >= 10:
            raise HTTPException(429, "Trop de demandes. Réessaie dans une heure.")
        token = secrets.token_urlsafe(32)
        db.add(AccountDraft(token_hash=service.digest(token), content=service.encrypt(body.document.model_dump()),
            source_hash=source, created_at=int(time.time()), expires_at=int(time.time()) + 86400))
        db.commit()
        return {"token": token}

    @router.post("/print", status_code=201)
    def save_print(body: SavePrint, member=Depends(current_member), db=Depends(db_session)):
        row = print_copy(db, member.id, body.document.model_dump())
        db.commit()
        return copy_summary(row)

    @router.post("/claim")
    def claim(body: ClaimCopy, member=Depends(current_member), db=Depends(db_session)):
        if bool(body.draftToken) == bool(body.contractId and body.access):
            raise HTTPException(422, "Choisis un seul contrat à conserver.")
        if body.draftToken:
            pending = db.scalar(select(AccountDraft).where(AccountDraft.token_hash == service.digest(body.draftToken)).with_for_update())
            if not pending or pending.expires_at <= int(time.time()):
                raise HTTPException(404, "Le retour vers ce contrat a expiré. Ouvre ton contrat et réessaie.")
            row = print_copy(db, member.id, service.decrypt(pending.content))
            db.delete(pending)
        else:
            contract = db.get(service.Contract, body.contractId)
            signer = db.scalar(select(service.Signer).where(service.Signer.contract_id == body.contractId,
                service.Signer.access_hash == service.digest(body.access), service.Signer.access_expires > int(time.time())))
            if not contract or not signer or contract.status != "completed" or contract.expires_at <= int(time.time()):
                raise HTTPException(404, "Vérifie et signe le contrat avant de conserver ta copie.")
            row = save_copy(db, member.id, "signed:" + contract.id, frozen_content(db, contract, signer), base64.b64decode(service.decrypt(contract.pdf)), restore=True)
        db.commit()
        return copy_summary(row)

    @router.get("")
    def list_copies(member=Depends(current_member), db=Depends(db_session)):
        agreements = list(db.execute(select(service.Contract, service.Signer).join(service.Signer).where(
            service.Signer.email_hash == service.digest("email:" + member.email.lower()),
            service.Contract.expires_at > int(time.time()), service.Contract.status != "withdrawn")))
        for contract, signer in agreements:
            if contract.status == "completed":
                save_copy(db, member.id, "signed:" + contract.id, frozen_content(db, contract, signer), base64.b64decode(service.decrypt(contract.pdf)))
        db.commit()
        copies = [copy_summary(row) for row in db.scalars(select(SavedContract).where(
            SavedContract.member_id == member.id, SavedContract.removed == False).order_by(SavedContract.created_at.desc()))]
        for contract, signer in agreements:
            if contract.status == "pending":
                doc = service.decrypt(contract.content)["document"]
                signatures = service.projection(db, contract, signer)["signatures"]
                copies.append({"id": contract.id, "title": MODELS[doc["model"]]["title"], "model": doc["model"],
                    "status": "pending", "names": [doc["nameA"], doc["nameB"]], "createdAt": service.iso(contract.created_at),
                    "signatureCount": sum(bool(s) for s in signatures)})
        return sorted(copies, key=lambda row: row["createdAt"], reverse=True)

    @router.get("/{copy_id}")
    def read_copy(copy_id: str, member=Depends(current_member), db=Depends(db_session)):
        row = db.scalar(select(SavedContract).where(SavedContract.id == copy_id, SavedContract.member_id == member.id, SavedContract.removed == False))
        if row:
            value = service.decrypt(row.content)
        else:
            contract, signer = agreement(db, copy_id, member)
            if contract.status == "completed":
                row = save_copy(db, member.id, "signed:" + contract.id, frozen_content(db, contract, signer), base64.b64decode(service.decrypt(contract.pdf)))
                if row.removed:
                    raise HTTPException(404, "Cette copie a été retirée de ton compte.")
                db.commit()
                value = service.decrypt(row.content)
                copy_id = row.id
            else:
                value = service.projection(db, contract, signer)
                value["status"] = "pending"
        value["sections"] = [{"title": title, "text": body} for title, body in sections(value["document"])]
        value["id"] = copy_id
        value["title"] = MODELS[value["document"]["model"]]["title"]
        return value

    @router.get("/{copy_id}/pdf")
    def copy_pdf(copy_id: str, member=Depends(current_member), db=Depends(db_session)):
        row = own_copy(db, copy_id, member)
        return Response(base64.b64decode(service.decrypt(row.pdf)), media_type="application/pdf", headers={
            "Content-Disposition": f'attachment; filename="contrat-kinq-{row.id[:8]}.pdf"', "Cache-Control": "private, no-store"})

    @router.post("/{contract_id}/sign")
    async def sign_from_account(contract_id: str, body: service.SignRequest, member=Depends(current_member), db=Depends(db_session)):
        contract, signer = agreement(db, contract_id, member, lock=True)
        service.apply_signature(db, contract, signer, body)
        archive_known_members(db, contract, member_class)
        db.commit()
        await service.deliver(db, contract)
        return {"ok": True}

    @router.delete("/{copy_id}")
    def remove_copy(copy_id: str, member=Depends(current_member), db=Depends(db_session)):
        row = own_copy(db, copy_id, member)
        row.removed = True
        row.content = service.encrypt({})
        row.pdf = None
        db.commit()
        return {"ok": True}

    app.include_router(router)

    @app.middleware("http")
    async def copy_headers(request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/api/member/contracts"):
            response.headers["Cache-Control"] = "private, no-store"
            response.headers["X-Robots-Tag"] = "noindex, nofollow"
        return response
