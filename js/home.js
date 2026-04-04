(function () {
  const homeList = document.getElementById('home-adhyay-list');

  GITA_DATA.adhyays.forEach(adhyay => {
    const unavailable = !adhyay.available;
    const hItem = document.createElement(adhyay.available ? 'a' : 'div');
    hItem.className = 'home-adhyay-item' + (unavailable ? ' unavailable' : '');
    if (adhyay.available) hItem.href = `adhyay.html?id=${adhyay.id}`;
    hItem.setAttribute('aria-label', `अध्याय ${adhyay.number} — ${adhyay.name}`);
    hItem.innerHTML = `
      <span class="hai-num">अध्याय ${adhyay.number}</span>
      <span class="hai-emoji">${adhyay.emoji}</span>
      <span class="hai-name">${adhyay.name}</span>
    `;
    if (homeList) homeList.appendChild(hItem);
  });

  // अध्याय सूची link → scroll to chapter list
  const suchiLink = document.querySelector('.header-suchi-btn');
  if (suchiLink) {
    suchiLink.addEventListener('click', (e) => {
      e.preventDefault();
      const target = document.getElementById('home-adhyay-list');
      if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }
})();
