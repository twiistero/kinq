"""Render the reviewed Events catalogue into the static Kinq page."""

from datetime import datetime
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
CATALOGUE = ROOT / "content" / "events.json"
PAGE = ROOT / "events.html"


def date_label(value):
    date = datetime.fromisoformat(value).date()
    return f"{date.day} {('janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre')[date.month - 1]} {date.year}"


def render(event):
    start = datetime.fromisoformat(event["start"])
    end = datetime.fromisoformat(event["end"])
    when = date_label(event["start"])
    if start.date() != end.date():
        when += f" — {date_label(event['end'])}"
    if "T" in event["start"]:
        when += f" · {start:%H:%M}"
    source = event["source"]
    if urlparse(source).scheme != "https":
        raise ValueError(f"Source HTTPS requise : {source}")
    e = lambda field: escape(str(event[field]), quote=True)
    return f'''<article class="event-card" data-scope="{e('scope')}" data-start="{e('start')}" data-end="{e('end')}" data-name="{e('name')}" data-city="{e('city')}">
  <div class="event-date" aria-hidden="true"><strong>{start.day:02d}</strong><span>{('JAN', 'FÉV', 'MAR', 'AVR', 'MAI', 'JUN', 'JUL', 'AOÛ', 'SEP', 'OCT', 'NOV', 'DÉC')[start.month - 1]}</span></div>
  <div class="event-main"><div class="event-meta"><span>{e('kind')}</span><span>{e('city')} · {e('country')}</span></div><h2>{e('name')}</h2><p class="event-when"><svg aria-hidden="true"><use href="#calendar"/></svg><time datetime="{e('start')}">{escape(when)}</time></p><p class="event-summary">{e('summary')}</p><div class="event-bottom"><span>Source vérifiée le {date_label(event['verified_on'])}</span><a class="underlink" href="{escape(source, quote=True)}" target="_blank" rel="noopener noreferrer">Voir chez l’organisateur <svg aria-hidden="true"><use href="#up"/></svg></a></div></div>
</article>'''


events = json.loads(CATALOGUE.read_text(encoding="utf-8"))
ids = [event["id"] for event in events]
if len(ids) != len(set(ids)):
    raise ValueError("Identifiants d’événements en double")
events.sort(key=lambda event: event["start"])
html = PAGE.read_text(encoding="utf-8")
cards = "\n".join(render(event) for event in events)
html, count = re.subn(r"(?s)(<!-- EVENTS:START -->).*?(<!-- EVENTS:END -->)", lambda match: f"{match[1]}\n{cards}\n{match[2]}", html)
if count != 1:
    raise ValueError("Marqueurs Events absents ou dupliqués")
PAGE.write_text(html, encoding="utf-8")
print(f"{len(events)} événements publiés dans {PAGE.name}")
