(() => {
  const cards = [...document.querySelectorAll('.event-card')];
  const records = cards.map(card => ({
    card,
    start: card.dataset.start.slice(0, 10),
    end: card.dataset.end.slice(0, 10),
    scope: card.dataset.scope,
    name: card.dataset.name,
    city: card.dataset.city
  }));
  const filterButtons = [...document.querySelectorAll('[data-event-filter]')];
  const empty = document.querySelector('#events-empty');
  const grid = document.querySelector('#events-calendar-grid');
  const monthLabel = document.querySelector('#events-month-label');
  const daySelection = document.querySelector('#events-day-selection');
  const clearDay = document.querySelector('#events-clear-day');
  const previousMonth = document.querySelector('.events-month-prev');
  const nextMonth = document.querySelector('.events-month-next');
  const now = new Date();
  const dateKey = date => `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
  const today = dateKey(now);
  const firstUpcoming = records.find(record => record.end >= today);
  const initialMonth = firstUpcoming && firstUpcoming.start.slice(0, 7) > today.slice(0, 7)
    ? firstUpcoming.start.slice(0, 7) : today.slice(0, 7);
  let [year, monthIndex] = initialMonth.split('-').map(Number);
  let month = new Date(year, monthIndex - 1, 1);
  let filter = 'all';
  let selectedDay = null;

  const dateLabel = date => new Intl.DateTimeFormat('fr-FR', { dateStyle: 'full' }).format(date);
  const matching = record => record.end >= today && (filter === 'all' || record.scope === filter);
  const onDay = (record, day) => record.start <= day && record.end >= day;

  function renderCalendar() {
    const year = month.getFullYear();
    const index = month.getMonth();
    monthLabel.textContent = new Intl.DateTimeFormat('fr-FR', { month: 'long', year: 'numeric' }).format(month);
    previousMonth.disabled = dateKey(month).slice(0, 7) <= today.slice(0, 7);
    grid.replaceChildren();
    const offset = (new Date(year, index, 1).getDay() + 6) % 7;
    for (let i = 0; i < offset; i += 1) {
      const spacer = document.createElement('span');
      spacer.setAttribute('aria-hidden', 'true');
      grid.append(spacer);
    }
    const days = new Date(year, index + 1, 0).getDate();
    for (let day = 1; day <= days; day += 1) {
      const date = new Date(year, index, day);
      const key = dateKey(date);
      const count = records.filter(record => matching(record) && onDay(record, key)).length;
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = String(day);
      button.className = 'events-calendar-day';
      button.classList.toggle('has-events', count > 0);
      button.classList.toggle('selected', key === selectedDay);
      button.setAttribute('aria-pressed', String(key === selectedDay));
      button.setAttribute('aria-label', `${dateLabel(date)} · ${count} ${count === 1 ? 'événement' : 'événements'}`);
      button.disabled = key < today;
      button.addEventListener('click', () => {
        selectedDay = selectedDay === key ? null : key;
        update();
        document.querySelector('#events-list').scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
      grid.append(button);
    }
  }

  function update() {
    let count = 0;
    for (const record of records) {
      const visible = matching(record) && (!selectedDay || onDay(record, selectedDay));
      record.card.hidden = !visible;
      if (visible) count += 1;
    }
    if (selectedDay) {
      const [year, month, day] = selectedDay.split('-').map(Number);
      daySelection.textContent = `${dateLabel(new Date(year, month - 1, day))} · ${count} ${count === 1 ? 'event' : 'events'}`;
      empty.textContent = 'Aucun event annoncé ce jour-là pour cette sélection. Choisis une autre date ou affiche tous les events.';
    } else {
      daySelection.textContent = 'Tous les événements à venir';
      empty.textContent = 'Aucun événement annoncé pour cette sélection. Reviens bientôt : l’agenda évolue avec les annonces des organisateurs.';
    }
    clearDay.hidden = !selectedDay;
    empty.hidden = count !== 0;
    renderCalendar();
  }

  filterButtons.forEach(button => button.addEventListener('click', () => {
    filter = button.dataset.eventFilter;
    filterButtons.forEach(item => {
      const active = item === button;
      item.classList.toggle('active', active);
      item.setAttribute('aria-pressed', String(active));
    });
    update();
  }));
  previousMonth.addEventListener('click', () => { month = new Date(month.getFullYear(), month.getMonth() - 1, 1); update(); });
  nextMonth.addEventListener('click', () => { month = new Date(month.getFullYear(), month.getMonth() + 1, 1); update(); });
  clearDay.addEventListener('click', () => { selectedDay = null; update(); });
  update();

  const proposalDialog = document.querySelector('#event-proposal-dialog');
  const proposalForm = document.querySelector('#event-proposal-form');
  const proposalStatus = document.querySelector('#event-proposal-status');
  const proposalSuccess = document.querySelector('#event-proposal-success');
  const nameKey = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim().toLowerCase().replace(/\s+/g, ' ');
  document.querySelector('#open-event-proposal').addEventListener('click', () => {
    proposalStatus.textContent = '';
    proposalForm.hidden = false;
    proposalSuccess.hidden = true;
    proposalForm.elements.date.min = today;
    proposalDialog.showModal();
    proposalForm.elements.name.focus();
  });
  proposalDialog.querySelector('.events-proposal-close').addEventListener('click', () => proposalDialog.close());
  proposalDialog.addEventListener('click', event => { if (event.target === proposalDialog) proposalDialog.close(); });
  document.querySelector('#event-proposal-another').addEventListener('click', () => {
    proposalForm.reset();
    proposalForm.hidden = false;
    proposalSuccess.hidden = true;
    proposalForm.elements.name.focus();
  });

  proposalForm.addEventListener('submit', event => {
    event.preventDefault();
    const proposal = Object.fromEntries(new FormData(proposalForm));
    let url;
    try {
      url = new URL(proposal.url);
    } catch {
      proposalStatus.textContent = 'Ajoute un lien officiel valide en https://.';
      return;
    }
    if (url.protocol !== 'https:') {
      proposalStatus.textContent = 'Utilise un lien officiel en https://.';
      return;
    }
    const duplicate = item => nameKey(item.name) === nameKey(proposal.name)
      && nameKey(item.city) === nameKey(proposal.city)
      && item.start?.slice(0, 10) === proposal.date;
    if (records.some(duplicate)) {
      proposalStatus.textContent = 'Cet événement à cette date figure déjà dans l’agenda.';
      return;
    }
    const subject = `Proposition d'event Kinq — ${proposal.name}`;
    const body = `Bonjour Kinq,\n\nJe propose cet événement pour l'agenda :\n\nNom : ${proposal.name}\nVille : ${proposal.city}\nDate : ${proposal.date}\nLien officiel : ${url.href}\nE-mail de contact : ${proposal.email}\n\nCette proposition reste soumise à vérification et au contrôle des doublons.`;
    proposalForm.hidden = true;
    proposalSuccess.hidden = false;
    window.location.href = `mailto:hello@kinq-app.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    document.querySelector('#event-proposal-another').focus();
  });
})();
