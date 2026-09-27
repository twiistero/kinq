(() => {
  'use strict';
  const items = window.KINQ_PICTOS;
  const families = {constraint:'Contrainte',impact:'Impact',sensation:'Sensations',control:'Contrôle',psych:'Psychologie',fetish:'Matières & vêtements',roleplay:'Roleplay',edge:'Edge',body:'Corps',fluids:'Fluides',sensitive:'Pratiques sensibles',combat:'Lutte & combat',corporeal:'Pratiques corporelles'};
  const $ = id => document.getElementById(id);
  const escape = text => String(text).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const norm = text => text.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  const svg = (item, size) => `<svg class="picto" viewBox="${item.viewBox || '0 0 96 96'}" aria-hidden="true"${size ? ` width="${size}" height="${size}"` : ''}>${item.body}</svg>`;
  const arrow = '<svg class="corner" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 19 19 5M5 5h14v14"/></svg>';
  let selected;
  try { selected = new Set(JSON.parse(localStorage.getItem('kinq-picto-selection-v1') || '[]').filter(id => items.some(item => item.id === id))); }
  catch { selected = new Set(); }
  let theme = 'black', onlySelected = false, active = null, visible = [], returnFocusId = null;
  let notificationTimeout;
  const featureIds = ['wrestling','feet','shibari','restraints','doll','belly','harness','sounding','fisting'];
  const featureTitles = ['Wrestling','Feet','Rope / Shibari','Menottes','Dollification','Dad bod','Harnais','Sounding','Fisting'];
  $('feature-strip').innerHTML = featureIds.map((id,i) => {
    const item = items.find(x => x.id === id);
    return `<button class="feature-card theme-black" data-open="${id}" aria-label="Examiner ${featureTitles[i]}">${svg(item)}<h3>${featureTitles[i]}</h3></button>`;
  }).join('');
  Object.entries(families).forEach(([value,name]) => {
    const option = document.createElement('option'); option.value = value;
    option.textContent = `${name} (${items.filter(i => i.category === value && i.source === 'v11').length})`;
    $('family').append(option);
  });
  function comparison() {
    const item = items.find(i => i.id === $('compare-select').value);
    $('before-art').innerHTML = svg(window.KINQ_PICTOS_V3.find(i => i.id === item.id));
    $('after-art').innerHTML = svg(item);
    $('after-caption').textContent = item.cue;
  }
  function render() {
    const query = norm($('search').value.trim());
    visible = items.filter(i => ($('family').value === 'all' || i.category === $('family').value) && (!onlySelected || selected.has(i.id)) && norm(`${i.name} ${i.search} ${i.cue} ${families[i.category]}`).includes(query));
    $('picto-grid').className = `picto-grid theme-${theme}`;
    $('picto-grid').innerHTML = visible.map(i => `<button class="picto-card" data-open="${i.id}" aria-label="Examiner ${escape(i.name)}${selected.has(i.id) ? ', retenu' : ''}"><span class="card-top"><span>${escape(families[i.category])}</span><span>${i.source === 'home' ? '+' : String(items.indexOf(i)+1).padStart(2,'0')}</span></span>${selected.has(i.id) ? '<svg class="chosen" viewBox="0 0 24 24" aria-hidden="true"><path d="m4 12 5 5L20 6"/></svg>' : ''}<span class="art">${svg(i)}</span><h3>${escape(i.name)}</h3></button>`).join('');
    $('empty').hidden = visible.length > 0;
    const referenceCount = visible.filter(i => i.source === 'v11').length;
    $('result-count').textContent = `${referenceCount} / 74 pictos${visible.some(i => i.source === 'home') ? ' + le harnais' : ''}`;
    $('selection-count').textContent = selected.size;
    $('selection-toggle').setAttribute('aria-pressed', onlySelected);
  }
  function detail() {
    const i = active;
    $('detail-art').className = `detail-art theme-${theme}`;
    $('detail-art').innerHTML = svg(i);
    $('detail-family').textContent = families[i.category];
    $('detail-title').textContent = i.name;
    $('detail-cue').textContent = i.cue;
    $('detail-reference').hidden = !i.reference;
    if (i.reference) $('detail-reference').href = i.reference; else $('detail-reference').removeAttribute('href');
    $('detail-sizes').innerHTML = [24,32,48,80].map(n => `<div>${svg(i,n)}<span>${n} px</span></div>`).join('');
    $('pick').textContent = selected.has(i.id) ? 'Retirer de ma sélection' : 'Retenir ce picto';
    $('pick').setAttribute('aria-pressed', selected.has(i.id));
    const idx = visible.findIndex(x => x.id === i.id);
    $('detail-index').textContent = idx >= 0 ? `${idx+1} / ${visible.length}` : 'Hors filtre';
    $('previous').disabled = idx <= 0;
    $('next').disabled = idx < 0 || idx >= visible.length-1;
  }
  function open(id) {
    active = items.find(i => i.id === id);
    if (!active) return;
    returnFocusId = id;
    detail(); $('inspector').showModal();
  }
  document.addEventListener('click', event => {
    const card = event.target.closest('[data-open]');
    if (card) open(card.dataset.open);
  });
  $('inspector').querySelector('.close').addEventListener('click', () => $('inspector').close());
  $('inspector').addEventListener('click', event => { if (event.target === $('inspector')) { const r = event.target.getBoundingClientRect(); if (event.clientX<r.left || event.clientX>r.right || event.clientY<r.top || event.clientY>r.bottom) event.target.close(); } });
  $('inspector').addEventListener('close', () => {
    const card = document.querySelector(`#picto-grid [data-open="${returnFocusId}"]`) || document.querySelector(`[data-open="${returnFocusId}"]`);
    if (card) card.focus({preventScroll:true}); else $('selection-toggle').focus({preventScroll:true});
  });
  $('previous').addEventListener('click', () => {const idx=visible.indexOf(active);if(idx>0){active=visible[idx-1];returnFocusId=active.id;detail();}});
  $('next').addEventListener('click', () => {const idx=visible.indexOf(active);if(idx>=0&&idx<visible.length-1){active=visible[idx+1];returnFocusId=active.id;detail();}});
  $('pick').addEventListener('click', () => {
    if (selected.has(active.id)) selected.delete(active.id); else selected.add(active.id);
    try {localStorage.setItem('kinq-picto-selection-v1',JSON.stringify([...selected]));} catch {notify('Sélection conservée pour cette page uniquement.');}
    render(); detail();
  });
  function notify(text) { $('status').textContent=text; $('status').classList.add('visible');clearTimeout(notificationTimeout);notificationTimeout=setTimeout(()=>$('status').classList.remove('visible'),2500); }
  $('download').addEventListener('click', () => {
    const tokens = {gray:['#111310','#b2ff1a','#dfe2dc','#858c7f'],acid:['#111310','#656c5e','#b2ff1a','#dfe2dc'],black:['#b2ff1a','#b2ff1a','#111310','#858c7f']}[theme];
    let body = active.body;
    ['ink','accent','cut','muted'].forEach((key,i) => { body = body.replaceAll(`var(--${key})`,tokens[i]); });
    const doc = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${active.viewBox || '0 0 96 96'}" role="img" aria-label="${escape(active.name)}"><title>${escape(active.name)}</title>${body}</svg>`;
    const url=URL.createObjectURL(new Blob([doc],{type:'image/svg+xml'}));
    const a=document.createElement('a');a.href=url;a.download=`kinq-${active.id}-${theme}.svg`;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
    notify('SVG préparé pour le téléchargement.');
  });
  $('search').addEventListener('input', render);
  $('family').addEventListener('change', render);
  $('compare-select').addEventListener('change', comparison);
  $('selection-toggle').addEventListener('click', () => {onlySelected=!onlySelected;render();});
  $('reset-filters').addEventListener('click', () => {$('search').value='';$('family').value='all';onlySelected=false;render();});
  $('size').addEventListener('change', () => {$('picto-grid').style.setProperty('--picto-size',`${$('size').value}px`);});
  document.querySelectorAll('[data-theme]').forEach(button => button.addEventListener('click', () => {
    theme=button.dataset.theme;
    document.querySelectorAll('[data-theme]').forEach(b=>b.setAttribute('aria-pressed',b===button));
    render();
  }));
  comparison();render();
})();
