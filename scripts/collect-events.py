"""Collect public organizer announcements into the Events review queue.

Only scripts/review-event.py can move a candidate into the published catalogue.
No event is inferred from a search result or from an undated page change.
"""

import argparse
from datetime import date, datetime, timedelta
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import unicodedata
from urllib.parse import urlencode, urlparse, urlsplit, urlunsplit
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "content" / "event-sources.json"
PUBLISHED = ROOT / "content" / "events.json"
CANDIDATES = ROOT / "content" / "event-candidates.json"
USER_AGENT = "Mozilla/5.0 (compatible; KinqEventsCollector/1.0; public organizer pages)"
MAX_RESPONSE_BYTES = 5_000_000


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}:
            self.skip += 1
        if tag in {"br", "p", "div", "li"}:
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"} and self.skip:
            self.skip -= 1
        if tag in {"p", "div", "li"}:
            self.parts.append(" ")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def plain(value):
    parser = PlainText()
    parser.feed(unescape(str(value or "")))
    return re.sub(r"\s+", " ", unescape("".join(parser.parts))).strip()


def fetch(url):
    if urlparse(url).scheme != "https":
        raise ValueError(f"URL HTTPS requise : {url}")
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json, text/html"})
    with urlopen(request, timeout=25) as response:
        data = response.read(MAX_RESPONSE_BYTES + 1)
        if len(data) > MAX_RESPONSE_BYTES:
            raise ValueError(f"Réponse trop volumineuse : {url}")
        return data.decode("utf-8", errors="replace"), response.headers


def fetch_json(url):
    body, headers = fetch(url)
    return json.loads(body), headers


def read_json(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def local_datetime(value, timezone):
    moment = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    return moment.replace(tzinfo=ZoneInfo(timezone))


def kind_for(name):
    lower = name.casefold()
    if any(word in lower for word in ("atelier", "initiation", "masterclass", "unlocker")):
        return "Atelier"
    if any(word in lower for word in ("apéro", "apero", "dîner", "dinner", "brunch")):
        return "Rencontre"
    if any(word in lower for word in ("festival", "weekend", "week-end")):
        return "Festival"
    return "Soirée"


def event_record(source, origin_id, name, start, end, url):
    name = plain(name)
    if not name or not origin_id or urlparse(url).scheme != "https":
        return None
    if isinstance(start, datetime):
        if not isinstance(end, datetime) or end < start:
            return None
        start_value, end_value = start.isoformat(timespec="minutes"), end.isoformat(timespec="minutes")
    else:
        if not isinstance(start, date) or not isinstance(end, date) or end < start:
            return None
        start_value, end_value = start.isoformat(), end.isoformat()
    return {
        "id": f"{source['id']}-{origin_id}",
        "source_id": source["id"],
        "origin_id": str(origin_id),
        "name": name[:100],
        "start": start_value,
        "end": end_value,
        "city": source["city"],
        "country": source["country"],
        "scope": source["scope"],
        "kind": kind_for(name),
        "summary": f"Événement annoncé par {source['name']}. Horaires et conditions d’accès à vérifier sur la fiche officielle.",
        "source": url,
    }


def collect_tribe(source, today):
    collected = []
    for page in range(1, 7):
        query = urlencode({"per_page": 50, "page": page, "start_date": today.isoformat()})
        payload, _ = fetch_json(f"{source['url']}?{query}")
        for item in payload.get("events", []):
            if item.get("status") != "publish":
                continue
            try:
                start = local_datetime(item["start_date"], item.get("timezone") or source["timezone"])
                end = local_datetime(item["end_date"], item.get("timezone") or source["timezone"])
                if item.get("all_day"):
                    start, end = start.date(), end.date()
            except (KeyError, TypeError, ValueError):
                continue
            record = event_record(source, item.get("id"), item.get("title"), start, end, item.get("url", ""))
            if record and record["end"][:10] >= today.isoformat():
                collected.append(record)
        if page >= int(payload.get("total_pages", 1)):
            break
    return collected


def collect_wordpress_acf(source, today):
    collected = []
    for page in range(1, 7):
        payload, headers = fetch_json(f"{source['url']}?{urlencode({'per_page': 100, 'page': page})}")
        for item in payload:
            fields = item.get("acf") or {}
            if not isinstance(fields, dict):
                continue
            raw_day = str(fields.get("event_date") or "")
            if not re.fullmatch(r"\d{8}", raw_day):
                continue
            try:
                day = datetime.strptime(raw_day, "%Y%m%d").date()
                if day < today:
                    continue
                start_time = str(fields.get("start_time") or "00:00:00")[:8]
                end_time = str(fields.get("end_time") or "23:59:00")[:8]
                start = local_datetime(f"{day} {start_time}", source["timezone"])
                end = local_datetime(f"{day} {end_time}", source["timezone"])
                if end < start:
                    end += timedelta(days=1)
            except ValueError:
                continue
            record = event_record(source, item.get("id"), item.get("title", {}).get("rendered"), start, end, item.get("link", ""))
            if record:
                collected.append(record)
        if page >= int(headers.get("X-WP-TotalPages", "1")):
            break
    return collected


def visible_end(text, start):
    parts = re.findall(r"(?:(\d{2}/\d{2}/\d{4})\s+)?(\d{1,2}:\d{2})\s*(AM|PM)", text, re.I)
    if len(parts) < 2:
        return start
    day, clock, meridiem = parts[-1]
    day = day or start.strftime("%d/%m/%Y")
    end = datetime.strptime(f"{day} {clock} {meridiem.upper()}", "%d/%m/%Y %I:%M %p").replace(tzinfo=start.tzinfo)
    if end < start:
        end += timedelta(days=1)
    return end


def collect_darklands_program(source, today):
    body, _ = fetch(source["url"])
    collected = []
    for block in re.findall(r'<article\b[^>]*\bloop-parties\b[^>]*>.*?</article>', body, re.S | re.I):
        link = re.search(r'<a\s+href="(https://darklands\.be/party/[^"?#]+/?)"', block, re.I)
        title = re.search(r'<h2\b[^>]*>(.*?)</h2>', block, re.S | re.I)
        clock = re.search(r'<time\b[^>]*datetime="([^"]+)"[^>]*>(.*?)</time>', block, re.S | re.I)
        if not (link and title and clock):
            continue
        try:
            start = datetime.strptime(clock[1], "%d/%m/%Y %H:%M").replace(tzinfo=ZoneInfo(source["timezone"]))
        except ValueError:
            continue
        if start.date() < today:
            continue
        end = visible_end(plain(clock[2]), start)
        slug = link[1].rstrip("/").rsplit("/", 1)[-1]
        record = event_record(source, f"{slug}-{start.year}", title[1], start, end, link[1])
        if record:
            collected.append(record)
    if not collected:
        raise ValueError("Aucune soirée datée trouvée dans le programme")
    return collected


ADAPTERS = {
    "tribe": collect_tribe,
    "wordpress_acf": collect_wordpress_acf,
    "darklands_program": collect_darklands_program,
}
COMPARE_FIELDS = ("name", "start", "end", "city", "country", "scope", "kind", "source")


def normalized(value):
    value = unicodedata.normalize("NFD", str(value).casefold())
    return re.sub(r"\s+", " ", "".join(char for char in value if unicodedata.category(char) != "Mn")).strip()


def url_key(value):
    parts = urlsplit(value)
    return urlunsplit((parts.scheme, parts.netloc.lower(), parts.path.rstrip("/"), "", ""))


def same_announcement(first, second):
    if first.get("source_id") and first.get("origin_id") and (first.get("source_id"), str(first.get("origin_id"))) == (second.get("source_id"), str(second.get("origin_id"))):
        return True
    if url_key(first.get("source", "")) == url_key(second.get("source", "")) and url_key(first.get("source", "")):
        return True
    return (normalized(first.get("name", "")), normalized(first.get("city", "")), first.get("start", "")[:10]) == (normalized(second.get("name", "")), normalized(second.get("city", "")), second.get("start", "")[:10])


def merge_candidates(collected_by_source, existing, published, today):
    previous = {item["id"]: item for item in existing}
    result = {}
    for source_id, records in collected_by_source.items():
        seen = set()
        for record in records:
            if record["id"] in seen:
                continue
            seen.add(record["id"])
            approved = next((item for item in published if same_announcement(item, record)), None)
            if approved and all(approved.get(field) == record.get(field) for field in COMPARE_FIELDS):
                continue
            old = previous.get(record["id"])
            if old and old.get("status") == "rejected" and old.get("event") == record:
                result[record["id"]] = old
                continue
            candidate = {
                "id": record["id"],
                "status": "pending",
                "mode": "update" if approved else "new",
                "target_id": approved["id"] if approved else None,
                "first_seen": old.get("first_seen", today.isoformat()) if old else today.isoformat(),
                "event": record,
            }
            if old and old.get("event") == record and old.get("status") == "pending" and old.get("mode") == candidate["mode"] and old.get("target_id") == candidate["target_id"]:
                result[record["id"]] = old
            else:
                result[record["id"]] = candidate
        for old in existing:
            if old.get("event", {}).get("source_id") == source_id and old["id"] not in seen and old.get("status") in {"pending", "source_missing", "rejected"}:
                result[old["id"]] = {**old, "status": "source_missing"} if old["status"] == "pending" else old
    for old in existing:
        if old.get("event", {}).get("source_id") not in collected_by_source:
            result[old["id"]] = old
    return sorted(result.values(), key=lambda item: (item["event"]["start"], item["id"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="enregistrer la file de validation")
    parser.add_argument("--today", type=date.fromisoformat, default=date.today(), help="date de référence YYYY-MM-DD")
    args = parser.parse_args()
    sources = read_json(SOURCES, [])
    published = read_json(PUBLISHED, [])
    previous = read_json(CANDIDATES, [])
    collected = {}
    failures = []
    for source in sources:
        adapter = ADAPTERS.get(source.get("adapter"))
        if not adapter:
            continue
        try:
            records = adapter(source, args.today)
            collected[source["id"]] = records
            print(f"{source['name']} : {len(records)} annonce(s) datée(s)")
        except Exception as error:
            failures.append(f"{source['name']} : {error}")
    candidates = merge_candidates(collected, previous, published, args.today)
    if args.write and collected:
        output = json.dumps(candidates, ensure_ascii=False, indent=2) + "\n"
        if not CANDIDATES.exists() or CANDIDATES.read_text(encoding="utf-8") != output:
            CANDIDATES.write_text(output, encoding="utf-8")
    print(f"{sum(item['status'] == 'pending' for item in candidates)} proposition(s) à valider · {len(failures)} source(s) en erreur")
    for failure in failures:
        print(f"ERREUR {failure}", file=sys.stderr)
    return 0 if collected else 1


if __name__ == "__main__":
    raise SystemExit(main())
