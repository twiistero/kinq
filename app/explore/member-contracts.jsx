'use client';
import {useEffect, useState} from 'react';
import {FileText} from 'lucide-react';
import {Arrow} from './frame';
import {ContractDocument, download} from './contracts';
import {copyText} from './export';
import {contractHandoffKey, memberRequest, useMember} from './member-session';

const labels={print:'À imprimer',signed:'Signé à deux',pending:'Signature en attente'};
function LoginLinks({next='/mes-contrats'}) {
  return <div className="kc-account-cta"><h2>Tes contrats, dans ton compte.</h2><p>Connecte-toi avec l’adresse utilisée pour tes signatures. Tes copies restent privées et sont accessibles dans l’app aussi.</p><div className="kx-actions"><a className="button" href={`/inscription?next=${next}`}>Créer mon compte <Arrow/></a><a className="button" href={`/connexion?next=${next}`}>Me connecter <Arrow/></a></div></div>;
}

export function MemberAccount() {
  const {member,loading,error}=useMember();
  return <section className="wrap kc-account-page"><h1>Mon compte.</h1>{loading ? <p>Chargement de ton compte…</p> : error ? <p role="status">{error}</p> : !member ? <LoginLinks next="/compte"/> : <>
    <p>{member.email}</p><article className="kc-account-cta"><FileText size={30} aria-hidden="true"/><h2>Mes contrats</h2><p>Retrouve tes versions à imprimer, tes contrats signés et les signatures en attente.</p><a className="button" href="/mes-contrats">Ouvrir Mes contrats <Arrow/></a></article>
    <div className="kx-actions"><a className="button" href="/application">Découvrir l’app <Arrow/></a><button className="text-button" onClick={async()=>{await memberRequest('/api/member/auth/logout',{method:'POST',csrf:member.csrf});window.location.assign('/connexion');}}>Me déconnecter</button></div>
  </>}</section>;
}

export default function MemberContracts() {
  const {member,loading,error:authError}=useMember();
  const [items,setItems]=useState(null),[record,setRecord]=useState(null),[error,setError]=useState(''),[busy,setBusy]=useState(false),[notice,setNotice]=useState('');
  const [name,setName]=useState(''),[accepted,setAccepted]=useState(false),[removing,setRemoving]=useState(false);
  async function load() {setItems(await memberRequest('/api/member/contracts'));}
  useEffect(()=>{if(!member)return;let active=true;
    (async()=>{
      const raw=sessionStorage.getItem(contractHandoffKey);
      if(raw){try {
        const value=JSON.parse(raw);await memberRequest('/api/member/contracts/claim',{method:'POST',csrf:member.csrf,body:JSON.stringify(value)});
        sessionStorage.removeItem(contractHandoffKey);if(active)setNotice('Ton contrat a été ajouté à ton compte.');
      }catch(error){
        if(error.status===404 || error.status===422 || error instanceof SyntaxError) sessionStorage.removeItem(contractHandoffKey);
        if(active)setError(error.message);
      }}
      const list=await memberRequest('/api/member/contracts');if(active)setItems(list);
    })().catch(error=>{if(active)setError(error.message);});
    return()=>{active=false;};
  },[member]);
  async function action(fn) {setBusy(true);setError('');try{await fn();}catch(error){setError(error.message);}finally{setBusy(false);}}
  return <section className="wrap kc-account-page"><a className="underlink" href="/compte">Mon compte <Arrow/></a><h1>Mes contrats.</h1><p>Tes versions à imprimer et tes contrats signés, accessibles ici et dans l’app Kinq.</p>
    {loading ? <p>Chargement de ton compte…</p> : authError ? <p role="status">{authError}</p> : !member ? <LoginLinks/> : <>
    <div className="kx-actions"><a className="button" href="/contrats">Créer un contrat <Arrow/></a><button type="button" className="text-button" disabled={busy} onClick={()=>action(async()=>{await load();if(record)setRecord(await memberRequest(`/api/member/contracts/${record.id}`));})}>Actualiser</button></div>
    {notice && <p role="status">{notice}</p>}{error && <p role="status">{error}</p>}
    {items===null && !error && <p>Chargement de tes contrats…</p>}
    {items?.length===0 && <div className="kc-account-cta"><h2>Ton premier contrat.</h2><p>Choisis un modèle, adapte les règles, puis conserve ton PDF ici. Les contrats signés avec ton adresse Kinq apparaissent dans cette rubrique.</p></div>}
    {record ? <><button type="button" className="text-button" onClick={()=>{setRecord(null);setRemoving(false);}}>Retour à mes contrats</button><div className="kc-final"><aside className="kc-final-tools"><h2>{record.title}</h2><p>{labels[record.status]}</p>
      {record.status==='pending' ? <>{!record.signatures[record.slot] && <form onSubmit={event=>{event.preventDefault();action(async()=>{
        await memberRequest(`/api/member/contracts/${record.id}/sign`,{csrf:member.csrf,method:'POST',body:JSON.stringify({name,accepted,contentHash:record.contentHash})});setRecord(null);setAccepted(false);setName('');await load();setNotice('Ta signature a été enregistrée.');
      });}}><label className="kx-field">Nom ou pseudo pour signer<input required maxLength={80} value={name} onChange={event=>setName(event.target.value)}/><small>Saisis exactement : {record.document[record.slot===0 ? 'nameA' : 'nameB']}.</small></label><label className="kc-check"><input required type="checkbox" checked={accepted} onChange={event=>setAccepted(event.target.checked)}/><span>J’ai lu cette version et je souhaite la signer, conserver ma copie privée et la recevoir par e-mail après les deux signatures.</span></label><button className="button" disabled={busy}>Signer cette version <Arrow/></button></form>}
        {record.partnerLink && <button className="button" onClick={()=>action(async()=>{await copyText(record.partnerLink);setNotice('Le lien privé a été copié.');})}>Copier le lien de l’autre personne <Arrow/></button>}
      </> : <><button className="button" disabled={busy} onClick={()=>action(async()=>download(await memberRequest(`/api/member/contracts/${record.id}/pdf`),'contrat-kinq.pdf'))}>Télécharger le PDF <Arrow/></button><button className="text-button" onClick={()=>setRemoving(true)}>Retirer de Mes contrats</button>{removing && <div className="kc-account-cta"><p>Retirer ta copie de ton compte ? La copie de l’autre personne et les PDF déjà téléchargés restent disponibles pour eux.</p><button className="button" disabled={busy} onClick={()=>action(async()=>{await memberRequest(`/api/member/contracts/${record.id}`,{csrf:member.csrf,method:'DELETE'});setRecord(null);setRemoving(false);await load();})}>Retirer ma copie</button><button className="text-button" onClick={()=>setRemoving(false)}>Garder ma copie</button></div>}</>}
    </aside><ContractDocument draft={record.document} signatures={record.signatures} reference={record.reference}/></div></> : <div className="kc-saved-list">{items?.map(item=><article key={item.id}><FileText size={28} aria-hidden="true"/><div><h2>{item.title}</h2><p>{item.names.filter(Boolean).join(' / ') || 'Version à personnaliser'}</p><p>{labels[item.status]}{item.status!=='print' && ` · ${item.signatureCount}/2 signatures`} · {new Date(item.createdAt).toLocaleDateString('fr-FR')}</p></div><button type="button" className="button" disabled={busy} onClick={()=>action(async()=>{setRecord(await memberRequest(`/api/member/contracts/${item.id}`));setName('');setAccepted(false);setRemoving(false);})}>Ouvrir <Arrow/></button></article>)}</div>}
    </>}
  </section>;
}
