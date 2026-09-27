import hashlib
import json
import os
import re
from pathlib import Path

from sqlalchemy.orm import Session

from .main import Base, DemoProfile, Event, LexiconEntry, PublicPage, engine

Base.metadata.create_all(engine)
source = Path(os.environ.get("KINQ_SEED_SOURCE", "/srv/source"))
if source.exists():
    with Session(engine) as db:
        for file in source.glob("*.html"):
            if file.name == "preview.html":
                continue
            html = file.read_text(encoding="utf-8")
            digest = hashlib.sha256(html.encode("utf-8")).hexdigest()
            page = db.get(PublicPage, file.name)
            if not page:
                db.add(PublicPage(path=file.name, html=html, source_hash=digest))
            elif page.source_hash != digest:
                page.html, page.source_hash = html, digest
        catalogue = source / "content/events.json"
        if catalogue.exists():
            items = sorted(json.loads(catalogue.read_text(encoding="utf-8")), key=lambda item: item["start"])
            cards = re.findall(r'<article class="event-card"[\s\S]*?</article>', (source / "events.html").read_text(encoding="utf-8"))
            if len(cards) != len(items):
                raise RuntimeError("Event cards and catalogue count differ")
            for item, card in zip(items, cards):
                item = {**item, "card_html": card}
                event = db.get(Event, item["id"])
                if event:
                    event.data = item
                else:
                    db.add(Event(id=item["id"], data=item))
        demos = source / "content/demo-profiles.json"
        if demos.exists():
            for item in json.loads(demos.read_text(encoding="utf-8")):
                profile = db.get(DemoProfile, item["id"])
                if profile:
                    profile.data = item
                else:
                    db.add(DemoProfile(id=item["id"], data=item))
        lexicon = source / "lexique.html"
        if lexicon.exists():
            cards = re.findall(r'<article data-term="([^"]+)" data-category="([^"]+)">[\s\S]*?</article>', lexicon.read_text(encoding="utf-8"))
            fragments = re.findall(r'<article data-term="[^"]+" data-category="[^"]+">[\s\S]*?</article>', lexicon.read_text(encoding="utf-8"))
            if len(cards) != 159 or len(fragments) != len(cards):
                raise RuntimeError("Lexicon cards could not be imported")
            for position, ((key, category), fragment) in enumerate(zip(cards, fragments)):
                entry = db.get(LexiconEntry, key)
                if entry:
                    entry.category, entry.position, entry.card_html = category, position, fragment
                else:
                    db.add(LexiconEntry(key=key, category=category, position=position, card_html=fragment))
        db.commit()
print("KINQ database ready")
