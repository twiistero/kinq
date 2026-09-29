import fs from 'node:fs';

const documents = JSON.parse(fs.readFileSync(new URL('./content/page-documents.json', import.meta.url), 'utf8'));
const journalSlugs = new Set(['premiers-pas','parler-de-ses-limites','les-mots-pour-se-comprendre','profil-et-vie-privee','premiere-rencontre','aftercare']);

export default {
  async redirects() {
    const legacyPages = Object.keys(documents)
      .filter(name => name.endsWith('.html'))
      .map(name => ({
        source: `/${name}`,
        destination: name === 'index.html' ? '/' : name === 'soirees.html' ? '/events' : journalSlugs.has(name.slice(0, -5)) ? `/guides/${name.slice(0, -5)}` : `/${name.slice(0, -5)}`,
        permanent: true,
      }));
    return [...legacyPages, {source: '/admin/index.html', destination: '/admin', permanent: true}];
  },
};
