'use client';
import {useState} from 'react';
import {Arrow} from './frame';
import {contractHandoffKey, memberRequest, useMember} from './member-session';

export default function ContractAccountCTA({document, signed}) {
  const {member,loading,error,retry} = useMember();
  const [busy,setBusy]=useState(false), [status,setStatus]=useState(''), [saved,setSaved]=useState(false);
  async function keep(destination) {
    setBusy(true);setStatus('');
    try {
      const payload=signed ? {contractId:signed.id,access:signed.access} : null;
      if(member) {
        await memberRequest(`/api/member/contracts/${signed ? 'claim' : 'print'}`,{
          csrf:member.csrf,method:'POST',body:JSON.stringify(payload || {document}),
        });
        setSaved(true);setStatus('Ton contrat est conservé dans Mes contrats.');
      } else {
        const handoff=payload || {draftToken:(await memberRequest('/api/contracts/account-draft',{
          method:'POST',body:JSON.stringify({document}),
        })).token};
        sessionStorage.setItem(contractHandoffKey,JSON.stringify(handoff));
        window.location.assign(`${destination}?next=/mes-contrats`);
      }
    } catch(error) {setStatus(error.message);} finally {setBusy(false);}
  }
  return <aside className="kc-account-cta" aria-label="Conserver mon contrat">
    <h3>Retrouve ton contrat.<br/><span>Sur Kinq aussi.</span></h3>
    <p>Conserve cette version dans « Mes contrats » pour la retrouver dans ton compte et dans l’app.</p>
    {loading ? <p>Vérification de ton compte…</p> : error ? <><p role="status">{error}</p><button className="text-button" onClick={retry}>Réessayer</button></> : saved ?
      <a className="button" href="/mes-contrats">Voir Mes contrats <Arrow/></a> : member ?
      <button type="button" className="button" disabled={busy} onClick={()=>keep()}>Conserver dans Mes contrats <Arrow/></button> :
      <div className="kx-actions"><button type="button" className="button" disabled={busy} onClick={()=>keep('/inscription')}>Créer mon compte <Arrow/></button><button type="button" className="button" disabled={busy} onClick={()=>keep('/connexion')}>Me connecter <Arrow/></button></div>}
    <p role="status" aria-live="polite">{status}</p>
  </aside>;
}
