import hashlib
import json
import os
from pathlib import Path

from sqlalchemy.orm import Session

from .main import Base, DemoProfile, Event, PageDocument, engine

Base.metadata.create_all(engine)
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
        demos = source / "content/demo-profiles.json"
        if demos.exists():
            for item in json.loads(demos.read_text(encoding="utf-8")):
                profile = db.get(DemoProfile, item["id"])
                if profile:
                    profile.data = item
                else:
                    db.add(DemoProfile(id=item["id"], data=item))
        db.commit()
print("KINQ database ready")
