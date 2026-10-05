'use client';

import {useMemo, useState} from 'react';
import {Arrow, KinkIcon} from './frame';

const families = [
  {id:'fetish',label:'Matières & styles'},
  {id:'roleplay',label:'Univers & imaginaires'},
  {id:'constraint',label:'Bondage & contrainte'},
  {id:'sensation',label:'Sensations'},
  {id:'control',label:'Contrôle'},
  {id:'ass',label:'Ass play'},
  {id:'impact',label:'Impact'},
  {id:'body',label:'Corps & attirances'},
  {id:'psych',label:'Dynamiques & rituels'},
  {id:'fluids',label:'Fluides'},
  {id:'advanced',label:'Pratiques avancées'},
];
const normalize = value => String(value).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr');
const categoryOf = item => ['edge','sensitive'].includes(item.category) ? 'advanced' : item.category;

export default function Universes({catalogue,descriptions}) {
  const [query,setQuery] = useState('');
  const [family,setFamily] = useState('all');
  const matches = useMemo(() => catalogue.filter(item => (family === 'all' || categoryOf(item) === family) && normalize(`${item.label} ${item.name} ${item.search || ''} ${descriptions[item.id].join(' ')}`).includes(normalize(query.trim()))),[catalogue,descriptions,family,query]);
  return <section className="kx-atlas wrap" aria-label="Répertoire des univers fetish">
    <div className="kx-atlas-tools"><label className="kx-field">Recherche un univers<input type="search" value={query} onChange={e => setQuery(e.target.value)} placeholder="Cuir, rubber, bondage…"/></label><label className="kx-field">Une famille<select aria-label="Une famille" value={family} onChange={e => setFamily(e.target.value)}><option value="all">Toutes les familles</option>{families.map(item => <option value={item.id} key={item.id}>{item.label}</option>)}</select></label><p role="status" aria-live="polite">{matches.length} univers</p></div>
    {!matches.length && <div className="kx-panel"><h2>Pas encore le bon mot ?</h2><p>Essaie un synonyme français ou anglais, ou élargis la famille.</p><button className="button" onClick={() => {setQuery('');setFamily('all');}}>Voir tous les univers <Arrow/></button></div>}
    {families.map(group => {const items=matches.filter(item => categoryOf(item) === group.id);return items.length ? <section className="kx-atlas-family" key={group.id}><div className="kx-section-heading"><h2>{group.label}<span>.</span></h2></div><div className="kx-universe-grid">{items.map(item => <details className="kx-universe" key={item.id}><summary><KinkIcon icon={item.icon}/><strong>{item.label}</strong></summary><div>{descriptions[item.id].map((paragraph,index) => <p key={index}>{paragraph}</p>)}<p className="eyebrow">TA FAÇON DE LE VIVRE</p><ul>{item.roles.map(role => <li key={role.id}>{role.label}</li>)}</ul><a className="underlink" href="/lexique">Explorer le lexique <Arrow/></a></div></details>)}</div></section> : null;})}
    <div className="kx-callout"><div><p className="eyebrow">ÇA TE PARLE ?</p><h2>Découvre ta signature.</h2><p>Note ce qui te fait kiffer, découvre tes plus grandes affinités et copie tes résultats dans ta bio.</p></div><a href="/profil-fetish" className="button">Faire le questionnaire <Arrow/></a></div>
  </section>;
}
