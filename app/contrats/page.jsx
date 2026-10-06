import ExploreFrame, {ExploreHero, ExploreLinks} from '../explore/frame';
import Contracts, {ContractFaq} from '../explore/contracts';
import {catalogue} from '../explore/contract-model.mjs';

export const metadata = {title:'Les contrats Kinq — Vos règles, votre jeu',description:'Dix accords personnalisables : BDSM, domination, chasteté, séance, bondage, discipline, pup play, service, collier et exclusivité. Guides et PDF Kinq.'};

export default function Page() {
  return <ExploreFrame page="contrats"><link rel="stylesheet" href="/contracts.css"/><ExploreHero title="Vos règles." accent="Votre jeu." intro="Dix modèles pour mettre vos envies et vos règles noir sur blanc. Choisissez votre jeu, précisez les rôles, les pratiques et la durée, puis relisez votre accord ensemble avant de l’imprimer ou de le signer."/><Contracts/><section className="wrap kc-page-faq"><h2>Les réponses à vos questions.</h2><p>Choix du modèle, exemples, impression et signature : les repères pour préparer un accord qui vous ressemble.</p><ContractFaq items={catalogue.faq}/></section><ExploreLinks showEyebrows={false} contractsPage/></ExploreFrame>;
}
