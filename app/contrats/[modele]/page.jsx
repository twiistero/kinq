import {notFound} from 'next/navigation';
import ExploreFrame, {ExploreHero, ExploreLinks} from '../../explore/frame';
import Contracts, {ContractFaq} from '../../explore/contracts';
import {catalogue, modelFor} from '../../explore/contract-model.mjs';

export async function generateMetadata({params}) {
  const {modele}=await params;
  const model=modelFor(modele);
  return model ? {title:`${model.title} — Kinq`,description:model.description} : {};
}

export default async function Page({params}) {
  const {modele}=await params;
  const model=modelFor(modele);
  if (!model) notFound();
  return <ExploreFrame page="contrats"><link rel="stylesheet" href="/contracts.css"/><ExploreHero title={model.title} intro={model.description}/><section className="wrap kc-model-intro"><p>{model.intro}</p><p>Le formulaire ci-dessous vous aide à préciser chaque point. Utilisez les exemples pour rédiger, puis remplacez les pratiques, noms et durées par vos choix.</p><ContractFaq items={model.faq}/><a className="underlink" href="/contrats">Voir tous les contrats</a></section><Contracts initialModel={model.id} showCatalogue={false}/><section className="wrap kc-page-faq"><h2>Pour aller au bout de votre accord.</h2><p>Relire, imprimer ou signer ensemble : les réponses aux questions fréquentes.</p><ContractFaq items={catalogue.faq}/></section><ExploreLinks showEyebrows={false} contractsPage/></ExploreFrame>;
}
