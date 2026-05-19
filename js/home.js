(function () {
  const EN_SUBTITLES = [
    "Arjuna's Despair", "Knowledge of the Self", "Path of Action",
    "Knowledge & Action", "Renunciation of Action", "Meditation",
    "Wisdom & Realization", "The Imperishable", "Royal Knowledge",
    "Divine Manifestations", "The Universal Form", "Path of Devotion",
    "Field & Knower", "Three Qualities", "Supreme Person",
    "Divine & Demonic", "Three Kinds of Faith", "Path of Liberation"
  ];

  const STATS = [
    "४६ श्लोक", "७२ श्लोक", "४३ श्लोक", "४२ श्लोक", "२९ श्लोक",
    "४७ श्लोक", "३० श्लोक", "२८ श्लोक", "३४ श्लोक", "४२ श्लोक",
    "५५ श्लोक", "२० श्लोक", "३५ श्लोक", "२७ श्लोक", "२० श्लोक",
    "२४ श्लोक", "२८ श्लोक", "७८ श्लोक"
  ];

  const grid = document.getElementById('chapters-grid');
  if (!grid) return;

  GITA_DATA.adhyays.forEach(adhyay => {
    const idx = adhyay.id - 1;
    const available = adhyay.available;
    const el = document.createElement(available ? 'a' : 'div');
    el.className = 'chapter' + (available ? '' : ' unavailable');
    if (available) el.href = `/adhyay?id=${adhyay.id}`;

    el.innerHTML = `
      <div class="num-block">
        <div class="roman">${adhyay.number}</div>
        <div class="label">अध्याय</div>
      </div>
      <div class="body">
        <h4 class="title">${adhyay.name}</h4>
        <p class="sub">${EN_SUBTITLES[idx] || ''}</p>
        <div class="stats"><span>${STATS[idx] || ''}</span><span>${adhyay.concepts.length} संकल्पना</span></div>
      </div>
    `;
    grid.appendChild(el);
  });
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

  if (scRef)     scRef.textContent = `आजची संकल्पना · अध्याय ${adhyay.number} · ${concept.emoji} ${concept.name}`;
  if (scShlok)   scShlok.textContent = concept.tagline;
  if (scOvi)     scOvi.innerHTML = trigger.paras[0];
  const conceptUrl = `/adhyay?id=${adhyay.id}&concept=${concept.id}`;
  const ctaLinked = trigger.cta.replace(
    /हे वाचा/g,
    `<a href="${conceptUrl}" style="color:var(--saffron);font-weight:600;text-decoration:underline;text-underline-offset:3px;">हे वाचा →</a>`
  );
  if (scMeaning) scMeaning.innerHTML = `<strong>आजचे करायचे काय?</strong> ${ctaLinked}`;

  // ── Today-verse section (आजचा पाठ) ───────────────────────────
  const tvRef   = document.getElementById('tv-ref');
  const tvQuote = document.getElementById('tv-quote');
  const tvCta   = document.getElementById('tv-cta');

  if (tvRef)   tvRef.textContent = `अध्याय ${adhyay.number} · ${concept.emoji} ${concept.name}`;
  // Use second para if available — it tends to be the more reflective one
  if (tvQuote) tvQuote.innerHTML = trigger.paras.length > 1 ? trigger.paras[1] : trigger.paras[0];
  // CTA with linked "हे वाचा"
  const tvCtaLinked = trigger.cta.replace(
    /हे वाचा/g,
    `<a href="${conceptUrl}" style="color:var(--saffron-glow);font-weight:600;text-decoration:underline;text-underline-offset:3px;">हे वाचा →</a>`
  );
  if (tvCta) tvCta.innerHTML = tvCtaLinked;
})();
