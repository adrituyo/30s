(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  document.documentElement.classList.add('js');

  // Pictures fade in once decoded. Nothing waits on scroll: what is on screen shows at once.
  $$('.t img').forEach(img => {
    const done = () => img.classList.add('in');
    if (img.complete) done(); else { img.addEventListener('load', done); img.addEventListener('error', done); }
  });

  // Before / after: the slider moves the line that splits the two pictures
  $$('.ba').forEach(ba => {
    const input = $('input', ba);
    const set = () => ba.style.setProperty('--pos', input.value + '%');
    input.addEventListener('input', set); set();
  });

  // Loops only play while on screen
  if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const vio = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting) e.target.play().catch(() => {}); else e.target.pause();
    }), { rootMargin: '100px' });
    $$('.t video').forEach(v => vio.observe(v));
  }

  // Index layout: the list on the left marks the project in view
  const links = new Map($$('.index a').map(a => [a.getAttribute('href').slice(1), a]));
  if (links.size) {
    const secs = $$('main > section[id]');
    const mark = () => {
      const y = scrollY + innerHeight * .35;
      let cur = secs[0];
      secs.forEach(s => { if (s.offsetTop <= y) cur = s; });
      if (scrollY + innerHeight >= document.documentElement.scrollHeight - 2) cur = null;   // past the work, in the footer
      links.forEach((a, id) => a.classList.toggle('on', cur && id === cur.id));
    };
    addEventListener('scroll', mark, { passive: true }); mark();
  }

  // Dock: the name and the address follow the visitor. It shows once the contact block has scrolled away
  // and steps aside at the end of the page, where the address is already on screen in large type.
  const dock = $('.dock');
  if (dock) {
    const marks = $$('.contact, .info .big, .info .fine');
    const seen = el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.bottom > 0 && r.top < innerHeight; };
    const place = () => { const on = !marks.some(seen); dock.classList.toggle('on', on); dock.inert = !on; };
    addEventListener('scroll', place, { passive: true }); addEventListener('resize', place); place();
  }

  // Email: one click copies the address as well as opening the mail app
  $$('[data-copy]').forEach(a => a.addEventListener('click', () => {
    navigator.clipboard && navigator.clipboard.writeText(a.dataset.copy).catch(() => {});
  }));

  // Viewer: click a picture to see it whole; arrows or swipe to move, Esc to close
  const tiles = $$('a.t');
  if (!tiles.length || !window.HTMLDialogElement) return;
  const lb = document.createElement('dialog');
  lb.className = 'lb';
  const L = document.body.dataset;   // the words come from the page, so they follow its language
  lb.innerHTML = `<button class="lb-close" aria-label="${L.close || 'Close'}">${L.close || 'Close'}</button><div class="lb-stage"></div>` +
    `<button class="lb-nav lb-prev" aria-label="${L.prev || 'Previous'}"></button><button class="lb-nav lb-next" aria-label="${L.next || 'Next'}"></button>` +
    '<div class="lb-bar"><span class="lb-cap"></span><span class="lb-n"></span></div>';
  document.body.append(lb);
  const stage = $('.lb-stage', lb);
  let i = 0;
  const show = n => {
    i = (n + tiles.length) % tiles.length;
    const t = tiles[i], src = t.getAttribute('href');
    const el = /\.(mp4|webm|mov)$/i.test(src) ? Object.assign(document.createElement('video'), { src, controls: true, autoplay: true, loop: true, playsInline: true })
      : Object.assign(document.createElement('img'), { src, alt: t.dataset.cap || '' });
    stage.replaceChildren(el);
    $('.lb-cap', lb).textContent = t.dataset.cap || '';
    $('.lb-n', lb).textContent = (i + 1) + ' / ' + tiles.length;
  };
  tiles.forEach((t, n) => t.addEventListener('click', e => {
    if (e.metaKey || e.ctrlKey || e.shiftKey) return;
    e.preventDefault(); show(n); lb.showModal();
  }));
  $('.lb-close', lb).addEventListener('click', () => lb.close());
  $('.lb-prev', lb).addEventListener('click', () => show(i - 1));
  $('.lb-next', lb).addEventListener('click', () => show(i + 1));
  lb.addEventListener('close', () => stage.replaceChildren());
  lb.addEventListener('keydown', e => {
    if (e.key === 'ArrowLeft') show(i - 1);
    if (e.key === 'ArrowRight') show(i + 1);
  });
  let x0 = null;
  lb.addEventListener('touchstart', e => { x0 = e.touches[0].clientX; }, { passive: true });
  lb.addEventListener('touchend', e => {
    if (x0 === null) return;
    const dx = e.changedTouches[0].clientX - x0; x0 = null;
    if (Math.abs(dx) > 50) show(i + (dx < 0 ? 1 : -1));
  });
})();
