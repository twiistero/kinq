(() => {
  const input = document.querySelector('#help-search');
  const buttons = [...document.querySelectorAll('[data-help-filter]')];
  const groups = [...document.querySelectorAll('[data-help-category]')];
  const count = document.querySelector('#help-result-count');
  const empty = document.querySelector('#help-empty');
  let active = 'all';

  const normalize = value => value.toLocaleLowerCase('fr').normalize('NFD').replace(/[\u0300-\u036f]/g, '');

  function update() {
    const query = normalize(input.value.trim());
    let total = 0;
    for (const group of groups) {
      const inCategory = active === 'all' || group.dataset.helpCategory === active;
      let visible = 0;
      for (const item of group.querySelectorAll('details')) {
        const match = inCategory && (!query || normalize(item.textContent).includes(query));
        item.hidden = !match;
        if (match) visible++;
      }
      group.hidden = visible === 0;
      total += visible;
    }
    count.textContent = `${total} ${total > 1 ? 'réponses' : 'réponse'}`;
    empty.hidden = total !== 0;
  }

  input.addEventListener('input', update);
  buttons.forEach(button => button.addEventListener('click', () => {
    active = button.dataset.helpFilter;
    buttons.forEach(item => {
      const selected = item === button;
      item.classList.toggle('is-active', selected);
      item.setAttribute('aria-pressed', String(selected));
    });
    update();
  }));

  function revealHash() {
    const id = decodeURIComponent(location.hash.slice(1));
    if (!id) return;
    const target = document.getElementById(id);
    if (!target) return;
    if (target.closest('.help-group')) {
      input.value = '';
      buttons[0].click();
      if (target.tagName === 'DETAILS') {
        target.open = true;
      }
    }
    requestAnimationFrame(() => target.scrollIntoView({ block: 'start' }));
  }

  update();
  revealHash();
  window.addEventListener('hashchange', revealHash);
})();
