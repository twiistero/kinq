const form = document.querySelector('#my-profile-form');
const preview = document.querySelector('#profile-preview');
const text = (value, fallback = '') => String(value || '').trim() || fallback;
const picker = document.querySelector('#kink-picker');
const featured = document.querySelector('#featured-kinks');
const featuredNames = ['Leather', 'Rubber / Latex', 'Sportswear', 'Pup play', 'ABDL / Diaper fetish', 'Bondage'];
const styleNames = ['Leather', 'Rubber / Latex', 'Sportswear', 'Uniform / Workwear', 'Boots', 'Sneakers', 'Socks', 'Underwear', 'Masks / Hoods', 'Neoprene / wetsuit', 'Lycra / spandex'];
const categories = {constraint:'Bondage & contraintes',impact:'Impact',sensation:'Sensations',control:'Contrôle',psych:'Dynamique mentale',edge:'Pratiques avancées',body:'Corps',fluids:'Fluides',sensitive:'Pratiques sensibles',combat:'Corps à corps',corporeal:'Pratiques corporelles'};
try {
  const items = JSON.parse(document.querySelector('#kink-taxonomy').textContent);
  items.push({name:'Domination / soumission',category:'psych',id:'discipline'});
  const groups = [{title:'Styles & matières', items:items.filter(item => styleNames.includes(item.name))}, {title:'Univers & imaginaires',items:items.filter(item => item.category === 'roleplay')}, {title:'Autres attirances',items:items.filter(item => item.category === 'fetish' && !styleNames.includes(item.name))}, ...Object.entries(categories).map(([key,title]) => ({title,items:items.filter(item => item.category === key)}))];
  for (const group of groups) {
    const details = document.createElement('details'); details.className = 'my-profile-kink-group';
    const summary = document.createElement('summary'); summary.innerHTML = `<span>${group.title}</span><small>${group.items.length} idées</small>`; details.append(summary);
    const choices = document.createElement('div'); choices.className = 'my-profile-choices';
    for (const item of group.items) {
      const label = document.createElement('label'); const input = document.createElement('input'); const span = document.createElement('span');
      input.type = 'checkbox'; input.name = group.title === 'Styles & matières' ? 'style' : 'practice'; input.value = item.name; span.textContent = item.name;
      if (item.id && /^[a-z0-9-]+$/.test(item.id)) { const image = document.createElement('img'); image.src = `assets/pictos/${item.id}.svg`; image.alt = ''; image.loading = 'lazy'; label.append(image); }
      label.append(input,span); choices.append(label);
      if (featuredNames.includes(item.name)) { const feature = label.cloneNode(true); feature.classList.add('my-profile-feature'); feature.querySelector('input').dataset.featured = item.name; feature.querySelector('input').removeAttribute('name'); featured.append(feature); }
    }
    details.append(choices); picker.append(details);
  }
  document.querySelector('#kink-search').addEventListener('input', event => { const q = event.target.value.trim().toLocaleLowerCase('fr'); for (const group of picker.querySelectorAll('details')) { let shown = 0; for (const label of group.querySelectorAll('label')) { label.hidden = Boolean(q) && !label.textContent.toLocaleLowerCase('fr').includes(q); if (!label.hidden) shown++; } group.hidden = Boolean(q) && !shown; if (q && shown) group.open = true; } });
  updatePreview();
} catch {picker.textContent = 'Catalogue indisponible dans cet aperçu.';}
function updatePreview() {
  const selected = [...form.querySelectorAll('#kink-picker input:checked')].map(el => el.value);
  const hasPuppy = selected.includes('Pup play');
  const hasBdsm = selected.includes('Domination / soumission');
  const contexts = {puppy:hasPuppy,bdsm:hasBdsm,leather:selected.includes('Leather'),rubber:selected.includes('Rubber / Latex'),diaper:selected.includes('ABDL / Diaper fetish'),bondage:selected.includes('Bondage')};
  for (const [kind, active] of Object.entries(contexts)) {
    for (const label of form.querySelectorAll(`[data-if="${kind}"]`)) { label.hidden = !active; label.querySelectorAll('select,input').forEach(el => {el.disabled = !active; if (!active) el.value = '';}); }
    for (const option of form.querySelectorAll(`[data-relation="${kind}"]`)) { option.hidden = !active; option.disabled = !active; }
  }
  const relation = form.elements.relation; if (relation.selectedOptions[0]?.disabled || relation.selectedOptions[0]?.closest('optgroup')?.disabled) relation.value = '';
  document.querySelector('#kink-count').textContent = selected.length ? `${selected.length} univers choisi${selected.length>1?'s':''}` : 'Aucun univers choisi pour l’instant';
  const data = new FormData(form);
  const pseudo = text(data.get('pseudo'), 'Ton pseudo');
  const age = Number(data.get('age'));
  const city = !data.has('hideCity') ? text(data.get('city')) : '';
  preview.querySelector('h2').textContent = `${pseudo}, ${age >= 18 && age <= 99 ? age : '18+'}${city ? ` · ${city}` : ''}`;
  preview.querySelector('.my-profile-avatar').classList.toggle('is-discreet',data.has('discreet'));
  preview.querySelector('.my-profile-photo-state').textContent = data.has('discreet') ? 'Album privé · sur demande' : 'Photo publique possible · plus tard';
  preview.querySelector('.my-profile-state').innerHTML = `<svg aria-hidden="true"><use href="#${data.has('invisible') ? 'lock' : 'search'}"/></svg> ${data.has('invisible') ? 'Mode invisible · par code ou lien' : 'Visible dans la recherche (simulation)'}`;
  preview.querySelector('.my-profile-bio').textContent = text(data.get('bio'));
  const tags = preview.querySelector('.my-profile-tags');
  tags.replaceChildren(...[...data.getAll('style'), ...data.getAll('practice')].map(kink => {const chip = document.createElement('span'); chip.textContent = kink; return chip;}));
  const details = [data.get('experience'),data.get('puppyRole') && `Puppy : ${data.get('puppyRole')}`,data.get('dynamic'),data.get('exclusivity') && `Relation : ${data.get('exclusivity')}`,data.get('sex') && `Sexe : ${data.get('sex')}`,data.get('gear'),data.get('sexualPosition') && `Position : ${data.get('sexualPosition')}`,data.get('gearDetail'),...['leatherDetail','rubberDetail','diaperDetail','bondageDetail'].map(key => data.get(key))].filter(Boolean).join(' · ');
  for (const key of ['details', 'wishes', 'limits']) {
    const block = preview.querySelector(`[data-section="${key}"]`);
    const value = key === 'details' ? details : key === 'limits' && data.has('hideLimits') ? '' : text(data.get(key));
    block.hidden = !value; block.querySelector('p').textContent = value;
  }
  const filled = ['pseudo','age','city','bio','wishes','limits','experience','puppyRole','dynamic','sex','gear','sexualPosition','gearDetail'].some(key => text(data.get(key))) || data.getAll('style').length || data.getAll('practice').length;
  preview.querySelector('.my-profile-empty').hidden = Boolean(filled);
  preview.querySelector('.my-profile-public').hidden = !filled;
}
form.addEventListener('input', event => {if (event.target.id === 'relation-code') updateRelationLookup(); markProfileDirty(); updatePreview();});
form.addEventListener('change', event => {
  if (event.target.dataset.featured) {const original = [...picker.querySelectorAll('input')].find(input => input.value === event.target.value); if (original) original.checked = event.target.checked;}
  else if (event.target.matches('#kink-picker input')) {const twin = [...featured.querySelectorAll('input')].find(input => input.value === event.target.value); if (twin) twin.checked = event.target.checked;}
  updateRelationLookup();
  markProfileDirty();
  updatePreview();
});
form.addEventListener('reset', () => requestAnimationFrame(() => { try { sessionStorage.removeItem('kinq-demo-my-profile'); } catch {} featured.querySelectorAll('input').forEach(input => input.checked = false); markProfileDirty(); updateRelationLookup(); updatePreview(); }));
document.querySelector('#preview-profile').addEventListener('click', () => {updatePreview();preview.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth',block:'start'});});
try { const saved = JSON.parse(sessionStorage.getItem('kinq-demo-my-profile') || 'null'); if (Array.isArray(saved)) [...form.querySelectorAll('input,select,textarea')].forEach((el, i) => { const item = saved[i]; if (!item || item.name !== el.name || el.type === 'file') return; if (el.type === 'checkbox' || el.type === 'radio') el.checked = item.checked; else el.value = item.value; }); } catch {}
updatePreview();

const validateProfile = document.querySelector('#validate-profile');
function markProfileDirty() {
  validateProfile.classList.remove('is-validated');
  validateProfile.querySelector('span').textContent = 'Valider mon profil';
}
validateProfile.addEventListener('click', () => {
  validateProfile.classList.add('is-validated');
  validateProfile.querySelector('span').textContent = 'Profil modifié !';
  updatePreview();
  try { sessionStorage.setItem('kinq-demo-my-profile', JSON.stringify([...form.querySelectorAll('input,select,textarea')].map(el => ({name:el.name, value:el.type === 'file' ? '' : el.value, checked:el.checked})))); } catch {}
});

// Local lookup illustrates the request flow with the four existing fictional profiles.
const relationCode = document.querySelector('#relation-code');
const relationResult = document.querySelector('#relation-result');
const relationConfirm = document.querySelector('#relation-confirm-wrap');
const relationSend = document.querySelector('#relation-send');
const relationStatus = document.querySelector('#relation-status');
let relationMatch = null;
function updateRelationLookup() {
  const code = relationCode.value.trim().toUpperCase();
  const next = code ? people.find(person => person.code.toUpperCase() === code) : null;
  if (next?.id !== relationMatch?.id || !next) {form.elements.relationConfirm.checked = false; relationStatus.textContent = 'Aucune demande réelle n’est envoyée dans cette maquette. La réponse Oui/Non sera ajoutée avec les comptes.';}
  relationMatch = next || null;
  relationConfirm.hidden = !next;
  relationSend.disabled = !next || !form.elements.relationConfirm.checked || !form.elements.relation.value;
  relationResult.hidden = !code;
  relationResult.replaceChildren();
  const symbol = document.createElementNS('http://www.w3.org/2000/svg','svg'); symbol.setAttribute('aria-hidden','true');
  const use = document.createElementNS('http://www.w3.org/2000/svg','use'); use.setAttribute('href', next ? '#check' : '#code'); symbol.append(use); relationResult.append(symbol);
  const message = document.createElement('span');
  if (next) {message.textContent = `${next.name}, ${next.age} · ${next.city} · profil fictif trouvé`; const link = document.createElement('a'); link.href = `profil.html?id=${encodeURIComponent(next.id)}`; link.textContent = 'Voir son profil'; message.append(' · ',link);}
  else message.textContent = 'Aucun profil fictif pour ce code.';
  relationResult.append(message);
}
relationSend.addEventListener('click', () => {if (!relationSend.disabled) relationStatus.textContent = `Demande prête pour ${relationMatch.name}. L’envoi et sa réponse Oui/Non nécessitent de vrais comptes.`;});
updateRelationLookup();

// Progress reflects reading position, regardless of how many fields are filled.
const progressBar = document.querySelector('.my-profile-progress');
const editor = document.querySelector('.my-profile-editor');
function updateScrollProgress() {
  const start = editor.getBoundingClientRect().top + window.scrollY;
  const end = editor.getBoundingClientRect().bottom + window.scrollY - window.innerHeight * .55;
  const amount = Math.min(1, Math.max(0, (window.scrollY - start) / Math.max(1, end - start)));
  progressBar.querySelector('span').style.width = `${Math.round(amount * 100)}%`;
  document.querySelector('#profile-progress').textContent = amount >= .98 ? 'Ton profil, à ta façon.' : 'Ton profil prend forme.';
}
addEventListener('scroll', updateScrollProgress, {passive:true});
addEventListener('resize', updateScrollProgress);
updateScrollProgress();
