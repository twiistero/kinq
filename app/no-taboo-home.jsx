import NoTabooFeed from './no-taboo-feed';

import {journalCatalogue} from './no-taboo-catalogue';

const Arrow = () => <svg aria-hidden="true"><use href="#up"/></svg>;
export default function NoTabooHome({published=[]}) {
  const other = journalCatalogue(published);
  return <div className="nt-site nt-home-refresh wrap"><header className="nt-masthead"><a href="/guides" aria-label="NO TABOO, accueil du journal"><strong>NO TABOO<span>.</span></strong><small>LE JOURNAL KINQ</small></a></header>
    <div className="nt-edition"><span>ENVIES · CULTURE KINK · RENCONTRES</span><span>LIBRES D’EN PARLER. LIBRES D’EXPLORER.</span></div><section className="nt-home-hero"><div className="nt-home-hero-copy"><h1>Tes envies.<br/><em>Sans détour.</em></h1><p>Envies, limites, rencontres : des articles pour comprendre ce qui t’attire, trouver tes mots et avancer sans te justifier.</p><a className="button" href="#selection">Trouver quoi lire <Arrow/></a></div><div className="nt-home-hero-art" aria-hidden="true"><span>NO<br/>TABOO<span>.</span></span><small>TES QUESTIONS ONT LEUR PLACE ICI.</small></div></section>
    <nav className="nt-home-nav" aria-label="Explorer le journal"><span>JE VEUX PARLER DE…</span><a href="/guides/premiers-pas">Premiers pas</a><a href="/guides/parler-de-ses-limites">Envies & limites</a><a href="/guides/les-mots-pour-se-comprendre">Les mots</a><a href="/guides/premiere-rencontre">Rencontres</a></nav>
    <section className="nt-home-list" id="selection"><div className="nt-home-list-head"><h2>Ça mérite qu’on en parle.</h2><p>À lire, à garder en tête, à glisser dans la conversation.</p></div><NoTabooFeed articles={other}/></section>
    <aside className="nt-home-outro"><div><h2>Les mots ouvrent<br/><em>des rencontres.</em></h2><p>Retrouve les profils, les rencontres et les conversations dans l’app Kinq.</p></div><a className="button" href="/application">Découvrir l’app Kinq <Arrow/></a></aside>
  </div>;
}
