import {cookies} from 'next/headers';
import {notFound, redirect} from 'next/navigation';
import PageDocument from '../page-document';
import JournalComments from '../journal-comments';

export const dynamic = 'force-dynamic';
const api = process.env.KINQ_API_URL || 'http://127.0.0.1:8000';
const memberPages = new Set(['compte.html','mon-profil.html','rencontres.html','profil.html']);
const legacyArticles = new Set(['premiers-pas','parler-de-ses-limites','les-mots-pour-se-comprendre','profil-et-vie-privee','premiere-rencontre','aftercare']);

async function getDocument(name) {
  const response = await fetch(`${api}/api/documents/${name}`, {cache: 'no-store'});
  if (response.status === 404) notFound();
  if (!response.ok) throw new Error('Contenu KINQ indisponible');
  return response.json();
}

async function getArticle(slug) {
  const response = await fetch(`${api}/api/articles/${slug}`, {cache: 'no-store'});
  if (response.status === 404) notFound();
  if (!response.ok) throw new Error('Article KINQ indisponible');
  return response.json();
}

async function route(params) {
  const slug = (await params).slug || [];
  if (slug.length === 0) return {name: 'index.html'};
  if (slug.length === 1 && slug[0] === 'admin') return {name: 'admin'};
  if (slug.length === 1 && /^[a-z0-9-]+$/.test(slug[0])) return {name: `${slug[0]}.html`};
  if (slug.length === 2 && slug[0] === 'journal' && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug[1])) return {name: 'journal-article.html', articleSlug: slug[1]};
  notFound();
}

export async function generateMetadata({params}) {
  const {name, articleSlug} = await route(params);
  if (articleSlug) {
    const article = await getArticle(articleSlug);
    return {title: `${article.title} — NO TABOO, KINQ`, description: article.summary};
  }
  const document = await getDocument(name);
  return {title: document.title, description: document.description || undefined};
}

function ArticleStory({article}) {
  return <>
    <header className="nt-masthead"><a href="/guides"><strong>NO TABOO<span>.</span></strong><small>LE JOURNAL KINQ</small></a></header>
    <article className="nt-story">
      <header className="nt-editorial-hero"><div className="nt-editorial-hero-copy"><p className="eyebrow">NO TABOO / JOURNAL</p><h1>{article.title}</h1><p>{article.summary}</p></div></header>
      <div className="nt-prose">{String(article.body).split(/\n\s*\n/).map((paragraph, index) => <p key={index}>{paragraph.split('\n').map((line, lineIndex) => <span key={lineIndex}>{line}{lineIndex < paragraph.split('\n').length - 1 && <br/>}</span>)}</p>)}</div>
      <a className="button" href="/guides">Retour au journal</a>
    </article>
    <JournalComments slug={article.slug}/>
  </>;
}

export default async function KinqPage({params}) {
  const {name, articleSlug} = await route(params);
  if (name === 'preview.html') notFound();
  if (name === 'soirees.html') redirect('/events');
  if (memberPages.has(name)) {
    const cookie = (await cookies()).toString();
    const response = await fetch(`${api}/api/member/me`, {headers: {cookie}, cache: 'no-store'});
    if (response.status === 401) redirect('/connexion');
    if (!response.ok) throw new Error('Espace membre indisponible');
  }
  const [document, article] = await Promise.all([getDocument(name), articleSlug ? getArticle(articleSlug) : Promise.resolve(null)]);
  const legacySlug = name.endsWith('.html') ? name.slice(0, -5) : '';
  return <PageDocument document={document} slot={article ? <ArticleStory article={article}/> : null}
    commentsSlot={legacyArticles.has(legacySlug) ? <JournalComments slug={legacySlug}/> : null}/>;
}
