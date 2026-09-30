import fs from 'node:fs';
const path = new URL('../legacy-pages/mon-profil.html', import.meta.url);
const catalogue = JSON.parse(fs.readFileSync(new URL('../content/profile-kinks.json', import.meta.url), 'utf8'));
const html = fs.readFileSync(path, 'utf8');
const pattern = /(<script type="application\/json" id="kink-taxonomy">)[\s\S]*?(<\/script>)/;
if (!pattern.test(html)) throw new Error('Profile catalogue slot not found');
fs.writeFileSync(path, html.replace(pattern, (_, start, end) => start + JSON.stringify(catalogue).replace(/</g, '\\u003c') + end));
