import fs from 'node:fs';

const documents = JSON.parse(fs.readFileSync(new URL('./content/page-documents.json', import.meta.url), 'utf8'));
const journalSlugs = new Set(['premiers-pas','parler-de-ses-limites','les-mots-pour-se-comprendre','profil-et-vie-privee','premiere-rencontre','aftercare']);

export default {
  async headers() {
    return [{source:'/contrats/signature/:path*',headers:[
      {key:'Referrer-Policy',value:'no-referrer'},
      {key:'X-Robots-Tag',value:'noindex, nofollow'},
      {key:'Cache-Control',value:'private, no-store'},
    ]}];
  },
  async redirects() {
    const legacyPages = Object.keys(documents)
      .filter(name => name.endsWith('.html'))
      .map(name => ({
        source: `/${name}`,
        destination: name === 'index.html' ? '/' : name === 'soirees.html' ? '/events' : journalSlugs.has(name.slice(0, -5)) ? `/guides/${name.slice(0, -5)}` : `/${name.slice(0, -5)}`,
        permanent: true,
      }));
    const appPages = ['rencontres','profil','mon-profil','compte','messages','connexions','pins','hooks'];
    const appRedirects = appPages.flatMap(page => [
      {source:`/${page}`, destination:'/application', permanent:false},
      {source:`/${page}.html`, destination:'/application', permanent:false},
    ]);
    return [...appRedirects, {source:'/p/:code([A-F0-9]{8})', destination:'/application?profil=KQ-:code', permanent:false}, ...legacyPages, {source:'/admin/index.html', destination:'/admin', permanent:true}];
  },
};
