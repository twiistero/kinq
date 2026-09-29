import {createElement} from 'react';
import {parseFragment} from 'parse5';

const allowed = new Set(['p', 'h2', 'h3', 'em', 'strong', 'ul', 'ol', 'li', 'blockquote', 'a', 'br']);
const excluded = new Set(['svg', 'script', 'style', 'iframe', 'img', 'object']);

function render(node, key) {
  if (node.nodeName === '#text') return node.value;
  if (!node.tagName || excluded.has(node.tagName)) return null;
  const children = (node.childNodes || []).map(render);
  if (!allowed.has(node.tagName)) return children;
  const attrs = {key};
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
    return source.split(/\n\s*\n/).filter(Boolean).map((paragraph, index) => <p key={index}>{paragraph}</p>);
  }
  return (parseFragment(source).childNodes || []).map(render);
}
