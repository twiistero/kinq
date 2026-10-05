import ExploreFrame, {ExploreHero, ExploreLinks} from '../explore/frame';
import MeetingKit from '../explore/meeting-kit';

export const metadata = {title:'Le kit de rencontre — Kinq',description:'Prépare une discussion sur tes envies, tes limites et le cadre de votre rencontre. Une fiche privée à compléter et à partager selon tes choix.'};

export default function Page() {
  return <ExploreFrame page="kit-rencontre"><ExploreHero eyebrow="LE KIT DE RENCONTRE" title="On se dit quoi," accent="avant de jouer ?" intro="Tes envies. Tes limites. Le cadre qui vous va. Une fiche simple pour lancer la conversation, à remplir seul puis à discuter ensemble."/><MeetingKit/><ExploreLinks/></ExploreFrame>;
}
