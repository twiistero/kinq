import NoTabooFeed from './no-taboo-feed';

import {journalCatalogue} from './no-taboo-catalogue';
import {JournalBrand, JournalMark, JournalTopics} from './no-taboo-shell';

const Arrow = () => <svg aria-hidden="true"><use href="#up"/></svg>;
export default function NoTabooHome({published=[]}) {
  const other = journalCatalogue(published);
  return <div className="nt-site nt-home-refresh wrap">
    <section className="nt-home-hero journal-full-hero"><div className="nt-home-hero-copy journal-full-copy"><JournalBrand/><h1 className="journal-hero-themes">Culture Kink.<br/>Pratiques.<br/><em>Rencontres.</em></h1><p>Envies, limites, rencontres : des articles pour comprendre ce qui t’attire, trouver tes mots et avancer sans te justifier.</p><a className="button" href="#selection">Trouver quoi lire <Arrow/></a></div><JournalMark/></section>
    <JournalTopics/>
    <section className="nt-home-list" id="selection"><div className="nt-home-list-head"><h2>Ça mérite qu’on en parle.</h2><p>À lire, à garder en tête, à glisser dans la conversation.</p></div><NoTabooFeed articles={other}/></section>
    <aside className="nt-home-outro"><div><h2>Les mots ouvrent<br/><em>des rencontres.</em></h2><p>Retrouve les profils, les rencontres et les conversations dans l’app Kinq.</p></div><a className="button" href="/application">Découvrir l’app Kinq <Arrow/></a></aside>
  </div>;
}
