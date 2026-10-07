import ExploreFrame from '../explore/frame';
import {MemberAccount} from '../explore/member-contracts';
export const metadata={title:'Mon compte — Kinq',robots:{index:false,follow:false}};
export default function Page(){return <ExploreFrame page="compte"><link rel="stylesheet" href="/contracts.css"/><MemberAccount/></ExploreFrame>;}
