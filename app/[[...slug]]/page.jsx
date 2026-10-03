import {notFound, permanentRedirect, redirect} from 'next/navigation';
import PageDocument from '../page-document';
import ArticleContent from '../article-content';
import NoTabooHome from '../no-taboo-home';
import NoTabooTeaser from '../no-taboo-teaser';
import AppPreviewJournal from '../app-preview-journal';

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

export default async function KinqPage({params}) {
  const {name, possibleArticleSlug, rootCandidate, nestedArticle} = await route(params);
  if (name === 'preview.html') notFound();
  if (name === 'soirees.html') redirect('/events');
  if (memberPages.has(name)) redirect('/application');
  let document = await getDocument(name, Boolean(possibleArticleSlug));
  const article = !document && possibleArticleSlug ? await getArticle(possibleArticleSlug) : null;
  if (article && rootCandidate) permanentRedirect(`/guides/${article.slug}`);
  if (article) document = await getDocument('journal-article.html');
  const legacySlug = name.endsWith('.html') ? name.slice(0, -5) : '';
  const commentSlug = article?.slug || (legacyArticles.has(legacySlug) ? legacySlug : '');
  const [comments, articles] = await Promise.all([commentSlug ? getComments(commentSlug) : Promise.resolve([]), name === 'index.html' || name === 'guides.html' || commentSlug ? getArticles() : Promise.resolve([])]);
  const catalogue = [...articles, ...legacyArticleCards].map(item => ({...item, href:`/guides/${item.slug}`}));
  const active = catalogue.findIndex(item => item.slug === commentSlug);
  const related = active < 0 ? [] : [1,2].map(offset => catalogue[(active + offset) % catalogue.length]).filter(item => item.slug !== commentSlug);
  const slot = commentSlug ? <ArticleContent document={document} article={article} slug={commentSlug} comments={comments} commentCount={comments.length} related={related}/> : name === 'guides.html' ? <NoTabooHome published={articles}/> : null;
  return <PageDocument document={document} slot={slot} slots={name === 'index.html' ? {journal:<NoTabooTeaser published={articles}/>, 'app-preview-journal':<AppPreviewJournal published={articles}/>} : undefined}
    bodyAttrs={article ? {...document.bodyAttrs, 'data-page': 'journal', 'data-breadcrumb-category': article.category || 'Entre nous', 'data-breadcrumb-title': article.title} : null}
    nestedArticle={nestedArticle}/>;
}
