import {JournalBrand, JournalMark, JournalTopics} from './no-taboo-shell';
import {parseFragment} from 'parse5';
import {RenderNode} from './page-document';
import JournalComments from './journal-comments';
import ArticleToc from './article-toc';

const allowed = new Set(['p','h2','h3','strong','b','em','i','a','ul','ol','li','blockquote','br']);

function textOf(node) {
  if (node?.tag === 'br') return ' ';
  return typeof node === 'string' ? node : (node?.children || []).map(textOf).join('');
}
function find(node, predicate) {
  if (!node || typeof node === 'string') return null;
  if (predicate(node)) return node;
  for (const child of node.children || []) {
    const match = find(child, predicate);
    if (match) return match;
  }
  return null;
}
function hasClass(name) { return node => (node.attrs?.class || '').split(/\s+/).includes(name); }
function withoutPhotos(node) {
  if (typeof node === 'string') return node;
  if (!node || node.tag === 'img' || node.tag === 'figure' || (node.attrs?.class || '').split(/\s+/).includes('eyebrow')) return null;
  return {...node, children:(node.children || []).map(withoutPhotos).filter(child => child !== null)};
}
function childrenOf(document) { return document?.nodes || []; }
function slugify(value) {
  return value.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'section';
}
function fromMcp(html) {
  const fragment = parseFragment(String(html || ''));
  const convert = node => {
    if (node.nodeName === '#text') return node.value;
    if (!allowed.has(node.tagName)) return (node.childNodes || []).flatMap(child => convert(child));
    const attrs = {};
    if (node.tagName === 'a') {
      const href = (node.attrs || []).find(item => item.name === 'href')?.value || '';
      if (/^https:\/\//i.test(href) || /^\//.test(href)) attrs.href = href;
    }
    return {tag: node.tagName, attrs, children: (node.childNodes || []).flatMap(child => convert(child))};
  };
  const parsed = (fragment.childNodes || []).flatMap(node => convert(node));
  if (parsed.some(node => typeof node !== 'string' && node.tag === 'h2')) return parsed;
  return String(html || '').split(/\n\s*\n/).filter(Boolean).map(block => {
    const trimmed = block.trim();
    if (trimmed.startsWith('## ')) return {tag:'h2',attrs:{},children:[trimmed.slice(3)]};
    return {tag:'p',attrs:{},children:[trimmed.replace(/<[^>]*>/g, '')]};
  });
}
function normalizeSections(nodes) {
  const sections = [];
  let current = null;
  let intro = [];
  for (const node of nodes) {
    if (typeof node !== 'string' && (node.tag === 'section' || node.tag === 'h2')) {
      if (current) sections.push(current);
      const heading = node.tag === 'h2' ? node : find(node, child => child.tag === 'h2');
      current = {title: textOf(heading) || 'À retenir', nodes: [node]};
    } else if (current) current.nodes.push(node);
    else intro.push(node);
  }
  if (current) sections.push(current);
  return {intro, sections};
}

export default function ArticleContent({article, document, slug, comments, commentCount, related=[]}) {
  const legacy = !article;
  const nodes = childrenOf(document);
  const hero = legacy && find({children:nodes}, hasClass('nt-editorial-hero'));
  const title = article?.title || textOf(find(hero, node => node.tag === 'h1')) || document?.title || '';
  const summary = article?.summary || textOf((hero?.children || []).find(node => hasClass('nt-editorial-hero-copy')(node))?.children?.find(node => node.tag === 'p' && !hasClass('eyebrow')(node))) || document?.description || '';
  const body = legacy && (find({children:nodes}, hasClass('nt-editorial-body')) || find({children:nodes}, hasClass('nt-prose')));
  const raw = legacy ? (body?.children || []) : fromMcp(article.body);
  const {intro, sections} = normalizeSections(raw.map(withoutPhotos).filter(node => node !== null));
  const firstIntroParagraph = intro.findIndex(node => typeof node !== 'string' && node.tag === 'p');
  const toc = sections.map((section, index) => ({...section, id: `${slugify(section.title)}-${index + 1}`}));
  return <div className="nt-site nt-reading nt-unified wrap">
    <article>
      <header className="nt-unified-hero journal-full-hero">
        <div className="nt-unified-hero-copy journal-full-copy"><JournalBrand/><p className="journal-hero-themes">Culture Kink / Pratiques / Rencontres</p><h1>{title}</h1><p className="nt-unified-deck">{summary}</p><div className="nt-unified-actions"><a className="button" href="#article">Lire l’article <svg aria-hidden="true"><use href="#arrow"/></svg></a><a className="nt-unified-comment-link" href="#commentaires">Commentaires ({commentCount ?? comments?.length ?? 0}) <svg aria-hidden="true"><use href="#arrow"/></svg></a></div></div>
        <JournalMark/>
      </header>
      <JournalTopics/>
      <div className="nt-unified-layout" id="article"><aside className="nt-unified-rail"><ArticleToc items={toc.map(({id,title})=>({id,title}))}/><div className="nt-author"><strong>Auteur : Kinq Team</strong></div></aside>
        <div className="nt-unified-body"><div className="nt-editorial-intro">{intro.length ? intro.map((node,index) => <RenderNode key={index} node={!legacy && index === firstIntroParagraph ? {...node,attrs:{...node.attrs,class:'nt-dropcap'}} : node}/>) : <p className="nt-dropcap">{summary}</p>}</div>{toc.map(item => <section className="nt-editorial-section" id={item.id} key={item.id}>{item.nodes.length ? item.nodes.map((node,index) => <RenderNode key={index} node={node}/>) : <h2>{item.title}</h2>}</section>)}</div>
      </div>
    </article>
    <div id="commentaires"><JournalComments slug={slug} initialComments={comments || []}/></div>
    {related.length > 0 && <nav className="nt-next" aria-label="Continuer à lire"><p className="eyebrow">CONTINUER À LIRE</p><div>{related.map((item,index) => <a href={item.href} key={item.slug}><small>{index === 0 ? 'À LIRE AUSSI' : 'ARTICLE SUIVANT'}</small><strong>{item.title}</strong></a>)}</div></nav>}
    <aside className="nt-end"><p className="eyebrow">Make it kinky.</p><h2>La suite se vit<br/><em>dans l’app.</em></h2><div><a className="button" href="/application">Découvrir l’app Kinq <svg aria-hidden="true"><use href="#up"/></svg></a></div></aside>
  </div>;
}
