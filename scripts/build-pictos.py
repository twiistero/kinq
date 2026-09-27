"""Build KINQ v4 icons from the unchanged taxonomy and minimal line symbols."""
import json
from pathlib import Path
from html import escape
from zipfile import ZipFile, ZIP_DEFLATED
from pictos_v4 import V4
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'assets/pictos'
# Frozen v1 metadata preserves existing IDs and labels for all 75 signs.
frozen = (ROOT / 'assets/pictos-v1/catalog.js').read_text()
rows = json.loads(frozen.split(' = ', 1)[1].rstrip(';\n'))
assert {r['id'] for r in rows} == set(V4)
DEFAULT = '--ink:#111310;--accent:#b2ff1a;--cut:#dfe2dc;--muted:#858c7f'
for row in rows:
    row.update(V4[row['id']])
    title = escape(row['name'], quote=True)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" style="{DEFAULT}" role="img" aria-label="{title}"><title>{title}</title>{row["body"]}</svg>\n'
    (OUT / (row['id']+'.svg')).write_text(svg)
(OUT / 'catalog.js').write_text('window.KINQ_PICTOS = '+json.dumps(rows, ensure_ascii=False, indent=2)+';\n')
(OUT / 'sprite.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"><defs>'+''.join(f'<symbol id="{r["id"]}" viewBox="0 0 24 24">{r["body"]}</symbol>' for r in rows)+'</defs></svg>\n')
with ZipFile(ROOT / 'assets/kinq-pictos-atelier.zip','w',ZIP_DEFLATED) as z:
    for path in sorted(OUT.glob('*.svg')): z.write(path,'svg/'+path.name)
    for relative in ['docs/pictogrammes.md','scripts/build-pictos.py','scripts/pictos_v4.py','assets/pictos/taxonomy.json','assets/pictos/catalog.js','assets/pictos-v1/catalog.js']:
        z.write(ROOT / relative,relative)
print('Built 75 v4 minimal icons, sprite, catalog and ZIP.')
