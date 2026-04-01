(function () {
  const list    = document.getElementById('adhyay-list');
  const toggle  = document.getElementById('sidebar-toggle');
  const sidebar = document.getElementById('sidebar');
  const close   = document.getElementById('sidebar-close');
  const backdrop= document.getElementById('sidebar-backdrop');

  // ── Render adhyay list ────────────────────────────────────────
  GITA_DATA.adhyays.forEach(adhyay => {
    const item = document.createElement(adhyay.available ? 'a' : 'div');
    item.className = 'sidebar-adhyay-item' + (adhyay.available ? '' : ' unavailable');
    if (adhyay.available) item.href = `adhyay.html?id=${adhyay.id}`;
    item.setAttribute('aria-label', `अध्याय ${adhyay.number} — ${adhyay.name}`);
    item.innerHTML = `
      <span class="item-emoji">${adhyay.emoji}</span>
      <div class="item-text">
        <span class="item-number">अध्याय ${adhyay.number}</span>
        <span class="item-name">${adhyay.name}</span>
      </div>
      ${adhyay.available ? '' : '<span class="coming-soon-badge">लवकरच</span>'}
    `;
    list.appendChild(item);
  });

  // ── Sidebar open/close ────────────────────────────────────────
  function openSidebar()  { sidebar.classList.add('open'); backdrop.classList.add('open'); document.body.style.overflow = 'hidden'; }
  function closeSidebar() { sidebar.classList.remove('open'); backdrop.classList.remove('open'); document.body.style.overflow = ''; }

  toggle.addEventListener('click', openSidebar);
  close.addEventListener('click', closeSidebar);
  backdrop.addEventListener('click', closeSidebar);
})();
