const form = document.querySelector('#my-profile-form');
const preview = document.querySelector('#profile-preview');
const text = (value, fallback = '') => String(value || '').trim() || fallback;
const picker = document.querySelector('#kink-picker');
const featured = document.querySelector('#featured-kinks');
const featuredNames = ['Leather', 'Rubber / Latex', 'Sportswear', 'Pup play', 'ABDL / Diaper fetish', 'Bondage'];
const categories = {constraint:'Bondage & contraintes',sensation:'Sensations',control:'Contrôle',ass:'Ass play',impact:'Impact',body:'Corps',psych:'Dynamique mentale',fluids:'Fluides',edge:'Pratiques avancées',sensitive:'Pratiques sensibles'};
try {
  const items = JSON.parse(document.querySelector('#kink-taxonomy').textContent);

  const groups = [{title:'Styles & matières', items:items.filter(item => item.field === 'style')}, {title:'Univers & imaginaires',items:items.filter(item => item.category === 'roleplay')}, ...Object.entries(categories).map(([key,title]) => ({title,items:items.filter(item => item.category === key)}))];
  for (const group of groups) {
    if (group.title === 'Ass play') {const order = ['Sodomie','Toys / plugs','Fisting','Enema play']; group.items.sort((a,b) => order.indexOf(a.name)-order.indexOf(b.name));}
    const details = document.createElement('details'); details.className = 'my-profile-kink-group';
    const summary = document.createElement('summary'); summary.innerHTML = `<span>${group.title}</span><small>${group.items.length} idée${group.items.length > 1 ? 's' : ''}</small>`; details.append(summary);
    const choices = document.createElement('div'); choices.className = 'my-profile-choices';
    for (const item of group.items) {
      const label = document.createElement('label'); const input = document.createElement('input'); const span = document.createElement('span');
      input.type = 'checkbox'; input.name = item.field; input.value = item.name; span.textContent = item.label; label.dataset.search = window.kinqPreferences.normalize([item.name,item.label,item.search,...item.variants.map(v => v.label)].join(' '));
      if (item.icon && /^[a-z0-9-]+$/.test(item.icon)) { const image = document.createElement('img'); image.src = `assets/pictos/${item.icon}.svg`; image.alt = ''; image.loading = 'lazy'; label.append(image); }
      label.append(input,span); choices.append(label);
      if (featuredNames.includes(item.name)) { const feature = label.cloneNode(true); feature.classList.add('my-profile-feature'); feature.querySelector('input').dataset.featured = item.name; feature.querySelector('input').removeAttribute('name'); featured.append(feature); }
    }
    details.append(choices); picker.append(details);
  }
  document.querySelector('#kink-search').addEventListener('input', event => {
    const q = window.kinqPreferences.normalize(event.target.value.trim()); let matches = 0;
    const cataloguePanel = document.querySelector('#kink-catalogue');
    if (q && !cataloguePanel.dataset.searching) {cataloguePanel.dataset.wasOpen=String(cataloguePanel.open);cataloguePanel.dataset.searching='true';}
    if (q) cataloguePanel.open = true;
    else if (cataloguePanel.dataset.searching) {cataloguePanel.open=cataloguePanel.dataset.wasOpen==='true';delete cataloguePanel.dataset.searching;}
    for (const group of picker.querySelectorAll('details')) {
      let shown = 0;
      if (q && !group.dataset.searching) {group.dataset.wasOpen = String(group.open); group.dataset.searching = 'true';}
      for (const label of group.querySelectorAll('label')) {label.hidden = Boolean(q) && !label.dataset.search.includes(q); if (!label.hidden) shown++;}
      matches += shown; group.hidden = Boolean(q) && !shown;
      if (q && shown) group.open = true;
      if (!q && group.dataset.searching) {group.open = group.dataset.wasOpen === 'true'; delete group.dataset.searching;}
    }
    document.querySelector('#kink-search-status').textContent = q ? (matches ? `${matches} univers trouvé${matches > 1 ? 's' : ''}` : 'Pas encore de résultat. Essaie un synonyme en français ou en anglais.') : '';
  });
  updatePreview();
} catch {picker.textContent = 'Catalogue indisponible. Réessaie dans un instant.';}
function updatePreview() {
  window.kinqPreferences.sync();
  for (const input of featured.querySelectorAll('input')) input.checked = [...picker.querySelectorAll('input:checked')].some(original => original.value === input.value);
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
  preview.querySelector('.my-profile-photo-state').textContent = data.has('discreet') ? 'Album privé · sur demande' : 'Photo publique après validation';
  preview.querySelector('.my-profile-state').innerHTML = `<svg aria-hidden="true"><use href="#${data.has('invisible') ? 'lock' : 'search'}"/></svg> ${data.has('invisible') ? 'Mode invisible · par code ou lien' : 'Visible dans la recherche'}`;
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
form.addEventListener('input', event => {if (event.target.id === 'kink-search' || event.target.dataset.mix) return; if (event.target.dataset.featured) {const original = [...picker.querySelectorAll('input')].find(input => input.value === event.target.value); if (original) original.checked = event.target.checked;} if (event.target.id === 'relation-code') updateRelationLookup(); markProfileDirty(); updatePreview();});
form.addEventListener('change', event => {
  if (event.target.dataset.mix) return;
  if (event.target.dataset.featured) {const original = [...picker.querySelectorAll('input')].find(input => input.value === event.target.value); if (original) original.checked = event.target.checked;}
  else if (event.target.matches('#kink-picker input')) {const twin = [...featured.querySelectorAll('input')].find(input => input.value === event.target.value); if (twin) twin.checked = event.target.checked;}
  updateRelationLookup();
  markProfileDirty();
  updatePreview();
});
form.addEventListener('reset', () => requestAnimationFrame(() => { window.kinqPreferences.reset(); document.querySelector('#kink-search').dispatchEvent(new Event('input')); featured.querySelectorAll('input').forEach(input => input.checked = false); markProfileDirty(); updateRelationLookup(); updatePreview(); window.kinqSaveProfile?.(); }));
document.querySelector('#preview-profile').addEventListener('click', () => {updatePreview();preview.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth',block:'start'});});
updatePreview();

const validateProfile = document.querySelector('#validate-profile');
function markProfileDirty() {
  validateProfile.classList.remove('is-validated');
  validateProfile.querySelector('span').textContent = 'Valider mon profil';
}
validateProfile.addEventListener('click', () => {
  if (!form.reportValidity()) return;
  updatePreview();
  window.kinqSaveProfile?.();
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
  if (next?.id !== relationMatch?.id || !next) {form.elements.relationConfirm.checked = false; relationStatus.textContent = 'Les liens entre membres se gèrent dans l’app Kinq.';}
  relationMatch = next || null;
  relationConfirm.hidden = !next;
  relationSend.disabled = !next || !form.elements.relationConfirm.checked || !form.elements.relation.value;
  relationResult.hidden = !code;
  relationResult.replaceChildren();
  const symbol = document.createElementNS('http://www.w3.org/2000/svg','svg'); symbol.setAttribute('aria-hidden','true');
  const use = document.createElementNS('http://www.w3.org/2000/svg','use'); use.setAttribute('href', next ? '#check' : '#code'); symbol.append(use); relationResult.append(symbol);
  const message = document.createElement('span');
  if (next) {message.textContent = `${next.name}, ${next.age} · ${next.city} · profil fictif trouvé`; const link = document.createElement('a'); link.href = `/profil?id=${encodeURIComponent(next.id)}`; link.textContent = 'Voir son profil'; message.append(' · ',link);}
  else message.textContent = 'Aucun profil fictif pour ce code.';
  relationResult.append(message);
}
relationSend.addEventListener('click', () => {if (!relationSend.disabled) relationStatus.textContent = `Demande prête pour ${relationMatch.name}. L’envoi et sa réponse Oui/Non nécessitent de vrais comptes.`;});
updateRelationLookup();

// Progress follows the reader through the profile editor, independent of form answers.
const progressBar = document.querySelector('.my-profile-progress');
const progressTitle = document.querySelector('#profile-progress');
const progressFill = progressBar.querySelector('span');
const progressEditor = document.querySelector('.my-profile-editor');
let progressMessage = '';
let progressAnimation;
let progressRevision = 0;
let progressFrame = 0;
function updateProfileProgress() {
  const top = progressEditor.getBoundingClientRect().top + window.scrollY;
  const bottom = progressEditor.getBoundingClientRect().bottom + window.scrollY;
  const finish = bottom - window.innerHeight * .6;
  const amount = Math.min(1, Math.max(0, (window.scrollY - top) / Math.max(1, finish - top)));
  const messages = ['Pose les bases', 'Complète tes infos', 'Ton profil prend forme', "C'est bien, continue", 'On y est presque !', 'Encore un peu...', "Oh oui c'est parfait !"];
  const index = amount === 1 ? 6 : Math.floor(amount * 6);
  const message = messages[index];
  progressFill.style.width = `${Math.round(amount * 100)}%`;
  if (message === progressMessage) return;
  const firstUpdate = !progressMessage;
  progressMessage = message;
  const revision = ++progressRevision;
  progressAnimation?.cancel();
  if (firstUpdate || matchMedia('(prefers-reduced-motion: reduce)').matches) {
    progressTitle.textContent = message;
    return;
  }
  progressAnimation = progressTitle.animate([{opacity:1,transform:'translateY(0)'},{opacity:0,transform:'translateY(-4px)'}], {duration:130,easing:'ease-in',fill:'forwards'});
  progressAnimation.finished.then(() => {
    if (revision !== progressRevision) return;
    progressTitle.textContent = message;
    progressAnimation.cancel();
    progressAnimation = progressTitle.animate([{opacity:0,transform:'translateY(4px)'},{opacity:1,transform:'translateY(0)'}], {duration:220,easing:'ease-out'});
  }).catch(() => {});
}
function scheduleProfileProgress() {
  if (progressFrame) return;
  progressFrame = requestAnimationFrame(() => {
    progressFrame = 0;
    updateProfileProgress();
  });
}
addEventListener('scroll', scheduleProfileProgress, {passive:true});
addEventListener('resize', scheduleProfileProgress);
updateProfileProgress();
