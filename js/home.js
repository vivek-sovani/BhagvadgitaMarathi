(function () {
  const STATS_MR = [
    "४६ श्लोक", "७२ श्लोक", "४३ श्लोक", "४२ श्लोक", "२९ श्लोक",
    "४७ श्लोक", "३० श्लोक", "२८ श्लोक", "३४ श्लोक", "४२ श्लोक",
    "५५ श्लोक", "२० श्लोक", "३५ श्लोक", "२७ श्लोक", "२० श्लोक",
    "२४ श्लोक", "२८ श्लोक", "७८ श्लोक"
  ];
  const STATS_EN = [
    "46 verses", "72 verses", "43 verses", "42 verses", "29 verses",
    "47 verses", "30 verses", "28 verses", "34 verses", "42 verses",
    "55 verses", "20 verses", "35 verses", "27 verses", "20 verses",
    "24 verses", "28 verses", "78 verses"
  ];

  const grid = document.getElementById('chapters-grid');
  if (!grid) return;

  function renderGrid() {
    const lang = (typeof getCurrentLang === 'function') ? getCurrentLang() : 'mr';
    const enData = (lang === 'en' && typeof GITA_DATA_EN !== 'undefined') ? GITA_DATA_EN : null;
    const stats = lang === 'en' ? STATS_EN : STATS_MR;
    const chLabel = (typeof t === 'function') ? t('chapter') : 'अध्याय';
    const cLabel  = (typeof t === 'function') ? t('conceptLabel') : 'संकल्पना';

    grid.innerHTML = '';
    GITA_DATA.adhyays.forEach(adhyay => {
      const idx = adhyay.id - 1;
      const available = adhyay.available;
      const enAdhyay = enData && enData.adhyays.find(a => a.id === adhyay.id);
      const displayName = (lang === 'en' && enAdhyay) ? enAdhyay.name : adhyay.name;
      const displayNum  = lang === 'en' ? adhyay.id : adhyay.number;
      const subtitle    = lang === 'en' ? '' : '';

      const el = document.createElement(available ? 'a' : 'div');
      el.className = 'chapter' + (available ? '' : ' unavailable');
      if (available) el.href = `./adhyay?id=${adhyay.id}`;

      el.innerHTML = `
        <div class="num-block">
          <div class="roman">${displayNum}</div>
          <div class="label">${chLabel}</div>
        </div>
        <div class="body">
          <h4 class="title">${displayName}</h4>
          <div class="stats"><span>${stats[idx] || ''}</span><span>${adhyay.concepts.length} ${cLabel}</span></div>
        </div>
      `;
      grid.appendChild(el);
    });
  }

  renderGrid();

  document.addEventListener('langchange', renderGrid);
})();

// ── Daily concept picker ──────────────────────────────────────────────────────
(function () {
  if (typeof GITA_DATA === 'undefined' || typeof GITA_TRIGGERS === 'undefined') return;

  // Build pool from concepts that have trigger data
  const pool = [];
  GITA_DATA.adhyays.forEach(adhyay => {
    if (!adhyay.available) return;
    const adhyayTriggers = GITA_TRIGGERS[adhyay.id];
    if (!adhyayTriggers) return;
    adhyay.concepts.forEach(concept => {
      if (adhyayTriggers[concept.id]) {
        pool.push({ adhyay, concept, trigger: adhyayTriggers[concept.id] });
      }
    });
  });
  if (!pool.length) return;

  // Same concept all day, rotates daily
  const now = new Date();
  const dayOfYear = Math.floor((now - new Date(now.getFullYear(), 0, 0)) / 86400000);
  const { adhyay, concept, trigger } = pool[dayOfYear % pool.length];

  // ── Scroll-card (आजचा श्लोक) ──────────────────────────────────
  const scRef     = document.getElementById('sc-ref');
  const scShlok   = document.getElementById('sc-shlok');
  const scOvi     = document.getElementById('sc-ovi');
  const scMeaning = document.getElementById('sc-meaning');

  const lang = (typeof getCurrentLang === 'function') ? getCurrentLang() : 'mr';
  const chNum = lang === 'en' ? adhyay.id : adhyay.number;
  const enAdhyay = (lang === 'en' && typeof GITA_DATA_EN !== 'undefined')
    && GITA_DATA_EN.adhyays.find(a => a.id === adhyay.id);
  const enConcept = enAdhyay && enAdhyay.concepts.find(c => c.id === concept.id);
  const displayName = (lang === 'en' && enConcept) ? enConcept.name : concept.name;
  const chLabel = (typeof t === 'function') ? t('chapter') : 'अध्याय';
  const todayCLabel = (typeof t === 'function') ? t('todayConcept') : 'आजची संकल्पना';
  const todayActionLabel = (typeof t === 'function') ? t('todayAction') : 'आजचे करायचे काय?';
  const readThisLabel = (typeof t === 'function') ? t('readThis') : 'हे वाचा';

  if (scRef)   scRef.textContent = `${todayCLabel} · ${chLabel} ${chNum} · ${concept.emoji} ${displayName}`;
  if (scShlok) scShlok.textContent = (lang === 'en' && enConcept && enConcept.tagline) ? enConcept.tagline : concept.tagline;
  if (scOvi)   scOvi.innerHTML = trigger.paras[0];
  const conceptUrl = `./adhyay?id=${adhyay.id}&concept=${concept.id}`;
  const ctaLinked = trigger.cta.replace(
    /हे वाचा/g,
    `<a href="${conceptUrl}" style="color:var(--saffron);font-weight:600;text-decoration:underline;text-underline-offset:3px;">${readThisLabel} →</a>`
  );
  if (scMeaning) scMeaning.innerHTML = `<strong>${todayActionLabel}</strong> ${ctaLinked}`;

  // ── Today-verse section (आजचा पाठ) ───────────────────────────
  const tvRef   = document.getElementById('tv-ref');
  const tvQuote = document.getElementById('tv-quote');
  const tvCta   = document.getElementById('tv-cta');

  if (tvRef)   tvRef.textContent = `${chLabel} ${chNum} · ${concept.emoji} ${displayName}`;
  if (tvQuote) tvQuote.innerHTML = trigger.paras.length > 1 ? trigger.paras[1] : trigger.paras[0];
  const tvCtaLinked = trigger.cta.replace(
    /हे वाचा/g,
    `<a href="${conceptUrl}" style="color:var(--saffron-glow);font-weight:600;text-decoration:underline;text-underline-offset:3px;">${readThisLabel} →</a>`
  );
  if (tvCta) tvCta.innerHTML = tvCtaLinked;
})();
