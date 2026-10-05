import catalogue from '../../content/profile-kinks.json';
import ExploreFrame, {ExploreHero, ExploreLinks} from '../explore/frame';
import SignatureQuiz from '../explore/signature-quiz';

export const metadata = {title:'Ton profil fetish — KINQ SIGNATURE',description:'Un questionnaire pour découvrir tes plus grandes affinités fetish et BDSM. Copie tes résultats pour ta bio ou une autre app de rencontre. Gratuit et sans compte.'};

export default function Page() {
  return <ExploreFrame page="profil-fetish"><ExploreHero eyebrow="KINQ SIGNATURE" title="C’est quoi," accent="ton kiff ?" intro="Ce qui t’excite. Ce qui te fait kiffer. Découvre tes plus grandes affinités, puis copie tes résultats où tu veux."/><SignatureQuiz catalogue={catalogue}/><ExploreLinks/></ExploreFrame>;
}
