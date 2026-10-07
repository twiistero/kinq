'use client';

import {useRef, useState} from 'react';
import {Check, FileText, Printer, Link as LinkIcon} from 'lucide-react';
import {Arrow, KinkIcon} from './frame';
import {catalogue, contractSections, contractText, freshDraft, modelFor} from './contract-model.mjs';
import {contractPdf} from './contract-pdf.mjs';
import {copyText} from './export';
import ContractAccountCTA from './contract-account-cta';

export function download(blob, filename) {
  const url=URL.createObjectURL(blob),link=document.createElement('a');
  link.href=url;link.download=filename;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
}

export async function contractApi(path, {token, verified, ...options} = {}) {
  const response=await fetch(`/api/contracts${path}`,{...options,cache:'no-store',headers:{'Content-Type':'application/json',...(token ? {Authorization:`Bearer ${token}`} : {}),...(verified ? {'X-Contract-Access':'verified'} : {})}});
  if (!response.ok) {
    let message='Le service de signature est indisponible. Ton texte reste dans cet onglet ; tu peux télécharger le PDF.';
    try {const body=await response.json();if (typeof body.detail==='string') message=body.detail;else if (response.status===422) message='Vérifie les champs : deux noms ou pseudos, deux adresses distinctes et des dates cohérentes.';} catch {}
    throw new Error(message);
  }
  return response.headers.get('content-type')?.includes('application/pdf') ? response.blob() : response.json();
}

export function ContractFaq({items, label='Questions sur cette rubrique'}) {
  return <div className="kc-faq" aria-label={label}>{items.map(item=><details key={item.question}><summary>{item.question}</summary><p>{item.answer}</p></details>)}</div>;
}

function Field({field, value, onChange}) {
  const id=`kc-field-${field.id}`;
  return <section className="kc-clause" aria-labelledby={`${id}-label`}>
    <label id={`${id}-label`} htmlFor={id}>{field.title}</label>
    <p id={`${id}-help`} className="kc-field-help">{field.help}</p>
    <textarea id={id} className="kc-textarea" aria-describedby={`${id}-help`} rows={4} maxLength={2000} value={value || ''} onChange={e=>onChange(e.target.value)}/>
    <details className="kc-field-guide">
      <summary>Exemple et conseils</summary>
      <div>
        <p className="kc-example">{field.example}</p>
        <button type="button" className="text-button" aria-label={`Utiliser cet exemple : ${field.title}`} onClick={()=>onChange(field.example)}>Utiliser cet exemple <Arrow/></button>
        <p className="kc-field-tip"><strong>{field.faq[0].question}</strong> {field.faq[0].answer}</p>
      </div>
    </details>
  </section>;
}

export function CopyableText({value, label='Texte à copier', rows=8}) {
  return <label className="kx-field kc-copy-text">{label}<textarea autoFocus readOnly rows={rows} value={value} onFocus={event=>event.target.select()}/><small>Le texte est sélectionné. Utilise ⌘C ou Ctrl+C pour le copier.</small></label>;
}

export function ContractBrand() {
  return <div className="kc-document-brand"><span className="kc-brand-powered">Powered by</span><img src="/assets/kinq-logo-print.svg" alt="Kinq" width="108" height="42"/><strong>Make it kinky.</strong><span className="kc-brand-domain">kinq-app.com</span></div>;
}

export function ContractDocument({draft, signatures, reference}) {
  const model=modelFor(draft.model);
  return <article className="kc-document" aria-label="Texte du contrat">
    <header><div><h2>{model.title}</h2>{reference && <p className="kc-reference">Référence : {reference}</p>}</div><ContractBrand/></header>
    {contractSections(draft).map((section,index)=><section key={section.title}><h3><span>{String(index+1).padStart(2,'0')}</span>{section.title}</h3><p>{section.text}</p></section>)}
    <section className="kc-signatures"><h3>Signatures</h3><div>{[draft.nameA,draft.nameB].map((name,index)=><div key={index}><strong>{name.trim() || `Personne ${index+1}`}</strong>{signatures?.[index] ? <><p>Signé par {signatures[index].name}</p><time dateTime={signatures[index].signedAt}>{new Date(signatures[index].signedAt).toLocaleString('fr-FR',{timeZone:'Europe/Paris'})} (Europe/Paris)</time></> : <><p>Date : __________________</p><p>Signature : __________________</p></>}</div>)}</div></section>
    <footer>Accord personnel de jeu{reference ? ` / ${reference}` : ''}</footer>
  </article>;
}

export default function Contracts({initialModel='bdsm',showCatalogue=true}) {
  const [selected,setSelected]=useState(initialModel);
  const [drafts,setDrafts]=useState(()=>Object.fromEntries(catalogue.models.map(model=>[model.id,freshDraft(model.id)])));
  const [step,setStep]=useState(0),[status,setStatus]=useState(''),[busy,setBusy]=useState(false),[mode,setMode]=useState('print'),[showCopy,setShowCopy]=useState(false);
  const [archiveDraft,setArchiveDraft]=useState(null);
  const [emailA,setEmailA]=useState(''),[emailB,setEmailB]=useState(''),[processing,setProcessing]=useState(false),[invitation,setInvitation]=useState(null);
  const editor=useRef(null);
  const draft=drafts[selected],model=modelFor(selected);
  const accountCTA=archiveDraft && <ContractAccountCTA key={JSON.stringify(archiveDraft)} document={archiveDraft}/>;
  function update(key,value) {if(invitation) return;setDrafts(previous=>({...previous,[selected]:{...previous[selected],[key]:value}}));setStatus('');}
  function field(id,value) {update('fields',{...draft.fields,[id]:value});}
  function move(next) {
    setStep(next);setStatus('');
    requestAnimationFrame(()=>{editor.current?.focus({preventScroll:true});editor.current?.scrollIntoView({block:'start',behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'});});
  }
  async function pdf(blank=false) {
    setBusy(true);setStatus('');
    try {const version=blank ? freshDraft(selected) : structuredClone(draft);download(await contractPdf(version),`contrat-${selected}-kinq${blank ? '-vierge' : ''}.pdf`);setStatus('Ton PDF est prêt.');setArchiveDraft(version);}
    catch(error) {setStatus(error.message || 'Impossible de préparer le PDF. Ton texte est conservé.');}
    finally {setBusy(false);}
  }
  async function create(event) {
    event.preventDefault();setBusy(true);setStatus('');
    try {const result=await contractApi('',{method:'POST',body:JSON.stringify({document:draft,emailA,emailB,processing})});setInvitation(result);setStatus('La version à signer est enregistrée. Vérifie ton adresse avant de la partager.');}
    catch(error) {setStatus(error.message);}
    finally {setBusy(false);}
  }
  return <>
    {showCatalogue && <section className="wrap kc-catalogue" aria-label="Choisir un contrat"><div className="kc-models">{catalogue.models.map(item=><article className={`kc-model${selected===item.id ? ' is-selected' : ''}`} key={item.id}><div className="kc-model-top"><KinkIcon icon={item.icon}/></div><h2>{item.short}</h2><p>{item.description}</p><button type="button" className="button" aria-pressed={selected===item.id} onClick={()=>{setSelected(item.id);setInvitation(null);setShowCopy(false);setArchiveDraft(null);move(0);}}>{selected===item.id ? 'Modèle choisi' : 'Choisir ce contrat'}{selected===item.id ? <Check size={17} aria-hidden="true"/> : <Arrow/>}</button><a className="kc-model-guide underlink" href={`/contrats/${item.id}`}>Comprendre ce contrat <Arrow/></a></article>)}</div><p className="kx-note">Les exemples donnent une formulation concrète. Adaptez les pratiques, les durées et les rôles à votre jeu avant de signer.</p></section>}
    <section className="wrap kc-editor" aria-label="Personnaliser le contrat">
      <header className="kc-editor-heading" ref={editor} tabIndex={-1}><div><h2>{showCatalogue ? model.title : model.tagline}</h2><p>Chaque rubrique a une consigne et un exemple à adapter. Remplissez les quatre étapes pour préparer votre contrat.</p></div><button className="text-button" disabled={busy} onClick={()=>pdf(true)}><FileText size={16} aria-hidden="true"/> Télécharger le modèle vierge</button></header>
      {step!==3 && accountCTA}
      <nav className="kc-steps" aria-label="Étapes de personnalisation">{['Les personnes','Les règles','Les permissions','Le contrat'].map((title,index)=><button key={title} type="button" className={step===index ? 'is-current' : ''} aria-current={step===index ? 'step' : undefined} disabled={Boolean(invitation) && index!==3} onClick={()=>move(index)}><span>0{index+1}</span>{title}</button>)}</nav>
      {step===0 && <div className="kc-form"><div className="kc-form-intro"><h3>Qui joue avec qui, et quand ?</h3><p>Indiquez vos noms ou pseudos, le rôle de chacun et les dates. Précisez ensuite les lieux et moments où vos règles s’appliquent.</p></div><div className="kc-two">{['A','B'].map((suffix,index)=><fieldset key={suffix}><legend>Personne {index+1}</legend><label className="kx-field">Nom ou pseudo<input autoComplete="off" maxLength={80} value={draft[`name${suffix}`]} onChange={e=>update(`name${suffix}`,e.target.value)}/><small>Le nom qui figurera dans le document et sera retapé pour signer en ligne.</small></label><label className="kx-field">Rôle choisi<input maxLength={80} value={draft[`role${suffix}`]} onChange={e=>update(`role${suffix}`,e.target.value)}/><small>Par exemple : dominant, soumis, switch, pup ou handler. Renommez le rôle proposé si besoin.</small></label></fieldset>)}</div><div className="kc-two"><label className="kx-field">Date de début<input type="date" value={draft.start} onChange={e=>update('start',e.target.value)}/><small>Le premier jour où l’accord s’applique.</small></label><label className="kx-field">Date de fin<input type="date" min={draft.start || undefined} value={draft.end} onChange={e=>update('end',e.target.value)}/><small>Le dernier jour prévu ; indiquez le renouvellement dans le champ suivant.</small></label></div><label className="kx-field">Durée et renouvellement<input maxLength={240} value={draft.duration} onChange={e=>update('duration',e.target.value)}/><small>Écrivez par exemple : « Chaque samedi pendant un mois, puis un point avant toute nouvelle période. » Pour une seule séance, utilisez la même date de début et de fin.</small></label><Field field={catalogue.common[0]} value={draft.fields.frame} onChange={value=>field('frame',value)}/></div>}
      {step===1 && <div className="kc-form"><div className="kc-form-intro"><h3>Écrivez vos règles de jeu.</h3><p>Décrivez les actions attendues, les rôles, le matériel et les moments concernés. Chaque exemple montre une phrase complète : remplacez ce qui ne vous ressemble pas.</p></div>{model.fields.map(item=><Field key={item.id} field={item} value={draft.fields[item.id]} onChange={value=>field(item.id,value)}/>)}</div>}
      {step===2 && <div className="kc-form"><div className="kc-form-intro"><h3>Autorisé. À demander. Exclu.</h3><p>Faites trois listes distinctes. Ajoutez vos signaux de pause et d’arrêt, la fin de séance, les règles sur les images et la façon de revoir l’accord.</p></div>{catalogue.common.slice(1).map(item=><Field key={item.id} field={item} value={draft.fields[item.id]} onChange={value=>field(item.id,value)}/>)}</div>}
      {step===3 && <div className="kc-final"><div className="kc-final-tools"><h3>Relisez votre contrat.</h3><p>Vérifiez les noms, les rôles, les dates et les clauses. Remplacez tous les crochets et les mentions « à préciser » avant de signer. Les e-mails n’apparaissent pas dans le document.</p><div className="kc-mode" role="group" aria-label="Format du contrat"><button type="button" className={mode==='print' ? 'is-selected' : ''} aria-pressed={mode==='print'} onClick={()=>setMode('print')}><Printer size={18} aria-hidden="true"/> À imprimer</button><button type="button" className={mode==='digital' ? 'is-selected' : ''} aria-pressed={mode==='digital'} onClick={()=>setMode('digital')}><LinkIcon size={18} aria-hidden="true"/> À signer en ligne</button></div>
        {mode==='print' ? <><div className="kx-actions"><button className="button" disabled={busy} onClick={()=>pdf()}>Télécharger le PDF <Arrow/></button><button className="button" onClick={()=>{setArchiveDraft(structuredClone(draft));window.print();}}>Imprimer <Printer size={16} aria-hidden="true"/></button></div><button className="text-button" onClick={async()=>{try {await copyText(contractText(draft));setStatus('Le texte du contrat a été copié.');}catch {setShowCopy(true);setStatus('Copie le texte sélectionné ci-dessous.');}}}>Copier le texte</button>{showCopy && <CopyableText value={contractText(draft)}/>}</> : <form onSubmit={create}><label className="kx-field">E-mail de {draft.nameA.trim() || 'la personne 1'}<input disabled={Boolean(invitation)} required type="email" autoComplete="email" value={emailA} onChange={e=>setEmailA(e.target.value)} maxLength={255}/></label><label className="kx-field">E-mail de {draft.nameB.trim() || 'la personne 2'}<input disabled={Boolean(invitation)} required type="email" autoComplete="off" value={emailB} onChange={e=>setEmailB(e.target.value)} maxLength={255}/></label><label className="kc-check"><input type="checkbox" required checked={processing} onChange={e=>setProcessing(e.target.checked)}/><span>Je souhaite enregistrer cette version privée et recevoir ma copie après les deux signatures. L’autre personne vérifiera elle-même son adresse et son accord.</span></label><button className="button" disabled={busy || !draft.nameA.trim() || !draft.nameB.trim() || Boolean(invitation)} type="submit">{busy ? 'Enregistrement…' : 'Créer la version à signer'} <Arrow/></button><p className="kx-note">Le lien expire après 14 jours sans les deux signatures. Le document signé reste téléchargeable pendant 30 jours. Une copie est envoyée séparément à chaque personne.</p>{invitation && <div className="kc-created"><p>Cette version est figée. Ouvre ton lien pour vérifier ton adresse, signer et obtenir le lien ou QR code de l’autre personne.</p><a className="button" href={`/contrats/signature/${invitation.id}#invitation=${invitation.invitation}`}>Vérifier et signer <Arrow/></a><p className="kx-note">Pour modifier cette version partagée, retirez-la depuis la page de signature puis créez-en une nouvelle.</p></div>}</form>}
      {accountCTA}</div><ContractDocument draft={draft}/></div>}
      <p className="kx-status" role="status" aria-live="polite">{status}</p><div className="kc-controls">{step>0 && <button type="button" className="text-button" disabled={Boolean(invitation)} onClick={()=>move(step-1)}>Étape précédente</button>}{step<3 && <button type="button" className="button" onClick={()=>move(step+1)}>Continuer <Arrow/></button>}</div>
    </section>
  </>;
}
