'use client';

import SequentialTitle from './sequential-title';
import {CoverWords,coverFor} from './no-taboo-covers';
import {useCallback, useEffect, useRef, useState} from 'react';

export default function NoTabooFeed({articles}) {
  const [visible, setVisible] = useState(3);
  const [loading, setLoading] = useState(false);
  const sentinel = useRef(null);
  const pending = useRef(null);
  const hasMore = visible < articles.length;
  const loadMore = useCallback(() => {
    if (pending.current || !hasMore) return;
    setLoading(true);
    // Give the arrival indicator a readable beat before revealing the next group.
    pending.current = setTimeout(() => {
      setVisible(count => Math.min(count + 3, articles.length));
      setLoading(false);
      pending.current = null;
    }, 400);
  }, [articles.length, hasMore]);
  useEffect(() => {
    if (!hasMore || !sentinel.current) return;
    const observer = new IntersectionObserver(entries => {
      if (entries.some(entry => entry.isIntersecting)) loadMore();
    }, {rootMargin:'0px 0px 250px 0px'});
    observer.observe(sentinel.current);
    return () => observer.disconnect();
  }, [hasMore, visible, loadMore]);
  useEffect(() => () => clearTimeout(pending.current), []);
  return <>
    <div className="nt-magazine-grid" aria-busy={loading}>{articles.slice(0, visible).map(item => <a className="nt-home-card" href={item.href || `/guides/${item.slug}`} key={item.slug}>
      <div className={`nt-home-card-art nt-cover-${coverFor(item.slug, item.art_words).theme}`}><CoverWords slug={item.slug} words={item.art_words}/><svg aria-hidden="true"><use href="#up"/></svg></div>
      <div className="nt-home-card-copy"><h3><SequentialTitle>{item.title}</SequentialTitle></h3><p>{item.summary}</p><span className="nt-home-card-link">Lire l’article <svg aria-hidden="true"><use href="#up"/></svg></span></div>
    </a>)}</div>
    {hasMore && <div className="nt-feed-more"><div className="nt-feed-loader" role="status" hidden={!loading}><img src="/assets/kinq-symbol.svg" alt=""/><span>La suite arrive…</span></div><button className="button" type="button" onClick={loadMore} disabled={loading}>Continuer la lecture</button><div ref={sentinel} className="nt-feed-sentinel" aria-hidden="true"/></div>}
    <noscript><div className="nt-feed-fallback">{articles.slice(3).map(item => <a href={item.href || `/guides/${item.slug}`} key={item.slug}>{item.title}</a>)}</div></noscript>
  </>;
}
