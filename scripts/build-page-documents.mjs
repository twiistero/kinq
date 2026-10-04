import './sync-profile-catalogue.mjs';
import fs from 'node:fs';
import path from 'node:path';
import {parse} from 'parse5';

const root = process.cwd();
const archive = path.join(root, 'legacy-pages');
const source = fs.existsSync(archive) ? archive : root;
if (!fs.existsSync(archive) && !fs.readdirSync(root).some(name => name.endsWith('.html'))) {
  const prepared = JSON.parse(fs.readFileSync(path.join(root, 'content/page-documents.json'), 'utf8'));
  if (!prepared['index.html']) throw new Error('Prepared homepage document missing');
  console.log(`Using ${Object.keys(prepared).length} prepared React page documents`);
  process.exit(0);
}
await import('./build-home-hero.mjs');
const files = fs.readdirSync(source).filter(name => name.endsWith('.html') && name !== 'preview.html');
const attrMap = attrs => Object.fromEntries((attrs || []).map(({name, value}) => [name, value]));
const textOf = node => (node.childNodes || []).map(child => child.value || textOf(child)).join('');
const scripts = [];
const journalSlugs = new Set(['premiers-pas','parler-de-ses-limites','les-mots-pour-se-comprendre','profil-et-vie-privee','premiere-rencontre','aftercare']);

function cleanPageHref(href) {
  const match = /^\/?([a-z0-9-]+)\.html([?#].*)?$/.exec(href || '');
  if (!match) return href;
  const page = match[1] === 'index' ? '/' : match[1] === 'soirees' ? '/events' : journalSlugs.has(match[1]) ? `/guides/${match[1]}` : `/${match[1]}`;
  return page + (match[2] || '');
}

function convert(node) {
  if (node.nodeName === '#text') return node.value;
  if (node.nodeName === '#comment') return null;
  if (!node.tagName) return null;
  const attrs = attrMap(node.attrs);
  if (node.tagName === 'a' && attrs.href) attrs.href = cleanPageHref(attrs.href);
  if (node.tagName === 'script' && attrs.src) {
    scripts.push({src: attrs.src, type: attrs.type || ''});
    return null;
  }
  if (node.tagName === 'script' && attrs.type !== 'application/json') return null;
  const children = (node.childNodes || []).map(convert).filter(child => child !== null);
  return {tag: node.tagName, attrs, children};
}

const documents = {};
for (const name of files) {
  scripts.length = 0;
  const document = parse(fs.readFileSync(path.join(source, name), 'utf8'));
  const html = document.childNodes.find(node => node.tagName === 'html');
  const head = html.childNodes.find(node => node.tagName === 'head');
  const body = html.childNodes.find(node => node.tagName === 'body');
  const title = head.childNodes.find(node => node.tagName === 'title');
  const description = head.childNodes.find(node => node.tagName === 'meta' && attrMap(node.attrs).name === 'description');
  const links = head.childNodes.filter(node => node.tagName === 'link').map(node => ({tag: 'link', attrs: attrMap(node.attrs), children: []}));
  const bodyNodes = (body.childNodes || []).map(convert).filter(child => child !== null);
  const headScripts = head.childNodes.filter(node => node.tagName === 'script' && attrMap(node.attrs).src).map(node => ({src: attrMap(node.attrs).src, type: attrMap(node.attrs).type || ''}));
  documents[name] = {
    title: title ? textOf(title) : 'KINQ',
    description: description ? attrMap(description.attrs).content : '',
    bodyAttrs: attrMap(body.attrs),
    links, nodes: bodyNodes, scripts: [...headScripts, ...scripts],
  };
}
const adminSource = fs.existsSync(path.join(source, 'admin/index.html')) ? path.join(source, 'admin/index.html') : path.join(root, 'admin/index.html');
if (fs.existsSync(adminSource)) {
  scripts.length = 0;
  const document = parse(fs.readFileSync(adminSource, 'utf8'));
  const html = document.childNodes.find(node => node.tagName === 'html');
  const head = html.childNodes.find(node => node.tagName === 'head');
  const body = html.childNodes.find(node => node.tagName === 'body');
  documents.admin = {
    title: textOf(head.childNodes.find(node => node.tagName === 'title')),
    description: '', bodyAttrs: attrMap(body.attrs),
    links: head.childNodes.filter(node => node.tagName === 'link').map(node => ({tag: 'link', attrs: attrMap(node.attrs), children: []})),
    nodes: body.childNodes.map(convert).filter(child => child !== null),
    scripts: [...head.childNodes.filter(node => node.tagName === 'script' && attrMap(node.attrs).src).map(node => ({src: attrMap(node.attrs).src, type: attrMap(node.attrs).type || ''})), ...scripts],
  };
}
fs.mkdirSync(path.join(root, 'content'), {recursive: true});
fs.writeFileSync(path.join(root, 'content/page-documents.json'), JSON.stringify(documents));
console.log(`Prepared ${Object.keys(documents).length} React page documents`);
