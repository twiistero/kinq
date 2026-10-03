"""Shared transactional code emails for the website and native app."""
import html
import base64
import os
import re
from email.utils import formataddr, parseaddr
from pathlib import Path
from string import Template

import httpx
from fastapi import HTTPException


CODE_TEMPLATE = Template((Path(__file__).parent / "templates" / "member-code.html").read_text(encoding="utf-8"))
LOGO_CONTENT = base64.b64encode((Path(__file__).parent / "templates" / "kinq-logo.png").read_bytes()).decode("ascii")
CODE_COPY = {
    "signup": ("Ton code pour créer ton compte KINQ", "Bienvenue chez KINQ.",
               "Saisis ce code sur le site ou dans l’app pour confirmer ton adresse e-mail et créer ton compte."),
    "login": ("Ton code de connexion KINQ", "Te revoilà.",
              "Saisis ce code sur le site ou dans l’app pour te connecter à ton compte."),
    "change": ("Confirme ta nouvelle adresse KINQ", "Ta nouvelle adresse.",
               "Saisis ce code dans ton compte pour confirmer ta nouvelle adresse e-mail."),
}


def code_email(code: str, purpose: str) -> dict:
    if not re.fullmatch(r"[0-9]{6}", code) or purpose not in CODE_COPY:
        raise ValueError("Invalid transactional code or purpose")
    subject, title, intro = CODE_COPY[purpose]
    expiry = "Ce code est valable 10 minutes et ne peut être utilisé qu’une seule fois."
    security = "Ne partage jamais ce code. Kinq Team ne te le demandera jamais."
    ignore = "Si tu n’as pas fait cette demande, ignore simplement cet e-mail."
    return {
        "attachments": [{"filename": "kinq-logo.png", "content": LOGO_CONTENT, "content_id": "kinq-logo"}],
        "subject": subject,
        "text": f"{title}\n\n{intro}\n\nTon code KINQ : {code}\n\n{expiry}\n{security}\n\n{ignore}\n\nKinq Team",
        "html": CODE_TEMPLATE.substitute({key: html.escape(value) for key, value in {
            "subject": subject, "title": title, "intro": intro, "code": code,
            "expiry": expiry, "security": security, "ignore": ignore,
        }.items()}),
    }


def resend_sender() -> str:
    # Preserve the verified mailbox even when its old display name is KINQ.
    configured = os.environ.get("KINQ_RESEND_FROM", "") or "connexion@kinq-app.com"
    _, address = parseaddr(configured)
    if "\r" in configured or "\n" in configured or not re.fullmatch(r"[^@\s<>]+@[^@\s<>]+\.[^@\s<>]+", address):
        raise HTTPException(503, "Adresse d’envoi des e-mails KINQ non configurée")
    return formataddr(("Kinq Team", address))


async def send_member_code(email: str, code: str, purpose: str) -> None:
    key = os.environ.get("KINQ_RESEND_API_KEY", "")
    if not key:
        raise HTTPException(503, "Envoi des e-mails KINQ non configuré")
    payload = {"from": resend_sender(), "to": [email], **code_email(code, purpose)}
    try:
        async with httpx.AsyncClient(timeout=12) as client:
            result = await client.post("https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {key}"}, json=payload)
    except httpx.RequestError:
        raise HTTPException(502, "Impossible d’envoyer le code. Réessaie dans un instant.") from None
    # Resend must accept the email before the caller persists a new challenge.
    try:
        accepted = result.status_code in (200, 201) and bool(result.json().get("id"))
    except (ValueError, AttributeError):
        accepted = False
    if not accepted:
        raise HTTPException(502, "Impossible d’envoyer le code. Réessaie dans un instant.")
