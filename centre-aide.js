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

  // Animate the native disclosure without losing its keyboard and screen-reader behavior.
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  document.querySelectorAll('.help-questions details').forEach(details => {
    const summary = details.querySelector('summary');
    const answer = details.querySelector('.help-answer');
    let frame;
    let timer;
    summary.addEventListener('click', event => {
      if (reducedMotion.matches) {
        delete details.dataset.helpExpanded;
        return;
      }
      event.preventDefault();
      const expanded = details.dataset.helpExpanded === 'true' || (details.dataset.helpExpanded === undefined && details.open);
      const next = !expanded;
      const start = details.getBoundingClientRect().height;
      clearTimeout(frame);
      clearTimeout(timer);
      details.classList.remove('is-animating');
      details.style.height = `${start}px`;
      details.open = true;
      details.dataset.helpExpanded = String(next);
      details.style.overflow = 'hidden';
      answer.style.opacity = next ? '0' : '1';
      answer.style.transform = next ? 'translateY(-6px)' : 'translateY(0)';
      const end = next ? details.scrollHeight + 2 : summary.offsetHeight + 2;
      frame = setTimeout(() => {
        details.classList.add('is-animating');
        details.style.height = `${end}px`;
        answer.style.opacity = next ? '1' : '0';
        answer.style.transform = next ? 'translateY(0)' : 'translateY(-6px)';
      }, 20);
      timer = setTimeout(() => {
        details.open = next;
        details.classList.remove('is-animating');
        details.style.height = '';
        details.style.overflow = '';
        answer.style.opacity = '';
        answer.style.transform = '';
      }, 380);
    });
  });

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
        target.dataset.helpExpanded = 'true';
      }
    }
    requestAnimationFrame(() => target.scrollIntoView({ block: 'start' }));
  }

  update();
  revealHash();
  window.addEventListener('hashchange', revealHash);
})();
