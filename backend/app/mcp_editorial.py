"""NO TABOO editorial MCP over HTTP, authorized with KINQ Workspace OAuth."""
import base64
import hashlib
import hmac
import html
import json
import re
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode, urlparse

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from sqlalchemy import DateTime, ForeignKey, JSON, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from .main import Article, ArticleDraft, Base, Comment, PUBLIC_ORIGIN, Staff, db_session, log

router = APIRouter()
RESOURCE = PUBLIC_ORIGIN + "/mcp"
SCOPES = {"articles.read", "articles.write"}
LEGACY_SLUGS = {"premiers-pas", "parler-de-ses-limites", "les-mots-pour-se-comprendre", "profil-et-vie-privee", "premiere-rencontre", "aftercare"}


def now():
    return datetime.now(timezone.utc)


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def fresh(value):
    return value.replace(tzinfo=timezone.utc) > now() if value and value.tzinfo is None else bool(value and value > now())


class OAuthClient(Base):
    __tablename__ = "mcp_oauth_clients"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    redirect_uris: Mapped[list] = mapped_column(JSON)


class OAuthCode(Base):
    __tablename__ = "mcp_oauth_codes"
    digest: Mapped[str] = mapped_column(String(64), primary_key=True)
    client_id: Mapped[str] = mapped_column(ForeignKey("mcp_oauth_clients.id"))
    staff_id: Mapped[int] = mapped_column(ForeignKey("staff.id"))
    redirect_uri: Mapped[str] = mapped_column(String(2048))
    challenge: Mapped[str] = mapped_column(String(128))
    scope: Mapped[str] = mapped_column(String(80))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class OAuthToken(Base):
    __tablename__ = "mcp_oauth_tokens"
    digest: Mapped[str] = mapped_column(String(64), primary_key=True)
    client_id: Mapped[str] = mapped_column(ForeignKey("mcp_oauth_clients.id"))
    staff_id: Mapped[int] = mapped_column(ForeignKey("staff.id"))
    scope: Mapped[str] = mapped_column(String(80))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


@router.get("/.well-known/oauth-protected-resource")
@router.get("/.well-known/oauth-protected-resource/mcp")
def protected_resource():
    return {"resource": RESOURCE, "authorization_servers": [PUBLIC_ORIGIN], "scopes_supported": sorted(SCOPES)}


@router.get("/.well-known/oauth-authorization-server")
def authorization_server():
    return {"issuer": PUBLIC_ORIGIN, "authorization_endpoint": PUBLIC_ORIGIN + "/oauth/authorize",
            "token_endpoint": PUBLIC_ORIGIN + "/oauth/token", "registration_endpoint": PUBLIC_ORIGIN + "/oauth/register",
            "response_types_supported": ["code"], "grant_types_supported": ["authorization_code"],
            "token_endpoint_auth_methods_supported": ["none"], "code_challenge_methods_supported": ["S256"],
            "scopes_supported": sorted(SCOPES)}


def allowed_redirect(uri):
    parsed = urlparse(uri)
    return (parsed.scheme == "https" and parsed.netloc == "chatgpt.com" and not parsed.fragment
            and (parsed.path.startswith("/connector/oauth/") or parsed.path == "/connector_platform_oauth_redirect"))


@router.post("/oauth/register")
async def register(request: Request, db: Session = Depends(db_session)):
    try:
        data = await request.json()
        redirects = data["redirect_uris"]
        if (not isinstance(redirects, list) or not 1 <= len(redirects) <= 5
                or not all(isinstance(uri, str) and allowed_redirect(uri) for uri in redirects)
                or data.get("token_endpoint_auth_method", "none") != "none"):
            raise ValueError()
    except (ValueError, TypeError, KeyError):
        raise HTTPException(400, "Client OAuth ou URL de retour invalide")
    client_id = secrets.token_urlsafe(24)
    db.add(OAuthClient(id=client_id, redirect_uris=redirects))
    db.commit()
    return JSONResponse({"client_id": client_id, "redirect_uris": redirects,
                         "token_endpoint_auth_method": "none", "grant_types": ["authorization_code"],
                         "response_types": ["code"]}, status_code=201)


def authorization_request(params, db):
    client_id, redirect_uri = params.get("client_id", ""), params.get("redirect_uri", "")
    client = db.get(OAuthClient, client_id)
    scope = set(params.get("scope", "articles.read articles.write").split())
    challenge = params.get("code_challenge", "")
    if (not client or redirect_uri not in client.redirect_uris or params.get("response_type") != "code"
            or params.get("code_challenge_method") != "S256" or not re.fullmatch(r"[A-Za-z0-9_-]{43}", challenge)
            or params.get("resource", RESOURCE) != RESOURCE or not scope or not scope.issubset(SCOPES)):
        raise HTTPException(400, "Demande OAuth invalide")
    return client, scope


@router.get("/oauth/authorize")
def authorize(request: Request, db: Session = Depends(db_session)):
    params = dict(request.query_params)
    _, scope = authorization_request(params, db)
    staff = db.get(Staff, request.session.get("staff_id")) if request.session.get("staff_id") else None
    if not staff or not staff.active:
        return RedirectResponse("/api/admin/auth/login?" + urlencode({"next": "/oauth/authorize?" + request.url.query}), status_code=303)
    if staff.role not in ("admin", "moderator") and "articles.write" in scope:
        raise HTTPException(403, "Rôle éditorial requis")
    csrf = request.session.get("csrf", "")
    fields = "".join(f'<input type="hidden" name="{html.escape(key, quote=True)}" value="{html.escape(value, quote=True)}">' for key, value in params.items())
    page = ("<!doctype html><html lang=fr><meta charset=utf-8><title>Connecter NO TABOO</title>"
            "<meta name=viewport content='width=device-width,initial-scale=1'>"
            "<style>body{font:18px system-ui;background:#101010;color:#fff;max-width:36rem;margin:10vh auto;padding:2rem}"
            "button{background:#b2ff1a;color:#111;border:0;padding:1rem 1.5rem;font:700 1rem system-ui;cursor:pointer}</style>"
            "<h1>Connecter NO TABOO à ChatGPT</h1><p>Compte : " + html.escape(staff.email) + "</p>"
            "<p>Accès demandé : " + html.escape(", ".join(sorted(scope))) + "</p>"
            "<p>ChatGPT pourra lire vos articles et, si autorisé, enregistrer des brouillons, publier et retirer des articles.</p>"
            "<form method=post action=/oauth/authorize>" + fields
            + '<input type="hidden" name="csrf" value="' + html.escape(csrf, quote=True) + '">'
            + "<button type=submit>Autoriser cette connexion</button></form></html>")
    return HTMLResponse(page, headers={"Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; form-action 'self' https://chatgpt.com; frame-ancestors 'none'", "Cache-Control": "no-store"})


@router.post("/oauth/authorize")
async def authorize_confirm(request: Request, db: Session = Depends(db_session)):
    form = await request.form()
    params = {key: str(value) for key, value in form.items()}
    client, scope = authorization_request(params, db)
    staff = db.get(Staff, request.session.get("staff_id")) if request.session.get("staff_id") else None
    if (request.headers.get("origin") != PUBLIC_ORIGIN or not staff or not staff.active
            or (staff.role not in ("admin", "moderator") and "articles.write" in scope)
            or not request.session.get("csrf") or not hmac.compare_digest(params.get("csrf", ""), request.session["csrf"])):
        raise HTTPException(403, "Autorisation refusée")
    code = secrets.token_urlsafe(32)
    db.add(OAuthCode(digest=digest(code), client_id=client.id, staff_id=staff.id,
                     redirect_uri=params["redirect_uri"], challenge=params["code_challenge"],
                     scope=" ".join(sorted(scope)), expires_at=now() + timedelta(minutes=5)))
    log(db, staff, "mcp.authorize", client.id)
    db.commit()
    redirect_uri = params["redirect_uri"]
    return RedirectResponse(redirect_uri + ("&" if "?" in redirect_uri else "?") + urlencode({"code": code, "state": params.get("state", "")}), status_code=303)


@router.post("/oauth/token")
async def token(request: Request, db: Session = Depends(db_session)):
    form = await request.form()
    grant = db.get(OAuthCode, digest(str(form.get("code", ""))))
    if (form.get("grant_type") != "authorization_code" or not grant or not fresh(grant.expires_at)
            or form.get("client_id") != grant.client_id or form.get("redirect_uri") != grant.redirect_uri
            or form.get("resource", RESOURCE) != RESOURCE):
        raise HTTPException(400, "Code OAuth invalide ou expiré")
    verifier = str(form.get("code_verifier", ""))
    computed = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    if not hmac.compare_digest(computed, grant.challenge):
        raise HTTPException(400, "Vérification PKCE invalide")
    staff = db.get(Staff, grant.staff_id)
    if not staff or not staff.active or ("articles.write" in grant.scope and staff.role not in ("admin", "moderator")):
        raise HTTPException(403, "Accès éditorial retiré")
    access_token = secrets.token_urlsafe(48)
    db.add(OAuthToken(digest=digest(access_token), client_id=grant.client_id, staff_id=staff.id,
                      scope=grant.scope, expires_at=now() + timedelta(days=30)))
    db.delete(grant)
    db.commit()
    return {"access_token": access_token, "token_type": "Bearer", "expires_in": 30 * 86400, "scope": grant.scope}


def authorized_staff(request, db, scope):
    header = request.headers.get("authorization", "")
    token = db.get(OAuthToken, digest(header[7:])) if header.startswith("Bearer ") else None
    if not token or not fresh(token.expires_at) or scope not in token.scope.split():
        return None
    staff = db.get(Staff, token.staff_id)
    if not staff or not staff.active or (scope == "articles.write" and staff.role not in ("admin", "moderator")):
        return None
    return staff


def snapshot(article, draft=None):
    published = {"slug": article.slug, "title": article.title, "summary": article.summary, "body": article.body, "art_words": article.art_words}
    pending = draft.payload if draft else (published if article.status == "draft" else None)
    return {"id": article.id, "status": article.status, "published": published if article.status == "published" else None,
            "draft": pending, "revision": digest(json.dumps({"published": published, "draft": pending, "status": article.status}, sort_keys=True, ensure_ascii=False)),
            "url": PUBLIC_ORIGIN + "/" + article.slug if article.status == "published" else None}


def article_by_slug(db, slug):
    article = db.scalar(select(Article).where(Article.slug == slug))
    if article:
        return article
    for row in db.scalars(select(Article).where(Article.status == "published")):
        draft = db.get(ArticleDraft, row.id)
        if draft and draft.payload.get("slug") == slug:
            return row
    return None


TOOLS = [
    {"name": "list_articles", "description": "Lister les articles NO TABOO gérés en base et leurs états. Les six articles historiques restent dans le code du site.", "inputSchema": {"type": "object", "properties": {}}, "annotations": {"readOnlyHint": True}, "securitySchemes": [{"type": "oauth2", "scopes": ["articles.read"]}]},
    {"name": "get_article", "description": "Lire un article et son brouillon, avec une révision à fournir pour toute modification.", "inputSchema": {"type": "object", "properties": {"slug": {"type": "string"}}, "required": ["slug"]}, "annotations": {"readOnlyHint": True}, "securitySchemes": [{"type": "oauth2", "scopes": ["articles.read"]}]},
    {"name": "save_article_draft", "description": "Créer ou modifier un brouillon NO TABOO. URL finale : /{slug}. title et summary sont du texte sans balises. body accepte des paragraphes HTML simples (p, h2, h3, em, strong, ul, ol, li), sans SVG, script ni image intégrée. art_words contient 2 ou 3 mots courts en majuscules pour l'encart graphique, par exemple MUSK, PITS, WORN. Vérifier le rendu du brouillon avant publication. Pour modifier, fournir la révision de get_article ; existing_slug identifie l'article si son slug change.", "inputSchema": {"type": "object", "properties": {"slug": {"type": "string"}, "existing_slug": {"type": "string"}, "title": {"type": "string"}, "summary": {"type": "string"}, "body": {"type": "string"}, "art_words": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 3}, "base_revision": {"type": "string"}}, "required": ["slug", "title", "summary", "body", "art_words"]}, "annotations": {"readOnlyHint": False, "destructiveHint": False}, "securitySchemes": [{"type": "oauth2", "scopes": ["articles.write"]}]},
    {"name": "publish_article", "description": "Publier explicitement le brouillon relu. Fournir sa révision actuelle obtenue par get_article.", "inputSchema": {"type": "object", "properties": {"slug": {"type": "string"}, "draft_revision": {"type": "string"}}, "required": ["slug", "draft_revision"]}, "annotations": {"readOnlyHint": False, "destructiveHint": False}, "securitySchemes": [{"type": "oauth2", "scopes": ["articles.write"]}]},
    {"name": "remove_article", "description": "Retirer immédiatement du site un article NO TABOO géré en base. Conserve le contenu en base pour restauration. Fournir sa révision et confirmer son slug.", "inputSchema": {"type": "object", "properties": {"slug": {"type": "string"}, "base_revision": {"type": "string"}, "confirm_slug": {"type": "string"}}, "required": ["slug", "base_revision", "confirm_slug"]}, "annotations": {"readOnlyHint": False, "destructiveHint": True}, "securitySchemes": [{"type": "oauth2", "scopes": ["articles.write"]}]},
]


def run_tool(name, args, staff, db):
    if name == "list_articles":
        return [{"slug": a.slug, "title": a.title, "status": a.status, "revision": snapshot(a, db.get(ArticleDraft, a.id))["revision"]}
                for a in db.scalars(select(Article).order_by(Article.updated_at.desc()))]
    slug = args.get("slug", "")
    if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise HTTPException(400, "Slug invalide")
    article = article_by_slug(db, args.get("existing_slug", slug) if name == "save_article_draft" else slug)
    if name == "get_article":
        if not article:
            raise HTTPException(404, "Article introuvable")
        return snapshot(article, db.get(ArticleDraft, article.id))
    if name == "save_article_draft":
        if slug in LEGACY_SLUGS:
            raise HTTPException(409, "Article historique géré dans le code du site")
        title, summary, body, art_words = args.get("title"), args.get("summary"), args.get("body"), args.get("art_words")
        if (not isinstance(title, str) or not 1 <= len(title.strip()) <= 255
                or not isinstance(summary, str) or not isinstance(body, str) or not body.strip()
                or not isinstance(art_words, list) or not 2 <= len(art_words) <= 3):
            raise HTTPException(400, "Titre, résumé ou corps invalide")
        if re.search(r"<[^>]*>", title + summary) or re.search(r"<\s*(?:svg|script|style|iframe|img)\b", body, re.I):
            raise HTTPException(400, "Balises interdites dans le titre, le résumé ou le corps")
        art_words = [word.strip().upper() for word in art_words if isinstance(word, str)]
        if not 2 <= len(art_words) <= 3 or any(not re.fullmatch(r"[A-ZÀ-ÖØ-Ý0-9 ?!.-]{2,12}", word) for word in art_words):
            raise HTTPException(400, "Mots de l'encart invalides")
        payload = {"slug": slug, "title": title.strip(), "summary": summary.strip(), "body": body.strip(), "art_words": art_words}
        if article:
            collision = article_by_slug(db, slug)
            if collision and collision.id != article.id:
                raise HTTPException(409, "Slug déjà utilisé")
            current = snapshot(article, db.get(ArticleDraft, article.id))
            if args.get("base_revision") != current["revision"]:
                raise HTTPException(409, "Révision dépassée : relire l’article")
            draft = db.get(ArticleDraft, article.id)
            if not draft:
                draft = ArticleDraft(article_id=article.id, payload=payload)
                db.add(draft)
            else:
                draft.payload = payload
                draft.updated_at = now()
        else:
            if args.get("base_revision") or args.get("existing_slug"):
                raise HTTPException(409, "L’article n’existe plus")
            article = Article(**payload, status="draft", updated_at=now())
            db.add(article)
            db.flush()
            db.add(ArticleDraft(article_id=article.id, payload=payload))
        article.updated_at = now()
        log(db, staff, "mcp.article.draft", str(article.id))
        db.commit()
        return snapshot(article, db.get(ArticleDraft, article.id))
    if not article:
        raise HTTPException(404, "Article introuvable")
    draft = db.get(ArticleDraft, article.id)
    current = snapshot(article, draft)
    if name == "publish_article":
        if args.get("draft_revision") != current["revision"] or not draft:
            raise HTTPException(409, "Brouillon ou révision invalide : relire l’article")
        new_slug = draft.payload["slug"]
        if new_slug in LEGACY_SLUGS or db.scalar(select(Article).where(Article.slug == new_slug, Article.id != article.id)):
            raise HTTPException(409, "Slug déjà utilisé")
        for key, value in draft.payload.items():
            setattr(article, key, value)
        article.status, article.updated_at = "published", now()
        db.delete(draft)
        log(db, staff, "mcp.article.publish", str(article.id))
        db.commit()
        return snapshot(article)
    if name == "remove_article":
        if args.get("confirm_slug") != slug or args.get("base_revision") != current["revision"]:
            raise HTTPException(409, "Confirmation ou révision invalide")
        article.status, article.updated_at = "archived", now()
        log(db, staff, "mcp.article.remove", str(article.id))
        db.commit()
        return snapshot(article, draft)
    raise HTTPException(404, "Outil inconnu")


@router.api_route("/mcp", methods=["GET", "POST", "DELETE"])
async def mcp(request: Request, db: Session = Depends(db_session)):
    if request.method != "POST":
        return Response(status_code=405, headers={"Allow": "POST"})
    challenge = f'Bearer resource_metadata="{PUBLIC_ORIGIN}/.well-known/oauth-protected-resource"'
    try:
        message = await request.json()
        method, message_id = message.get("method"), message.get("id")
    except (ValueError, AttributeError):
        return JSONResponse({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "JSON invalide"}}, status_code=400)
    if method == "notifications/initialized":
        return Response(status_code=202)
    if method == "initialize":
        result = {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}},
                  "serverInfo": {"name": "kinq-no-taboo", "version": "1.0.0"},
                  "instructions": "Lire l’article, enregistrer un brouillon, le relire, puis publier ou retirer seulement sur demande explicite. Les six articles historiques sont gérés dans le code et ne sont pas modifiables par ce MCP."}
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        staff = authorized_staff(request, db, "articles.read")
        if not staff:
            return Response(status_code=401, headers={"WWW-Authenticate": challenge})
        params = message.get("params") or {}
        name, args = params.get("name"), params.get("arguments") or {}
        tool = next((item for item in TOOLS if item["name"] == name), None)
        if not tool:
            return JSONResponse({"jsonrpc": "2.0", "id": message_id, "error": {"code": -32601, "message": "Outil inconnu"}})
        if not isinstance(args, dict):
            return JSONResponse({"jsonrpc": "2.0", "id": message_id, "error": {"code": -32602, "message": "Arguments invalides"}})
        if tool["securitySchemes"][0]["scopes"][0] == "articles.write" and not authorized_staff(request, db, "articles.write"):
            return JSONResponse({"jsonrpc": "2.0", "id": message_id,
                                 "result": {"content": [{"type": "text", "text": "Accès éditorial requis"}], "isError": True,
                                            "_meta": {"mcp/www_authenticate": [challenge + ', error="insufficient_scope"']}}})
        try:
            value = run_tool(name, args, staff, db)
            result = {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False, default=str)}],
                      "structuredContent": value if isinstance(value, dict) else {"items": value}}
        except HTTPException as exc:
            result = {"content": [{"type": "text", "text": str(exc.detail)}], "isError": True}
    else:
        return JSONResponse({"jsonrpc": "2.0", "id": message_id, "error": {"code": -32601, "message": "Méthode inconnue"}})
    return JSONResponse({"jsonrpc": "2.0", "id": message_id, "result": result}, headers={"Cache-Control": "no-store"})
