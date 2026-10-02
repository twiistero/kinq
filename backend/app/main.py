"""KINQ private administration API. All writes require a Workspace session."""
import os
import re
import secrets
import uuid
import hashlib
import hmac
import html
import base64
import math
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse, Response
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from pydantic import BaseModel, Field
from .profile_preferences import ProfileEdit
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, JSON, LargeBinary, String, Text, UniqueConstraint, create_engine, func, select, or_
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


class PrivatePhoto(Base):
    # Existing photos remain public. A row marks an explicitly private photo.
    __tablename__ = "private_photos"
    photo_id: Mapped[str] = mapped_column(ForeignKey("photos.id"), primary_key=True)


class PhotoAccessRequest(Base):
    __tablename__ = "photo_access_requests"
    __table_args__ = (UniqueConstraint("owner_id", "requester_id"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("members.id"), index=True)
    requester_id: Mapped[int] = mapped_column(ForeignKey("members.id"), index=True)
    status: Mapped[str] = mapped_column(String(12), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


def public_photo_condition():
    return ~Photo.id.in_(select(PrivatePhoto.photo_id))


class Article(Base):
    __tablename__ = "articles"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(180), unique=True)
    title: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text, default="")
    body: Mapped[str] = mapped_column(Text, default="")
    art_words: Mapped[list] = mapped_column(JSON, default=list)
    category: Mapped[str] = mapped_column(String(40), default="Entre nous")
    status: Mapped[str] = mapped_column(String(20), default="draft")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ArticleDraft(Base):
    __tablename__ = "article_drafts"
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), primary_key=True)
    payload: Mapped[dict] = mapped_column(JSON)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"))
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"))
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")


class JournalComment(Base):
    __tablename__ = "journal_comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    article_slug: Mapped[str] = mapped_column(String(180), index=True)
    author_name: Mapped[str] = mapped_column(String(80))
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("journal_comments.id"), nullable=True)
    staff_id: Mapped[int | None] = mapped_column(ForeignKey("staff.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


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


class MemberLoginCode(Base):
    """Explicitly provisioned member credential; no client-side or global fallback."""
    __tablename__ = "member_login_codes"
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), primary_key=True)
    digest: Mapped[str] = mapped_column(String(64))


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


class MemberActivity(Base):
    __tablename__ = "member_activity"
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), primary_key=True)
    seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class MemberLocation(Base):
    # Only the authenticated location endpoint writes here; coordinates never
    # enter profile JSON or a public response. One current fix, no history.
    __tablename__ = "member_locations"
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), primary_key=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    accuracy: Mapped[float] = mapped_column(Float)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class MemberMessage(Base):
    __tablename__ = "member_messages"
    __table_args__ = (UniqueConstraint("sender_id", "nonce"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("members.id"), index=True)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("members.id"), index=True)
    body: Mapped[str] = mapped_column(Text)
    nonce: Mapped[str] = mapped_column(String(36))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


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


def profile_projection(profile: MemberProfile, member: Member, db: Session, viewer: Member):
    data = profile.data or {}
    approved = list(db.scalars(select(Photo).where(Photo.member_id == member.id, Photo.status == "approved", public_photo_condition()).order_by(Photo.created_at.desc(), Photo.id)))
    photos = [f"/api/photos/{photo.id}" for photo in approved] if not data.get("discreet") else []
    consent = db.get(MemberConsent, member.id)
    activity = db.get(MemberActivity, member.id)
    safe = lambda value, limit: html.escape(str(value or "")[:limit], quote=True)
    fields = ("experience", "dynamic", "exclusivity", "sex", "sexualPosition", "gear", "gearDetail", "relation", "wishes", "bio", "instagram", "twitter", "kinkPreferences")
    details = {key: data[key] for key in fields if key in data}
    if not data.get("hideLimits") and "limits" in data:
        details["limits"] = data["limits"]
    distance, measured_at = profile_distance(viewer, member, db)
    return {
        "id": f"member-{member.id}", "name": safe(data.get("pseudo") or "Membre", 80),
        "age": int(data.get("age") or 18), "city": "" if data.get("hideCity") else safe(data.get("city"), 80),
        "kinks": [safe(k, 80) for k in list(data.get("style") or []) + list(data.get("practice") or [])][:120],
        "role": safe(data.get("dynamic"), 80), "intent": "", "pace": "",
        "quote": safe(data.get("wishes"), 300), "bio": safe(data.get("bio"), 1000),
        "photo": photos[0] if photos else None, "photos": photos,
        "distanceKm": distance, "distanceUpdatedAt": measured_at,
        "code": profile.code, "details": {"data": details},
        "joinedAt": consent.accepted_at.replace(tzinfo=timezone.utc).isoformat(timespec="seconds") if consent else None,
        "online": bool(activity and not data.get("discreet") and not data.get("invisible") and activity.seen_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc) - timedelta(seconds=90)),
        "lastSeenAt": activity.seen_at.replace(tzinfo=timezone.utc).isoformat(timespec="seconds") if activity and not data.get("discreet") and not data.get("invisible") else None,
        "shareURL": PUBLIC_ORIGIN + "/p/" + profile.code.removeprefix("KQ-"),
    }


@app.get("/api/profiles")
def public_profiles(member: Member = Depends(current_member), db: Session = Depends(db_session)):
    return [profile_projection(profile, target, db, member)
        for profile, target in db.execute(select(MemberProfile, Member).join(Member, Member.id == MemberProfile.member_id).where(~Member.id.in_(blocked_ids(member.id))))
        if effective_member_status(target) == "active" and not (profile.data or {}).get("invisible")]


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
    location = db.get(MemberLocation, member.id)
    if location:
        db.delete(location)
    credential = db.get(MemberLoginCode, member.id) if member and body.purpose == "login" else None
    if credential:
        digest = credential.digest
    else:
        if not key:
            raise HTTPException(503, "Envoi des e-mails KINQ non configuré")
        code = f"{secrets.randbelow(1_000_000):06d}"
        digest = code_digest(email, code)
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
    challenge.digest = digest
    challenge.purpose = body.purpose
    challenge.expires_at = now + timedelta(minutes=10)
    challenge.sent_at = now
    challenge.attempts = 0
    challenge.consent = body.purpose == "signup"
    db.commit()
    return {"ok": True, "delivery": "configured_code" if credential else "email"}


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
    return {"code": profile.code if profile else None, "data": profile.data if profile else {},
            "view": profile_projection(profile, member, db, member) if profile else None,
            "locationEnabled": db.get(MemberLocation, member.id) is not None}


class LocationEdit(BaseModel):
    latitude: float = Field(ge=-90, le=90, allow_inf_nan=False)
    longitude: float = Field(ge=-180, le=180, allow_inf_nan=False)
    accuracy: float = Field(ge=0, le=5000, allow_inf_nan=False)


@app.put("/api/member/location")
def save_member_location(body: LocationEdit, member: Member = Depends(current_member), db: Session = Depends(db_session)):
    fix = db.get(MemberLocation, member.id)
    if not fix:
        fix = MemberLocation(member_id=member.id)
        db.add(fix)
    fix.latitude, fix.longitude, fix.accuracy = body.latitude, body.longitude, body.accuracy
    fix.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"ok": True}


@app.delete("/api/member/location")
def remove_member_location(member: Member = Depends(current_member), db: Session = Depends(db_session)):
    fix = db.get(MemberLocation, member.id)
    if fix:
        db.delete(fix)
        db.commit()
    return {"ok": True}


def profile_distance(viewer: Member, target: Member, db: Session):
    if viewer.id == target.id:
        return None, None
    for person in (viewer, target):
        profile = db.get(MemberProfile, person.id)
        data = profile.data if profile else {}
        if not profile or data.get("invisible") or data.get("discreet") or data.get("hideCity", True):
            return None, None
    fixes = [db.get(MemberLocation, person.id) for person in (viewer, target)]
    now = datetime.now(timezone.utc)
    if any(not fix or fix.accuracy > 1000 or not 0 <= (now - fix.updated_at.replace(tzinfo=timezone.utc)).total_seconds() <= 180 for fix in fixes):
        return None, None
    a, b = fixes
    lat1, lat2 = math.radians(a.latitude), math.radians(b.latitude)
    dlat, dlon = lat2 - lat1, math.radians(b.longitude - a.longitude)
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    km = 6371.0088 * 2 * math.asin(math.sqrt(min(1, max(0, h))))
    # A kilometre estimate, never coordinates or a metre-level tracking signal.
    return math.floor(km + 0.5), min(fix.updated_at for fix in fixes).replace(tzinfo=timezone.utc).isoformat(timespec="seconds")


@app.post("/api/member/presence")
def member_presence(member: Member = Depends(current_member), db: Session = Depends(db_session)):
    activity = db.get(MemberActivity, member.id)
    now = datetime.now(timezone.utc)
    if activity:
        activity.seen_at = now
    else:
        db.add(MemberActivity(member_id=member.id, seen_at=now))
    db.commit()
    return {"ok": True}


class MemberBlock(Base):
    __tablename__ = "member_blocks"
    owner_id: Mapped[int] = mapped_column(ForeignKey("members.id"), primary_key=True)
    target_id: Mapped[int] = mapped_column(ForeignKey("members.id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class MemberReport(Base):
    __tablename__ = "member_reports"
    __table_args__ = (UniqueConstraint("reporter_id", "nonce"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("members.id"), index=True)
    target_id: Mapped[int] = mapped_column(ForeignKey("members.id"), index=True)
    reason: Mapped[str] = mapped_column(String(30))
    detail: Mapped[str] = mapped_column(Text, default="")
    nonce: Mapped[str] = mapped_column(String(36))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


def blocked_ids(member_id: int):
    # Both directions: neither person can discover or contact the other.
    return select(MemberBlock.target_id).where(MemberBlock.owner_id == member_id).union(
        select(MemberBlock.owner_id).where(MemberBlock.target_id == member_id))


def members_blocked(db: Session, first: int, second: int):
    return bool(db.get(MemberBlock, (first, second)) or db.get(MemberBlock, (second, first)))


def message_target(target_id: int, member: Member, db: Session):
    target = db.get(Member, target_id)
    profile = db.get(MemberProfile, target_id)
    if target_id == member.id or not target or effective_member_status(target) != "active" or not profile or profile.data.get("invisible") or members_blocked(db, member.id, target_id):
        raise HTTPException(404, "Profil indisponible")
    return target


def message_projection(message: MemberMessage):
    return {"id": message.id, "senderID": message.sender_id, "body": message.body,
            "createdAt": message.created_at.replace(tzinfo=timezone.utc).isoformat(timespec="seconds")}


class MemberNotification(Base):
    __tablename__ = "member_notifications"
    __table_args__ = (UniqueConstraint("event_key"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("members.id"), index=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey("members.id"), index=True)
    kind: Mapped[str] = mapped_column(String(12))
    event_key: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


def add_member_notification(db: Session, recipient_id: int, actor_id: int, kind: str, event_key: str, created_at=None):
    if recipient_id == actor_id or members_blocked(db, recipient_id, actor_id):
        return
    # A concurrent duplicate must not abort the message/signal transaction.
    from sqlalchemy.exc import IntegrityError
    try:
        with db.begin_nested():
            db.add(MemberNotification(id=str(uuid.uuid4()), recipient_id=recipient_id,
                actor_id=actor_id, kind=kind, event_key=event_key,
                created_at=created_at or datetime.now(timezone.utc)))
            db.flush()
    except IntegrityError:
        if not db.scalar(select(MemberNotification.id).where(MemberNotification.event_key == event_key)):
            raise


def notification_query(member_id: int):
    # Suppress inaccessible identities, including after a moderation/privacy change.
    now = datetime.now(timezone.utc)
    return select(MemberNotification, Member, MemberProfile).join(
        Member, Member.id == MemberNotification.actor_id).join(
        MemberProfile, MemberProfile.member_id == Member.id).where(
        MemberNotification.recipient_id == member_id,
        ~Member.id.in_(blocked_ids(member_id)),
        or_(Member.status == "active", (Member.status == "banned_temporary") & (Member.ban_until <= now)),
        func.coalesce(MemberProfile.data["invisible"].as_boolean(), False) == False,
        # Messages remain attributable to their sender even in discreet mode.
        or_(MemberNotification.kind.in_(("message", "photo", "photo_grant")), func.coalesce(MemberProfile.data["discreet"].as_boolean(), False) == False))


@app.get("/api/member/notifications")
def member_notifications(member: Member = Depends(current_member), db: Session = Depends(db_session)):
    query = notification_query(member.id)
    unread = db.scalar(select(func.count()).select_from(query.where(MemberNotification.read_at.is_(None)).subquery()))
    items = []
    for notification, actor, profile in db.execute(query.order_by(MemberNotification.created_at.desc(), MemberNotification.id).limit(100)):
        data = profile.data or {}
        photo = None if data.get("discreet") else db.scalar(select(Photo).where(Photo.member_id == actor.id, Photo.status == "approved", public_photo_condition()).order_by(Photo.created_at.desc(), Photo.id).limit(1))
        items.append({"id": notification.id, "actorID": f"member-{actor.id}",
            "actorName": str(data.get("pseudo") or actor.name or "Membre")[:80],
            "photo": f"/api/photos/{photo.id}" if photo else None, "kind": notification.kind,
            "createdAt": notification.created_at.replace(tzinfo=timezone.utc).isoformat(timespec="seconds"),
            "read": notification.read_at is not None,
            "isTest": actor.email.startswith("presentation-") and actor.email.endswith("@example.invalid")})
    return {"items": items, "unreadCount": unread or 0}


def photo_access_projection(item, owner_id: int, requester_id: int, db: Session):
    photos = []
    if item and item.status == "accepted":
        photos = ["/api/member/private-photos/" + p.id for p in db.scalars(select(Photo).join(
            PrivatePhoto, PrivatePhoto.photo_id == Photo.id).where(
            Photo.member_id == owner_id, Photo.status == "approved").order_by(Photo.created_at.desc(), Photo.id))]
    return {"id": item.id if item else None, "status": item.status if item else "none", "photos": photos}


@app.get("/api/member/photo-access/{target_id}")
def get_photo_access(target_id: int, member: Member = Depends(current_member), db: Session = Depends(db_session)):
    message_target(target_id, member, db)
    item = db.scalar(select(PhotoAccessRequest).where(PhotoAccessRequest.owner_id == target_id, PhotoAccessRequest.requester_id == member.id))
    return photo_access_projection(item, target_id, member.id, db)


@app.post("/api/member/photo-access/{target_id}")
def request_photo_access(target_id: int, member: Member = Depends(current_member), db: Session = Depends(db_session)):
    message_target(target_id, member, db)
    from sqlalchemy.exc import IntegrityError
    item = db.scalar(select(PhotoAccessRequest).where(PhotoAccessRequest.owner_id == target_id, PhotoAccessRequest.requester_id == member.id))
    if not item:
        # Deduplicate concurrent taps and notifications in the same transaction.
        try:
            with db.begin_nested():
                item = PhotoAccessRequest(id=str(uuid.uuid4()), owner_id=target_id, requester_id=member.id, status="pending")
                db.add(item); db.flush()
        except IntegrityError:
            item = db.scalar(select(PhotoAccessRequest).where(PhotoAccessRequest.owner_id == target_id, PhotoAccessRequest.requester_id == member.id))
            if not item:
                raise
        add_member_notification(db, target_id, member.id, "photo", "photo-request:" + item.id)
        db.commit()
    return photo_access_projection(item, target_id, member.id, db)


@app.get("/api/member/photo-access-requests")
def received_photo_requests(member: Member = Depends(current_member), db: Session = Depends(db_session)):
    rows = []
    for item, requester, profile in db.execute(select(PhotoAccessRequest, Member, MemberProfile).join(
        Member, Member.id == PhotoAccessRequest.requester_id).join(MemberProfile, MemberProfile.member_id == Member.id).where(
        PhotoAccessRequest.owner_id == member.id).order_by(PhotoAccessRequest.created_at.desc()).limit(100)):
        if effective_member_status(requester) != "active" or profile.data.get("invisible") or members_blocked(db, member.id, requester.id):
            continue
        rows.append({"id": item.id, "requesterID": f"member-{requester.id}", "name": str(profile.data.get("pseudo") or "Membre")[:80],
                     "status": item.status, "createdAt": item.created_at.replace(tzinfo=timezone.utc).isoformat(timespec="seconds")})
    return rows


class PhotoAccessDecision(BaseModel):
    status: str


@app.put("/api/member/photo-access-requests/{request_id}")
def decide_photo_access(request_id: uuid.UUID, body: PhotoAccessDecision, member: Member = Depends(current_member), db: Session = Depends(db_session)):
    item = db.get(PhotoAccessRequest, str(request_id))
    if not item or item.owner_id != member.id:
        raise HTTPException(404, "Demande indisponible")
    if body.status not in ("accepted", "declined"):
        raise HTTPException(400, "Décision invalide")
    message_target(item.requester_id, member, db)
    if item.status != body.status:
        item.status, item.updated_at = body.status, datetime.now(timezone.utc)
        if body.status == "accepted":
            add_member_notification(db, item.requester_id, member.id, "photo_grant", "photo-grant:" + item.id + ":" + item.updated_at.isoformat())
        db.commit()
    return {"ok": True, "status": item.status}


@app.get("/api/member/private-photos/{photo_id}")
def private_photo(photo_id: str, member: Member = Depends(current_member), db: Session = Depends(db_session)):
    photo = db.get(Photo, photo_id)
    owner = db.get(Member, photo.member_id) if photo else None
    profile = db.get(MemberProfile, photo.member_id) if photo else None
    if not photo or not db.get(PrivatePhoto, photo_id) or photo.status != "approved" or not owner or effective_member_status(owner) != "active" or not profile or profile.data.get("invisible") or members_blocked(db, member.id, photo.member_id):
        raise HTTPException(404, "Photo indisponible")
    if photo.member_id != member.id and not db.scalar(select(PhotoAccessRequest.id).where(
        PhotoAccessRequest.owner_id == photo.member_id, PhotoAccessRequest.requester_id == member.id, PhotoAccessRequest.status == "accepted")):
        raise HTTPException(404, "Photo indisponible")
    return Response(photo.data, media_type=photo.mime, headers={"Cache-Control": "no-store, private", "Vary": "Cookie", "X-Content-Type-Options": "nosniff"})


class NotificationRead(BaseModel):
    ids: list[uuid.UUID] = Field(default_factory=list, max_length=100)


@app.put("/api/member/notifications/read")
def read_member_notifications(body: NotificationRead, member: Member = Depends(current_member), db: Session = Depends(db_session)):
    now = datetime.now(timezone.utc)
    for item in db.scalars(select(MemberNotification).where(MemberNotification.recipient_id == member.id,
            MemberNotification.id.in_([str(value) for value in body.ids]), MemberNotification.read_at.is_(None))):
        item.read_at = now
    db.commit()
    return {"ok": True}


@app.post("/api/member/profile-visits/{target_id}")
def visit_member_profile(target_id: int, member: Member = Depends(current_member), db: Session = Depends(db_session)):
    message_target(target_id, member, db)
    profile = db.get(MemberProfile, member.id)
    data = profile.data if profile else {}
    if not profile or data.get("discreet") or data.get("invisible"):
        return {"ok": True}
    now = datetime.now(timezone.utc)
    # At most one notification for this pair in a rolling 24-hour period.
    previous = db.scalar(select(MemberNotification.id).where(MemberNotification.recipient_id == target_id,
        MemberNotification.actor_id == member.id, MemberNotification.kind == "visit",
        MemberNotification.created_at > now - timedelta(hours=24)))
    if not previous:
        add_member_notification(db, target_id, member.id, "visit", f"visit:{member.id}:{target_id}:{now.date().isoformat()}", now)
        db.commit()
    return {"ok": True}


@app.get("/api/member/profiles/{target_id}")
def member_profile_detail(target_id: int, member: Member = Depends(current_member), db: Session = Depends(db_session)):
    target = message_target(target_id, member, db)
    return profile_projection(db.get(MemberProfile, target_id), target, db, member)


@app.get("/api/member/blocks")
def member_blocks(member: Member = Depends(current_member), db: Session = Depends(db_session)):
    # Only expose a minimal label for blocks initiated by this member.
    return [{"id": f"member-{item.target_id}", "name": html.escape(str((profile.data or {}).get("pseudo") or "Membre")[:80]) if profile else "Membre"}
        for item, profile in db.execute(select(MemberBlock, MemberProfile).outerjoin(MemberProfile,
            MemberProfile.member_id == MemberBlock.target_id).where(MemberBlock.owner_id == member.id).order_by(MemberBlock.created_at.desc()))]


@app.put("/api/member/blocks/{target_id}")
def block_member(target_id: int, member: Member = Depends(current_member), db: Session = Depends(db_session)):
    existing = db.get(MemberBlock, (member.id, target_id))
    if not existing:
        # A reciprocal block cannot prevent someone from creating their own block.
        target, profile = db.get(Member, target_id), db.get(MemberProfile, target_id)
        if target_id == member.id or not target or not profile or effective_member_status(target) != "active":
            raise HTTPException(404, "Profil indisponible")
        from sqlalchemy.exc import IntegrityError
        try:
            with db.begin_nested():
                db.add(MemberBlock(owner_id=member.id, target_id=target_id)); db.flush()
        except IntegrityError:
            if not db.get(MemberBlock, (member.id, target_id)): raise
    for row in db.scalars(select(MemberSignal).where(or_(
        (MemberSignal.member_id == member.id) & (MemberSignal.target_id == f"member-{target_id}"),
        (MemberSignal.member_id == target_id) & (MemberSignal.target_id == f"member-{member.id}")))):
        db.delete(row)
    for row in db.scalars(select(MemberNotification).where(or_(
        (MemberNotification.actor_id == member.id) & (MemberNotification.recipient_id == target_id),
        (MemberNotification.actor_id == target_id) & (MemberNotification.recipient_id == member.id)))):
        db.delete(row)
    for row in db.scalars(select(PhotoAccessRequest).where(or_(
        (PhotoAccessRequest.owner_id == member.id) & (PhotoAccessRequest.requester_id == target_id),
        (PhotoAccessRequest.owner_id == target_id) & (PhotoAccessRequest.requester_id == member.id)))):
        db.delete(row)
    db.commit()
    return {"ok": True}


@app.delete("/api/member/blocks/{target_id}")
def unblock_member(target_id: int, member: Member = Depends(current_member), db: Session = Depends(db_session)):
    row = db.get(MemberBlock, (member.id, target_id))
    if row: db.delete(row)
    db.commit()
    return {"ok": True}


class ReportEdit(BaseModel):
    reason: str = Field(max_length=30)
    detail: str = Field(default="", max_length=1000)
    nonce: uuid.UUID


@app.post("/api/member/reports/{target_id}")
def report_member(target_id: int, body: ReportEdit, member: Member = Depends(current_member), db: Session = Depends(db_session)):
    message_target(target_id, member, db)
    if body.reason not in ("profile", "photo", "harassment", "spam", "other") or (body.reason == "other" and not body.detail.strip()):
        raise HTTPException(400, "Précise le motif du signalement")
    previous = db.scalar(select(MemberReport).where(MemberReport.reporter_id == member.id, MemberReport.nonce == str(body.nonce)))
    detail = body.detail.strip()
    if previous:
        if (previous.target_id, previous.reason, previous.detail) != (target_id, body.reason, detail):
            raise HTTPException(409, "Signalement déjà utilisé")
        return {"ok": True, "status": previous.status}
    recent = db.scalar(select(func.count()).select_from(MemberReport).where(MemberReport.reporter_id == member.id, MemberReport.created_at > datetime.now(timezone.utc) - timedelta(hours=1)))
    if recent >= 10: raise HTTPException(429, "Trop de signalements. Réessaie plus tard.")
    from sqlalchemy.exc import IntegrityError
    try:
        with db.begin_nested():
            db.add(MemberReport(id=str(uuid.uuid4()), reporter_id=member.id, target_id=target_id,
                reason=body.reason, detail=detail, nonce=str(body.nonce))); db.flush()
    except IntegrityError:
        previous = db.scalar(select(MemberReport).where(MemberReport.reporter_id == member.id, MemberReport.nonce == str(body.nonce)))
        if not previous: raise
        if (previous.target_id, previous.reason, previous.detail) != (target_id, body.reason, detail): raise HTTPException(409, "Signalement déjà utilisé")
    db.commit()
    return {"ok": True, "status": "pending"}


@app.get("/api/admin/member-reports")
def member_report_queue(_: Staff = Depends(editor), db: Session = Depends(db_session)):
    return [{"id": row.id, "reporter_id": row.reporter_id, "target_id": row.target_id, "reason": row.reason,
             "detail": row.detail, "status": row.status, "created_at": row.created_at}
        for row in db.scalars(select(MemberReport).where(MemberReport.status == "pending").order_by(MemberReport.created_at).limit(100))]


class ReportDecision(BaseModel):
    status: str


@app.patch("/api/admin/member-reports/{report_id}")
def review_member_report(report_id: uuid.UUID, body: ReportDecision, staff: Staff = Depends(editor), db: Session = Depends(db_session)):
    row = db.get(MemberReport, str(report_id))
    if not row or body.status not in ("reviewed", "dismissed"): raise HTTPException(400, "Décision invalide")
    row.status = body.status
    log(db, staff, "member_report." + body.status, row.id); db.commit()
    return {"ok": True}


@app.get("/api/member/conversations")
def conversations(member: Member = Depends(current_member), db: Session = Depends(db_session)):
    recent = db.scalars(select(MemberMessage).where(or_(MemberMessage.sender_id == member.id, MemberMessage.recipient_id == member.id)).order_by(MemberMessage.created_at.desc(), MemberMessage.id).limit(500))
    peers = {}
    blocked = set(db.scalars(blocked_ids(member.id)))
    for message in recent:
        peer = message.recipient_id if message.sender_id == member.id else message.sender_id
        if peer not in peers and peer not in blocked:
            peers[peer] = {"id": f"member-{peer}", "lastMessage": message.body, "updatedAt": message.created_at.replace(tzinfo=timezone.utc).isoformat(timespec="seconds")}
    # Received previews are independent of the most recent sent message.
    incoming = db.scalars(select(MemberMessage).where(MemberMessage.recipient_id == member.id).order_by(MemberMessage.created_at.desc(), MemberMessage.id).limit(500))
    for message in incoming:
        peer = peers.get(message.sender_id)
        if peer is not None and "lastReceivedAt" not in peer:
            peer["lastReceivedMessage"] = message.body
            peer["lastReceivedAt"] = message.created_at.replace(tzinfo=timezone.utc).isoformat(timespec="seconds")
    return list(peers.values())


@app.get("/api/member/messages/{target_id}")
def messages(target_id: int, member: Member = Depends(current_member), db: Session = Depends(db_session)):
    message_target(target_id, member, db)
    rows = list(db.scalars(select(MemberMessage).where(or_(
        (MemberMessage.sender_id == member.id) & (MemberMessage.recipient_id == target_id),
        (MemberMessage.sender_id == target_id) & (MemberMessage.recipient_id == member.id)
    )).order_by(MemberMessage.created_at.desc(), MemberMessage.id).limit(200)))
    return [message_projection(message) for message in reversed(rows)]


class MessageEdit(BaseModel):
    body: str = Field(min_length=1, max_length=2000)
    nonce: uuid.UUID


@app.post("/api/member/messages/{target_id}")
def send_message(target_id: int, body: MessageEdit, member: Member = Depends(current_member), db: Session = Depends(db_session)):
    message_target(target_id, member, db)
    text = body.body.strip()
    if not text:
        raise HTTPException(400, "Écris un message")
    existing = db.scalar(select(MemberMessage).where(MemberMessage.sender_id == member.id, MemberMessage.nonce == str(body.nonce)))
    if existing:
        if existing.recipient_id != target_id or existing.body != text:
            raise HTTPException(409, "Envoi déjà utilisé")
        return message_projection(existing)
    now = datetime.now(timezone.utc)
    count = db.scalar(select(func.count()).select_from(MemberMessage).where(MemberMessage.sender_id == member.id, MemberMessage.created_at > now - timedelta(minutes=1)))
    if count >= 20:
        raise HTTPException(429, "Attends un instant avant de renvoyer un message")
    message = MemberMessage(id=str(uuid.uuid4()), sender_id=member.id, recipient_id=target_id, body=text, nonce=str(body.nonce), created_at=now)
    db.add(message)
    add_member_notification(db, target_id, member.id, "message", "message:" + message.id, now)
    db.commit()
    return message_projection(message)


@app.get("/api/member/signals")
def get_member_signals(member: Member = Depends(current_member), db: Session = Depends(db_session)):
    blocked = {f"member-{target}" for target in db.scalars(blocked_ids(member.id))}
    signals = [s for s in db.scalars(select(MemberSignal).where(MemberSignal.member_id == member.id, MemberSignal.target_id.like("member-%"))) if s.target_id not in blocked]
    return {"pins": [s.target_id for s in signals if s.kind == "pin"],
            "hooks": [s.target_id for s in signals if s.kind == "hook"]}


class SignalEdit(BaseModel):
    kind: str
    target_id: str
    active: bool


@app.put("/api/member/signals")
def set_member_signal(body: SignalEdit, member: Member = Depends(current_member), db: Session = Depends(db_session)):
    if body.kind not in ("pin", "hook") or not re.fullmatch(r"member-\d+", body.target_id):
        raise HTTPException(400)
    if body.target_id.startswith("member-"):
        target_id = int(body.target_id.split("-", 1)[1])
        target = db.get(Member, target_id)
        target_profile = db.get(MemberProfile, target_id)
        if target_id == member.id or not target or effective_member_status(target) != "active" or not target_profile or target_profile.data.get("invisible") or members_blocked(db, member.id, target_id):
            raise HTTPException(404)
    existing = db.scalar(select(MemberSignal).where(MemberSignal.member_id == member.id, MemberSignal.target_id == body.target_id, MemberSignal.kind == body.kind))
    if body.active and not existing:
        signal = MemberSignal(member_id=member.id, target_id=body.target_id, kind=body.kind)
        db.add(signal); db.flush()
        actor_profile = db.get(MemberProfile, member.id)
        if actor_profile and not actor_profile.data.get("discreet") and not actor_profile.data.get("invisible"):
            add_member_notification(db, target_id, member.id, body.kind, f"signal:{signal.id}")
    elif not body.active and existing:
        for notification in db.scalars(select(MemberNotification).where(MemberNotification.event_key == f"signal:{existing.id}")):
            db.delete(notification)
        db.delete(existing)
    db.commit()
    return {"ok": True}


@app.put("/api/member/profile")
def save_member_profile(body: ProfileEdit, member: Member = Depends(current_member), db: Session = Depends(db_session)):
    profile = db.get(MemberProfile, member.id)
    if not profile:
        profile = MemberProfile(member_id=member.id, code="KQ-" + secrets.token_hex(4).upper(), data={})
        db.add(profile)
    profile.data = body.model_dump()["data"]
    profile.updated_at = datetime.now(timezone.utc)
    member.name = str(body.data.get("pseudo", ""))[:255]
    db.commit()
    return {"ok": True, "code": profile.code}


@app.post("/api/member/photos")
async def member_photo(photo: UploadFile = File(), visibility: str = Form("public"), member: Member = Depends(current_member), db: Session = Depends(db_session)):
    if visibility not in ("public", "private"):
        raise HTTPException(400, "Visibilité invalide")
    data = await photo.read(5_000_001)
    mime = "image/jpeg" if data.startswith(b"\xff\xd8\xff") else "image/png" if data.startswith(b"\x89PNG\r\n\x1a\n") else "image/webp" if data.startswith(b"RIFF") and data[8:12] == b"WEBP" else ""
    if not mime or len(data) > 5_000_000:
        raise HTTPException(400, "JPEG, PNG ou WebP de 5 Mo maximum")
    item = Photo(id=str(uuid.uuid4()), member_id=member.id, mime=mime, data=data, status="pending")
    db.add(item)
    if visibility == "private":
        db.flush()
        db.add(PrivatePhoto(photo_id=item.id))
    db.commit()
    return {"id": item.id, "status": "pending", "message": "Photo en modération."}


@app.delete("/api/member/account")
def close_member_account(request: Request, member: Member = Depends(current_member), db: Session = Depends(db_session)):
    erase_member(db, member)
    db.commit()
    request.session.clear()
    return {"ok": True}


def erase_member(db: Session, member: Member):
    for model, first, second in ((MemberBlock, MemberBlock.owner_id, MemberBlock.target_id), (MemberReport, MemberReport.reporter_id, MemberReport.target_id)):
        for record in db.scalars(select(model).where(or_(first == member.id, second == member.id))):
            db.delete(record)
    # Erase both sides of the member's exchanges; other pairs remain intact.
    for message in db.scalars(select(MemberMessage).where(or_(MemberMessage.sender_id == member.id, MemberMessage.recipient_id == member.id))):
        db.delete(message)
    for notification in db.scalars(select(MemberNotification).where(or_(MemberNotification.actor_id == member.id, MemberNotification.recipient_id == member.id))):
        db.delete(notification)
    credential = db.get(MemberLoginCode, member.id)
    if credential:
        db.delete(credential)
    for challenge in db.scalars(select(MemberCode).where(or_(MemberCode.email == member.email, MemberCode.member_id == member.id))):
        db.delete(challenge)
    for model in (MemberConsent, MemberActivity, MemberLocation):
        record = db.get(model, member.id)
        if record:
            db.delete(record)
    for access in db.scalars(select(PhotoAccessRequest).where(or_(PhotoAccessRequest.owner_id == member.id, PhotoAccessRequest.requester_id == member.id))):
        db.delete(access)
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
        private = db.get(PrivatePhoto, photo.id)
        if private:
            db.delete(private)
            db.flush()  # The private marker references the photo being removed.
        db.delete(photo)
    member.email = f"deleted-{member.id}@invalid.local"
    member.name = ""
    member.status = "deleted"
    member.ban_until = None
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
def login(request: Request, next: str = ""):
    if not CLIENT_ID or not CLIENT_SECRET or not ADMIN_EMAIL:
        raise HTTPException(503, "OAuth KINQ non configuré")
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    request.session["oauth_state"] = state
    request.session["oauth_nonce"] = nonce
    request.session["oauth_verifier"] = verifier
    if next.startswith("/oauth/authorize?") and len(next) < 4000:
        request.session["login_next"] = next
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
    login_next = request.session.get("login_next", "/admin")
    request.session.clear()
    request.session["staff_id"] = staff.id
    request.session["csrf"] = secrets.token_urlsafe(32)
    return RedirectResponse(login_next, status_code=303)


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
def public_photo(photo_id: str, request: Request, db: Session = Depends(db_session)):
    p = db.get(Photo, photo_id)
    m = db.get(Member, p.member_id) if p else None
    if not p or db.get(PrivatePhoto, photo_id) or p.status != "approved" or not m or effective_member_status(m) != "active" or (request.session.get("member_id") and members_blocked(db, int(request.session["member_id"]), m.id)):
        raise HTTPException(404)
    return Response(p.data, media_type=p.mime, headers={"X-Content-Type-Options": "nosniff", "Cache-Control": "no-store, private", "Vary": "Cookie"})


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
    return [public_article(a, include_body=False) for a in db.scalars(select(Article).where(Article.status == "published").order_by(Article.updated_at.desc()))]


def public_article(article: Article, include_body: bool = True):
    plain = lambda value: html.unescape(re.sub(r"<[^>]+>", "", value or ""))
    art_words = article.art_words or (["MUSK.", "PITS.", "WORN."] if article.slug == "odeur-mec-plus-excitante-que-physique" else ["NO", "TABOO."])
    reading_minutes = max(1, round(len(plain(article.body).split()) / 220))
    result = {"slug": article.slug, "title": plain(article.title), "summary": plain(article.summary), "art_words": art_words, "category": article.category, "reading_minutes": reading_minutes}
    if include_body:
        result["body"] = article.body
    return result


@app.get("/api/articles/{slug}")
def published_article(slug: str, db: Session = Depends(db_session)):
    article = db.scalar(select(Article).where(Article.slug == slug, Article.status == "published"))
    if not article:
        raise HTTPException(404)
    return public_article(article)


LEGACY_JOURNAL_SLUGS = {"premiers-pas", "parler-de-ses-limites", "les-mots-pour-se-comprendre", "profil-et-vie-privee", "premiere-rencontre", "aftercare"}


def published_journal_slug(slug: str, db: Session) -> bool:
    return slug in LEGACY_JOURNAL_SLUGS or bool(db.scalar(select(Article.id).where(Article.slug == slug, Article.status == "published")))


def comment_payload(comment: JournalComment) -> dict:
    return {"id": comment.id, "article_slug": comment.article_slug, "author_name": comment.author_name,
            "body": comment.body, "status": comment.status, "created_at": comment.created_at.isoformat()}


class NewJournalComment(BaseModel):
    author_name: str = Field(min_length=1, max_length=80)
    body: str = Field(min_length=1, max_length=2000)
    website: str = Field(default="", max_length=200)


class TeamReply(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


@app.get("/api/journal/{slug}/comments")
def public_journal_comments(slug: str, db: Session = Depends(db_session)):
    if not published_journal_slug(slug, db):
        raise HTTPException(404)
    rows = list(db.scalars(select(JournalComment).where(JournalComment.article_slug == slug, JournalComment.status == "approved").order_by(JournalComment.created_at, JournalComment.id)))
    roots = {c.id: {**comment_payload(c), "replies": []} for c in rows if c.parent_id is None}
    for c in rows:
        if c.parent_id in roots and c.staff_id is not None:
            roots[c.parent_id]["replies"].append(comment_payload(c))
    return list(roots.values())


@app.post("/api/journal/{slug}/comments", status_code=202)
def submit_journal_comment(slug: str, body: NewJournalComment, db: Session = Depends(db_session)):
    if not published_journal_slug(slug, db):
        raise HTTPException(404)
    if body.website:
        return {"status": "pending"}
    name, message = body.author_name.strip(), body.body.strip()
    if not name or not message:
        raise HTTPException(422, "Le pseudo et le commentaire sont requis")
    if name.casefold() == "kinq team":
        raise HTTPException(422, "Ce nom est réservé à l’équipe")
    db.add(JournalComment(article_slug=slug, author_name=name, body=message, status="pending"))
    db.commit()
    return {"status": "pending"}


@app.get("/api/admin/comments")
def comments(_: Staff = Depends(editor), db: Session = Depends(db_session)):
    roots = list(db.scalars(select(JournalComment).where(JournalComment.parent_id.is_(None)).order_by(JournalComment.id.desc()).limit(200)))
    replies = list(db.scalars(select(JournalComment).where(JournalComment.parent_id.in_([c.id for c in roots])).order_by(JournalComment.id))) if roots else []
    by_parent = {c.id: [] for c in roots}
    for reply in replies:
        by_parent[reply.parent_id].append(comment_payload(reply))
    return [{**comment_payload(c), "replies": by_parent[c.id]} for c in sorted(roots, key=lambda c: (c.status != "pending", -c.id))]


@app.patch("/api/admin/comments/{comment_id}")
def decide_comment(comment_id: int, body: Decision, staff: Staff = Depends(editor), db: Session = Depends(db_session)):
    c = db.get(JournalComment, comment_id)
    if not c or c.parent_id is not None:
        raise HTTPException(404)
    if body.status not in ("approved", "rejected"):
        raise HTTPException(400)
    c.status = body.status
    log(db, staff, "comment." + body.status, str(comment_id))
    db.commit()
    return {"ok": True}


@app.post("/api/admin/comments/{comment_id}/reply", status_code=201)
def reply_to_comment(comment_id: int, body: TeamReply, staff: Staff = Depends(editor), db: Session = Depends(db_session)):
    parent = db.get(JournalComment, comment_id)
    if not parent or parent.parent_id is not None or parent.status != "approved":
        raise HTTPException(400, "Validez ce commentaire avant de répondre")
    message = body.body.strip()
    if not message:
        raise HTTPException(422, "La réponse est requise")
    reply = JournalComment(article_slug=parent.article_slug, author_name="Kinq Team", body=message,
                           status="approved", parent_id=parent.id, staff_id=staff.id)
    db.add(reply)
    db.flush()
    log(db, staff, "comment.reply", str(reply.id))
    db.commit()
    return comment_payload(reply)


# SessionMiddleware must wrap the CSRF middleware so request.session exists there.
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET, same_site="lax", https_only=PUBLIC_ORIGIN.startswith("https://"), session_cookie="kinq_session", max_age=8 * 3600)

# The editorial MCP shares the Workspace identity and Article tables.
from .mcp_editorial import router as mcp_router  # noqa: E402
app.include_router(mcp_router)



from .wallet_card import register_kinqcard  # noqa: E402
register_kinqcard(app, current_member, db_session, get_member_profile, Photo, PUBLIC_ORIGIN)
