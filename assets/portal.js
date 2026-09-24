'use strict';
(() => {
  const cards = Array.from(document.querySelectorAll('[data-project]'));
  const search = document.querySelector('#project-search');
  const filters = Array.from(document.querySelectorAll('[data-filter]'));
  const normalize = text => text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('fr');
  let category = 'all';
  function filterProjects() {
    const query = normalize(search?.value || '').trim();
    let count = 0;
    cards.forEach(card => {
      const shown = (category === 'all' || card.dataset.category === category) && normalize(card.dataset.search).includes(query);
      card.hidden = !shown;
      if (shown) count++;
    });
    const result = document.querySelector('.result-count');
    const empty = document.querySelector('.empty-state');
    if (result) result.textContent = `${count} projet${count === 1 ? '' : 's'}`;
    if (empty) empty.hidden = count !== 0;
  }
  filters.forEach(button => button.addEventListener('click', () => {
    category = button.dataset.filter;
    filters.forEach(other => other.setAttribute('aria-pressed', String(other === button)));
    filterProjects();
  }));
  search?.addEventListener('input', filterProjects);
  document.querySelectorAll('[data-share]').forEach(button => button.addEventListener('click', async () => {
    const feedback = document.querySelector('.share-feedback');
    try {
      if (navigator.share) {
        await navigator.share({ title: document.title, url: location.href });
      } else if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(location.href);
        feedback.textContent = 'Lien copié. Vous pouvez le partager.';
      } else {
        feedback.textContent = `Lien à partager : ${location.href}`;
      }
    } catch (error) {
      if (error.name !== 'AbortError') feedback.textContent = `Lien à partager : ${location.href}`;
    }
  }));
  document.querySelectorAll('[data-updated]').forEach(time => {
    const date = new Date(time.dateTime);
    if (!Number.isNaN(date.getTime())) time.textContent = new Intl.DateTimeFormat('fr-FR', {dateStyle:'long',timeStyle:'short',timeZone:'Asia/Jerusalem'}).format(date) + ' · Jérusalem';
  });
})();
