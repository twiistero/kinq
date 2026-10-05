import PageEffects from '../legacy-scripts';

const scripts = [{src:'/shell.js'}, {src:'/app.js'}];

export function Arrow() {
  return <svg aria-hidden="true"><use href="#arrow"/></svg>;
}

export function KinkIcon({icon, className = ''}) {
  return <img className={`kx-icon ${className}`} src={`/assets/pictos/${icon}.svg`} alt="" width="48" height="48"/>;
}

export function ExploreHero({eyebrow, title, accent, intro, children}) {
  return <section className="kx-hero wrap">
    <div><p className="eyebrow">{eyebrow}</p><h1>{title}<br/><span>{accent}</span></h1><p className="kx-lead">{intro}</p>{children}</div>
  </section>;
}

export function ExploreLinks() {
  return <section className="kx-related wrap" aria-label="Continuer à explorer"><p className="eyebrow">CONTINUE À EXPLORER</p><div className="kx-link-grid">
    <article className="home-journal-invitation kx-explore-card"><p className="eyebrow">LE JOURNAL KINQ</p><h3>NO <span>TABOO.</span></h3><p>Des articles pour explorer tes envies et la culture kink.</p><a className="button" href="/guides">Explorer le journal <Arrow/></a></article>
    <article className="home-journal-invitation kx-explore-card"><p className="eyebrow">LES UNIVERS FETISH</p><h3>Trouve<br/><span>les mots.</span></h3><p>Matières, sensations, pratiques : découvre les univers qui te parlent.</p><a className="button" href="/univers-fetish">Découvrir les univers <Arrow/></a></article>
    <article className="home-journal-invitation kx-explore-card"><p className="eyebrow">LE KIT DE RENCONTRE</p><h3>Parlons<br/><span>de nos envies.</span></h3><p>Prépare un texte à partager pour faire connaissance.</p><a className="button" href="/kit-rencontre">Ouvrir le kit <Arrow/></a></article>
  </div></section>;
}

export default function ExploreFrame({page, children}) {
  return <>
    <link rel="stylesheet" href="/styles.css"/>
    <link rel="stylesheet" href="/explore.css"/>
    <div id="site-header"/>
    <main id="page-main" className="kx">{children}</main>
    <div id="site-footer"/>
    <dialog id="dialog"><button className="dialog-close" aria-label="Fermer"><svg aria-hidden="true"><use href="#close"/></svg></button><div id="dialog-content"/></dialog>
    <div id="toast" role="status" aria-live="polite"/>
    <PageEffects bodyAttrs={{'data-page':page}} scripts={scripts}/>
  </>;
}
