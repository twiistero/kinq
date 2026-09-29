import {createElement} from 'react';
import PageEffects from './legacy-scripts';

const booleanAttrs = new Set(['checked','disabled','hidden','multiple','open','readonly','required','selected','autofocus','novalidate','controls','loop','muted','playsinline']);
const renamed = {class:'className',for:'htmlFor',crossorigin:'crossOrigin',tabindex:'tabIndex',maxlength:'maxLength',readonly:'readOnly',autofocus:'autoFocus',novalidate:'noValidate',playsinline:'playsInline',viewbox:'viewBox',preserveaspectratio:'preserveAspectRatio',srcset:'srcSet',stroke:'stroke', 'stroke-width':'strokeWidth','stroke-linecap':'strokeLinecap','stroke-linejoin':'strokeLinejoin','fill-rule':'fillRule','clip-rule':'clipRule'};
const voidTags = new Set(['area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr']);

function styleObject(value) {
  return Object.fromEntries(String(value).split(';').map(part => {
    const colon = part.indexOf(':');
    if (colon < 0) return null;
    const key = part.slice(0, colon).trim().replace(/-([a-z])/g, (_, char) => char.toUpperCase());
    return [key, part.slice(colon + 1).trim()];
  }).filter(Boolean));
}

export function RenderNode({node, slot, commentsSlot, commentCountSlot, articlesSlot, featureSlot}) {
  if (typeof node === 'string') return node;
  if (!node || !node.tag) return null;
  const attrs = {};
  for (const [name, value] of Object.entries(node.attrs || {})) {
    if (name.startsWith('on')) continue;
    const key = renamed[name] || name;
    attrs[key] = name === 'style' ? styleObject(value) : booleanAttrs.has(name) ? true : value;
  }
  if (slot && attrs.id === 'dynamic-story') return createElement(node.tag, attrs, slot);
  if (commentsSlot && attrs.id === 'journal-comments') return createElement(node.tag, attrs, commentsSlot);
  if (commentCountSlot && attrs.id === 'journal-comment-count') return createElement(node.tag, attrs, commentCountSlot);
  if (featureSlot && attrs.id === 'a-la-une') return featureSlot;
  if (attrs.id === 'journal-dynamic-articles') return createElement(node.tag, attrs,
    ...(node.children || []).map((child, index) => <RenderNode key={index} node={child}/>), articlesSlot);
  if (node.tag === 'script' && attrs.type === 'application/json') {
    return createElement('script', {...attrs, dangerouslySetInnerHTML: {__html: (node.children || []).join('')}});
  }
  if (voidTags.has(node.tag)) return createElement(node.tag, attrs);
  return createElement(node.tag, attrs, ...(node.children || []).map((child, index) => <RenderNode key={index} node={child} slot={slot} commentsSlot={commentsSlot} commentCountSlot={commentCountSlot} articlesSlot={articlesSlot} featureSlot={featureSlot}/>));
}

export default function PageDocument({document, slot, commentsSlot, commentCountSlot, articlesSlot, featureSlot, bodyAttrs}) {
  return <>
    {document.links.map((link, index) => <RenderNode key={`link-${index}`} node={link}/>)}
    {document.nodes.map((node, index) => <RenderNode key={index} node={node} slot={slot} commentsSlot={commentsSlot} commentCountSlot={commentCountSlot} articlesSlot={articlesSlot} featureSlot={featureSlot}/>)}
    <PageEffects bodyAttrs={bodyAttrs || document.bodyAttrs} scripts={document.scripts}/>
  </>;
}
