'use client';

import {useMemo, useState} from 'react';
import {Arrow, KinkIcon} from './frame';

const families = [
  {id:'fetish',label:'Matières & styles',intro:'Une matière, une silhouette, un détail. Porter et admirer sont deux façons de vivre un univers.'},
  {id:'roleplay',label:'Univers & imaginaires',intro:'Des ambiances et des rôles à définir entre adultes, selon les envies de chacun.'},
  {id:'constraint',label:'Bondage & contrainte',intro:'Un intérêt pour la contrainte ne précise ni le rôle, ni le cadre souhaité.'},
  {id:'sensation',label:'Sensations',intro:'Des perceptions et des contacts variés. L’intensité se discute séparément.'},
  {id:'control',label:'Contrôle',intro:'Des règles et des jeux choisis ensemble, dans un cadre révocable.'},
  {id:'ass',label:'Ass play',intro:'Les pratiques se distinguent. Une affinité pour l’une ne vaut pas accord pour les autres.'},
  {id:'impact',label:'Impact',intro:'Donner et recevoir sont des rôles spécifiques. Ils ne disent pas automatiquement dom ou sub.'},
  {id:'body',label:'Corps & attirances',intro:'Ce qui attire ton regard ou te parle dans le contact. Aucune apparence n’est imposée.'},
  {id:'psych',label:'Dynamiques & rituels',intro:'Les mots, les rôles et les rituels prennent leur sens dans les accords entre partenaires.'},
  {id:'fluids',label:'Fluides',intro:'Des attirances qui restent personnelles et nécessitent des échanges explicites.'},
  {id:'advanced',label:'Pratiques avancées',intro:'Ces univers impliquent des risques particuliers. Ce répertoire décrit des intérêts ; il ne fournit aucune instruction de pratique.'},
];
const normalize = value => String(value).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr');
const categoryOf = item => ['edge','sensitive'].includes(item.category) ? 'advanced' : item.category;

export default function Universes({catalogue}) {
  const [query,setQuery] = useState('');
  const [family,setFamily] = useState('all');
  const matches = useMemo(() => catalogue.filter(item => (family === 'all' || categoryOf(item) === family) && normalize(`${item.label} ${item.name} ${item.search || ''}`).includes(normalize(query.trim()))),[catalogue,family,query]);
  return <section className="kx-atlas wrap" aria-label="Répertoire des univers fetish">
    <div className="kx-atlas-tools"><label className="kx-field">Recherche un univers<input type="search" value={query} onChange={e => setQuery(e.target.value)} placeholder="Cuir, rubber, bondage…"/></label><label className="kx-field">Une famille<select aria-label="Une famille" value={family} onChange={e => setFamily(e.target.value)}><option value="all">Toutes les familles</option>{families.map(item => <option value={item.id} key={item.id}>{item.label}</option>)}</select></label><p role="status" aria-live="polite">{matches.length} univers</p></div>
    {!matches.length && <div className="kx-panel"><h2>Pas encore le bon mot ?</h2><p>Essaie un synonyme français ou anglais, ou élargis la famille.</p><button className="button" onClick={() => {setQuery('');setFamily('all');}}>Voir tous les univers <Arrow/></button></div>}
    {families.map(group => {const items=matches.filter(item => categoryOf(item) === group.id);return items.length ? <section className="kx-atlas-family" key={group.id}><div className="kx-section-heading"><h2>{group.label}<span>.</span></h2><p>{group.intro}</p></div><div className="kx-universe-grid">{items.map(item => <details className="kx-universe" key={item.id}><summary><KinkIcon icon={item.icon}/><strong>{item.label}</strong></summary><div><p>{item.help || 'Un univers à exprimer avec tes mots, selon tes envies et tes limites.'}</p><p className="eyebrow">TA FAÇON DE LE VIVRE</p><ul>{item.roles.map(role => <li key={role.id}>{role.label}</li>)}</ul><a className="underlink" href="/lexique">Explorer le lexique <Arrow/></a></div></details>)}</div></section> : null;})}
    <div className="kx-callout"><div><p className="eyebrow">ÇA TE PARLE ?</p><h2>Découvre ta signature.</h2><p>Une première exploration de tes affinités, avec des mots que tu choisis de partager.</p></div><a href="/profil-fetish" className="button">Faire le questionnaire <Arrow/></a></div>
  </section>;
}
