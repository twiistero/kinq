"""Review collected Events candidates before publishing them on the static site."""

import argparse
from datetime import date, datetime
import json
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
CANDIDATES = ROOT / "content" / "event-candidates.json"
PUBLISHED = ROOT / "content" / "events.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def checked_event(event):
    required = ("id", "source_id", "origin_id", "name", "start", "end", "city", "country", "scope", "kind", "summary", "source")
    missing = [field for field in required if not event.get(field)]
    if missing:
        raise ValueError(f"Champs manquants : {', '.join(missing)}")
    if urlparse(event["source"]).scheme != "https":
        raise ValueError("La fiche officielle doit utiliser HTTPS")
    start = datetime.fromisoformat(event["start"])
    end = datetime.fromisoformat(event["end"])
    if end < start or end.date() < date.today():
        raise ValueError("Dates incohérentes ou événement terminé")
    if event["scope"] not in {"france", "europe"}:
        raise ValueError("Périmètre invalide")
    return event


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list", help="afficher les propositions à valider")
    listing.add_argument("--source", help="limiter à une source")
    listing.add_argument("--all", action="store_true", help="afficher toutes les propositions")
    approval = commands.add_parser("approve", help="publier une proposition vérifiée")
    approval.add_argument("id")
    approval.add_argument("--summary", help="résumé éditorial court")
    approval.add_argument("--kind", help="catégorie affichée")
    approval.add_argument("--end", help="date/heure de fin corrigée, au format ISO")
    rejection = commands.add_parser("reject", help="écarter une proposition")
    rejection.add_argument("id")
    rejection.add_argument("--reason", required=True)
    args = parser.parse_args()
    candidates = read(CANDIDATES)

    if args.command == "list":
        items = [item for item in candidates if item["status"] == "pending" and (not args.source or item["event"]["source_id"] == args.source)]
        for item in items if args.all else items[:20]:
            event = item["event"]
            print(f"{item['id']} · {event['start'][:10]} · {event['city']} · {event['name']} · {item['mode']}")
        print(f"{len(items)} proposition(s) à valider" + ("" if args.all or len(items) <= 20 else " (20 affichées)"))
        return 0

    candidate = next((item for item in candidates if item["id"] == args.id), None)
    if not candidate:
        parser.error(f"Proposition inconnue : {args.id}")
    if args.command == "reject":
        candidate["status"] = "rejected"
        candidate["reason"] = args.reason.strip()
        write(CANDIDATES, candidates)
        print(f"Écarté : {args.id}")
        return 0
    if candidate["status"] != "pending":
        parser.error("La source n'est plus confirmée ou cette proposition n'est plus en attente")

    event = dict(candidate["event"])
    if args.summary:
        event["summary"] = args.summary.strip()
    if args.kind:
        event["kind"] = args.kind.strip()
    if args.end:
        event["end"] = args.end.strip()
    event["verified_on"] = date.today().isoformat()
    try:
        checked_event(event)
    except ValueError as error:
        parser.error(str(error))

    published = read(PUBLISHED)
    matches = [index for index, item in enumerate(published) if item["id"] in {event["id"], candidate.get("target_id")} or (item.get("source_id"), str(item.get("origin_id"))) == (event["source_id"], event["origin_id"])]
    if len(matches) > 1:
        parser.error("Plusieurs fiches publiées correspondent à cette proposition")
    if matches:
        previous = published[matches[0]]
        event["id"] = previous["id"]
        if not args.summary:
            event["summary"] = previous["summary"]
        published[matches[0]] = event
    else:
        published.append(event)
    published.sort(key=lambda item: item["start"])
    write(PUBLISHED, published)
    write(CANDIDATES, [item for item in candidates if item["id"] != args.id])
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build-events.py")], cwd=ROOT, check=True)
    print(f"Publié après validation : {event['name']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
