'use client';

import {useMemo, useRef, useState} from 'react';
import {Arrow, KinkIcon} from './frame';
import {affinity, buildSignature, chapters, experienceLabels, questionCount, scale, signatureText, traitChapters, universeCount} from './signature-model.mjs';
import {copyText} from './export';

function Scale({id,label,value,onChange}) {
  return <fieldset className="kx-scale"><legend>{label}</legend><div>
    {scale.map(option => <label key={option.value} className={value === option.value ? 'is-selected' : ''}><input type="radio" name={id} value={option.value} checked={value === option.value} onChange={() => onChange(option.value)}/><span>{option.label}</span></label>)}
    <label className={'kx-unknown '+(value === null ? 'is-selected' : '')}><input type="radio" name={id} value="unknown" checked={value === null} onChange={() => onChange(null)}/><span>Je ne sais pas encore</span></label>
  </div></fieldset>;
}

function Score({item}) {
  const caption = item.kind === 'trait' ? item.meaning : [item.experience,item.role].filter(Boolean).join(' · ');
  return <article className="kx-score"><div className="kx-score-heading">{item.icon && <KinkIcon icon={item.icon}/>}<strong>{item.label}</strong><b>{item.score} %</b></div><div className="kx-bar" role="meter" aria-label={'Affinité '+item.label} aria-valuenow={item.score} aria-valuemin={0} aria-valuemax={100}><span style={{width:item.score+'%'}}/></div>{caption && <p>{caption}</p>}</article>;
}

export default function SignatureQuiz({catalogue}) {
  const [started,setStarted] = useState(false);
  const [step,setStep] = useState(0);
  const [answers,setAnswers] = useState({});
  const [finished,setFinished] = useState(false);
  const [selected,setSelected] = useState([]);
  const [status,setStatus] = useState('');
  const [busy,setBusy] = useState(false);
  const [resetRequested,setResetRequested] = useState(false);
  const heading = useRef(null);
  const byId = useMemo(() => new Map(catalogue.map(item => [item.id,item])),[catalogue]);
  const result = useMemo(() => buildSignature(answers,catalogue),[answers,catalogue]);
  const chapter = chapters[step] || traitChapters[step-chapters.length];
  const isTrait = step >= chapters.length;
  const totalSteps = chapters.length + traitChapters.length;

  function update(id,key,value) {
    setAnswers(previous => ({...previous,[id]:{...previous[id],[key]:value}}));
  }
  function focusHeading() {
    requestAnimationFrame(() => {
      heading.current?.focus({preventScroll:true});
      heading.current?.scrollIntoView({block:'start',behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'});
    });
  }
  function move(next) {setStep(next);setStatus('');focusHeading();}
  function finish() {
    setSelected(result.topScores.map(item => item.id));
    setFinished(true);focusHeading();
  }
  async function share() {
    setStatus('');setBusy(true);
    try {
      await copyText(signatureText(result,selected));setStatus('Tes résultats ont été copiés.');
    } catch {setStatus('La copie est indisponible ici. Sélectionne le texte ci-dessous pour le copier.');}
    finally {setBusy(false);}
  }
  function reset() {
    setStarted(false);setFinished(false);setStep(0);setAnswers({});setSelected([]);setStatus('');setResetRequested(false);focusHeading();
  }

  if (!started) return <section className="kx-signature-intro wrap" aria-labelledby="signature-start-title">
    <div className="kx-signature-poster"><div className="kx-poster-top"><span>KINQ SIGNATURE</span><img src="/assets/kinq-symbol.svg" alt="" width="52" height="52"/></div><p>TES KIFFS.<br/>TES FANTASMES.<br/><span>TA SIGNATURE.</span></p><div className="kx-poster-bottom"><span>Fetish</span><span>BDSM</span><span>Rôles</span></div></div>
    <div className="kx-start-copy"><h2 id="signature-start-title" ref={heading} tabIndex={-1}>Qu’est-ce<br/>qui t’excite ?</h2><p>{questionCount} questions directes. {universeCount} univers fetish et des tendances BDSM. Note ce qui te fait kiffer, dans tes fantasmes ou dans ta pratique.</p><p>Un test pour le plaisir de découvrir tes kiffs. Tu peux passer une question et revenir en arrière.</p><ul className="kx-check-list"><li>Tes plus grandes affinités, classées par score.</li><li>Des pourcentages de kiff et ton expérience à part.</li><li>Un texte prêt à copier-coller dans ta bio ou ailleurs.</li></ul><p className="kx-note">Tes réponses restent dans cet onglet ; un rechargement les efface.</p><button className="button" onClick={() => {setStarted(true);focusHeading();}}>Faire le test <Arrow/></button></div>
  </section>;

  if (finished) return <section className="kx-result wrap" aria-labelledby="signature-result-title">
    <div className="kx-result-top"><div><p className="eyebrow">TES PLUS GRANDES AFFINITÉS</p><h2 id="signature-result-title" ref={heading} tabIndex={-1}>{result.title}</h2><p>{result.explanation}</p><p className="kx-note">{result.responseCount} réponses sur {questionCount}. Les questions passées ne comptent pas comme un désintérêt.</p></div><div className="kx-result-stamp"><img src="/assets/kinq-symbol.svg" alt="" width="90" height="90"/><span>TES KIFFS.<br/>TES MOTS.</span></div></div>
    <div className="kx-result-grid"><div>
      {result.positiveTraits.length > 0 && <section className="kx-traits"><h3>Tes profils BDSM.</h3><p className="kx-note">Plusieurs noms peuvent te correspondre. Ils traduisent tes réponses sur le contrôle, la douleur ou la provocation.</p>{result.positiveTraits.map(item => <Score item={item} key={item.id}/>)}</section>}
      <h3>Tes kiffs les plus forts.</h3><p className="kx-note">Tes cinq premières affinités, à partir de 50 %. 100 % signifie « À fond ».</p><div className="kx-score-list">{result.ranked.length ? result.ranked.slice(0,5).map(item => <Score item={item} key={item.id}/>) : <p>Aucun kiff marqué pour le moment.</p>}</div>
      <details className="kx-details"><summary>Voir tous mes scores fetish</summary>{result.shareItems.filter(item => item.kind === 'universe').map(item => <Score item={item} key={item.id}/>)}{!result.answered.length && <p>Tu n’as pas encore renseigné d’univers.</p>}</details>
      <details className="kx-details"><summary>Les univers que je n’ai pas renseignés</summary><p>{result.assessed.filter(item => item.score === null).map(item => item.label).join(' · ') || 'Tu as répondu pour tous les univers du parcours.'}</p></details>
      <details className="kx-details"><summary>Voir toutes mes tendances</summary>{result.traits.filter(item => item.score !== null).map(item => <Score item={item} key={item.id}/>)}{result.traits.every(item => item.score === null) && <p>Tu n’as pas renseigné les questions de tendances.</p>}</details>
    </div><aside className="kx-share-panel"><h3>Tes résultats,<br/>à copier-coller.</h3><fieldset className="kx-share-choices"><legend>Choisis les affinités à partager</legend>{result.shareItems.length ? result.shareItems.map(item => <label key={item.id}><input type="checkbox" checked={selected.includes(item.id)} onChange={e => {setSelected(previous => e.target.checked ? [...previous,item.id] : previous.filter(id => id !== item.id));setStatus('');}}/>{item.label} : {item.score} %</label>) : <p>Aucun score à afficher pour le moment.</p>}</fieldset><label className="kx-field">Ton texte à copier-coller<textarea readOnly rows={9} onFocus={e => e.target.select()} value={signatureText(result,selected)}/></label><div className="kx-actions"><button className="button" disabled={busy || !selected.length} onClick={share}>Copier mes résultats <Arrow/></button></div><p role="status" aria-live="polite" className="kx-status">{status}</p><p className="kx-note">À coller dans ta bio, une autre app de rencontre ou un message.</p></aside></div>
    <details className="kx-details"><summary>Comment sont calculés les scores ?</summary><p>Une question directe par univers : 0 (« Pas du tout »), 1, 2, 3 ou 4 (« À fond »), soit 0, 25, 50, 75 ou 100 % d’affinité. Les questions passées et « Je ne sais pas encore » sont exclus. L’expérience et la façon de vivre un kink ne changent pas son score.</p><p>Le titre reprend tes trois kiffs les plus forts, à partir de 50 %. Si aucun univers ne ressort, il reprend les tendances BDSM les plus fortes. Tu retrouves tous les autres scores dans les listes dépliables.</p><p>Dom, Sub, Sadique, Masochiste, Brat et Brat tamer viennent de leurs questions directes. Switch reprend le plus faible de tes scores Dom et Sub. Chaque score est indépendant : tes affinités ne s’additionnent pas pour faire 100 %.</p></details>
    <div className="kx-result-actions"><button className="button" onClick={() => {setFinished(false);move(0);}}>Modifier mes réponses <Arrow/></button><button className="text-button" onClick={() => setResetRequested(true)}>Effacer et recommencer</button>{resetRequested && <div className="kx-reset"><p>Effacer toutes tes réponses de cet onglet ?</p><button className="button small" onClick={reset}>Oui, effacer</button><button className="text-button" onClick={() => setResetRequested(false)}>Garder mes réponses</button></div>}</div>
  </section>;

  return <section className="kx-quiz wrap" aria-labelledby="signature-chapter-title">
    <div className="kx-quiz-progress"><span>ÉTAPE {step+1} / {totalSteps}</span><span>{result.responseCount} / {questionCount} réponses</span><progress max={totalSteps} value={step+1} aria-label="Progression des étapes"/></div>
    <div className="kx-chapter-heading"><h2 id="signature-chapter-title" ref={heading} tabIndex={-1}>{chapter.title}</h2><p>{chapter.intro}</p></div>
    <div className="kx-question-grid">{chapter.items.map(question => {
      if (isTrait) return <article key={question.id} className="kx-question"><h3>{question.label}</h3><Scale id={'dynamics-'+question.id} label={question.prompt} value={answers.dynamics?.[question.id]} onChange={value => update('dynamics',question.id,value)}/></article>;
      const item=byId.get(question.id),answer=answers[item.id] || {},score=affinity([answer.kiff]);
      return <article key={item.id} className="kx-question"><div className="kx-question-title"><KinkIcon icon={item.icon}/><h3>{item.label}</h3><a className="underlink" href="/lexique" target="_blank" rel="noopener" aria-label={'Comprendre '+item.label+' dans le lexique, nouvel onglet'}>Le mot <Arrow/></a></div><Scale id={item.id+'-kiff'} label={question.prompt} value={answer.kiff} onChange={value => update(item.id,'kiff',value)}/>{score !== null && score > 0 && <details className="kx-optional"><summary>Mon expérience et ma façon de le vivre</summary><label className="kx-field">Mon expérience<select aria-label="Mon expérience" value={answer.experience || ''} onChange={e => update(item.id,'experience',e.target.value)}><option value="">Je ne précise pas</option>{Object.entries(experienceLabels).map(([id,label]) => <option value={id} key={id}>{label}</option>)}</select></label><label className="kx-field">Ma façon de le vivre<select aria-label="Ma façon de le vivre" value={answer.role || ''} onChange={e => update(item.id,'role',e.target.value)}><option value="">Je ne précise pas</option>{item.roles.map(role => <option value={role.id} key={role.id}>{role.label}</option>)}</select></label></details>}</article>;
    })}</div>
    <div className="kx-quiz-controls"><button className="text-button" disabled={step === 0} onClick={() => move(step-1)}>← Retour</button><span>Réponds à ton rythme. Tu peux passer.</span><button className="button" onClick={() => step === totalSteps-1 ? finish() : move(step+1)}>{step === totalSteps-1 ? 'Voir ma signature' : 'Continuer'} <Arrow/></button></div>
  </section>;
}
