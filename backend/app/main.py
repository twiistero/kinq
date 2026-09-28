"""KINQ private administration API. All writes require a Workspace session."""
import os
import re
import secrets
import uuid
import hashlib
import hmac
import html
import base64
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse, Response
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from pydantic import BaseModel, Field
from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, LargeBinary, String, Text, UniqueConstraint, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from starlette.middleware.sessions import SessionMiddleware

DATABASE_URL = os.environ.get("DATABASE_URL", "")
CLIENT_ID = os.environ.get("KINQ_GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("KINQ_GOOGLE_CLIENT_SECRET", "")
ADMIN_EMAIL = os.environ.get("KINQ_OWNER_EMAIL", "").lower()
SESSION_SECRET = os.environ.get("KINQ_SESSION_SECRET", "")
PUBLIC_ORIGIN = os.environ.get("KINQ_PUBLIC_ORIGIN", "http://127.0.0.1:4173").rstrip("/")
UPLOAD_KEY = os.environ.get("KINQ_UPLOAD_KEY", "")
if not DATABASE_URL or len(SESSION_SECRET) < 32:
    raise RuntimeError("DATABASE_URL and a 32+ character KINQ_SESSION_SECRET are required")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(engine)


class Base(DeclarativeBase):
    pass


class Staff(Base):
    __tablename__ = "staff"
    id: Mapped[int] = mapped_column(primary_key=True)
    google_sub: Mapped[str] = mapped_column(String(255), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(255), default="")
    role: Mapped[str] = mapped_column(String(20), default="user")
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Member(Base):
    __tablename__ = "members"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[str] = mapped_column(String(30), default="active")
    ban_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Photo(Base):
    __tablename__ = "photos"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"))
    mime: Mapped[str] = mapped_column(String(30))
    data: Mapped[bytes] = mapped_column(LargeBinary)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("staff.id"), nullable=True)


class Article(Base):
    __tablename__ = "articles"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(180), unique=True)
    title: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text, default="")
    body: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="draft")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"))
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"))
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")


class Audit(Base):
    __tablename__ = "admin_audit"
    id: Mapped[int] = mapped_column(primary_key=True)
    staff_id: Mapped[int] = mapped_column(ForeignKey("staff.id"))
    action: Mapped[str] = mapped_column(String(80))
    target: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class PageDocument(Base):
    __tablename__ = "page_documents"
    path: Mapped[str] = mapped_column(String(180), primary_key=True)
    data: Mapped[dict] = mapped_column(JSON)
    source_hash: Mapped[str] = mapped_column(String(64))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


DEFAULT_PIXEL_SITE_ID = "fca55491-6359-4ef0-86c0-2b1c02a5f4d2"


class SiteSetting(Base):
    __tablename__ = "site_settings"
    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    value: Mapped[str] = mapped_column(String(255), default="")


class Event(Base):
    __tablename__ = "events"
    id: Mapped[str] = mapped_column(String(120), primary_key=True)
    data: Mapped[dict] = mapped_column(JSON)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class MemberCode(Base):
    __tablename__ = "member_codes"
    email: Mapped[str] = mapped_column(String(255), primary_key=True)
    digest: Mapped[str] = mapped_column(String(64))
    purpose: Mapped[str] = mapped_column(String(12))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    attempts: Mapped[int] = mapped_column(default=0)
    consent: Mapped[bool] = mapped_column(Boolean, default=False)
    member_id: Mapped[int | None] = mapped_column(ForeignKey("members.id"), nullable=True)


class MemberProfile(Base):
    __tablename__ = "member_profiles"
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), primary_key=True)
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    code: Mapped[str] = mapped_column(String(12), unique=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class MemberConsent(Base):
    __tablename__ = "member_consents"
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), primary_key=True)
    accepted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    version: Mapped[str] = mapped_column(String(30))


class DemoProfile(Base):
    __tablename__ = "demo_profiles"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    data: Mapped[dict] = mapped_column(JSON)


class MemberSignal(Base):
    __tablename__ = "member_signals"
    __table_args__ = (UniqueConstraint("member_id", "target_id", "kind"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"))
    target_id: Mapped[str] = mapped_column(String(40))
    kind: Mapped[str] = mapped_column(String(10))


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


def db_session():
    with SessionLocal() as db:
        yield db


def current_staff(request: Request, db: Session = Depends(db_session)) -> Staff:
    sid = request.session.get("staff_id")
    staff = db.get(Staff, sid) if sid else None
    if not staff or not staff.active:
        raise HTTPException(401, "Connexion Workspace requise")
    return staff


def admin(staff: Staff = Depends(current_staff)) -> Staff:
    if staff.role != "admin" or staff.email != ADMIN_EMAIL:
        raise HTTPException(403, "Réservé à l’administrateur KINQ")
    return staff


def editor(staff: Staff = Depends(current_staff)) -> Staff:
    if staff.role not in ("admin", "moderator"):
        raise HTTPException(403, "Rôle de modération requis")
    return staff


def log(db: Session, staff: Staff, action: str, target: str):
    db.add(Audit(staff_id=staff.id, action=action, target=target))


def effective_member_status(member: Member) -> str:
    if member.status == "banned_temporary" and member.ban_until and member.ban_until <= datetime.now(timezone.utc):
        return "active"
    return member.status


def require_service_key(value: str):
    if not UPLOAD_KEY or not secrets.compare_digest(value, UPLOAD_KEY):
        raise HTTPException(401)


@app.get("/healthz")
def health():
    return {"ok": True}


@app.get("/api/documents/{page_path:path}")
def page_document(page_path: str, db: Session = Depends(db_session)):
    if not page_path or "/" in page_path or (page_path != "admin" and not page_path.endswith(".html")):
        raise HTTPException(404)
    page = db.get(PageDocument, page_path)
    if not page:
        raise HTTPException(404)
    return page.data


@app.get("/api/events")
def public_events(db: Session = Depends(db_session)):
    return [event.data for event in db.scalars(select(Event).order_by(Event.id))]


def current_member(request: Request, db: Session = Depends(db_session)) -> Member:
    member_id = request.session.get("member_id")
    member = db.get(Member, member_id) if member_id else None
    if not member or effective_member_status(member) != "active":
        raise HTTPException(401, "Connexion requise")
    return member


@app.get("/api/profiles")
def public_profiles(_: Member = Depends(current_member), db: Session = Depends(db_session)):
    result = [p.data for p in db.scalars(select(DemoProfile).order_by(DemoProfile.id))]
    for profile, member in db.execute(select(MemberProfile, Member).join(Member, Member.id == MemberProfile.member_id)):
        data = profile.data or {}
        if effective_member_status(member) != "active" or data.get("invisible"):
            continue
        approved = db.scalar(select(Photo).where(Photo.member_id == member.id, Photo.status == "approved").order_by(Photo.created_at.desc()))
        safe = lambda value, limit: html.escape(str(value or "")[:limit], quote=True)
        result.append({
            "id": f"member-{member.id}", "name": safe(data.get("pseudo") or "Membre", 80),
            "age": int(data.get("age") or 18), "city": "" if data.get("hideCity") else safe(data.get("city"), 80),
            "kinks": [safe(k, 80) for k in list(data.get("style") or []) + list(data.get("practice") or [])][:40],
            "role": safe(data.get("dynamic"), 80), "intent": "", "pace": "",
            "quote": safe(data.get("wishes"), 240), "bio": safe(data.get("bio"), 1000),
            "photo": f"/api/photos/{approved.id}" if approved and not data.get("discreet") else None,
            "code": profile.code,
        })
    return result


def normalized_email(value: str) -> str:
    email = value.strip().lower()
    if len(email) > 255 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise HTTPException(400, "Adresse e-mail invalide")
    return email


def code_digest(email: str, code: str) -> str:
    return hmac.new(SESSION_SECRET.encode(), f"{email}:{code}".encode(), hashlib.sha256).hexdigest()


class CodeRequest(BaseModel):
    email: str
    purpose: str
    adult: bool = False
    terms: bool = False
    charter: bool = False


@app.post("/api/member/auth/request")
async def request_member_code(body: CodeRequest, request: Request, db: Session = Depends(db_session)):
    if request.headers.get("origin") != PUBLIC_ORIGIN:
        raise HTTPException(403, "Origine invalide")
    if body.purpose not in ("signup", "login"):
        raise HTTPException(400)
    email = normalized_email(body.email)
    if body.purpose == "signup" and not (body.adult and body.terms and body.charter):
        raise HTTPException(400, "Accords requis")
    key = os.environ.get("KINQ_RESEND_API_KEY", "")
    sender = os.environ.get("KINQ_RESEND_FROM", "KINQ <connexion@kinq-app.com>")
    if not key:
        raise HTTPException(503, "Envoi des e-mails KINQ non configuré")
    member = db.scalar(select(Member).where(Member.email == email))
    if member and effective_member_status(member) != "active":
        return {"ok": True}
    if body.purpose == "login" and not member:
        return {"ok": True}
    if body.purpose == "signup" and member:
        return {"ok": True}
    now = datetime.now(timezone.utc)
    challenge = db.get(MemberCode, email)
    if challenge and challenge.sent_at.replace(tzinfo=timezone.utc) > now - timedelta(seconds=60):
        raise HTTPException(429, "Attends une minute avant de demander un autre code")
    code = f"{secrets.randbelow(1_000_000):06d}"
    async with httpx.AsyncClient(timeout=12) as client:
        result = await client.post("https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {key}"},
            json={"from": sender, "to": [email], "subject": "Ton code KINQ",
                  "text": f"Ton code KINQ est {code}. Il expire dans 10 minutes. Si tu n'as rien demandé, ignore ce message."})
    if result.status_code not in (200, 201):
        raise HTTPException(502, "Impossible d'envoyer le code")
    if not challenge:
        challenge = MemberCode(email=email, digest="", purpose=body.purpose, expires_at=now, sent_at=now)
        db.add(challenge)
    challenge.digest = code_digest(email, code)
    challenge.purpose = body.purpose
    challenge.expires_at = now + timedelta(minutes=10)
    challenge.sent_at = now
    challenge.attempts = 0
    challenge.consent = body.purpose == "signup"
    db.commit()
    return {"ok": True}


class CodeVerify(BaseModel):
    email: str
    code: str


@app.post("/api/member/auth/verify")
def verify_member_code(body: CodeVerify, request: Request, db: Session = Depends(db_session)):
    if request.headers.get("origin") != PUBLIC_ORIGIN:
        raise HTTPException(403, "Origine invalide")
    email = normalized_email(body.email)
    challenge = db.get(MemberCode, email)
    now = datetime.now(timezone.utc)
    if not challenge or challenge.expires_at.replace(tzinfo=timezone.utc) <= now or challenge.attempts >= 5:
        raise HTTPException(400, "Code expiré ou invalide")
    challenge.attempts += 1
    if not re.fullmatch(r"\d{6}", body.code) or not secrets.compare_digest(challenge.digest, code_digest(email, body.code)):
        db.commit()
        raise HTTPException(400, "Code expiré ou invalide")
    member = db.scalar(select(Member).where(Member.email == email))
    if not member and challenge.purpose == "signup" and challenge.consent:
        member = Member(email=email)
        db.add(member)
        db.flush()
        db.add(MemberConsent(member_id=member.id, accepted_at=now, version="2026-09-27"))
    if not member or effective_member_status(member) != "active":
        raise HTTPException(403)
    db.delete(challenge)
    db.commit()
    request.session.clear()
    request.session["member_id"] = member.id
    request.session["member_csrf"] = secrets.token_urlsafe(32)
    return {"ok": True, "id": member.id}


@app.get("/api/member/me")
def member_me(request: Request, member: Member = Depends(current_member)):
    return {"id": member.id, "email": member.email, "name": member.name,
            "csrf": request.session.get("member_csrf")}


@app.post("/api/member/auth/logout")
def member_logout(request: Request):
    request.session.clear()
    return {"ok": True}


@app.get("/api/member/profile")
def get_member_profile(member: Member = Depends(current_member), db: Session = Depends(db_session)):
    profile = db.get(MemberProfile, member.id)
    return {"code": profile.code if profile else None, "data": profile.data if profile else {}}


@app.get("/api/member/signals")
def get_member_signals(member: Member = Depends(current_member), db: Session = Depends(db_session)):
    signals = list(db.scalars(select(MemberSignal).where(MemberSignal.member_id == member.id)))
    return {"pins": [s.target_id for s in signals if s.kind == "pin"],
            "hooks": [s.target_id for s in signals if s.kind == "hook"]}


class SignalEdit(BaseModel):
    kind: str
    target_id: str
    active: bool


@app.put("/api/member/signals")
def set_member_signal(body: SignalEdit, member: Member = Depends(current_member), db: Session = Depends(db_session)):
    if body.kind not in ("pin", "hook") or not re.fullmatch(r"(?:member-\d+|[a-z]{2,20})", body.target_id):
        raise HTTPException(400)
    if body.target_id.startswith("member-"):
        target_id = int(body.target_id.split("-", 1)[1])
        target = db.get(Member, target_id)
        target_profile = db.get(MemberProfile, target_id)
        if target_id == member.id or not target or effective_member_status(target) != "active" or not target_profile or target_profile.data.get("invisible"):
            raise HTTPException(404)
    elif not db.get(DemoProfile, body.target_id):
        raise HTTPException(404)
    existing = db.scalar(select(MemberSignal).where(MemberSignal.member_id == member.id, MemberSignal.target_id == body.target_id, MemberSignal.kind == body.kind))
    if body.active and not existing:
        db.add(MemberSignal(member_id=member.id, target_id=body.target_id, kind=body.kind))
    elif not body.active and existing:
        db.delete(existing)
    db.commit()
    return {"ok": True}


class ProfileEdit(BaseModel):
    data: dict[str, str | bool | list[str]]


@app.put("/api/member/profile")
def save_member_profile(body: ProfileEdit, member: Member = Depends(current_member), db: Session = Depends(db_session)):
    if len(str(body.data)) > 15000 or any(len(str(value)) > 2000 for value in body.data.values()):
        raise HTTPException(400, "Profil trop long")
    if any(not isinstance(body.data.get(key, []), list) or len(body.data.get(key, [])) > 40 for key in ("style", "practice")):
        raise HTTPException(400, "Univers invalides")
    age = str(body.data.get("age") or "")
    if age and (not age.isdigit() or not 18 <= int(age) <= 99):
        raise HTTPException(400, "Âge invalide")
    profile = db.get(MemberProfile, member.id)
    if not profile:
        profile = MemberProfile(member_id=member.id, code="KQ-" + secrets.token_hex(4).upper(), data={})
        db.add(profile)
    profile.data = body.data
    profile.updated_at = datetime.now(timezone.utc)
    member.name = str(body.data.get("pseudo", ""))[:255]
    db.commit()
    return {"ok": True, "code": profile.code}


@app.post("/api/member/photos")
async def member_photo(photo: UploadFile = File(), member: Member = Depends(current_member), db: Session = Depends(db_session)):
    data = await photo.read(5_000_001)
    mime = "image/jpeg" if data.startswith(b"\xff\xd8\xff") else "image/png" if data.startswith(b"\x89PNG\r\n\x1a\n") else "image/webp" if data.startswith(b"RIFF") and data[8:12] == b"WEBP" else ""
    if not mime or len(data) > 5_000_000:
        raise HTTPException(400, "JPEG, PNG ou WebP de 5 Mo maximum")
    item = Photo(id=str(uuid.uuid4()), member_id=member.id, mime=mime, data=data, status="pending")
    db.add(item)
    db.commit()
    return {"id": item.id, "status": "pending", "message": "Photo en modération."}


@app.delete("/api/member/account")
def close_member_account(request: Request, member: Member = Depends(current_member), db: Session = Depends(db_session)):
    erase_member(db, member)
    db.commit()
    request.session.clear()
    return {"ok": True}


def erase_member(db: Session, member: Member):
    challenge = db.get(MemberCode, member.email)
    if challenge:
        db.delete(challenge)
    profile = db.get(MemberProfile, member.id)
    if profile:
        db.delete(profile)
    for signal in db.scalars(select(MemberSignal).where(
        (MemberSignal.member_id == member.id) | (MemberSignal.target_id == f"member-{member.id}")
    )):
        db.delete(signal)
    for comment in db.scalars(select(Comment).where(Comment.member_id == member.id)):
        db.delete(comment)
    for photo in db.scalars(select(Photo).where(Photo.member_id == member.id)):
        photo.data, photo.status = b"", "deleted"
    member.email = f"deleted-{member.id}@invalid.local"
    member.name = ""
    member.status = "deleted"
    member.deleted_at = datetime.now(timezone.utc)


class EmailChange(BaseModel):
    email: str
    code: str = ""


@app.post("/api/member/email/request")
async def request_email_change(body: EmailChange, member: Member = Depends(current_member), db: Session = Depends(db_session)):
    email = normalized_email(body.email)
    if email == member.email or db.scalar(select(Member).where(Member.email == email)):
        raise HTTPException(409, "Adresse déjà utilisée")
    key = os.environ.get("KINQ_RESEND_API_KEY", "")
    if not key:
        raise HTTPException(503, "Envoi des e-mails KINQ non configuré")
    now = datetime.now(timezone.utc)
    challenge = db.get(MemberCode, email)
    if challenge and challenge.sent_at.replace(tzinfo=timezone.utc) > now - timedelta(seconds=60):
        raise HTTPException(429, "Attends une minute avant de demander un autre code")
    code = f"{secrets.randbelow(1_000_000):06d}"
    async with httpx.AsyncClient(timeout=12) as client:
        result = await client.post("https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {key}"},
            json={"from": os.environ.get("KINQ_RESEND_FROM", "KINQ <connexion@kinq-app.com>"),
                  "to": [email], "subject": "Confirme ta nouvelle adresse KINQ",
                  "text": f"Ton code de confirmation KINQ est {code}. Il expire dans 10 minutes."})
    if result.status_code not in (200, 201):
        raise HTTPException(502, "Impossible d'envoyer le code")
    if not challenge:
        challenge = MemberCode(email=email, digest="", purpose="change", expires_at=now, sent_at=now)
        db.add(challenge)
    challenge.digest, challenge.purpose, challenge.member_id = code_digest(email, code), "change", member.id
    challenge.expires_at, challenge.sent_at, challenge.attempts = now + timedelta(minutes=10), now, 0
    db.commit()
    return {"ok": True}


@app.post("/api/member/email/verify")
def verify_email_change(body: EmailChange, member: Member = Depends(current_member), db: Session = Depends(db_session)):
    email = normalized_email(body.email)
    challenge = db.get(MemberCode, email)
    if not challenge or challenge.purpose != "change" or challenge.member_id != member.id or challenge.expires_at.replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc) or challenge.attempts >= 5:
        raise HTTPException(400, "Code expiré ou invalide")
    challenge.attempts += 1
    if not re.fullmatch(r"\d{6}", body.code) or not secrets.compare_digest(challenge.digest, code_digest(email, body.code)):
        db.commit()
        raise HTTPException(400, "Code expiré ou invalide")
    if db.scalar(select(Member).where(Member.email == email)):
        raise HTTPException(409)
    member.email = email
    db.delete(challenge)
    db.commit()
    return {"ok": True}


@app.get("/api/admin/auth/login")
def login(request: Request):
    if not CLIENT_ID or not CLIENT_SECRET or not ADMIN_EMAIL:
        raise HTTPException(503, "OAuth KINQ non configuré")
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    request.session["oauth_state"] = state
    request.session["oauth_nonce"] = nonce
    request.session["oauth_verifier"] = verifier
    params = {"client_id": CLIENT_ID, "redirect_uri": PUBLIC_ORIGIN + "/api/admin/auth/callback", "response_type": "code", "scope": "openid email profile", "state": state, "nonce": nonce, "code_challenge": challenge, "code_challenge_method": "S256", "hd": "theethercompany.com", "prompt": "select_account"}
    return RedirectResponse("https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params))


@app.get("/api/admin/auth/callback")
async def callback(request: Request, code: str = "", state: str = "", db: Session = Depends(db_session)):
    def failed(reason: str):
        request.session.clear()
        return RedirectResponse("/admin?auth_error=" + reason, status_code=303)

    expected = request.session.pop("oauth_state", None)
    nonce = request.session.pop("oauth_nonce", None)
    verifier = request.session.pop("oauth_verifier", None)
    if not code or not expected or not nonce or not verifier or not secrets.compare_digest(state, expected):
        return failed("state")
    try:
        async with httpx.AsyncClient(timeout=12) as client:
            result = await client.post("https://oauth2.googleapis.com/token", data={"code": code, "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "redirect_uri": PUBLIC_ORIGIN + "/api/admin/auth/callback", "grant_type": "authorization_code", "code_verifier": verifier})
    except httpx.RequestError:
        return failed("google")
    if result.status_code != 200:
        return failed("google")
    try:
        identity = id_token.verify_oauth2_token(result.json()["id_token"], google_requests.Request(), CLIENT_ID)
    except Exception:
        return failed("google")
    email = str(identity.get("email", "")).lower()
    if not identity.get("sub") or not secrets.compare_digest(str(identity.get("nonce", "")), nonce):
        return failed("google")
    if identity.get("hd") != "theethercompany.com" or identity.get("email_verified") is not True or not email.endswith("@theethercompany.com"):
        return failed("workspace")
    staff = db.scalar(select(Staff).where(Staff.google_sub == identity["sub"]))
    if staff and staff.email != email:
        return failed("account")
    if not staff:
        existing = db.scalar(select(Staff).where(Staff.email == email))
        if existing and existing.google_sub.startswith("email:") and email == ADMIN_EMAIL:
            staff = existing
            staff.google_sub = identity["sub"]
        elif existing:
            return failed("account")
    if not staff:
        staff = Staff(google_sub=identity["sub"], email=email, name=identity.get("name", ""), role="admin" if email == ADMIN_EMAIL else "user")
        db.add(staff)
        db.flush()
    staff.name = identity.get("name", staff.name)
    db.commit()
    request.session.clear()
    request.session["staff_id"] = staff.id
    request.session["csrf"] = secrets.token_urlsafe(32)
    return RedirectResponse("/admin", status_code=303)


@app.post("/api/admin/auth/logout")
def logout(request: Request):
    request.session.clear()
    return {"ok": True}


@app.get("/api/admin/me")
def me(request: Request, staff: Staff = Depends(current_staff)):
    return {"id": staff.id, "email": staff.email, "name": staff.name, "role": staff.role, "csrf": request.session["csrf"]}


@app.get("/api/public/settings/analytics")
def public_analytics_settings(db: Session = Depends(db_session)):
    setting = db.get(SiteSetting, "analytics_site_id")
    return {"site_id": setting.value if setting else DEFAULT_PIXEL_SITE_ID}


@app.get("/api/admin/settings/analytics")
def admin_analytics_settings(_: Staff = Depends(current_staff), db: Session = Depends(db_session)):
    return public_analytics_settings(db)


class AnalyticsSettingChange(BaseModel):
    site_id: str


@app.put("/api/admin/settings/analytics")
def update_analytics_settings(body: AnalyticsSettingChange, staff: Staff = Depends(admin), db: Session = Depends(db_session)):
    site_id = body.site_id.strip().lower()
    if site_id and not re.fullmatch(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", site_id):
        raise HTTPException(400, "Identifiant de pixel invalide")
    setting = db.get(SiteSetting, "analytics_site_id")
    if setting:
        setting.value = site_id
    else:
        db.add(SiteSetting(key="analytics_site_id", value=site_id))
    log(db, staff, "settings.analytics", site_id or "disabled")
    db.commit()
    return {"site_id": site_id}


@app.middleware("http")
async def csrf_protect(request: Request, call_next):
    if request.url.path.startswith("/api/admin/") and request.method in ("POST", "PATCH", "PUT", "DELETE") and request.url.path != "/api/admin/auth/logout":
        origin = request.headers.get("origin")
        if origin != PUBLIC_ORIGIN or not request.session.get("csrf") or not secrets.compare_digest(request.headers.get("x-csrf-token", ""), request.session["csrf"]):
            return Response("CSRF", status_code=403)
    if request.url.path.startswith("/api/member/") and request.method in ("POST", "PATCH", "PUT", "DELETE") and request.url.path not in ("/api/member/auth/request", "/api/member/auth/verify"):
        origin = request.headers.get("origin")
        if origin != PUBLIC_ORIGIN or not request.session.get("member_csrf") or not secrets.compare_digest(request.headers.get("x-csrf-token", ""), request.session["member_csrf"]):
            return Response("CSRF", status_code=403)
    return await call_next(request)


@app.get("/api/admin/staff")
def staff_list(_: Staff = Depends(current_staff), db: Session = Depends(db_session)):
    return [{"id": s.id, "name": s.name, "email": s.email, "role": s.role, "active": s.active} for s in db.scalars(select(Staff).order_by(Staff.id))]


class RoleChange(BaseModel):
    role: str


@app.patch("/api/admin/staff/{staff_id}/role")
def change_role(staff_id: int, body: RoleChange, owner: Staff = Depends(admin), db: Session = Depends(db_session)):
    target = db.get(Staff, staff_id)
    if not target or body.role not in ("user", "moderator") or target.id == owner.id:
        raise HTTPException(400, "Rôle invalide")
    target.role = body.role
    log(db, owner, "staff.role", target.email)
    db.commit()
    return {"ok": True}


@app.get("/api/admin/members")
def members(_: Staff = Depends(editor), db: Session = Depends(db_session)):
    return [{"id": m.id, "email": m.email, "name": m.name, "status": effective_member_status(m), "ban_until": m.ban_until, "deleted_at": m.deleted_at} for m in db.scalars(select(Member).order_by(Member.id.desc()).limit(200))]


class MemberRegistration(BaseModel):
    email: str = Field(max_length=255)
    name: str = Field(default="", max_length=255)


@app.post("/api/internal/members")
def register_member(body: MemberRegistration, x_kinq_upload_key: str = Header(default=""), db: Session = Depends(db_session)):
    # Server-to-server bridge for the future member authentication service.
    require_service_key(x_kinq_upload_key)
    email = body.email.strip().lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise HTTPException(400, "Adresse invalide")
    member = db.scalar(select(Member).where(Member.email == email))
    if not member:
        member = Member(email=email, name=body.name.strip())
        db.add(member)
        db.commit()
        db.refresh(member)
    return {"id": member.id, "status": effective_member_status(member)}


class MemberEdit(BaseModel):
    name: str = Field(max_length=255)


@app.patch("/api/admin/members/{member_id}")
def edit_member(member_id: int, body: MemberEdit, staff: Staff = Depends(editor), db: Session = Depends(db_session)):
    m = db.get(Member, member_id)
    if not m or m.deleted_at:
        raise HTTPException(404)
    m.name = body.name.strip()
    log(db, staff, "member.edit", str(member_id))
    db.commit()
    return {"ok": True}


class StatusChange(BaseModel):
    status: str
    until: datetime | None = None


@app.patch("/api/admin/members/{member_id}/status")
def member_status(member_id: int, body: StatusChange, staff: Staff = Depends(editor), db: Session = Depends(db_session)):
    m = db.get(Member, member_id)
    if not m or m.deleted_at or body.status not in ("active", "suspended", "banned_temporary", "banned_permanent"):
        raise HTTPException(400, "Statut invalide")
    if body.status == "banned_temporary" and (not body.until or body.until <= datetime.now(timezone.utc)):
        raise HTTPException(400, "Date de fin future requise")
    m.status, m.ban_until = body.status, body.until if body.status == "banned_temporary" else None
    log(db, staff, "member.status." + body.status, str(member_id))
    db.commit()
    return {"ok": True}


@app.delete("/api/admin/members/{member_id}")
def delete_member(member_id: int, owner: Staff = Depends(admin), db: Session = Depends(db_session)):
    m = db.get(Member, member_id)
    if not m or m.deleted_at:
        raise HTTPException(404)
    erase_member(db, m)
    log(db, owner, "member.delete", str(member_id))
    db.commit()
    return {"ok": True}


@app.post("/api/photos")
async def upload_photo(member_id: int = Form(), photo: UploadFile = File(), x_kinq_upload_key: str = Header(default=""), db: Session = Depends(db_session)):
    # Called by a future authenticated KINQ member service, never directly by the prototype.
    require_service_key(x_kinq_upload_key)
    member = db.get(Member, member_id)
    if not member or effective_member_status(member) != "active":
        raise HTTPException(403)
    data = await photo.read(5_000_001)
    mime = "image/jpeg" if data.startswith(b"\xff\xd8\xff") else "image/png" if data.startswith(b"\x89PNG\r\n\x1a\n") else "image/webp" if data.startswith(b"RIFF") and data[8:12] == b"WEBP" else ""
    if not mime or len(data) > 5_000_000:
        raise HTTPException(400, "JPEG, PNG ou WebP de 5 Mo maximum")
    item = Photo(id=str(uuid.uuid4()), member_id=member_id, mime=mime, data=data, status="pending")
    db.add(item)
    db.commit()
    return {"id": item.id, "status": "pending", "message": "Photo en modération. Elle ne sera visible qu’après validation."}


@app.get("/api/admin/photos")
def photo_queue(_: Staff = Depends(editor), db: Session = Depends(db_session)):
    return [{"id": p.id, "member_id": p.member_id, "status": p.status, "created_at": p.created_at} for p in db.scalars(select(Photo).where(Photo.status == "pending").order_by(Photo.created_at).limit(100))]


@app.get("/api/admin/photos/{photo_id}/preview")
def photo_preview(photo_id: str, _: Staff = Depends(editor), db: Session = Depends(db_session)):
    p = db.get(Photo, photo_id)
    if not p or p.status == "deleted":
        raise HTTPException(404)
    return Response(p.data, media_type=p.mime, headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"})


@app.get("/api/photos/{photo_id}")
def public_photo(photo_id: str, db: Session = Depends(db_session)):
    p = db.get(Photo, photo_id)
    m = db.get(Member, p.member_id) if p else None
    if not p or p.status != "approved" or not m or effective_member_status(m) != "active":
        raise HTTPException(404)
    return Response(p.data, media_type=p.mime, headers={"X-Content-Type-Options": "nosniff"})


class Decision(BaseModel):
    status: str


@app.patch("/api/admin/photos/{photo_id}")
def decide_photo(photo_id: str, body: Decision, staff: Staff = Depends(editor), db: Session = Depends(db_session)):
    p = db.get(Photo, photo_id)
    if not p or p.status != "pending" or body.status not in ("approved", "rejected"):
        raise HTTPException(400)
    p.status, p.reviewed_by = body.status, staff.id
    if body.status == "rejected":
        p.data = b""
    log(db, staff, "photo." + body.status, photo_id)
    db.commit()
    return {"ok": True}


@app.get("/api/admin/articles")
def articles(_: Staff = Depends(current_staff), db: Session = Depends(db_session)):
    return [{"id": a.id, "slug": a.slug, "title": a.title, "summary": a.summary, "body": a.body, "status": a.status} for a in db.scalars(select(Article).order_by(Article.updated_at.desc()))]


class ArticleEdit(BaseModel):
    slug: str = Field(max_length=180)
    title: str = Field(max_length=255)
    summary: str = ""
    body: str = ""
    status: str = "draft"


def validate_article(body: ArticleEdit):
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", body.slug) or not body.title.strip() or body.status not in ("draft", "published"):
        raise HTTPException(400, "Article invalide")


@app.post("/api/admin/articles")
def create_article(body: ArticleEdit, staff: Staff = Depends(editor), db: Session = Depends(db_session)):
    validate_article(body)
    if db.scalar(select(Article).where(Article.slug == body.slug)):
        raise HTTPException(409, "Slug déjà utilisé")
    a = Article(**body.model_dump())
    db.add(a)
    db.flush()
    log(db, staff, "article.create", str(a.id))
    db.commit()
    return {"id": a.id}


@app.put("/api/admin/articles/{article_id}")
def update_article(article_id: int, body: ArticleEdit, staff: Staff = Depends(editor), db: Session = Depends(db_session)):
    validate_article(body)
    a = db.get(Article, article_id)
    if not a:
        raise HTTPException(404)
    if db.scalar(select(Article).where(Article.slug == body.slug, Article.id != article_id)):
        raise HTTPException(409, "Slug déjà utilisé")
    for key, value in body.model_dump().items():
        setattr(a, key, value)
    a.updated_at = datetime.now(timezone.utc)
    log(db, staff, "article.update", str(article_id))
    db.commit()
    return {"ok": True}


@app.delete("/api/admin/articles/{article_id}")
def delete_article(article_id: int, staff: Staff = Depends(editor), db: Session = Depends(db_session)):
    a = db.get(Article, article_id)
    if not a:
        raise HTTPException(404)
    db.delete(a)
    log(db, staff, "article.delete", str(article_id))
    db.commit()
    return {"ok": True}


@app.get("/api/articles")
def published_articles(db: Session = Depends(db_session)):
    return [{"slug": a.slug, "title": a.title, "summary": a.summary, "body": a.body} for a in db.scalars(select(Article).where(Article.status == "published").order_by(Article.updated_at.desc()))]


@app.get("/api/articles/{slug}")
def published_article(slug: str, db: Session = Depends(db_session)):
    article = db.scalar(select(Article).where(Article.slug == slug, Article.status == "published"))
    if not article:
        raise HTTPException(404)
    return {"slug": article.slug, "title": article.title, "summary": article.summary, "body": article.body}


@app.get("/api/admin/comments")
def comments(_: Staff = Depends(editor), db: Session = Depends(db_session)):
    return [{"id": c.id, "article_id": c.article_id, "member_id": c.member_id, "body": c.body, "status": c.status} for c in db.scalars(select(Comment).order_by(Comment.id.desc()).limit(200))]


@app.patch("/api/admin/comments/{comment_id}")
def decide_comment(comment_id: int, body: Decision, staff: Staff = Depends(editor), db: Session = Depends(db_session)):
    c = db.get(Comment, comment_id)
    if not c or body.status not in ("approved", "rejected"):
        raise HTTPException(400)
    c.status = body.status
    log(db, staff, "comment." + body.status, str(comment_id))
    db.commit()
    return {"ok": True}


# SessionMiddleware must wrap the CSRF middleware so request.session exists there.
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET, same_site="lax", https_only=PUBLIC_ORIGIN.startswith("https://"), session_cookie="kinq_session", max_age=8 * 3600)
