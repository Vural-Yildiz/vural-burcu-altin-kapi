(() => {
  'use strict';
  const welcome = document.querySelector('#welcome');
  const cinema = document.querySelector('#cinema');
  const invitation = document.querySelector('#davet');
  const video = document.querySelector('#invitation-film');
  const loader = document.querySelector('#film-loader');
  const soundButton = document.querySelector('#sound-toggle');
  const openButton = document.querySelector('#open-invitation');
  const progress = document.querySelector('#film-progress');
  const toast = document.querySelector('#toast');
  let state = 'welcome';
  let muted = false;
  let toastTimer;
  let loadingTimer;
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function notify(message) {
    clearTimeout(toastTimer);
    toast.textContent = message;
    toast.hidden = false;
    toastTimer = setTimeout(() => { toast.hidden = true; }, 3500);
  }

  function setState(next) {
    state = next;
    document.body.dataset.state = next;
    welcome.hidden = next !== 'welcome';
    cinema.hidden = next !== 'playing';
    invitation.hidden = next !== 'invitation';
    document.body.style.overflow = next === 'playing' ? 'hidden' : '';
  }

  function showInvitation(updateHash = true) {
    video.pause();
    clearTimeout(loadingTimer);
    loader.hidden = true;
    setState('invitation');
    if (updateHash) history.replaceState(null, '', '#davet');
    window.scrollTo(0, 0);
    const title = document.querySelector('#couple-title');
    title.setAttribute('tabindex', '-1');
    title.focus({ preventScroll: true });
  }

  async function playFilm() {
    if (state === 'playing') return;
    history.replaceState(null, '', location.pathname + location.search);
    setState('playing');
    video.currentTime = 0;
    video.muted = muted;
    progress.style.width = '0%';
    loadingTimer = setTimeout(() => { if (state === 'playing' && video.readyState < 3) loader.hidden = false; }, 450);
    try {
      await video.play();
      soundButton.focus({ preventScroll: true });
    } catch (error) {
      showInvitation();
      notify('Film açılamadı. Davetinizi hemen görüntüleyebilirsiniz.');
    }
  }

  openButton.addEventListener('click', () => {
    if (reduceMotion) showInvitation();
    else playFilm();
  });
  document.querySelector('#replay-film').addEventListener('click', playFilm);
  document.querySelector('#skip-film').addEventListener('click', () => showInvitation());
  document.querySelector('.skip-link').addEventListener('click', event => { event.preventDefault(); showInvitation(); });
  soundButton.addEventListener('click', () => {
    muted = !muted;
    video.muted = muted;
    soundButton.textContent = muted ? 'Sesi aç' : 'Sesi kapat';
    soundButton.setAttribute('aria-pressed', String(muted));
  });
  video.addEventListener('playing', () => { loader.hidden = true; clearTimeout(loadingTimer); });
  video.addEventListener('waiting', () => { if (state === 'playing') loader.hidden = false; });
  video.addEventListener('timeupdate', () => {
    if (Number.isFinite(video.duration) && video.duration > 0) progress.style.width = `${Math.min(100, video.currentTime / video.duration * 100)}%`;
  });
  video.addEventListener('ended', () => showInvitation());
  video.addEventListener('error', () => {
    if (state === 'playing') { showInvitation(); notify('Davetinizi görüntüleyebilirsiniz. Film şu anda açılamadı.'); }
  });
  document.addEventListener('keydown', event => { if (event.key === 'Escape' && state === 'playing') showInvitation(); });
  window.addEventListener('hashchange', () => { if (location.hash === '#davet') showInvitation(false); });

  document.querySelector('#share-invitation').addEventListener('click', async () => {
    const url = new URL(location.href);
    url.hash = '';
    const data = { title: 'Vural & Burcu · Davetlisiniz', text: 'Bir ömrün en tatlı telaşındayız; şahidimiz olun.', url: url.href };
    if (navigator.share) {
      try { await navigator.share(data); return; }
      catch (error) { if (error.name === 'AbortError') return; }
    }
    try { await navigator.clipboard.writeText(url.href); notify('Davet bağlantısı kopyalandı.'); }
    catch (error) { notify('Bağlantıyı adres çubuğundan kopyalayabilirsiniz.'); }
  });

  async function loadDetails() {
    try {
      const response = await fetch('invitation.json', { cache: 'no-cache' });
      if (!response.ok) return;
      const details = await response.json();
      if (details.location) document.querySelectorAll('[data-location]').forEach(el => { el.textContent = details.location; });
      const fields = [['TARİH', details.date], ['SAAT', details.time], ['DÜĞÜN YERİ', details.venue]];
      const list = document.querySelector('#event-details');
      for (const [label, value] of fields) {
        if (!value) continue;
        const term = document.createElement('dt'); term.textContent = label;
        const text = document.createElement('dd'); text.textContent = value;
        list.append(term, text);
      }
      list.hidden = !list.children.length;
    } catch (error) { /* The supplied invitation still works without optional details. */ }
  }
  if (location.hash === '#davet') showInvitation(false);
  loadDetails();
})();
