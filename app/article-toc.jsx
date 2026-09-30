'use client';
import {useState} from 'react';

export default function ArticleToc({items}) {
  const [open,setOpen]=useState(true);
  return <nav className="nt-article-toc" aria-label="Sommaire de l’article">
    <span className="nt-rail-label nt-toc-desktop-label">DANS CET ARTICLE</span>
    <button className="nt-toc-toggle" type="button" aria-expanded={open} aria-controls="nt-toc-items" onClick={()=>setOpen(value=>!value)}>Sommaire <svg viewBox="0 0 24 24" aria-hidden="true"><path d={open?'m6 15 6-6 6 6':'m6 9 6 6 6-6'}/></svg></button>
    <ol id="nt-toc-items" data-collapsed={!open}>{items.map(item=><li key={item.id}><a href={`#${item.id}`}>{item.title}</a></li>)}</ol>
  </nav>;
}
