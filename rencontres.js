(() => {
'use strict';
const $=s=>document.querySelector(s);
let demoConnected=false;
const memberGreeting=document.createElement('div');
memberGreeting.className='encounters-member';
memberGreeting.hidden=true;
const hello=document.createElement('span');
hello.className='encounters-hello';
const accountLink=document.createElement('a');
accountLink.href='/compte';
accountLink.textContent='Mon compte';
memberGreeting.append(hello,accountLink);
document.querySelector('#site-header .header .account').prepend(memberGreeting);
function updateMemberGreeting(){
 const pseudo=memberName || String(myProfileData.pseudo||'').trim();
 hello.textContent=`Salut, ${pseudo||'toi'} !`;
}
const paths={search:'<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',sliders:'<path d="M4 7h9m4 0h3M4 17h3m4 0h9"/><circle cx="15" cy="7" r="2"/><circle cx="9" cy="17" r="2"/>',close:'<path d="m6 6 12 12M18 6 6 18"/>',arrow:'<path d="M4 12h16m-6-6 6 6-6 6"/>',chevron:'<path d="m6 9 6 6 6-6"/>',pin:'<path d="m14 3 7 7-4 1-4 6-2-2-7 7 7-7-2-2 6-4Z"/>',hook:'<path d="M7 3v12a5 5 0 0 0 10 0v-5l-4 4"/>',user:'<circle cx="12" cy="8" r="4"/><path d="M4 22v-3a8 8 0 0 1 16 0v3"/>',up:'<path d="M5 19 19 5M5 5h14v14"/>'};
const svg=n=>`<svg aria-hidden="true" viewBox="0 0 24 24">${paths[n]||paths.arrow}</svg>`;
document.querySelectorAll('[data-icon]').forEach(el=>el.innerHTML=svg(el.dataset.icon));
const aliases={leather:'Leather',sportswear:'Sportswear',rubber:'Rubber',pup:'Puppy',lycra:'Lycra',diaper:'Diaper',harness:'Harnais',hood:'Masques',denim:'Denim'};
const catalog=window.KINQ_PICTOS.map(k=>({...k,name:aliases[k.id]||k.name}));
const universes=Object.fromEntries(catalog.map(k=>[k.name,k.id]));
const quick=['Leather','Sportswear','Rubber','Puppy','Bondage','Lycra'];
let profiles=window.KINQ_DEMO_PROFILES;
let memberCsrf="";
let memberName="";
let myProfileData={};
// Different gear combinations provide realistic filter fixtures without inventing more members.
const extras={alex:['Harnais','Boots'],tom:['Sneakers','Lycra'],max:['Masques'],leo:['Socks'],noe:['Diaper'],sacha:['Rope / Shibari'],eli:['Collar / leash'],adam:['Boots'],yan:['Neoprene / wetsuit'],milo:['Underwear'],raph:['Harnais'],jules:['Masques']};
const temperaments={alex:'Top',tom:'Versatile',max:'Bottom',leo:'Ça dépend du feeling',noe:'Versatile bottom',sacha:'Power top',eli:'Side (sans pénétration)',adam:'Top',yan:'Bottom',milo:'Je préfère ne pas répondre',raph:'Versatile top',jules:'Versatile'};
profiles.forEach(p=>{p.kinks=[...p.kinks,...(extras[p.id]||[])];p.temperament=temperaments[p.id]});
const pins=new Set(),hooks=new Set();
async function saveSignal(kind,target_id,active){try{const response=await fetch('/api/member/signals',{method:'PUT',credentials:'same-origin',headers:{'Content-Type':'application/json','X-CSRF-Token':memberCsrf},body:JSON.stringify({kind,target_id,active})});if(!response.ok)throw Error();}catch{toast('Impossible d’enregistrer ce choix.');}}
let timer;function toast(t){$('#toast').textContent=t;$('#toast').classList.add('show');clearTimeout(timer);timer=setTimeout(()=>$('#toast').classList.remove('show'),3000)}
const defaults={q:'',universes:[],city:'',min:18,max:80,temperament:'',photo:false,collection:'all'};
const query=new URLSearchParams(location.search);
let state={...defaults,q:query.get('q')||'',universes:(query.get('universes')||query.get('kink')||'').split(',').filter(k=>k in universes),city:['Paris','Lyon','Bordeaux','Lille','Nantes','Marseille'].includes(query.get('city'))?query.get('city'):'',min:Math.max(18,Math.min(80,Number(query.get('min'))||18)),max:Math.max(18,Math.min(80,Number(query.get('max'))||80)),temperament:['Side (sans pénétration)','Bottom','Power bottom','Versatile bottom','Versatile','Versatile top','Top','Power top','Service top','Ça dépend du feeling'].includes(query.get('temperament'))?query.get('temperament'):'',photo:query.get('photo')==='1',collection:['pins','hooks'].includes(query.get('view'))?query.get('view'):'all'};
if(state.min>state.max)[state.min,state.max]=[state.max,state.min];
const normalize=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
const pageSize=12,maxRendered=72;
let lastCriteria='',showMe=false,streamItems=[],streamKey=0,loading=false,loadTimer;
const grid=$('#discovery-grid'),streamLoader=$('#stream-loader'),streamSentinel=$('#stream-sentinel');
function shuffle(items){const list=items.slice();for(let i=list.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[list[i],list[j]]=[list[j],list[i]]}return list}
function nextBatch(visible){const batch=shuffle(visible).slice(0,pageSize);const previous=streamItems.at(-1)?.profile.id;if(batch.length>1&&batch[0].id===previous){const other=batch.findIndex(p=>p.id!==previous);[batch[0],batch[other]]=[batch[other],batch[0]]}return batch.map(profile=>({profile,key:++streamKey}))}
function filter(s){return profiles.filter(p=>(!s.universes.length||s.universes.some(k=>p.kinks.includes(k)))&&(!s.city||p.city===s.city)&&p.age>=s.min&&p.age<=s.max&&(!s.temperament||p.temperament===s.temperament)&&(!s.photo||p.photo)&&(s.collection==='all'||(s.collection==='pins'?pins:hooks).has(p.id))&&normalize(`${p.name} ${p.city} ${p.kinks.join(' ')} ${p.code} ${p.role}`).includes(normalize(s.q.trim())))}
function updateUrl(){const q=new URLSearchParams();Object.entries(state).forEach(([k,v])=>{if(k==='universes'){if(v.length)q.set(k,v.join(','))}else if(v!==defaults[k])q.set(k==='collection'?'view':k,k==='photo'?'1':String(v))});history.replaceState(null,'',location.pathname+(q.size?'?'+q:''))}
function criteria(){return [['city',state.city],['age',state.min!==18||state.max!==80?`${state.min}–${state.max} ans`:''],['temperament',state.temperament],['photo',state.photo?'Avec photo':''],...state.universes.map(k=>['kink:'+k,k])].filter(([,v])=>v)}
const gear=(name)=>universes[name]?`<img src="assets/pictos/${universes[name]}.svg?v=4.4" alt="${name}" title="${name}">`:'';
const mutualDemo=new Set(['alex','sacha','eli']);
function hookStatus(p){return `<span class="dc-hook-status ${mutualDemo.has(p.id)?'is-mutual':''}">${p.id.startsWith('member-')?'Hook envoyé':mutualDemo.has(p.id)?'Réciproque · simulation':'En attente · simulation'}</span>`}
function card(p,key,arrival=-1){return `<article class="discover-card ${p.photo?'':'is-discreet'}${arrival<0?'':' is-arriving'}" data-stream-key="${key}"${arrival<0?'':` style="--arrival-index:${arrival}"`}><button class="dc-open" data-peek="${p.id}" aria-label="Découvrir ${p.name}, ${p.age} ans"><span class="dc-visual">${p.photo?`<img src="${p.photo}" alt="" loading="lazy" decoding="async">`:`<span class="dc-private"><img src="assets/kinq-symbol.svg" alt=""><span>Photo sur demande</span></span>`}</span><span class="dc-top"><span>${p.city}</span><span>${p.role}</span></span><span class="dc-body"><span class="dc-title">${p.name}<small>${p.age}</small></span>${state.collection==='hooks'?hookStatus(p):''}<span class="dc-bottom"><span class="dc-gears">${p.kinks.slice(0,3).map(gear).join('')}</span><span class="dc-reveal">${svg('up')}</span></span></span></button></article>`}
function render(){const visible=filter(state),signature=JSON.stringify(state)+'|'+visible.map(p=>p.id).join(',');if(signature!==lastCriteria){clearTimeout(loadTimer);loading=false;streamLoader.hidden=true;streamItems=(state.collection==='all'?shuffle(visible):visible).slice(0,pageSize).map(profile=>({profile,key:++streamKey}));lastCriteria=signature}
 $('#discover-search').value=state.q;
 document.querySelectorAll('[data-collection]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.collection===(showMe?'me':state.collection))));
 $('#universe-chips').innerHTML=quick.map(k=>`<button data-kink="${k}" aria-label="${k}" aria-pressed="${state.universes.includes(k)}">${gear(k)}<span>${k}</span></button>`).join('');
 $('#active-criteria').replaceChildren(...criteria().map(([key,label])=>{const b=document.createElement('button');b.dataset.remove=key;b.textContent=label;b.insertAdjacentHTML('beforeend',svg('close'));b.setAttribute('aria-label',`Retirer le critère ${label}`);return b}));
 $('#filter-count').textContent=criteria().length;$('#kink-count').textContent=state.universes.length||catalog.length;
 document.querySelectorAll('[data-kink-check]').forEach(c=>c.checked=state.universes.includes(c.value));
 $('#pin-count').textContent=profiles.filter(p=>pins.has(p.id)).length;$('#hook-count').textContent=profiles.filter(p=>hooks.has(p.id)).length;$('#browse-pane').hidden=showMe;$('#my-profile-pane').hidden=!showMe;if(showMe)renderMyProfile();
 $('#collection-title').textContent={all:'Explore.',pins:'Tes Pins.',hooks:'Tes Hooks.'}[state.collection];
 $('#result-count').textContent=`${visible.length} profil${visible.length>1?'s':''}`;$('#hooks-context').hidden=state.collection!=='hooks';
 grid.innerHTML=streamItems.map(({profile,key})=>card(profile,key)).join('');
 streamSentinel.hidden=showMe||state.collection!=='all'||visible.length<6;
 $('#discovery-empty').hidden=visible.length>0;$('#empty-copy').textContent=state.collection==='hooks'?'Les profils auxquels tu as fait un Hook apparaîtront ici.':state.collection==='pins'?'Garde un profil en Pin depuis sa fiche pour le retrouver ici.':'Aucun profil de test pour ces critères. Retire un filtre pour explorer plus largement.';updateUrl();}
function loadNextBatch(){
 if(loading||showMe||state.collection!=='all')return;
 const visible=filter(state);if(visible.length<6)return;
 loading=true;streamLoader.hidden=false;
 const signature=lastCriteria;
 loadTimer=setTimeout(()=>{
  if(signature!==lastCriteria||showMe){loading=false;streamLoader.hidden=true;return}
  const batch=nextBatch(visible);
  grid.insertAdjacentHTML('beforeend',batch.map(({profile,key},i)=>card(profile,key,i%4)).join(''));
  streamItems.push(...batch);
  if(streamItems.length>maxRendered){const columns=getComputedStyle(grid).gridTemplateColumns.split(' ').length,drop=Math.ceil((streamItems.length-maxRendered)/columns)*columns,anchor=grid.children[drop],before=anchor.getBoundingClientRect().top;for(let i=0;i<drop;i++)grid.firstElementChild.remove();streamItems.splice(0,drop);window.scrollBy(0,anchor.getBoundingClientRect().top-before)}
  loading=false;streamLoader.hidden=true;
  if(grid.getBoundingClientRect().height<window.innerHeight+100)requestAnimationFrame(loadNextBatch);
 },520);
}
const streamObserver=new IntersectionObserver(entries=>{if(entries.some(entry=>entry.isIntersecting))loadNextBatch()},{rootMargin:'0px 0px 700px 0px'});
streamObserver.observe(streamSentinel);
function loadOnScroll(){if(!streamSentinel.hidden&&streamSentinel.getBoundingClientRect().top<window.innerHeight+700)loadNextBatch()}
window.addEventListener('scroll',loadOnScroll,{passive:true});
window.addEventListener('wheel',event=>{if(event.deltaY>0)loadOnScroll()},{passive:true});
window.addEventListener('touchmove',loadOnScroll,{passive:true});
const picker=$('#kink-picker');
$('#kink-options').innerHTML=catalog.slice().sort((a,b)=>a.name.localeCompare(b.name,'fr')).map(k=>`<label data-kink-option data-search="${normalize(k.name+' '+k.search)}"><input type="checkbox" data-kink-check aria-label="${k.name}" value="${k.name}">${gear(k.name)}<span>${k.name}</span></label>`).join('');
$('#kink-options').addEventListener('change',e=>{const c=e.target;if(!c.matches('[data-kink-check]'))return;state.universes=c.checked?[...state.universes,c.value]:state.universes.filter(k=>k!==c.value);render()});
$('#kink-search').addEventListener('input',e=>{let n=0;document.querySelectorAll('[data-kink-option]').forEach(el=>{el.hidden=!el.dataset.search.includes(normalize(e.target.value.trim()));if(!el.hidden)n++});$('#kink-empty').hidden=n>0});
function closeKinks(){picker.open=false;picker.querySelector('summary').focus()}
$('#close-kinks').addEventListener('click',closeKinks);$('#done-kinks').addEventListener('click',closeKinks);
$('#clear-kinks').addEventListener('click',()=>{state.universes=[];render()});
picker.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();closeKinks()}});
document.addEventListener('click',e=>{if(picker.open&&!picker.contains(e.target))picker.open=false});
const sheet=$('#discovery-filters'),form=$('#discovery-filter-form'),peek=$('#discovery-profile');
function renderMyProfile(){
 const get=n=>String(myProfileData[n]||'').trim();
 const checked=n=>Boolean(myProfileData[n]);
 const pseudo=get('pseudo'),age=get('age'),city=checked('hideCity')?'':get('city');
 const hasProfile=Boolean(pseudo||age||get('bio')||(myProfileData.style?.length||myProfileData.practice?.length));
 $('#my-profile-name').textContent=hasProfile?`${pseudo||'Ton pseudo'}, ${age||'18+'}${city?' · '+city:''}`:'Ton profil se dessine ici.';
 $('#my-profile-summary').textContent=hasProfile?get('bio')||'Une présentation à écrire dans ton profil.':'Compose ton profil pour voir ce que les autres découvriront.';
 $('#my-profile-visibility').textContent=hasProfile?(checked('invisible')?'Mode invisible · par code ou lien':'Visible dans la recherche'):'Aperçu visiteur';
 $('#my-profile-photo-state').textContent=checked('discreet')||!hasProfile?'Photo sur demande':'Photo publique après validation';
 const kinks=[...new Set([...(myProfileData.style||[]),...(myProfileData.practice||[])])];
 $('#my-profile-kinks').replaceChildren(...kinks.map(k=>{const e=document.createElement('span');e.textContent=k;return e}));
 const details=[get('experience'),get('puppyRole')&&`Puppy : ${get('puppyRole')}`,get('dynamic'),get('exclusivity')&&`Relation : ${get('exclusivity')}`,get('sex')&&`Sexe : ${get('sex')}`,get('gear'),get('sexualPosition')&&`Position : ${get('sexualPosition')}`,get('gearDetail'),...['leatherDetail','rubberDetail','diaperDetail','bondageDetail'].map(get)].filter(Boolean).join(' · ');
 for(const [key,value] of Object.entries({details,wishes:get('wishes'),limits:checked('hideLimits')?'':get('limits')})){
  const block=$(`[data-my-profile-section="${key}"]`);block.hidden=!value;block.querySelector('p').textContent=value;
 }
}
function fillForm(s){['city','min','max','temperament'].forEach(k=>form.elements[k].value=s[k]);form.elements.photo.checked=s.photo;preview()}
function draft(){return {...state,city:form.elements.city.value,min:Number(form.elements.min.value),max:Number(form.elements.max.value),temperament:form.elements.temperament.value,photo:form.elements.photo.checked}}
function preview(){const s=draft();form.elements.max.setCustomValidity(s.min>s.max?'L’âge maximum doit être supérieur ou égal à l’âge minimum.':'');$('#filter-preview').textContent=s.min>s.max?'Vérifie la tranche d’âge.':`${filter(s).length} profil${filter(s).length>1?'s':''} dans cette sélection`}
$('#open-filters').addEventListener('click',()=>{sheet.hidden=!sheet.hidden;$('#open-filters').setAttribute('aria-expanded',String(!sheet.hidden));if(!sheet.hidden)fillForm(state)});
form.addEventListener('input',preview);form.addEventListener('change',preview);
form.addEventListener('submit',e=>{e.preventDefault();if(!form.reportValidity())return;state=draft();render();sheet.hidden=true;$('#open-filters').setAttribute('aria-expanded','false')});
$('#reset-sheet').addEventListener('click',()=>fillForm(defaults));
$('#discover-search').addEventListener('input',e=>{state.q=e.target.value;render()});
$('#clear-discovery').addEventListener('click',()=>{state={...defaults,universes:[]};render()});
let focusAfterPeek=null;
function openProfile(id){const p=profiles.find(p=>p.id===id);peek.innerHTML=`<button data-close-peek aria-label="Fermer le profil">${svg('close')}</button><div class="peek-layout"><div class="peek-visual">${p.photo?`<img src="${p.photo}" alt="Photo de profil validée par KINQ">`:`<div class="peek-private"><img src="assets/kinq-symbol.svg" alt="Symbole KINQ"><span>Photo sur demande</span></div>`}</div><div class="peek-body"><p class="eyebrow">${p.city.toUpperCase()} / ${p.id.startsWith("member-")?"MEMBRE KINQ":"PROFIL FICTIF"}</p><h2>${p.name}, ${p.age}</h2><div class="peek-tags">${p.kinks.map(k=>`<span>${gear(k)}${k}</span>`).join('')}<span>${p.role}</span></div><blockquote>« ${p.quote} »</blockquote><p>${p.bio}</p><h3>À son rythme</h3><p>${p.pace}. Échanger d’abord sur nos envies et nos limites.</p>${p.photo?'':'<p class="peek-disclosure">Photo sur demande dans le futur service. Aucun album privé dans cet aperçu.</p>'}${hooks.has(p.id)?`<p class="peek-hook-status">${p.id.startsWith('member-')?'Hook envoyé':mutualDemo.has(p.id)?'Hook réciproque · simulation':'Hook en attente · simulation'}</p>`:''}<div class="peek-actions"><button data-discover-pin="${p.id}" aria-pressed="${pins.has(p.id)}">${pins.has(p.id)?'Épinglé':'Garder en Pin'}</button><button data-discover-hook="${p.id}" aria-pressed="${hooks.has(p.id)}">${hooks.has(p.id)?'Hook envoyé':'Faire un Hook'}</button></div><p class="demo-note">${p.id.startsWith("member-") ? p.code + " · Profil membre." : p.code + " · Identité et préférences inventées. Aucun membre réel ne sera contacté."}</p></div></div>`;peek.showModal()}
document.querySelector('.space-tabs').addEventListener('click',e=>{const b=e.target.closest('[data-collection]');if(!b)return;showMe=b.dataset.collection==='me';if(!showMe)state.collection=b.dataset.collection;render()});
document.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;
 if(b.dataset.kink){const k=b.dataset.kink;state.universes=state.universes.includes(k)?state.universes.filter(x=>x!==k):[...state.universes,k];render();document.querySelector(`[data-kink="${k}"]`)?.focus()}
 if(b.dataset.remove){const k=b.dataset.remove;if(k.startsWith('kink:'))state.universes=state.universes.filter(x=>x!==k.slice(5));else if(k==='age'){state.min=18;state.max=80}else state[k]=defaults[k];render();$('#open-filters').focus()}
 if(b.dataset.peek){focusAfterPeek=b;openProfile(b.dataset.peek)}
 if(b.hasAttribute('data-close-peek'))peek.close();
 if(b.dataset.discoverPin){const id=b.dataset.discoverPin;pins.has(id)?pins.delete(id):pins.add(id);saveSignal('pin',id,pins.has(id));render();b.setAttribute('aria-pressed',pins.has(id));b.textContent=pins.has(id)?'Épinglé':'Garder en Pin';toast(pins.has(id)?'Profil gardé dans tes Pins.':'Profil retiré de tes Pins.')}
 if(b.dataset.discoverHook){const id=b.dataset.discoverHook;hooks.has(id)?hooks.delete(id):hooks.add(id);saveSignal('hook',id,hooks.has(id));render();b.setAttribute('aria-pressed',hooks.has(id));b.textContent=hooks.has(id)?'Hook envoyé':'Faire un Hook';const note=peek.querySelector('.peek-hook-status');if(note)note.textContent=hooks.has(id)?(mutualDemo.has(id)?'Hook réciproque · simulation':'Hook en attente · simulation'):'';toast(id.startsWith('member-')?'Hook enregistré.':'Démonstration : aucun membre réel n’a été contacté.')}
});
peek.addEventListener('close',()=>{(focusAfterPeek?.isConnected?focusAfterPeek:$('#discover-search')).focus()});
[peek].forEach(d=>d.addEventListener('click',e=>{if(e.target!==d)return;const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close()}));
function syncAccess(){
 document.body.classList.toggle('is-demo-connected',demoConnected);
 $('#encounters-gate').hidden=demoConnected;
 $('#discovery-inner').hidden=!demoConnected;
 memberGreeting.hidden=!demoConnected;
 if(demoConnected)updateMemberGreeting();
 if(demoConnected)render();
}
$('#enter-encounters-demo').addEventListener('click',()=>location.href='/connexion');
$('#leave-encounters-demo').addEventListener('click',async()=>{await fetch('/api/member/auth/logout',{method:'POST',credentials:'same-origin',headers:{'X-CSRF-Token':memberCsrf}});location.href='/connexion'});
window.addEventListener('pageshow',()=>{if(demoConnected)updateMemberGreeting()});
Promise.all([fetch('/api/member/me').then(r=>r.json()),fetch('/api/profiles').then(r=>r.json()),fetch('/api/member/signals').then(r=>r.json()),fetch('/api/member/profile').then(r=>r.json())]).then(([me,items,signals,myProfile])=>{
 memberCsrf=me.csrf;memberName=me.name||'';myProfileData=myProfile.data||{};profiles=items;profiles.forEach(p=>{if(extras[p.id])p.kinks=[...p.kinks,...extras[p.id]];p.temperament=temperaments[p.id]||p.temperament||''});
 pins.clear();hooks.clear();for(const id of signals.pins)pins.add(id);for(const id of signals.hooks)hooks.add(id);
 demoConnected=true;syncAccess();
}).catch(()=>{$('#encounters-gate').hidden=false;toast('Profils momentanément indisponibles.');});
})();
