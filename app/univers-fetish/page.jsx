import catalogue from '../../content/profile-kinks.json';
import descriptions from '../../content/fetish-descriptions.json';
import ExploreFrame, {ExploreHero, ExploreLinks} from '../explore/frame';
import Universes from '../explore/universes';

export const metadata = {title:'Les univers fetish — Kinq',description:'90 kinks disponibles sur Kinq : matières, styles, pratiques BDSM et imaginaires. Découvre ce qu’ils sont, ce qu’ils évoquent et trouve les mecs qui partagent tes kiffs.'};

export default function Page() {
  return <ExploreFrame page="univers-fetish"><ExploreHero eyebrow="LES UNIVERS FETISH" title="Un monde kinky." accent="Ta place dedans." intro="Tous ces kinks sont disponibles sur Kinq pour que chacun puisse les vivre librement. Affiche ceux qui te font kiffer sur ton profil et retrouve les mecs qui partagent tes envies. Matières, styles, pratiques : découvre ce qui se cache derrière chaque univers."/><Universes catalogue={catalogue} descriptions={descriptions}/><ExploreLinks/></ExploreFrame>;
}
