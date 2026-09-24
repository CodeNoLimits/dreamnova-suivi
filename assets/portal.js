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
  // Preserve an active catalogue view across a verified publication refresh.
  try {
    const key = `portal:view:${location.pathname}`;
    const saved = JSON.parse(sessionStorage.getItem(key) || 'null');
    sessionStorage.removeItem(key);
    if (saved) {
      category = filters.some(button => button.dataset.filter === saved.category) ? saved.category : 'all';
      if (search) search.value = saved.query || '';
      filters.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === category)));
      filterProjects();
      requestAnimationFrame(() => window.scrollTo(0, saved.scroll || 0));
    }
  } catch (_) { /* Storage may be disabled; navigation still works. */ }
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
  const revision = document.querySelector('meta[name="portal-revision"]')?.content;
  const dataPath = document.querySelector('meta[name="portal-data"]')?.content;
  const freshness = document.querySelector('[data-freshness]');
  const refresh = document.querySelector('[data-refresh]');
  let pendingRevision = null;
  let checking = false;
  function isBusy() {
    const editing = document.activeElement?.matches('input,textarea,select,[contenteditable="true"]');
    const playing = Array.from(document.querySelectorAll('video,audio')).some(media => !media.paused && !media.ended);
    return editing || playing;
  }
  async function loadPublication(force = false) {
    if (!pendingRevision || (!force && isBusy())) return;
    const target = new URL(location.href);
    target.searchParams.set('v', pendingRevision);
    const response = await fetch(target, {cache:'no-store', signal:AbortSignal.timeout(10000)});
    if (!response.ok) throw new Error('Publication unavailable');
    const doc = new DOMParser().parseFromString(await response.text(), 'text/html');
    if (doc.querySelector('meta[name="portal-revision"]')?.content !== pendingRevision) {
      freshness.textContent = 'Nouvelle publication en cours de diffusion.';
      return; // A CDN can briefly expose the new manifest before its HTML.
    }
    if (!force && (isBusy() || document.hidden)) return;
    try {
      sessionStorage.setItem(`portal:view:${location.pathname}`, JSON.stringify({category,query:search?.value || '',scroll:scrollY}));
    } catch (_) { /* Optional view restoration. */ }
    location.replace(target.href);
  }
  async function checkPublication() {
    if (checking || document.hidden || !revision || !dataPath || !freshness) return;
    checking = true;
    try {
      const endpoint = new URL(dataPath, location.href);
      endpoint.searchParams.set('check', Date.now());
      const response = await fetch(endpoint, {cache:'no-store', signal:AbortSignal.timeout(10000)});
      if (!response.ok) throw new Error('Status unavailable');
      const data = await response.json();
      if (!Array.isArray(data.projects) || !Number.isFinite(Date.parse(data.updatedAt))) throw new Error('Invalid status');
      if (Date.parse(data.updatedAt) > Date.parse(revision)) {
        pendingRevision = data.updatedAt;
        refresh.hidden = false;
        freshness.textContent = 'Une nouvelle version est disponible.';
        await loadPublication();
      } else {
        freshness.textContent = 'Version à jour · contrôle toutes les 30 s';
      }
    } catch (_) {
      freshness.textContent = 'Vérification momentanément indisponible · liens conservés';
    } finally { checking = false; }
  }
  refresh?.addEventListener('click', () => loadPublication(true).catch(() => {
    freshness.textContent = 'Actualisation indisponible. Réessayez dans un instant.';
  }));
  document.addEventListener('visibilitychange', checkPublication);
  setInterval(checkPublication, 30000);
  checkPublication();
})();
