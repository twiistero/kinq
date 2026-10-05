import ExploreFrame, {Arrow, ExploreHero, ExploreLinks, KinkIcon} from '../explore/frame';

export const metadata = {title:'Comment ça marche — Kinq',description:'Crée ton compte, exprime tes envies et retrouve tes rencontres dans l’app Kinq. Découvre les profils, les Pins, les Hooks et les messages.'};

const steps = [
  {title:'Ton adresse e-mail. Et c’est tout.',icon:'service',text:'Crée ton compte avec ton adresse e-mail et vérifie-la avec le code reçu. Tu te connectes ensuite avec un code, sans mot de passe à retenir.',href:'/inscription',link:'Créer mon compte'},
  {title:'Un profil à ta façon.',icon:'leather',text:'Dans l’app, choisis tes photos, présente-toi et indique les univers qui te parlent. Tu peux préciser ta façon de vivre chaque kink et choisir la visibilité de tes informations.',href:'/profil-fetish',link:'Trouver les mots de mon profil'},
  {title:'Le feeling commence ici.',icon:'pup',text:'Découvre les profils et utilise les filtres pour retrouver les univers qui t’intéressent. La localisation est facultative et les distances dépendent de positions autorisées et récentes.',href:'/application',link:'Découvrir l’application'},
  {title:'Discute. Échange. Rencontre.',icon:'body-worship',text:'Un Pin garde un profil dans tes connexions, un Hook exprime ton intérêt, un message ouvre la discussion. Les envies et les limites se parlent avant une rencontre.',href:'/kit-rencontre',link:'Préparer une discussion'},
];

export default function Page() {
  return <ExploreFrame page="comment-ca-marche"><ExploreHero eyebrow="COMMENT ÇA MARCHE" title="Quelques étapes." accent="Puis le feeling." intro="Le compte commence sur le site. Ton profil, tes rencontres et tes discussions se vivent dans l’app Kinq."><a className="button" href="/inscription">Créer mon compte <Arrow/></a></ExploreHero><section className="kx-steps wrap">{steps.map((step,index) => <article key={step.title}><div className="kx-step-top"><span>0{index+1}</span><KinkIcon icon={step.icon}/></div><h2>{step.title}</h2><p>{step.text}</p><a className="underlink" href={step.href}>{step.link} <Arrow/></a></article>)}</section><section className="kx-callout wrap"><div><p className="kx-eyebrow">À TON RYTHME</p><h2>L’app arrive.<br/>L’univers est déjà là.</h2><p>Kinq sera disponible sur iOS et Android. En attendant, tu peux créer ton compte, explorer NO TABOO et découvrir ta signature fetish.</p></div><a className="button" href="/application">L’application Kinq <Arrow/></a></section><ExploreLinks/></ExploreFrame>;
}
