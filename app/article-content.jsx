import {createElement} from 'react';
import {parseFragment} from 'parse5';

const allowed = new Set(['p', 'h2', 'h3', 'em', 'strong', 'ul', 'ol', 'li', 'blockquote', 'a', 'br']);
const excluded = new Set(['svg', 'script', 'style', 'iframe', 'img', 'object']);
const editorialHighlights = new Map([
  ['Ce que tu aimes, ce n’est pas “la transpiration”, c’est l’odeur du mec', 'l’odeur du mec'],
  ['Aisselles, pieds, jock, cuir : chacun a ses préférences', 'ses préférences'],
  ['Pourquoi sentir quelqu’un peut être plus intime que le regarder', 'plus intime'],
  ['Dans un rapport Dom/sub, ça peut devenir un vrai levier', 'un vrai levier'],
  ['Dire que tu aimes l’odeur d’un mec reste parfois plus difficile que parler de sexe', 'l’odeur d’un mec'],
]);

function render(node, key, className) {
  if (node.nodeName === '#text') return node.value;
  if (!node.tagName || excluded.has(node.tagName)) return null;
  const children = (node.childNodes || []).map(render);
  if (!allowed.has(node.tagName)) return children;
  const attrs = {key};
  if (className) attrs.className = className;
  if (node.tagName === 'a') {
    const href = node.attrs?.find(attr => attr.name === 'href')?.value || '';
    if (href.startsWith('/') && !href.startsWith('//') || /^https:\/\//.test(href)) {
      attrs.href = href;
      if (href.startsWith('https://')) attrs.rel = 'noopener noreferrer';
    } else return children;
  }
  return createElement(node.tagName, attrs, ...children);
}

export default function ArticleContent({body}) {
  const source = String(body || '').trim();
  if (!/<(?:p|h2|h3|ul|ol|blockquote)\b/i.test(source)) {
    return <div className="nt-editorial-body nt-user-article" id="article">{source.split(/\n\s*\n/).filter(Boolean).map((paragraph, index) => <p key={index}>{paragraph}</p>)}</div>;
  }
  const nodes = parseFragment(source).childNodes || [];
  const intro = [];
  const sections = [];
  for (const node of nodes) {
    if (node.tagName === 'h2') {
      const title = textContent(node).trim();
      const base = title.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'section';
      let id = base;
      for (let index = 2; sections.some(section => section.id === id); index++) id = `${base}-${index}`;
      sections.push({id, title, heading: node, content: []});
    } else if (sections.length) sections.at(-1).content.push(node);
    else intro.push(node);
  }
  return <div className="nt-editorial-reading-layout">
    {sections.length > 0 && <nav className="nt-editorial-toc" id="sommaire" aria-label="Sommaire de l’article"><div><h2>SOMMAIRE</h2></div><ol>{sections.map(section => <li key={section.id}><a href={`#${section.id}`}>{section.title}<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14m-6-6 6 6-6 6" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg></a></li>)}</ol></nav>}
    <div className="nt-editorial-body nt-user-article" id="article">
      {intro.length > 0 && <div className="nt-editorial-intro"><p className="eyebrow">POUR COMMENCER</p>{intro.map((node, index) => render(node, index, node.tagName === 'p' && intro.findIndex(item => item.tagName === 'p') === index ? 'nt-dropcap' : undefined))}</div>}
      {sections.map(section => <section className="nt-editorial-section" id={section.id} key={section.id}>
        {section.heading.childNodes?.some(node => node.tagName === 'em') ? render(section.heading, 'heading') : <h2>{highlightHeading(section.title)}</h2>}{section.content.map((node, index) => render(node, index))}
      </section>)}
    </div>
  </div>;
}

function textContent(node) {
  if (node.nodeName === '#text') return node.value || '';
  return (node.childNodes || []).map(textContent).join('');
}

function highlightHeading(title) {
  const phrase = editorialHighlights.get(title);
  if (!phrase) return title;
  const at = title.indexOf(phrase);
  return <>{title.slice(0, at)}<em>{phrase}</em>{title.slice(at + phrase.length)}</>;
}
