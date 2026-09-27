import fs from 'node:fs';

const documents = JSON.parse(fs.readFileSync(new URL('./content/page-documents.json', import.meta.url), 'utf8'));

export default {
  async redirects() {
    const legacyPages = Object.keys(documents)
      .filter(name => name.endsWith('.html'))
      .map(name => ({
        source: `/${name}`,
        destination: name === 'index.html' ? '/' : name === 'soirees.html' ? '/events' : `/${name.slice(0, -5)}`,
        permanent: true,
      }));
    return [...legacyPages, {source: '/admin/index.html', destination: '/admin', permanent: true}];
  },
};
