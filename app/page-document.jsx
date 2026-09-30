import {createElement} from 'react';
import PageEffects from './legacy-scripts';

const booleanAttrs = new Set(['checked','disabled','hidden','multiple','open','readonly','required','selected','autofocus','novalidate','controls','loop','muted','playsinline']);
const renamed = {class:'className',for:'htmlFor',crossorigin:'crossOrigin',tabindex:'tabIndex',maxlength:'maxLength',readonly:'readOnly',autofocus:'autoFocus',novalidate:'noValidate',playsinline:'playsInline',viewbox:'viewBox',preserveaspectratio:'preserveAspectRatio',srcset:'srcSet',stroke:'stroke', 'stroke-width':'strokeWidth','stroke-linecap':'strokeLinecap','stroke-linejoin':'strokeLinejoin','fill-rule':'fillRule','clip-rule':'clipRule'};
const voidTags = new Set(['area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr']);
const journalSlugs = new Set(['premiers-pas','parler-de-ses-limites','les-mots-pour-se-comprendre','profil-et-vie-privee','premiere-rencontre','aftercare']);

function nestedPath(value) {
  if (value?.startsWith('/') && journalSlugs.has(value.slice(1))) return `/guides${value}`;
  if (!value || /^(?:[a-z][a-z0-9+.-]*:|\/|#)/i.test(value)) return value;
  const match = value.match(/^([a-z0-9-]+)\.html([?#].*)?$/i);
  if (match) return match[1] === 'guides' ? `/guides${match[2] || ''}` : `${journalSlugs.has(match[1]) ? '/guides' : ''}/${match[1]}${match[2] || ''}`;
  return `/${value}`;
}

function styleObject(value) {
  return Object.fromEntries(String(value).split(';').map(part => {
    const colon = part.indexOf(':');
    if (colon < 0) return null;
    const key = part.slice(0, colon).trim().replace(/-([a-z])/g, (_, char) => char.toUpperCase());
    return [key, part.slice(colon + 1).trim()];
  }).filter(Boolean));
}

export function RenderNode({node, slot, commentsSlot, commentCountSlot, articlesSlot, featureSlot, nestedArticle}) {
  if (typeof node === 'string') return node;
  if (!node || !node.tag) return null;
  const attrs = {};
  for (const [name, value] of Object.entries(node.attrs || {})) {
    if (name.startsWith('on')) continue;
    const key = renamed[name] || name;
    attrs[key] = name === 'style' ? styleObject(value) : booleanAttrs.has(name) ? true : nestedArticle && (name === 'href' || name === 'src') ? nestedPath(value) : value;
  }
  if (slot && (attrs.id === 'dynamic-story' || attrs.id === 'page-main')) return createElement(node.tag, attrs, slot);
  if (commentsSlot && attrs.id === 'journal-comments') return createElement(node.tag, attrs, commentsSlot);
  if (commentCountSlot && attrs.id === 'journal-comment-count') return createElement(node.tag, attrs, commentCountSlot);
  if (featureSlot && attrs.id === 'a-la-une') return featureSlot;
  if (attrs.id === 'journal-dynamic-articles') return createElement(node.tag, attrs,
    ...(node.children || []).map((child, index) => <RenderNode key={index} node={child}/>), articlesSlot);
  if (node.tag === 'script' && attrs.type === 'application/json') {
    return createElement('script', {...attrs, dangerouslySetInnerHTML: {__html: (node.children || []).join('')}});
  }
  if (voidTags.has(node.tag)) return createElement(node.tag, attrs);
  return createElement(node.tag, attrs, ...(node.children || []).map((child, index) => <RenderNode key={index} node={child} slot={slot} commentsSlot={commentsSlot} commentCountSlot={commentCountSlot} articlesSlot={articlesSlot} featureSlot={featureSlot} nestedArticle={nestedArticle}/>));
}

export default function PageDocument({document, slot, commentsSlot, commentCountSlot, articlesSlot, featureSlot, nestedArticle, bodyAttrs}) {
  return <>
    {document.links.map((link, index) => <RenderNode key={`link-${index}`} node={link} nestedArticle={nestedArticle}/>)}
    {document.nodes.map((node, index) => <RenderNode key={index} node={node} slot={slot} commentsSlot={commentsSlot} commentCountSlot={commentCountSlot} articlesSlot={articlesSlot} featureSlot={featureSlot} nestedArticle={nestedArticle}/>)}
    <PageEffects bodyAttrs={bodyAttrs || document.bodyAttrs} scripts={nestedArticle ? document.scripts.map(script => ({...script, src: nestedPath(script.src)})) : document.scripts}/>
  </>;
}
