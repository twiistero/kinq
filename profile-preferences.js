(() => {
  const form = document.querySelector('#my-profile-form');
  const catalogue = JSON.parse(document.querySelector('#kink-taxonomy').textContent);
  const byId = new Map(catalogue.map(item => [item.id, item]));
  const host = document.querySelector('#kink-preferences');
  const preferences = new Map();
  let combinations = [];
  // Keep previously saved free text for compatibility without exposing a new input.
  let legacyCustom = '';
  const cards = new Map();
  const normalize = value => String(value).normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const el = (tag, text, className) => { const node = document.createElement(tag); if (text) node.textContent = text; if (className) node.className = className; return node; };
  const button = (text, action) => { const node = el('button', text); node.type = 'button'; node.addEventListener('click', action); return node; };
  const selected = () => catalogue.filter(item => [...form.querySelectorAll('#kink-picker input:checked')].some(input => input.value === item.name));
  const notify = () => form.dispatchEvent(new Event('input', {bubbles: true}));
  host.append(el('p', 'TU PEUX PRÉCISER ?', 'eyebrow'));
  const empty = el('p', 'Choisis un univers ci-dessus pour retrouver ici ses nuances.', 'kp-empty'); host.append(empty);
  const list = el('div', '', 'kp-cards'); host.append(list);
  const sourceNote = el('p', 'Besoin de décoder un mot ? ', 'my-profile-hint');
  const lexicon = el('a', 'Ouvre le lexique KINQ'); lexicon.href='/lexique'; lexicon.target='_blank'; lexicon.rel='noopener'; sourceNote.append(lexicon, ' dans un nouvel onglet.');host.append(sourceNote);

  function choiceGroup(title, options, item, key) {
    const fieldset = el('fieldset', '', 'kp-options'); fieldset.append(el('legend', title));
    const laterLabel = el('label', '', 'kp-later');
    const later = el('input'); later.type = 'checkbox'; later.name = `kp-${item.id}-later`;
    later.checked = !preferences.get(item.id)[key];
    laterLabel.append(later, el('span', 'Je répondrai plus tard')); fieldset.append(laterLabel);
    later.addEventListener('change', () => {
      if (later.checked) {
        preferences.get(item.id)[key] = '';
        fieldset.querySelectorAll('input[type=radio]').forEach(input => {input.checked = false;});
      }
      updateSummary(item); notify();
    });
    for (const option of options) {
      const label = el('label'); const input = el('input'); input.type = 'radio';
      input.name = `kp-${item.id}-${key}`; input.value = option.id;
      input.checked = preferences.get(item.id)[key] === option.id;
      input.addEventListener('change', () => {
        preferences.get(item.id)[key] = option.id; later.checked = false;
        updateSummary(item); notify();
      });
      label.append(input,el('span',option.label)); fieldset.append(label);
    }
    return fieldset;
  }
  function updateSummary(item) {
    const value = preferences.get(item.id); const card = cards.get(item.id); if (!card) return;
    const summary = [item.roles.find(option => option.id === value.role)?.label].filter(Boolean);
    card.querySelector('.kp-summary').textContent = summary.join(' · ') || 'Je répondrai plus tard';
  }
  function createCard(item) {
    if (!preferences.has(item.id)) preferences.set(item.id, {interest:'',role:'',experience:'',variants:[]});
    const card = el('details', '', 'kp-card'); card.dataset.kinkId = item.id;
    const summary = el('summary'); summary.append(el('strong', item.label),el('small','','kp-summary')); card.append(summary);
    if (item.help) card.append(el('p',item.help,'kp-help'));
    card.append(choiceGroup('Ta façon de le vivre', item.roles, item, 'role'));
    card.append(button('Retirer cet univers', () => {
      const input = [...form.querySelectorAll('#kink-picker input')].find(input => input.value === item.name);
      input.checked = false; input.dispatchEvent(new Event('change',{bubbles:true}));
      const focusTarget = [...document.querySelectorAll('#featured-kinks input')].find(input => input.value === item.name);
      if (focusTarget) focusTarget.focus(); else {input.closest('details').open=true; input.focus();}
    }));
    cards.set(item.id,card); updateSummary(item); return card;
  }
  function sync() {
    const items = selected(); const ids = new Set(items.map(item => item.id));
    for (const [id,card] of cards) if (!ids.has(id)) {card.remove();cards.delete(id);preferences.delete(id);}
    for (const item of items) if (!cards.has(item.id)) list.append(createCard(item));
    empty.hidden = items.length > 0;
    // Retain old stored combinations only while all their universes remain selected.
    combinations = combinations.filter(mix => mix.every(id => ids.has(id)));
  }
  function restore(data) {
    preferences.clear();cards.clear();list.replaceChildren();
    const saved = data.kinkPreferences;
    if (saved?.version === 1) {
      for (const value of saved.items || []) if (byId.has(value.id)) preferences.set(value.id, {interest:value.interest || '',role:value.role || '',experience:value.experience || '',variants:value.variants || []});
      combinations = (saved.combinations || []).map(mix => [...mix].sort()); legacyCustom = saved.custom || '';
    } else {
      combinations=[];legacyCustom='';
      // Preserve explicit legacy answers, without inferring a per-kink role from general preferences.
      const bondage = {'Attacher':'tie','Être attaché':'tied','Les deux':'both'}[data.bondageDetail];
      if (bondage) preferences.set('bondage',{interest:'',role:bondage,experience:'',variants:[]});
      const pup = {Pup:'pup',Handler:'handler'}[data.puppyRole];
      if (pup) preferences.set('pup-play',{interest:'',role:pup,experience:'',variants:[]});
      const legacy = ['leatherDetail','rubberDetail','diaperDetail'].filter(key=>data[key]).map(key=>`${{leatherDetail:'Cuir',rubberDetail:'Latex',diaperDetail:'Diaper'}[key]} : ${data[key]}`);
      if (data.puppyRole && !pup) legacy.push(`Pup : ${data.puppyRole}`);
      legacyCustom=legacy.join(' · ').slice(0,300);
    }
    sync();
  }
  for (const select of form.querySelectorAll('select')) {
    const wrap = el('span', '', 'kp-select-wrap');
    select.before(wrap); wrap.append(select);
    const svg = document.createElementNS('http://www.w3.org/2000/svg','svg');
    svg.setAttribute('viewBox','0 0 24 24'); svg.setAttribute('aria-hidden','true');
    const path = document.createElementNS('http://www.w3.org/2000/svg','path'); path.setAttribute('d','m6 9 6 6 6-6');
    svg.append(path);wrap.append(svg);
  }
  window.kinqPreferences = {
    catalogue, normalize, sync, restore,
    getData: () => ({version:1, items:selected().map(item => ({id:item.id,...preferences.get(item.id)})), combinations, custom:legacyCustom}),
    reset: () => {preferences.clear();combinations=[];legacyCustom='';cards.clear();list.replaceChildren();sync();}
  };
})();
