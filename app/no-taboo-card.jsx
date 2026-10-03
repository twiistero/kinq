import SequentialTitle from './sequential-title';
import {CoverWords, coverFor} from './no-taboo-covers';

export default function NoTabooCard({article, showSummary = true}) {
  return <a className="nt-home-card" href={article.href || `/guides/${article.slug}`}>
    <div className={`nt-home-card-art nt-cover-${coverFor(article.slug).theme}`}><CoverWords slug={article.slug} words={article.art_words}/><svg aria-hidden="true"><use href="#up"/></svg></div>
    <div className="nt-home-card-copy"><h3><SequentialTitle>{article.title}</SequentialTitle></h3>{showSummary && <p>{article.summary}</p>}<span className="nt-home-card-link">Lire l’article <svg aria-hidden="true"><use href="#up"/></svg></span></div>
  </a>;
}
