"""Detect changes on selected organizer pages for editorial review.

This does not publish events: dates and access conditions need human validation.
"""

from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "content" / "event-sources.json"
STATE = ROOT / "content" / "event-source-state.json"
REVIEW = ROOT / "content" / "event-review.json"


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.capture = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}:
            self.skip += 1
        if tag in {"h1", "h2", "h3", "h4", "time"}:
            self.capture += 1
            if tag == "time":
                self.parts.extend(value for name, value in attrs if name == "datetime" and value)

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"} and self.skip:
            self.skip -= 1
        if tag in {"h1", "h2", "h3", "h4", "time"} and self.capture:
            self.capture -= 1

    def handle_data(self, data):
        if not self.skip and self.capture:
            self.parts.append(data)


def read_json(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def fetch_signature(url):
    request = Request(url, headers={"User-Agent": "KinqEventsSourceMonitor/0.1 (+manual review)"})
    with urlopen(request, timeout=20) as response:
        parser = Text()
        parser.feed(response.read().decode("utf-8", errors="replace"))
    normalized = re.sub(r"\s+", " ", " ".join(parser.parts)).strip()
    return sha256(normalized.encode("utf-8")).hexdigest()


def main():
    baseline = "--baseline" in sys.argv
    state = read_json(STATE, {})
    review = read_json(REVIEW, [])
    sources = [source for source in read_json(SOURCES, []) if source.get("monitor", True)]
    changed = 0
    failed = 0
    for source in sources:
        try:
            signature = fetch_signature(source["url"])
        except Exception as error:
            failed += 1
            print(f"Erreur {source['name']}: {error}")
            continue
        previous = state.get(source["id"])
        if previous and previous != signature and not baseline:
            review.append({"source_id": source["id"], "source_name": source["name"], "url": source["url"], "detected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "status": "pending", "note": "Page source modifiée : vérifier les dates, annulations et nouveaux événements."})
            changed += 1
        state[source["id"]] = signature
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REVIEW.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(sources)} sources suivies · {changed} changement(s) à valider · {failed} erreur(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
