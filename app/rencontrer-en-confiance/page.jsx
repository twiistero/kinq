import ExploreFrame, {Arrow, ExploreHero, ExploreLinks} from '../explore/frame';

export const metadata = {title:'Rencontrer en confiance — Kinq',description:'Exprime tes envies et tes limites, choisis ce que tu partages et découvre les outils de confidentialité et de signalement de Kinq.'};

const points = [
  ['Tes envies se discutent.','Un univers en commun, un Hook ou une signature fetish ouvre une conversation. Cela ne signifie jamais un accord pour une pratique. Prenez le temps de préciser ce que chacun souhaite, ce qui reste à discuter et ce qui est exclu.'],
  ['Tu peux changer d’avis.','Avant ou pendant une rencontre, un accord reste révocable. Un doute, une pause ou un arrêt doit pouvoir être exprimé et respecté. Décidez ensemble de la façon de communiquer, sans pression.'],
  ['Tes informations, tes choix.','Dans l’app, tes préférences de visibilité contrôlent ce que tu partages. La localisation est facultative. Les photos privées nécessitent une autorisation distincte, que leur propriétaire peut retirer.'],
  ['Tu gardes la main sur tes échanges.','Le blocage et le signalement permettent d’agir sur un contact ou un comportement dans l’app. Le signalement transmet les éléments à examiner ; il ne garantit pas une intervention immédiate.'],
  ['Une rencontre se prépare.','Pour un premier contact, choisis un cadre où tu te sens à l’aise et garde la possibilité de partir. Échange sur les attentes, la discrétion, les photos et les limites. Aucun profil, badge ou questionnaire ne garantit la sécurité d’une personne.'],
  ['Le respect continue après.','Les portraits, albums et captures de profils ne se partagent pas sans accord. Une autorisation de voir une photo ne donne pas celui de la diffuser. Reprenez la discussion si vos envies ou vos accords évoluent.'],
];

export default function Page() {
  return <ExploreFrame page="rencontrer-en-confiance"><ExploreHero eyebrow="RENCONTRER EN CONFIANCE" title="Le feeling compte." accent="Tes limites aussi." intro="Des échanges clairs, des choix personnels et des outils pour garder la main. La confiance se construit ensemble."><a className="button" href="/contrats">Personnaliser un contrat <Arrow/></a></ExploreHero><section className="kx-trust-grid wrap">{points.map(([title,text],index) => <article key={title}><span className="kx-step-number">0{index+1}</span><h2>{title}</h2><p>{text}</p></article>)}</section><section className="kx-trust-links wrap"><a href="/charte">Notre charte <Arrow/></a><a href="/confidentialite">Tes données et leur confidentialité <Arrow/></a><a href="/centre-aide">Le centre d’aide <Arrow/></a><a href="/guides/parler-de-ses-limites">Parler de ses limites <Arrow/></a></section><p className="kx-note wrap">Repères sur le consentement : <a href="https://ncsfreedom.org/wp-content/uploads/2019/12/Consent-Counts-Statement-summary.pdf" target="_blank" rel="noopener">NCSF — Consent Counts (en anglais, nouvel onglet)</a>. Les outils présentés se trouvent dans l’app, dont le téléchargement sera proposé au lancement.</p><ExploreLinks/></ExploreFrame>;
}
