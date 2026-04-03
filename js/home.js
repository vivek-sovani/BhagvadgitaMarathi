(function () {
  const sidebarList  = document.getElementById('adhyay-list');
  const homeList     = document.getElementById('home-adhyay-list');
  const toggle       = document.getElementById('sidebar-toggle');
  const sidebar      = document.getElementById('sidebar');
  const close        = document.getElementById('sidebar-close');
  const backdrop     = document.getElementById('sidebar-backdrop');

  // ── Render adhyay list (sidebar + home panel) ─────────────────
  GITA_DATA.adhyays.forEach(adhyay => {
    const unavailable = !adhyay.available;

    // Sidebar item
    const sItem = document.createElement(adhyay.available ? 'a' : 'div');
    sItem.className = 'sidebar-adhyay-item' + (unavailable ? ' unavailable' : '');
    if (adhyay.available) sItem.href = `adhyay.html?id=${adhyay.id}`;
    sItem.setAttribute('aria-label', `अध्याय ${adhyay.number} — ${adhyay.name}`);
    sItem.innerHTML = `
      <span class="item-num">अ${adhyay.number}</span>
      <span class="item-emoji">${adhyay.emoji}</span>
      <span class="item-name">${adhyay.name}</span>
    `;
    if (sidebarList) sidebarList.appendChild(sItem);

    // Home page menu item
    const hItem = document.createElement(adhyay.available ? 'a' : 'div');
    hItem.className = 'home-adhyay-item' + (unavailable ? ' unavailable' : '');
    if (adhyay.available) hItem.href = `adhyay.html?id=${adhyay.id}`;
    hItem.setAttribute('aria-label', `अध्याय ${adhyay.number} — ${adhyay.name}`);
    hItem.innerHTML = `
      <span class="hai-num">अ${adhyay.number}</span>
      <span class="hai-emoji">${adhyay.emoji}</span>
      <span class="hai-name">${adhyay.name}</span>
    `;
    if (homeList) homeList.appendChild(hItem);
  });

  // ── Sidebar open/close ────────────────────────────────────────
  function openSidebar()  { sidebar.classList.add('open'); backdrop.classList.add('open'); document.body.style.overflow = 'hidden'; }
  function closeSidebar() { sidebar.classList.remove('open'); backdrop.classList.remove('open'); document.body.style.overflow = ''; }

  if (toggle)   toggle.addEventListener('click', openSidebar);
  if (close)    close.addEventListener('click', closeSidebar);
  if (backdrop) backdrop.addEventListener('click', closeSidebar);
})();
