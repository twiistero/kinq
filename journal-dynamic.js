const escapeHtml=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
try {
  const response=await fetch('/api/articles');
  if (!response.ok) throw Error('Articles indisponibles');
  const articles=await response.json();
  if (document.body.dataset.page==='journal' && articles.length) {
    const section=document.createElement('section');
    section.className='nt-section';
    section.innerHTML=`<div class="nt-heading"><h2>LE JOURNAL CONTINUE</h2></div><div class="articles nt-grid">${articles.map(a=>`<a class="article nt-card" href="/journal/${encodeURIComponent(a.slug)}"><div class="article-copy"><p class="eyebrow">NO TABOO</p><h3>${escapeHtml(a.title)}</h3><p>${escapeHtml(a.summary)}</p><span class="link-label">Lire l’article</span></div></a>`).join('')}</div>`;
    document.querySelector('.nt-bridge')?.before(section);
  }
  if (document.body.dataset.page==='dynamic-article') {
    const slug=new URLSearchParams(location.search).get('slug');
    const article=articles.find(a=>a.slug===slug);
    const target=document.querySelector('#dynamic-story');
    if (!article) target.textContent='Cet article n’est pas disponible.';
    else {
      document.title=article.title+' — NO TABOO, KINQ';
      target.innerHTML=`<header class="nt-masthead"><a href="/guides.html"><strong>NO TABOO<span>.</span></strong><small>LE JOURNAL KINQ</small></a></header><article class="nt-story"><header class="nt-editorial-hero"><div class="nt-editorial-hero-copy"><p class="eyebrow">NO TABOO / JOURNAL</p><h1>${escapeHtml(article.title)}</h1><p>${escapeHtml(article.summary)}</p></div></header><div class="nt-prose">${escapeHtml(article.body).split(/\n\s*\n/).map(p=>`<p>${p.replaceAll('\n','<br>')}</p>`).join('')}</div><a class="button" href="/guides.html">Retour au journal</a></article>`;
    }
  }
} catch { /* The original static journal remains readable when the API is offline. */ }
