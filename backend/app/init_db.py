import hashlib
import json
import os
import re
import html
from pathlib import Path

from sqlalchemy.orm import Session

from .main import Article, Base, Event, PageDocument, engine

Base.metadata.create_all(engine)
with engine.begin() as connection:
    connection.exec_driver_sql("ALTER TABLE articles ADD COLUMN IF NOT EXISTS art_words JSON NOT NULL DEFAULT '[]'")
    connection.exec_driver_sql("ALTER TABLE articles ADD COLUMN IF NOT EXISTS category VARCHAR(40) NOT NULL DEFAULT 'Entre nous'")
with Session(engine) as db:
    article = db.query(Article).filter_by(slug="odeur-mec-plus-excitante-que-physique").one_or_none()
    if article:
        clean_body = re.sub(r"^\s*<svg\b[\s\S]*?</svg>\s*", "", article.body, count=1, flags=re.I)
        clean_title = html.unescape(re.sub(r"<[^>]+>", "", article.title))
        if clean_body != article.body or clean_title != article.title or article.art_words != ["MUSK.", "PITS.", "WORN."]:
            article.body = clean_body
            article.title = clean_title
            article.art_words = ["MUSK.", "PITS.", "WORN."]
            db.commit()
source = Path(os.environ.get("KINQ_SEED_SOURCE", "/srv/source"))
if source.exists():
    with Session(engine) as db:
        documents = source / "content/page-documents.json"
        if documents.exists():
            for name, data in json.loads(documents.read_text(encoding="utf-8")).items():
                digest = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
                page = db.get(PageDocument, name)
                if not page:
                    db.add(PageDocument(path=name, data=data, source_hash=digest))
                elif page.source_hash != digest:
                    page.data, page.source_hash = data, digest
        catalogue = source / "content/events.json"
        if catalogue.exists():
            items = sorted(json.loads(catalogue.read_text(encoding="utf-8")), key=lambda item: item["start"])
            for item in items:
                event = db.get(Event, item["id"])
                if event:
                    event.data = item
                else:
                    db.add(Event(id=item["id"], data=item))
        db.commit()
print("KINQ database ready")
