"""Owner-only KinqCard passes. Signing keys stay in server-mounted secrets."""
import hashlib
import html
import io
import json
import os
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree

from fastapi import Depends, HTTPException
from fastapi.responses import Response


class WalletUnavailable(Exception):
    pass


def signing_material():
    """Fail closed for absent, expired, mismatched or invalid certificates."""
    from cryptography import x509
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID

    names = ("KINQ_WALLET_PASS_TYPE_ID", "KINQ_WALLET_TEAM_ID", "KINQ_WALLET_CERT_PATH", "KINQ_WALLET_KEY_PATH", "KINQ_WALLET_WWDR_PATH")
    values = [os.environ.get(name, "") for name in names]
    if not all(values):
        raise WalletUnavailable()
    pass_type, team, cert_path, key_path, wwdr_path = values
    if not re.fullmatch(r"pass\.[A-Za-z0-9.-]+", pass_type) or not re.fullmatch(r"[A-Z0-9]{10}", team):
        raise WalletUnavailable()
    try:
        def certificate(path):
            data = Path(path).read_bytes()
            return x509.load_pem_x509_certificate(data) if data.startswith(b"-----BEGIN") else x509.load_der_x509_certificate(data)
        cert, wwdr = certificate(cert_path), certificate(wwdr_path)
        password = os.environ.get("KINQ_WALLET_KEY_PASSWORD", "").encode() or None
        key = serialization.load_pem_private_key(Path(key_path).read_bytes(), password=password)
        now = datetime.now(timezone.utc)
        for item in (cert, wwdr):
            if not item.not_valid_before_utc <= now < item.not_valid_after_utc:
                raise WalletUnavailable()
        if cert.subject.get_attributes_for_oid(NameOID.USER_ID)[0].value != pass_type:
            raise WalletUnavailable()
        if cert.subject.get_attributes_for_oid(NameOID.ORGANIZATIONAL_UNIT_NAME)[0].value != team:
            raise WalletUnavailable()
        if not wwdr.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value.startswith("Apple Worldwide Developer Relations"):
            raise WalletUnavailable()
        cert.verify_directly_issued_by(wwdr)
        if not isinstance(key, rsa.RSAPrivateKey) or key.public_key().public_numbers() != cert.public_key().public_numbers():
            raise WalletUnavailable()
        return pass_type, team, cert, key, wwdr
    except WalletUnavailable:
        raise
    except Exception:
        # Do not expose file paths, PEM content, passwords or crypto diagnostics.
        raise WalletUnavailable() from None


def png(image):
    out = io.BytesIO(); image.save(out, format="PNG"); return out.getvalue()


def image_assets(portrait=None):
    from PIL import Image, ImageDraw, ImageOps
    # The original brand SVG is copied by the shared asset synchronization script.
    root = ElementTree.fromstring(Path(__file__).with_name("wallet-symbol.svg").read_text())
    path = root.find("{http://www.w3.org/2000/svg}path").attrib["d"]
    numbers = [int(n) for n in re.findall(r"\d+", path)]
    points = list(zip(numbers[::2], numbers[1::2]))
    assets = {}
    for scale in (1, 2, 3):
        suffix = "" if scale == 1 else f"@{scale}x"
        for name, width, height in (("icon", 29, 29), ("logo", 36, 36)):
            icon = Image.new("RGBA", (width*scale, height*scale))
            factor = width*scale/64
            ImageDraw.Draw(icon).polygon([(x*factor,y*factor) for x,y in points], fill=(18,20,22,255))
            assets[f"{name}{suffix}.png"] = png(icon)
        if portrait:
            try:
                with Image.open(io.BytesIO(portrait)) as source:
                    source = ImageOps.exif_transpose(source).convert("RGB")
                    # Fresh PNG has no original metadata or EXIF location.
                    assets[f"thumbnail{suffix}.png"] = png(ImageOps.fit(source, (90*scale,90*scale)))
            except (OSError, ValueError, Image.DecompressionBombError):
                pass
    return assets


def build_pass(view, origin, material, portrait=None):
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.serialization import pkcs7
    pass_type, team, cert, key, wwdr = material
    code = view["code"]
    origin_url = urlparse(origin)
    if origin_url.scheme != "https" or not origin_url.netloc or origin_url.query or origin_url.fragment:
        raise WalletUnavailable()
    url = origin.rstrip("/") + "/p/" + code.removeprefix("KQ-")
    payload = {
        "formatVersion": 1, "passTypeIdentifier": pass_type, "teamIdentifier": team,
        "serialNumber": "kinqcard-" + code, "organizationName": "Kinq",
        "description": "KinqCard de " + html.unescape(view["name"]), "logoText": "KINQCARD",
        "backgroundColor": "rgb(178, 255, 26)", "foregroundColor": "rgb(18, 20, 22)", "labelColor": "rgb(36, 40, 30)",
        "sharingProhibited": False,
        "barcodes": [{"format": "PKBarcodeFormatQR", "message": url, "messageEncoding": "iso-8859-1", "altText": code}],
        "generic": {
            "primaryFields": [{"key": "pseudo", "label": "", "value": html.unescape(view["name"])}],
            "secondaryFields": [{"key": "code", "label": "TON CODE", "value": code}],
            "auxiliaryFields": [{"key": "powered", "label": "", "value": "Powered by Kinq"}],
            "backFields": [{"key": "profile", "label": "TON PROFIL", "value": url},
                {"key": "privacy", "label": "VISIBILITÉ", "value": "Le QR ouvre ton profil. Tes réglages de visibilité restent appliqués. Aucun accès à tes photos privées n’est inclus."}],
        },
    }
    files = image_assets(portrait)
    files["pass.json"] = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
    # Wallet's bundle format specifically requires SHA-1 file hashes.
    manifest = json.dumps({name:hashlib.sha1(data).hexdigest() for name,data in files.items()}, separators=(",", ":")).encode()
    signature = pkcs7.PKCS7SignatureBuilder().set_data(manifest).add_signer(cert,key,hashes.SHA256()).add_certificate(wwdr).sign(
        serialization.Encoding.DER, [pkcs7.PKCS7Options.DetachedSignature, pkcs7.PKCS7Options.Binary])
    files.update({"manifest.json":manifest,"signature":signature})
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name,data in files.items(): archive.writestr(name,data)
    return output.getvalue()


def register_kinqcard(app, current_member, db_session, get_profile, photo_model, origin):
    @app.get("/api/member/kinqcard/wallet")
    def wallet_status(member=Depends(current_member)):
        try: signing_material(); available = True
        except WalletUnavailable: available = False
        return Response(json.dumps({"available":available}), media_type="application/json", headers={"Cache-Control":"private, no-store"})

    @app.get("/api/member/kinqcard/pass")
    def wallet_pass(member=Depends(current_member), db=Depends(db_session)):
        try: material = signing_material()
        except WalletUnavailable:
            raise HTTPException(503, "L’ajout à Apple Wallet n’est pas encore activé.") from None
        view = get_profile(member,db).get("view")
        if not view or not view.get("code"):
            raise HTTPException(409, "Complète ton profil avant de créer ta KinqCard.")
        portrait = None
        if view.get("photo", "") and view["photo"].startswith("/api/photos/"):
            photo = db.get(photo_model,view["photo"].split("/")[-1])
            # get_profile's owner projection already excludes private/discreet photos.
            if photo and photo.member_id == member.id and photo.status == "approved": portrait = photo.data
        try: content = build_pass(view,origin,material,portrait)
        except WalletUnavailable:
            raise HTTPException(503, "La carte Apple Wallet est temporairement indisponible.") from None
        return Response(content,media_type="application/vnd.apple.pkpass",headers={
            "Cache-Control":"private, no-store", "Content-Disposition":'attachment; filename="KinqCard.pkpass"'})
