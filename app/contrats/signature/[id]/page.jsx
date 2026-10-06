import ExploreFrame from '../../../explore/frame';
import ContractSigning from '../../../explore/contract-signing';

export const metadata = {title:'Votre accord privé — Kinq',robots:{index:false,follow:false}};

export default async function Page({params}) {
  const {id}=await params;
  return <ExploreFrame page="contrats"><link rel="stylesheet" href="/contracts.css"/><ContractSigning id={id}/></ExploreFrame>;
}
