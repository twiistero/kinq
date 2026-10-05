import catalogue from '../../content/profile-kinks.json';
import ExploreFrame, {ExploreHero, ExploreLinks} from '../explore/frame';
import Universes from '../explore/universes';

export const metadata = {title:'Les univers fetish — Kinq',description:'Explore les matières, les styles, les pratiques et les imaginaires du catalogue Kinq. Recherche un univers et découvre les mots pour exprimer tes envies.'};

export default function Page() {
  return <ExploreFrame page="univers-fetish"><ExploreHero eyebrow="LES UNIVERS FETISH" title="Un monde kinky." accent="Ta place dedans." intro="Une matière, une pratique, un imaginaire. Explore les univers Kinq et les différentes façons de les vivre."/><Universes catalogue={catalogue}/><ExploreLinks/></ExploreFrame>;
}
