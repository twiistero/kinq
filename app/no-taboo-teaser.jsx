import NoTabooCard from './no-taboo-card';
import {journalCatalogue} from './no-taboo-catalogue';

export default function NoTabooTeaser({published}) {
  const selection = journalCatalogue(published).slice(0, 3);
  return <>
    <div className="journal-masthead"><div><strong>NO TABOO<span aria-hidden="true">.</span></strong><span>LE JOURNAL KINQ</span></div><a className="button" href="/guides">Explore NO TABOO <svg aria-hidden="true"><use href="#up"/></svg></a></div>
    <div className="journal-body">
      <div className="home-journal-intro"><h2>Tes envies.<br/><em>Sans détour.</em></h2><p>Envies, limites, culture kink, rencontres : des articles pour comprendre ce qui t’attire, trouver tes mots et explorer à ton rythme.</p></div>
      <div className="nt-magazine-grid home-journal-selection">{selection.map(article => <NoTabooCard article={article} showSummary={false} key={article.slug}/>)}</div>
      <div className="home-journal-invitation"><div><h3>Une question en tête ?<br/>Une envie à explorer ?</h3><p>Premiers pas, mots, désirs, limites… Trouve ta prochaine lecture dans NO TABOO.</p></div><a className="button" href="/guides">Découvrir tout le journal <svg aria-hidden="true"><use href="#up"/></svg></a></div>
    </div>
  </>;
}
