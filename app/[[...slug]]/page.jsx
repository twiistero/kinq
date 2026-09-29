import {cookies} from 'next/headers';
import {notFound, permanentRedirect, redirect} from 'next/navigation';
import PageDocument from '../page-document';
import JournalComments from '../journal-comments';
import ArticleContent from '../article-content';

export const dynamic = 'force-dynamic';
const api = process.env.KINQ_API_URL || 'http://127.0.0.1:8000';
const memberPages = new Set(['compte.html','mon-profil.html','rencontres.html','profil.html']);
const legacyArticles = new Set(['premiers-pas','parler-de-ses-limites','les-mots-pour-se-comprendre','profil-et-vie-privee','premiere-rencontre','aftercare']);

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
  if (slug.length === 1 && /^[a-z0-9-]+$/.test(slug[0])) return {name: `${slug[0]}.html`, possibleArticleSlug: slug[0]};
  if (slug.length === 2 && slug[0] === 'journal' && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug[1])) permanentRedirect(`/${slug[1]}`);
  notFound();
}

export async function generateMetadata({params}) {
  const {name, possibleArticleSlug} = await route(params);
  const document = await getDocument(name, Boolean(possibleArticleSlug));
  if (!document && possibleArticleSlug) {
    const article = await getArticle(possibleArticleSlug);
    return {title: `${article.title} — NO TABOO, KINQ`, description: article.summary, alternates: {canonical: `/${article.slug}`}};
  }
  return {title: document.title, description: document.description || undefined};
}

function ArtWords({words}) {
  return <span>{(words?.length ? words : ['NO', 'TABOO']).map((word, index) => <span key={index}>{word}{index < (words?.length || 2) - 1 && <br/>}</span>)}</span>;
}

function DynamicArticles({articles}) {
  if (!articles.length) return null;
  return <><div className="nt-heading"><h2>LE JOURNAL CONTINUE</h2></div><div className="articles nt-grid">{articles.map(article =>
    <a className="article nt-card" href={`/${article.slug}`} key={article.slug}>
      <div className="article-art art-three nt-dynamic-art"><ArtWords words={article.art_words}/><svg aria-hidden="true"><use href="#up"/></svg></div>
      <p className="eyebrow">NO TABOO</p><h3><span className="link-label">{article.title}</span></h3><p className="nt-card-summary">{article.summary}</p>
    </a>)}</div></>;
}

function ArticleStory({article, comments}) {
  return <>
    <header className="nt-masthead"><a href="/guides"><strong>NO TABOO<span>.</span></strong><small>LE JOURNAL KINQ</small></a></header>
    <article className="nt-story">
      <header className="nt-editorial-hero nt-editorial-hero-generic"><div className="nt-editorial-hero-copy"><p className="eyebrow">NO TABOO / JOURNAL</p><h1>{article.title}</h1><p>{article.summary}</p><div className="nt-hero-actions"><a className="nt-editorial-scroll nt-comment-jump" href="#article">Lire l’article <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v15m-6-6 6 6 6-6" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg></a><CommentCount count={comments.length}/></div></div><div className="nt-editorial-hero-art" aria-hidden="true"><ArtWords words={article.art_words}/></div></header>
      <div className="nt-story-layout" id="article"><aside><span>NO TABOO</span><p>{article.summary}</p><a href="/guides">Retour au journal</a></aside><div className="nt-prose"><ArticleContent body={article.body}/></div></div>
      <a className="button" href="/guides">Retour au journal</a>
    </article>
    <div id="journal-comments"><JournalComments slug={article.slug} initialComments={comments}/></div>
  </>;
}

export default async function KinqPage({params}) {
  const {name, possibleArticleSlug} = await route(params);
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
  if (article) document = await getDocument('journal-article.html');
  const legacySlug = name.endsWith('.html') ? name.slice(0, -5) : '';
  const commentSlug = article?.slug || (legacyArticles.has(legacySlug) ? legacySlug : '');
  const [comments, articles] = await Promise.all([commentSlug ? getComments(commentSlug) : Promise.resolve([]), name === 'guides.html' ? getArticles() : Promise.resolve([])]);
  return <PageDocument document={document} slot={article ? <ArticleStory article={article} comments={comments}/> : null}
    commentsSlot={legacyArticles.has(legacySlug) ? <JournalComments slug={legacySlug} initialComments={comments}/> : null}
    commentCountSlot={legacyArticles.has(legacySlug) ? <CommentCount count={comments.length}/> : null}
    articlesSlot={name === 'guides.html' && articles.length ? <DynamicArticles articles={articles}/> : null}/>;
}
