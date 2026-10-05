'use client';
import {useEffect,useRef} from 'react';

export default function ArticleToc({items}) {
  const disclosure=useRef(null);
  useEffect(()=>{
    const mobile=window.matchMedia('(max-width:760px)');
    const sync=()=>{if(!mobile.matches && disclosure.current) disclosure.current.open=true;};
    sync();
    mobile.addEventListener('change',sync);
    return ()=>mobile.removeEventListener('change',sync);
  },[]);
  return <nav className="nt-article-toc" aria-label="Sommaire de l’article">
    <span className="nt-rail-label nt-toc-desktop-label">DANS CET ARTICLE</span>
    <details className="nt-toc-disclosure" ref={disclosure} open><summary className="nt-toc-toggle">Sommaire</summary>
      <ol id="nt-toc-items">{items.map(item=><li key={item.id}><a href={`#${item.id}`}>{item.title}</a></li>)}</ol>
    </details>
  </nav>;
}
