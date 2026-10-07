import ExploreFrame from '../explore/frame';
import MemberContracts from '../explore/member-contracts';
export const metadata={title:'Mes contrats — Kinq',robots:{index:false,follow:false}};
export default function Page(){return <ExploreFrame page="mes-contrats"><link rel="stylesheet" href="/contracts.css"/><MemberContracts/></ExploreFrame>;}
