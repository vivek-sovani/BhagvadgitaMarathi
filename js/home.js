(function () {
  const grid = document.getElementById('adhyay-grid');
  if (!grid) return;

  GITA_DATA.adhyays.forEach(adhyay => {
    const card = document.createElement('div');
    card.className = 'adhyay-card' + (adhyay.available ? '' : ' unavailable');
    card.setAttribute('role', adhyay.available ? 'button' : 'presentation');
    card.setAttribute('tabindex', adhyay.available ? '0' : '-1');
    card.setAttribute('aria-label', `अध्याय ${adhyay.number} — ${adhyay.name}`);

    card.innerHTML = `
      <div class="card-emoji">${adhyay.emoji}</div>
      <div class="card-number">अध्याय ${adhyay.number}</div>
      <div class="card-name">${adhyay.name}</div>
      ${!adhyay.available ? '<span class="coming-soon-badge">लवकरच</span>' : ''}
    `;

    if (adhyay.available) {
      const go = () => { window.location.href = `adhyay.html?id=${adhyay.id}`; };
      card.addEventListener('click', go);
      card.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); go(); } });
    }

    grid.appendChild(card);
  });
})();
