'use client';

import {useState} from 'react';
import {Arrow} from './frame';
import {copyText, downloadText} from './export';

const sections = [
  {id:'feeling',title:'Le feeling que je cherche.',prompt:'Qu’est-ce qui me ferait passer un bon moment ?',placeholder:'Une discussion, une rencontre, une ambiance…'},
  {id:'desires',title:'Ce qui me fait envie.',prompt:'Quels univers et quelles façons de jouer ai-je envie de discuter ?',placeholder:'Mes envies, mon rôle, ce que je voudrais découvrir…'},
  {id:'limits',title:'Mes limites.',prompt:'Qu’est-ce que je ne souhaite pas ? Qu’est-ce qui reste à discuter ?',placeholder:'Mes non, mes sujets à préciser…'},
  {id:'frame',title:'Le cadre que je choisis.',prompt:'Que souhaitons-nous convenir sur le lieu, le rythme, les photos et la discrétion ?',placeholder:'Le contexte, ce qui peut être partagé, le temps prévu…'},
  {id:'communication',title:'Comment on communique.',prompt:'Comment exprimer une pause, un doute ou un arrêt ?',placeholder:'Les mots ou signes convenus ensemble…'},
  {id:'after',title:'Après, on en parle.',prompt:'Qu’est-ce qui me ferait du bien après notre rencontre ?',placeholder:'Un moment calme, un échange, reprendre contact…'},
];
const checks = ['Nous avons parlé de nos envies et de nos limites.','Nous savons comment demander une pause ou arrêter.','Nous avons convenu de ce qui peut être photographié ou partagé.','Chacun reste libre de changer d’avis, même après avoir préparé cette fiche.'];

export default function MeetingKit() {
  const [answers,setAnswers] = useState({});
  const [checked,setChecked] = useState([]);
  const [included,setIncluded] = useState(sections.map(item => item.id));
  const [status,setStatus] = useState('');
  const [confirmReset,setConfirmReset] = useState(false);
  const shareable = sections.filter(item => included.includes(item.id) && answers[item.id]?.trim());
  const text = ['MON KIT DE RENCONTRE · KINQ',...shareable.map(item => `${item.title}\n${answers[item.id].trim()}`),'Cette fiche prépare une discussion. Elle ne vaut pas consentement. Chacun peut changer d’avis à tout moment.'].join('\n\n');
  async function copy() {
    try {await copyText(text);setStatus('Les rubriques choisies ont été copiées.');}
    catch {setStatus('La copie est indisponible ici. Tu peux sélectionner le texte du résumé ou télécharger la fiche.');}
  }
  return <section className="kx-kit wrap"><p className="kx-note">Tes notes restent dans cet onglet. Elles ne sont ni envoyées à Kinq ni enregistrées. Un rechargement les efface.</p><div className="kx-kit-grid"><div>{sections.map((item,index) => <section className="kx-kit-section" key={item.id}><span className="kx-step-number">0{index+1}</span><div><h2>{item.title}</h2><p>{item.prompt}</p><label className="kx-field"><span className="kx-sr-only">{item.title}</span><textarea maxLength={2000} rows={3} value={answers[item.id] || ''} placeholder={item.placeholder} onChange={e => setAnswers(previous => ({...previous,[item.id]:e.target.value}))}/></label></div></section>)}<fieldset className="kx-checks"><legend>Des points à discuter ensemble.</legend>{checks.map((text,index) => <label key={index}><input type="checkbox" checked={checked.includes(index)} onChange={e => setChecked(previous => e.target.checked ? [...previous,index] : previous.filter(item => item !== index))}/>{text}</label>)}</fieldset></div><aside className="kx-share-panel"><p className="eyebrow">LA DISCUSSION COMMENCE ICI</p><h2>Choisis ce<br/>que tu partages.</h2><fieldset className="kx-share-choices"><legend>Rubriques à inclure</legend>{sections.map(item => <label key={item.id}><input type="checkbox" checked={included.includes(item.id)} onChange={e => setIncluded(previous => e.target.checked ? [...previous,item.id] : previous.filter(id => id !== item.id))}/>{item.title}</label>)}</fieldset><label className="kx-field">Le résumé choisi<textarea readOnly value={text} rows={9}/></label><div className="kx-actions"><button className="button" disabled={!shareable.length} onClick={copy}>Copier ma fiche <Arrow/></button><button className="button" disabled={!shareable.length} onClick={() => {downloadText(text,'mon-kit-rencontre-kinq.txt');setStatus('Ta fiche texte est prête à télécharger.');}}>Télécharger la fiche <Arrow/></button></div><p className="kx-status" role="status" aria-live="polite">{status}</p><button className="text-button" onClick={() => setConfirmReset(true)}>Effacer mes notes</button>{confirmReset && <div className="kx-reset"><p>Effacer toutes les notes de cet onglet ?</p><button className="button small" onClick={() => {setAnswers({});setChecked([]);setStatus('Tes notes ont été effacées.');setConfirmReset(false);}}>Oui, effacer</button><button className="text-button" onClick={() => setConfirmReset(false)}>Garder mes notes</button></div>}</aside></div><div className="kx-callout"><div><h2>Préparer, c’est en parler.</h2><p>Une case cochée ne vérifie pas l’accord de l’autre personne. Cette fiche ouvre la conversation ; les accords se confirment ensemble et restent révocables.</p></div><a className="button" href="/guides/parler-de-ses-limites">Parler de ses limites <Arrow/></a></div><p className="kx-note">Repères sur le consentement : <a href="https://ncsfreedom.org/wp-content/uploads/2019/12/Consent-Counts-Statement-summary.pdf" target="_blank" rel="noopener">NCSF — Consent Counts (en anglais, nouvel onglet)</a>.</p></section>;
}
