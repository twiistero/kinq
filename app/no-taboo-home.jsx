import NoTabooFeed from './no-taboo-feed';

const historic = [
  {slug:'premiers-pas',title:'Curieux, mais pas sûr de toi ? Tu es au bon endroit.',category:'Premiers pas',word:'DÉBUT',summary:'Une première porte pour explorer à ton rythme.'},
  {slug:'parler-de-ses-limites',title:'Parler de ses limites sans casser le feeling.',category:'Entre nous',word:'LIMITES',summary:'Trouver les mots pour dire ce qui te va, et ce qui ne te va pas.'},
  {slug:'les-mots-pour-se-comprendre',title:'Les mots pour te comprendre. Pas pour t’enfermer.',category:'Le lexique',word:'MOTS',summary:'Des repères simples, sans te mettre dans une case.'},
  {slug:'profil-et-vie-privee',title:'Ton profil, tes règles. Tu choisis ce que tu partages.',category:'Vie privée',word:'PRIVÉ',summary:'Garder la main sur ce que tu dévoiles.'},
  {slug:'premiere-rencontre',title:'Du premier message à la première rencontre.',category:'Rencontres',word:'RDV',summary:'Passer du chat au réel, à ton rythme.'},
  {slug:'aftercare',title:'L’aftercare : la connexion continue après.',category:'Entre nous',word:'APRÈS',summary:'L’attention portée à l’autre ne s’arrête pas au moment partagé.'},
];
const Arrow = () => <svg aria-hidden="true"><use href="#up"/></svg>;
export default function NoTabooHome({published=[]}) {
  const other = [...published.map(item => ({...item,category:'Nouveau',word:'KINQ',href:`/guides/${item.slug}`})), ...historic];
  return <div className="nt-site nt-home-refresh wrap"><header className="nt-masthead"><a href="/guides" aria-label="NO TABOO, accueil du journal"><strong>NO TABOO<span>.</span></strong><small>LE JOURNAL KINQ</small></a></header>
    <div className="nt-edition"><span>ENVIES · CULTURE KINK · RENCONTRES</span><span>LIBRES D’EN PARLER. LIBRES D’EXPLORER.</span></div><section className="nt-home-hero"><div className="nt-home-hero-copy"><h1>Tes envies.<br/><em>Sans détour.</em></h1><p>Envies, limites, rencontres : des articles pour comprendre ce qui t’attire, trouver tes mots et avancer sans te justifier.</p><a className="button" href="#selection">Trouver quoi lire <Arrow/></a></div><div className="nt-home-hero-art" aria-hidden="true"><span>NO<br/>TABOO<span>.</span></span><small>TES QUESTIONS ONT LEUR PLACE ICI.</small></div></section>
    <nav className="nt-home-nav" aria-label="Explorer le journal"><span>JE VEUX PARLER DE…</span><a href="/guides/premiers-pas">Premiers pas</a><a href="/guides/parler-de-ses-limites">Envies & limites</a><a href="/guides/les-mots-pour-se-comprendre">Les mots</a><a href="/guides/premiere-rencontre">Rencontres</a></nav>
    <section className="nt-home-list" id="selection"><div className="nt-home-list-head"><h2>Ça mérite qu’on en parle.</h2><p>À lire, à garder en tête, à glisser dans la conversation.</p></div><NoTabooFeed articles={other}/></section>
    <aside className="nt-home-outro"><div><h2>Les mots ouvrent<br/><em>des rencontres.</em></h2><p>Envie de poursuivre la conversation avec des mecs qui te parlent vraiment ?</p></div><a className="button" href="/rencontres">Explorer les rencontres <Arrow/></a></aside>
  </div>;
}
