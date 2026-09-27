const icon = name => `<svg aria-hidden="true"><use href="#${name}"/></svg>`;
const people = [
 {id:'alex',name:'Alex',age:32,city:'Paris',kink:'Leather',tags:'Leather · Dom · Connexion régulière',photo:"https://static.wixstatic.com/media/739d69_8f8ce9ef74c34d25803f679a3f8127e4~mv2.jpg/v1/fill/w_480%2Ch_720%2Cal_c%2Cq_80%2Cusm_0.66_1.00_0.01%2Cenc_avif%2Cquality_auto/739d69_8f8ce9ef74c34d25803f679a3f8127e4~mv2.jpg",code:'KQ-7M4X9P',bio:'Le cuir, les échanges francs et les rencontres qui prennent leur temps. Curieux de découvrir la personne derrière le profil.'},
 {id:'tom',name:'Tom',age:28,city:'Lyon',kink:'Sportswear',tags:'Sportswear · Switch · Curieux',photo:"https://mr-riegillio.com/cdn/shop/articles/sylven-meets-rj-585763.jpg?v=1607874225&width=1200",code:'KQ-8N2R6T',bio:'Du sport, du feeling et de la curiosité. Partant pour faire connaissance autour d’un verre, sans pression.'},
 {id:'max',name:'Max',age:35,city:'Bordeaux',kink:'Rubber',tags:'Rubber · Gear · Play partner',photo:"https://www.invinciblerubber.com/image/cache/catalog/SU056_h-840x840.jpg",code:'KQ-3W9F5A',bio:'Passionné de gear. J’aime discuter des envies et des limites avant de se rencontrer. Le feeling passe avant tout.'},
 {id:'leo',name:'Léo',age:30,city:'Paris',kink:'Sportswear',tags:'Street · Nylon · À découvrir',photo:"https://www.scallychav.co.uk/cdn/shop/files/FDCA6A7D-D889-4DFA-AD34-30F6174243C3.jpg?v=1778270620&width=1445",code:'KQ-6B2D8H',bio:'Ici pour explorer, échanger et rencontrer des mecs bien dans leurs baskets. Rien à prouver, tout à découvrir.'}
];
const hooks=new Set(),pins=new Set();
const params=new URLSearchParams(location.search);let currentFilter=['Leather','Sportswear','Rubber'].includes(params.get('kink'))?params.get('kink'):'Tous',currentView=['pins','hooks'].includes(params.get('view'))?params.get('view'):'all',searchText='',cityFilter='',toastTimer;
function syncFilters(){document.querySelectorAll('[data-filter]').forEach(x=>{x.classList.toggle('active',x.dataset.filter===currentFilter);x.setAttribute('aria-pressed',String(x.dataset.filter===currentFilter))});document.querySelectorAll('[data-view]').forEach(x=>{x.classList.toggle('active',x.dataset.view===currentView);x.setAttribute('aria-pressed',String(x.dataset.view===currentView))})}

function toast(text){const el=document.querySelector('#toast');el.textContent=text;el.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.classList.remove('show'),3200)}
function render(){const grid=document.querySelector('#profiles');if(!grid)return;const visible=people.filter(p=>(currentFilter==='Tous'||p.kink===currentFilter)&&(currentView==='all'||(currentView==='pins'?pins:hooks).has(p.id))&&(!cityFilter||p.city===cityFilter)&&(`${p.name} ${p.city} ${p.code}`.toLocaleLowerCase('fr').includes(searchText)));document.querySelectorAll('.empty').forEach(e=>e.hidden=visible.length>0);grid.innerHTML=visible.map(p=>`<article class="profile"><div class="profile-photo" data-person="${p.id}"><img src="${p.photo}" alt="Photo d’illustration du profil fictif ${p.name}" loading="lazy"><button class="profile-open" aria-label="Voir le profil de ${p.name}" data-profile="${p.id}"></button><button class="pin-button" aria-label="${pins.has(p.id)?'Retirer des Pins':'Ajouter aux Pins'} ${p.name}" aria-pressed="${pins.has(p.id)}" data-pin="${p.id}">${icon('pin')}</button><span class="profile-city">${p.city}</span></div><div class="profile-heading"><h3>${p.name}<span>, ${p.age}</span></h3><button class="hook-button" aria-label="${hooks.has(p.id)?'Retirer le Hook envoyé à':'Envoyer un Hook à'} ${p.name}" aria-pressed="${hooks.has(p.id)}" data-hook="${p.id}">${icon('hook')}${hooks.has(p.id)?'Envoyé':'Hook'}</button></div><div class="tags">${p.tags}</div></article>`).join('')}
const dialog=document.querySelector('#dialog');const menu=document.querySelector('#mega-menu');
menu.addEventListener('close',()=>document.querySelector('.menu-toggle').setAttribute('aria-expanded','false'));
let menuClosing=null;
function openMenu(){if(menu.open)return;menu.showModal();document.querySelector('.menu-toggle').setAttribute('aria-expanded','true');menu.animate([{transform:'translateX(-100%)'},{transform:'translateX(0)'}],{duration:matchMedia('(prefers-reduced-motion: reduce)').matches?0:420,easing:'cubic-bezier(.22,1,.36,1)'});}
function closeMenu(){if(!menu.open)return Promise.resolve();if(menuClosing)return menuClosing;menuClosing=menu.animate([{transform:'translateX(0)'},{transform:'translateX(-100%)'}],{duration:matchMedia('(prefers-reduced-motion: reduce)').matches?0:320,easing:'cubic-bezier(.64,0,.78,0)',fill:'forwards'}).finished.catch(()=>{}).then(()=>{menu.close();menu.getAnimations().forEach(a=>a.cancel());menuClosing=null;});return menuClosing;}
menu.addEventListener('cancel',e=>{e.preventDefault();closeMenu()});
menu.addEventListener('click',async e=>{if(e.target===menu){closeMenu();return;}const a=e.target.closest('a');if(a){e.preventDefault();await closeMenu();location.href=a.href;}});

function modal(html){document.querySelector('#dialog-content').innerHTML=html;if(!dialog.open)dialog.showModal()}
const content={
 download:`<p class="eyebrow">KINQ / L’APP</p><h2>Ton univers.<br>Dans ta poche.</h2><p>L’app Kinq est en préparation. Le téléchargement sur iOS et Android sera disponible au lancement.</p><p>Tu peux déjà explorer le concept sur ce site.</p><button class="button" data-explore>Découvrir Kinq ${icon('arrow')}</button>`,
 coming:`<p class="eyebrow">APERÇU DU CONCEPT</p><h2>Hors ligne.<br>En préparation.</h2><p>Cette page présente la future rubrique. Les exemples sont fictifs : aucun événement, lieu ou réservation réelle n’est proposé ici.</p>`,
 message:`<p class="eyebrow">CONVERSATION / DÉMONSTRATION</p><h2>Un premier mot.</h2><p>La messagerie sera connectée à de vrais comptes dans le produit final. Aucun message ne peut être envoyé aux personnes photographiées dans cet aperçu.</p>`,
 album:`<p class="eyebrow">ALBUM PRIVÉ</p><h2>C’est toi<br>qui choisis.</h2><p>Dans le produit final, le membre pourra accepter ou refuser l’accès et le retirer à tout moment. Cet album de démonstration ne contient aucune photo privée.</p>`,

 join:`<p class="eyebrow">BIENVENUE DANS LE CONCEPT KINQ</p><h2>Le début<br>d’une connexion.</h2><p>Tu explores la première maquette de Kinq. Les inscriptions ne sont pas encore ouvertes et aucun compte n’est créé ici.</p><p>En attendant, découvre les profils fictifs et essaie le Hook ou les Pins.</p><button class="button" data-explore>Explorer l’aperçu ${icon('arrow')}</button>`,
 login:`<p class="eyebrow">KINQ / CONNEXION</p><h2>On se retrouve<br>bientôt.</h2><p>La connexion sera disponible avec le lancement du service. Cette version est un prototype interactif, sans compte ni données personnelles.</p><button class="button" data-explore>Voir les profils de démonstration ${icon('arrow')}</button>`,
 trust:`<p class="eyebrow">NOTRE APPROCHE</p><h2>Libre d’être toi.<br>Libre de dire non.</h2><p>Kinq est pensé pour les hommes adultes : chacun choisit ce qu’il partage, ses envies et ses limites. Un Hook ou un kink en commun n’est jamais un consentement.</p><p>La visibilité choisie est déjà disponible dans le profil. Les albums privés, le blocage et le signalement restent en préparation.</p><p>Le produit prévoit une connexion par code aléatoire, aucune revente de données personnelles et un affichage choisi par le membre. Une équipe de modération active doit accompagner les débutants comme les membres expérimentés.</p><p>Les comptes et la modération des photos sont actifs. Les autres protections indiquées ci-dessus sont en préparation.</p>`
};
const articles={start:['PREMIERS PAS','La curiosité suffit.','Tu n’as pas besoin de te définir dès le premier jour. Être attiré par une matière, une tenue ou une dynamique ne t’oblige à rien.','Commence par les mots qui te parlent. Tu peux dire « je suis curieux » et poser des questions sans promettre une rencontre ou une pratique.','Prends le temps de discuter. Tes envies peuvent évoluer, et tu peux changer d’avis à tout moment.'],limits:['ENTRE NOUS','Des limites claires.<br>Du feeling en plus.','Parler de ce qui te plaît et de ce que tu ne souhaites pas permet de mieux se comprendre. Cette discussion peut commencer simplement : « Ça me tente, mais j’aimerais qu’on en parle avant. »','Distingue ce qui te fait envie, ce qui reste à discuter et ce que tu ne veux pas. Tu n’as pas à justifier un refus.','Une préférence affichée sur un profil ne vaut pas accord. Le consentement se construit dans l’échange et peut être retiré à tout moment.'],words:['LE LEXIQUE','Des mots.<br>Pas des cases.','Dom et sub décrivent des rôles dans une dynamique de domination et de soumission consentie. Switch désigne quelqu’un qui peut apprécier différents rôles selon le contexte.','Ces mots ne définissent ni toute une personnalité, ni automatiquement une position sexuelle. Chacun peut leur donner une place différente.','Le plus simple reste de demander à l’autre ce que ces mots signifient pour lui. Et tu peux tout à fait explorer sans choisir d’étiquette.']};
Object.assign(articles,{
 privacy:['VIE PRIVÉE','Ton profil.<br>Tes règles.','Tu n’as pas besoin de tout montrer pour créer une connexion. Choisis les photos et les informations que tu souhaites partager, selon ton niveau de confort.','Prends le temps de découvrir la personne avant de communiquer tes coordonnées ou des images privées. Une demande n’est jamais une obligation.','Ton choix peut changer. Pouvoir retirer un accès, bloquer un contact ou signaler un comportement fait partie des protections prévues pour Kinq.'],
 meet:['RENCONTRES','Du message<br>au premier rendez-vous.','Un échange qui te plaît peut donner envie de se rencontrer. Parle de tes attentes : un verre, une discussion, découvrir un univers. Rien de plus n’est implicite.','Pour un premier rendez-vous, choisis un cadre où tu te sens à l’aise et garde la liberté de partir. Tu peux prévenir une personne de confiance de ton programme.','Le feeling se découvre aussi en vrai. Tu peux ralentir, poser une question, changer de projet ou dire non, même si les messages étaient enthousiastes.'],
 after:['ENTRE NOUS','Et après ?<br>On en parle aussi.','L’aftercare, c’est l’attention portée à chacun après un moment partagé. Cela peut être une discussion, du calme, de la proximité ou un peu d’espace.','Parlez de vos préférences en amont. N’imagine pas que l’autre souhaite la même chose que toi : demande-lui, écoute sa réponse et respecte son choix.','Un message plus tard peut permettre de partager son ressenti, si vous en avez tous les deux envie. Il n’existe pas de rituel unique ni d’obligation de proximité.']
});
document.addEventListener('click',async e=>{const b=e.target.closest('button');if(!b)return;
 if(b.dataset.modal==='join'||b.dataset.modal==='login'){if(menu.open)await closeMenu();location.href=b.dataset.modal==='join'?'/inscription':'/connexion';return;}
 if(b.dataset.modal){if(menu.open)await closeMenu();modal(content[b.dataset.modal]);}
 if(b.matches('.dialog-close'))dialog.close();
 if(b.hasAttribute('data-explore')){dialog.close();location.href='/rencontres'}
 if(b.dataset.filter){currentFilter=b.dataset.filter;document.querySelectorAll('[data-filter]').forEach(x=>{x.classList.toggle('active',x.dataset.filter===currentFilter);x.setAttribute('aria-pressed',x.dataset.filter===currentFilter)});render()}
 if(b.dataset.universe)location.href='/rencontres'+(b.dataset.universe==='Tous'?'':'?kink='+encodeURIComponent(b.dataset.universe));
 if(b.dataset.pin||b.dataset.hook)location.href='/connexion';
 if(b.dataset.profile)location.href='/profil?id='+encodeURIComponent(b.dataset.profile);
 if(b.dataset.copy){try{await navigator.clipboard.writeText(b.dataset.copy);toast('Code de démonstration copié.')}catch{toast('Copie le code affiché dans le profil.')}}
 if(b.dataset.article){const a=articles[b.dataset.article];modal(`<p class="eyebrow">${a[0]} / NO TABOO</p><h2>${a[1]}</h2>${a.slice(2).map(t=>`<p>${t}</p>`).join('')}<p class="demo-note">Texte de présentation du concept éditorial.</p>`)}
 if(b.matches('.menu-toggle'))openMenu();
 if(b.matches('.menu-close'))await closeMenu();
 if(b.dataset.view){currentView=b.dataset.view;syncFilters();render()}
 if(b.matches('.filter-toggle')){const filters=document.querySelector('#extra-filters');filters.hidden=!filters.hidden;b.setAttribute('aria-expanded',String(!filters.hidden))}
 if(b.hasAttribute('data-reset')){currentFilter='Tous';currentView='all';searchText='';cityFilter='';document.querySelector('#profile-search').value='';document.querySelector('#city-filter').value='';syncFilters();render()}

});
dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close()}});render();

document.querySelector('#profile-search')?.addEventListener('input',e=>{searchText=e.target.value.trim().toLocaleLowerCase('fr');render()});
document.querySelector('#city-filter')?.addEventListener('change',e=>{cityFilter=e.target.value;render()});
if(document.querySelector('.lex-terms')){const input=document.querySelector('#term-search'),items=[...document.querySelectorAll('.lex-terms [data-term]')],filters=[...document.querySelectorAll('[data-lex-filter]')];let category='all';const normalize=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr');function update(){const q=normalize(input.value.trim());let shown=0;items.forEach(item=>{item.hidden=(category!=='all'&&item.dataset.category!==category)||!normalize(item.textContent+' '+item.dataset.term).includes(q);if(!item.hidden)shown++});document.querySelector('#term-empty').hidden=shown>0;document.querySelector('#term-count').textContent=shown+' '+(shown===1?'mot':'mots');}input.addEventListener('input',update);filters.forEach(button=>button.addEventListener('click',()=>{category=button.dataset.lexFilter;filters.forEach(filter=>{const active=filter===button;filter.classList.toggle('active',active);filter.setAttribute('aria-pressed',String(active))});update()}));update()}
const detail=document.querySelector('#profile-detail');

syncFilters();

// Homepage motion: never blocks navigation, pauses offscreen and honors reduced motion.
const reduceMotion=matchMedia('(prefers-reduced-motion: reduce)');
const heroSlides=[...document.querySelectorAll('.hero-slide')];
if(heroSlides.length){
 let currentSlide=0,heroVisible=true,transitionTimer;
 heroSlides.forEach(slide=>{slide.loading='eager'});
 function chooseSlide(){
  const next=Array.from({length:heroSlides.length-1},(_,offset)=>(currentSlide+offset+1)%heroSlides.length).find(index=>heroSlides[index].complete&&heroSlides[index].naturalWidth);
  if(next===undefined)return;
  const previous=heroSlides[currentSlide],incoming=heroSlides[next];
  clearTimeout(transitionTimer);
  heroSlides.forEach(slide=>slide.classList.remove('is-leaving','is-entering'));
  previous.classList.add('is-leaving');
  previous.classList.remove('is-active');
  incoming.classList.add('is-active','is-entering');
  previous.setAttribute('aria-hidden','true');
  incoming.setAttribute('aria-hidden','false');
  currentSlide=next;
  transitionTimer=setTimeout(()=>{previous.classList.remove('is-leaving');incoming.classList.remove('is-entering')},1900);
 }
 new IntersectionObserver(entries=>{heroVisible=entries[0].isIntersecting}).observe(document.querySelector('.hero-art'));
 setInterval(()=>{if(!reduceMotion.matches&&heroVisible&&!document.hidden)chooseSlide()},6500);
}
function renderWall(background,photos,columns=5){
 background.innerHTML=Array.from({length:columns},(_,col)=>{const group=Array.from({length:3},(_,row)=>{const i=(col*2+row)%photos.length;return `<div class="wall-portrait"><img src="${photos[i]}" alt="" loading="lazy"><div class="wall-card-icons">${icon('hook')}${icon('pin')}</div></div>`}).join('');return `<div class="wall-column"><div class="wall-track"><div class="wall-group">${group}</div><div class="wall-group">${group}</div></div></div>`}).join('');
}
const wall=document.querySelector('.people-wall');
if(wall){
 const pup='https://armyofmen.com/cdn/shop/files/head-harness-pup-scout-blue-model-front.jpg?v=1757678289&width=1200';
 const sportDuo='https://mr-riegillio.com/cdn/shop/files/MR_R62699_copy.jpg?v=1770812952&width=1600';
 const wallPhotos=[...people.map(p=>p.photo),pup,sportDuo];
 renderWall(document.querySelector('#wall-background'),wallPhotos);
 const pause=document.querySelector('#wall-pause');let wallPaused=reduceMotion.matches;
 function syncWallPause(){wall.classList.toggle('is-paused',wallPaused);pause.setAttribute('aria-pressed',String(wallPaused));pause.setAttribute('aria-label',wallPaused?'Reprendre la tapisserie':'Mettre la tapisserie en pause');pause.innerHTML=icon(wallPaused?'play':'pause')}
 pause.addEventListener('click',()=>{wallPaused=!wallPaused;syncWallPause()});
 reduceMotion.addEventListener('change',e=>{if(e.matches){wallPaused=true;syncWallPause()}});
 new IntersectionObserver(entries=>wall.classList.toggle('is-offscreen',!entries[0].isIntersecting)).observe(wall);
 document.addEventListener('visibilitychange',()=>wall.classList.toggle('is-tab-hidden',document.hidden));
 syncWallPause();
}
const journalWall=document.querySelector('.nt-end-tapestry');
if(journalWall){
 const journalPhotos=[...people.map(p=>p.photo),'https://armyofmen.com/cdn/shop/files/head-harness-pup-scout-blue-model-front.jpg?v=1757678289&width=1200','https://mr-riegillio.com/cdn/shop/files/MR_R62699_copy.jpg?v=1770812952&width=1600'];
 renderWall(journalWall.querySelector('.wall-background'),journalPhotos,3);
 const syncJournalMotion=()=>journalWall.classList.toggle('is-paused',reduceMotion.matches);
 reduceMotion.addEventListener('change',syncJournalMotion);
 new IntersectionObserver(entries=>journalWall.classList.toggle('is-offscreen',!entries[0].isIntersecting)).observe(journalWall);
 document.addEventListener('visibilitychange',()=>journalWall.classList.toggle('is-tab-hidden',document.hidden));
 syncJournalMotion();
}

// Measure actual text lines so underlines stop at letters, exclude icons,
// and travel through wrapped titles in reading order.
function prepareTextLinks(){
 const plain='.underlink,.text-button,footer button,footer a:not(.logo),.desktop-nav a,.mega-bottom a,.mega-bottom button,.mega-shortcuts a,.profile-code button';
 document.querySelectorAll(plain).forEach(link=>{
  if(link.hasAttribute('data-ink-link'))return;
  link.setAttribute('data-ink-link','');
  [...link.childNodes].filter(n=>n.nodeType===Node.TEXT_NODE&&n.textContent.trim()).forEach(node=>{
   const label=document.createElement('span');label.className='ink-label';label.textContent=node.textContent.trim();node.replaceWith(label);
  });
 });
 document.querySelectorAll('.article,.mega-links>a,.relation-link').forEach(link=>{
  link.setAttribute('data-ink-link','');
  const label=link.querySelector('.link-label')||link.querySelector(':scope > span')?.querySelector('strong')||link.querySelector(':scope > span');
  if(label)label.classList.add('ink-label');
 });
}
function drawTextUnderline(label){
 label.querySelectorAll('.ink-line').forEach(line=>line.remove());
 const base=label.getBoundingClientRect();if(!base.width||!base.height)return;
 const lines=[];const walker=document.createTreeWalker(label,NodeFilter.SHOW_TEXT);
 while(walker.nextNode()){
  const node=walker.currentNode;
  for(let i=0;i<node.length;i++){
   if(/\s/.test(node.textContent[i]))continue;
   const range=document.createRange();range.setStart(node,i);range.setEnd(node,i+1);
   const r=range.getBoundingClientRect();if(!r.width)continue;
   let line=lines.find(l=>Math.abs(l.bottom-r.bottom)<3);
   if(!line){line={left:r.left,right:r.right,bottom:r.bottom};lines.push(line)}
   else{line.left=Math.min(line.left,r.left);line.right=Math.max(line.right,r.right)}
  }
 }
 lines.sort((a,b)=>a.bottom-b.bottom);const total=lines.reduce((n,l)=>n+l.right-l.left,0);let travelled=0;
 lines.forEach(l=>{
  const width=l.right-l.left,stroke=document.createElement('span');stroke.className='ink-line';stroke.setAttribute('aria-hidden','true');
  const journalOffset=label.closest('.nt-title-link')?-4:1;
  stroke.style.cssText=`left:${l.left-base.left}px;top:${l.bottom-base.top+journalOffset}px;width:${width}px;--duration:${width/total*210}ms;--start:${travelled/total*210}ms;--return:${(total-travelled-width)/total*210}ms`;
  label.append(stroke);travelled+=width;
 });
}
prepareTextLinks();
const underlineObserver=new ResizeObserver(entries=>entries.forEach(entry=>drawTextUnderline(entry.target)));
document.querySelectorAll('.ink-label').forEach(label=>underlineObserver.observe(label));
document.fonts.ready.then(()=>document.querySelectorAll('.ink-label').forEach(drawTextUnderline));
const ticker=document.querySelector('.ticker-track');
if(ticker){new IntersectionObserver(entries=>ticker.style.animationPlayState=entries[0].isIntersecting?'':'paused').observe(ticker);document.addEventListener('visibilitychange',()=>ticker.style.animationPlayState=document.hidden?'paused':'')}

// The logo star moves briefly on hover and at quiet, regular intervals.
const brandLinks=[...document.querySelectorAll('a.logo')];
function spinBrand(link){
 if(reduceMotion.matches||document.hidden)return;
 const star=link.querySelector('.brand-mark svg');if(!star)return;
 const transform=getComputedStyle(star).transform;
 const matrix=new DOMMatrixReadOnly(transform==='none'?undefined:transform);
 const angle=Math.atan2(matrix.b,matrix.a)*180/Math.PI;
 star.getAnimations().forEach(animation=>animation.cancel());
 star.animate([{transform:`rotate(${angle}deg)`},{transform:'rotate(360deg)'}],{duration:2000,easing:'cubic-bezier(.45,0,.2,1)'});
}
brandLinks.forEach(link=>{
 link.addEventListener('pointerenter',()=>spinBrand(link));
 link.addEventListener('focus',()=>spinBrand(link));
});
setInterval(()=>brandLinks.forEach(link=>{
 const box=link.getBoundingClientRect();
 if(box.width&&box.bottom>0&&box.top<innerHeight&&(!menu.open||menu.contains(link)))spinBrand(link);
}),16000);
reduceMotion.addEventListener('change',()=>{
 if(reduceMotion.matches)brandLinks.forEach(link=>link.querySelector('.brand-mark svg')?.getAnimations().forEach(animation=>animation.cancel()));
});

// Manual gear ribbon: mouse drag, native touch/trackpad scrolling and arrows.
const gearViewport=document.querySelector('.gear-viewport');
if(gearViewport){
 const group=gearViewport.querySelector('.gear-group');
 const arrows=[...document.querySelectorAll('[data-gear-direction]')];
 let drag=null,suppressClickUntil=0;
 function syncGearArrows(){const max=gearViewport.scrollWidth-gearViewport.clientWidth;arrows.forEach(b=>b.disabled=Number(b.dataset.gearDirection)<0?gearViewport.scrollLeft<=1:gearViewport.scrollLeft>=max-1)}
 arrows.forEach(b=>b.addEventListener('click',()=>{const distance=group.querySelector('.gear-card').getBoundingClientRect().width+parseFloat(getComputedStyle(group).gap);gearViewport.scrollBy({left:Number(b.dataset.gearDirection)*distance,behavior:reduceMotion.matches?'instant':'smooth'})}));
 gearViewport.addEventListener('pointerdown',e=>{if(e.pointerType!=='mouse'||e.button!==0)return;drag={id:e.pointerId,x:e.clientX,left:gearViewport.scrollLeft,moved:false};});
 gearViewport.addEventListener('pointermove',e=>{if(!drag||drag.id!==e.pointerId)return;const dx=e.clientX-drag.x;if(!drag.moved&&Math.abs(dx)<6)return;if(!drag.moved){drag.moved=true;gearViewport.setPointerCapture(e.pointerId);gearViewport.classList.add('is-dragging')}e.preventDefault();gearViewport.scrollLeft=drag.left-dx;});
 function finishDrag(e){if(!drag||drag.id!==e.pointerId)return;if(drag.moved){suppressClickUntil=performance.now()+300;if(gearViewport.hasPointerCapture(e.pointerId))gearViewport.releasePointerCapture(e.pointerId)}drag=null;gearViewport.classList.remove('is-dragging')}
 gearViewport.addEventListener('pointerup',finishDrag);gearViewport.addEventListener('pointercancel',finishDrag);
 gearViewport.addEventListener('pointerleave',e=>{if(drag&&!drag.moved)finishDrag(e)});
 gearViewport.addEventListener('click',e=>{if(performance.now()<suppressClickUntil){e.preventDefault();e.stopImmediatePropagation()}},true);
 gearViewport.addEventListener('wheel',e=>{if(e.ctrlKey||Math.abs(e.deltaX)>Math.abs(e.deltaY))return;const delta=e.deltaY*(e.deltaMode===1?16:e.deltaMode===2?gearViewport.clientWidth:1),max=gearViewport.scrollWidth-gearViewport.clientWidth;if((delta>0&&gearViewport.scrollLeft<max-1)||(delta<0&&gearViewport.scrollLeft>1)){e.preventDefault();gearViewport.scrollLeft+=delta}},{passive:false});
 gearViewport.addEventListener('scroll',syncGearArrows,{passive:true});new ResizeObserver(syncGearArrows).observe(gearViewport);syncGearArrows();
}
const gearDescriptions={Leather:'L’uniforme cuir, les détails, l’attitude. Un univers à partager à ta façon.',Sportswear:'Sneakers, chaussettes et tracksuits. Tes codes sportifs, tes rencontres.',Rubber:'La combinaison latex, la matière et les reflets. Explore ta seconde peau.',Puppy:'Masques, accessoires et codes puppy. Suis ta curiosité, dans le respect des envies de chacun.',Bondage:'Chaînes, liens et accessoires. La confiance et les limites se discutent toujours à deux.',Lycra:'Lutte, singlets et tenues près du corps. Un univers de matières et de silhouettes.',Diaper:'Un univers autour des couches pour adultes. Tes préférences ont leur place, sans jugement.',Harnais:'Du cuir, des sangles et des anneaux. Trouve les mecs qui partagent tes codes.',Boots:'Bottes, rangers et détails affirmés. À chacun son allure.',Masques:'Cagoules et masques. Une autre façon d’explorer ton univers.'};
document.addEventListener('click',e=>{const button=e.target.closest('[data-gear]');if(!button)return;const name=button.dataset.gear;if(!gearDescriptions[name])return;modal(`<p class="eyebrow">TON TERRAIN DE JEU</p><h2>${name}</h2><p>${gearDescriptions[name]}</p><button class="button" data-modal="join">Créer mon compte ${icon('up')}</button>`)});
document.querySelectorAll('.lex-card').forEach(card=>card.addEventListener('click',()=>{const open=card.getAttribute('aria-pressed')!=='true';card.setAttribute('aria-pressed',String(open));const word=card.querySelector('.lex-card-front strong').textContent;card.setAttribute('aria-label',(open?'Masquer':'Voir')+' la définition de '+word)}));
