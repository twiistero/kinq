import {Fragment} from 'react';
import {cookies} from 'next/headers';
import {notFound, permanentRedirect, redirect} from 'next/navigation';
import PageDocument from '../page-document';
import JournalComments from '../journal-comments';
import ArticleContent from '../article-content';

export const dynamic = 'force-dynamic';
const api = process.env.KINQ_API_URL || 'http://127.0.0.1:8000';
const memberPages = new Set(['compte.html','mon-profil.html','rencontres.html','profil.html']);
const legacyArticles = new Set(['premiers-pas','parler-de-ses-limites','les-mots-pour-se-comprendre','profil-et-vie-privee','premiere-rencontre','aftercare']);
const legacyArticleCards = [
  {slug: 'premiers-pas', title: 'Curieux, mais pas sûr de toi ? Tu es au bon endroit.'},
  {slug: 'parler-de-ses-limites', title: 'Parler de ses limites sans casser le feeling.'},
  {slug: 'les-mots-pour-se-comprendre', title: 'Les mots pour te comprendre. Pas pour t’enfermer.'},
  {slug: 'profil-et-vie-privee', title: 'Ton profil, tes règles. Tu choisis ce que tu partages.'},
  {slug: 'premiere-rencontre', title: 'Du premier message à la première rencontre.'},
  {slug: 'aftercare', title: 'L’aftercare : la connexion continue après.'},
];

async function getDocument(name, optional = false) {
  const response = await fetch(`${api}/api/documents/${name}`, {cache: 'no-store'});
  if (response.status === 404) return optional ? null : notFound();
  if (!response.ok) throw new Error('Contenu KINQ indisponible');
  return response.json();
}

async function getArticles() {
  const response = await fetch(`${api}/api/articles`, {cache: 'no-store'});
  if (!response.ok) throw new Error('Journal KINQ indisponible');
  return response.json();
}

async function getArticle(slug) {
  const response = await fetch(`${api}/api/articles/${slug}`, {cache: 'no-store'});
  if (response.status === 404) notFound();
  if (!response.ok) throw new Error('Article KINQ indisponible');
  return response.json();
}

async function getComments(slug) {
  const response = await fetch(`${api}/api/journal/${slug}/comments`, {cache: 'no-store'});
  if (!response.ok) throw new Error('Commentaires KINQ indisponibles');
  return response.json();
}

function CommentCount({count}) {
  return <a className="nt-editorial-scroll nt-comment-jump" href="#journal-comments">{count} commentaire{count > 1 ? 's' : ''}
    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v15m-6-6 6 6 6-6" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
  </a>;
}

async function route(params) {
  const slug = (await params).slug || [];
  if (slug.length === 0) return {name: 'index.html'};
  if (slug.length === 1 && slug[0] === 'admin') return {name: 'admin'};
  if (slug.length === 1 && legacyArticles.has(slug[0])) permanentRedirect(`/guides/${slug[0]}`);
  if (slug.length === 1 && /^[a-z0-9-]+$/.test(slug[0])) return {name: `${slug[0]}.html`, possibleArticleSlug: slug[0], rootCandidate: true};
  if (slug.length === 2 && slug[0] === 'guides' && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug[1])) return {name: `${slug[1]}.html`, possibleArticleSlug: slug[1], nestedArticle: true};
  if (slug.length === 2 && slug[0] === 'journal' && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug[1])) permanentRedirect(`/guides/${slug[1]}`);
  notFound();
}

export async function generateMetadata({params}) {
  const {name, possibleArticleSlug, rootCandidate, nestedArticle} = await route(params);
  const document = await getDocument(name, Boolean(possibleArticleSlug));
  if (!document && possibleArticleSlug) {
    const article = await getArticle(possibleArticleSlug);
    if (rootCandidate) permanentRedirect(`/guides/${article.slug}`);
    return {title: `${article.title} — NO TABOO, KINQ`, description: article.summary, alternates: {canonical: `/guides/${article.slug}`}};
  }
  return {title: document.title, description: document.description || undefined, ...(nestedArticle ? {alternates: {canonical: `/guides/${possibleArticleSlug}`}} : {})};
}

function ArtWords({words}) {
  const lines = words?.length ? words : ['NO', 'TABOO'];
  return <span>{lines.map((word, index) => <Fragment key={index}>{index === lines.length - 1 ? <em>{word}</em> : word}{index < lines.length - 1 && <br/>}</Fragment>)}</span>;
}

function DynamicArticles({articles}) {
  if (!articles.length) return null;
  return <>{articles.slice(1).map(article =>
    <a className="article nt-card" href={`/guides/${article.slug}`} key={article.slug}>
      <div className="article-art art-two"><ArtWords words={article.art_words}/><svg aria-hidden="true"><use href="#up"/></svg></div>
      <p className="eyebrow">{article.category?.toUpperCase() || 'ENTRE NOUS'} · {article.reading_minutes || 4} MIN</p><h3><span className="link-label">{article.title}</span></h3><p className="nt-card-summary"></p>
    </a>)}<a className="article nt-card" href="/guides/premiers-pas"><div className="article-art art-one"><ArtWords words={['FIRST', 'TIME?']}/><svg aria-hidden="true"><use href="#up"/></svg></div><p className="eyebrow">PREMIERS PAS · 26 MIN</p><h3><span className="link-label">Curieux, mais pas sûr de toi ? Tu es au bon endroit.</span></h3><p className="nt-card-summary"></p></a></>;
}

function DynamicFeature({article}) {
  if (!article) return null;
  return <section className="nt-feature" id="a-la-une"><div className="nt-feature-head"><p className="eyebrow">À LA UNE / {article.category?.toUpperCase() || 'ENTRE NOUS'}</p><h2><a className="nt-title-link" data-ink-link href={`/guides/${article.slug}`}><span className="ink-label">{article.title}</span></a></h2></div><a className="nt-feature-art" href={`/guides/${article.slug}`} aria-label={`Lire ${article.title}`}><ArtWords words={article.art_words}/><svg aria-hidden="true"><use href="#up"/></svg></a><div className="nt-feature-summary"><p>{article.summary}</p><a className="button" href={`/guides/${article.slug}`}>Lire l’article <svg aria-hidden="true"><use href="#up"/></svg></a></div></section>;
}

function ArticleNavigation({article, articles}) {
  const cards = [...articles, ...legacyArticleCards];
  const index = cards.findIndex(card => card.slug === article.slug);
  if (index < 0 || cards.length < 2) return null;
  const previous = cards[(index - 1 + cards.length) % cards.length];
  const next = cards[(index + 1) % cards.length];
  return <section className="nt-next"><p className="eyebrow">CONTINUER À LIRE</p><div>
    <a href={`/guides/${previous.slug}`}><small><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m15 6-6 6 6 6"/></svg> ARTICLE PRÉCÉDENT</small><strong>{previous.title}</strong></a>
    <a href={`/guides/${next.slug}`}><small>ARTICLE SUIVANT <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m9 6 6 6-6 6"/></svg></small><strong>{next.title}</strong></a>
  </div></section>;
}

function ArticleStory({article, comments, articles}) {
  return <>
    <header className="nt-masthead"><a href="/guides"><strong>NO TABOO<span>.</span></strong><small>LE JOURNAL KINQ</small></a></header>
    <article className="nt-story">
      <header className="nt-editorial-hero nt-editorial-hero-generic"><div className="nt-editorial-hero-copy"><p className="eyebrow">NO TABOO / {article.category?.toUpperCase() || 'ENTRE NOUS'}</p><h1>{article.title}</h1><p>{article.summary}</p><div className="nt-hero-actions"><a className="nt-editorial-scroll nt-comment-jump" href="#sommaire">Lire l’article <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v15m-6-6 6 6 6-6" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg></a><CommentCount count={comments.length}/></div></div><div className="article-art art-one nt-editorial-hero-art" aria-hidden="true"><ArtWords words={article.art_words}/></div></header>
      <ArticleContent body={article.body}/>
    </article>
    <div id="journal-comments"><JournalComments slug={article.slug} initialComments={comments}/></div>
    <ArticleNavigation article={article} articles={articles}/>
  </>;
}

export default async function KinqPage({params}) {
  const {name, possibleArticleSlug, rootCandidate, nestedArticle} = await route(params);
  if (name === 'preview.html') notFound();
  if (name === 'soirees.html') redirect('/events');
  if (memberPages.has(name)) {
    const cookie = (await cookies()).toString();
    const response = await fetch(`${api}/api/member/me`, {headers: {cookie}, cache: 'no-store'});
    if (response.status === 401) redirect('/connexion');
    if (!response.ok) throw new Error('Espace membre indisponible');
  }
  let document = await getDocument(name, Boolean(possibleArticleSlug));
  const article = !document && possibleArticleSlug ? await getArticle(possibleArticleSlug) : null;
  if (article && rootCandidate) permanentRedirect(`/guides/${article.slug}`);
  if (article) document = await getDocument('journal-article.html');
  const legacySlug = name.endsWith('.html') ? name.slice(0, -5) : '';
  const commentSlug = article?.slug || (legacyArticles.has(legacySlug) ? legacySlug : '');
  const [comments, articles] = await Promise.all([commentSlug ? getComments(commentSlug) : Promise.resolve([]), name === 'guides.html' || article ? getArticles() : Promise.resolve([])]);
  return <PageDocument document={document} slot={article ? <ArticleStory article={article} comments={comments} articles={articles}/> : null}
    bodyAttrs={article ? {...document.bodyAttrs, 'data-page': 'journal', 'data-breadcrumb-category': article.category || 'Entre nous', 'data-breadcrumb-title': article.title} : null}
    commentsSlot={legacyArticles.has(legacySlug) ? <JournalComments slug={legacySlug} initialComments={comments}/> : null}
    commentCountSlot={legacyArticles.has(legacySlug) ? <CommentCount count={comments.length}/> : null}
    articlesSlot={name === 'guides.html' && articles.length ? <DynamicArticles articles={articles}/> : null}
    featureSlot={name === 'guides.html' && articles.length ? <DynamicFeature article={articles[0]}/> : null}
    nestedArticle={nestedArticle}/>;
}
