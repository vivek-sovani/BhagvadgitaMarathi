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
    if (available) el.href = `./adhyay?id=${adhyay.id}`;

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

// ── Continue reading (पुढे वाचा) ───────────────────────────────────────────────
// Reads the last-read concept saved by adhyay.js and points the user to the
// NEXT concept in the adhyay-by-adhyay, concept-by-concept sequence. Also lets
// the user manually reset that pointer to any adhyay/concept via a small modal.
(function () {
  const wrap = document.getElementById('resume-wrap');
  const card = document.getElementById('resume-card');
  if (!wrap || !card || typeof GITA_DATA === 'undefined') return;

  const avail = GITA_DATA.adhyays.filter(a => a.available && a.concepts && a.concepts.length);
  if (!avail.length) return;

  const toDevNum = n => String(n).replace(/[0-9]/g, d => '०१२३४५६७८९'[d]);

  function loadLast() {
    try {
      const raw = localStorage.getItem('gita-last-read');
      return raw ? JSON.parse(raw) : null;
    } catch (e) { return null; }
  }

  // Compute the next concept to read from the last-read pointer, then paint the card.
  function render() {
    const last = loadLast();
    let target, resumed = false, finished = false, lastConcept = null;
    const lastAdhyay = last && GITA_DATA.adhyays.find(a => a.id === last.adhyayId);

    if (!lastAdhyay) {
      // Never read anything (or stale data) — start at the very beginning
      target = { adhyay: avail[0], concept: avail[0].concepts[0] };
    } else {
      resumed = true;
      const cIdx = lastAdhyay.concepts.findIndex(c => c.id === last.conceptId);
      lastConcept = cIdx > -1 ? lastAdhyay.concepts[cIdx] : null;

      if (cIdx > -1 && cIdx < lastAdhyay.concepts.length - 1) {
        // Next concept within the same adhyay
        target = { adhyay: lastAdhyay, concept: lastAdhyay.concepts[cIdx + 1] };
      } else {
        // Move on to the first concept of the next available adhyay
        const aIdx = avail.findIndex(a => a.id === lastAdhyay.id);
        const nextA = (aIdx > -1 && aIdx < avail.length - 1) ? avail[aIdx + 1] : null;
        if (nextA) {
          target = { adhyay: nextA, concept: nextA.concepts[0] };
        } else {
          // Reached the end — re-offer the last concept read
          finished = true;
          target = { adhyay: lastAdhyay, concept: lastConcept || lastAdhyay.concepts[0] };
        }
      }
    }

    const a = target.adhyay, c = target.concept;
    const emojiEl   = document.getElementById('rc-emoji');
    const eyebrowEl = document.getElementById('rc-eyebrow');
    const titleEl   = document.getElementById('rc-title');
    const metaEl    = document.getElementById('rc-meta');
    const btnEl     = card.querySelector('.rc-btn');

    if (emojiEl) emojiEl.textContent = c.emoji || a.emoji || '📖';
    if (eyebrowEl) eyebrowEl.textContent = finished
      ? 'सर्व अध्याय वाचून झाले 🎉'
      : resumed ? 'पुढे वाचा' : 'इथून सुरू करा';
    if (titleEl) titleEl.textContent = c.name;
    if (metaEl) {
      let meta = `अध्याय ${a.number} · ${a.name} · संकल्पना ${toDevNum(c.id)}`;
      if (resumed && lastConcept && !finished) {
        meta = `मागील: ${lastConcept.name}  →  ${meta}`;
      }
      metaEl.textContent = meta;
    }
    if (btnEl) {
      // Preserve the arrow svg, only swap the leading label
      const svg = btnEl.querySelector('svg');
      btnEl.textContent = finished ? 'पुन्हा वाचा ' : resumed ? 'पुढे चला ' : 'सुरू करा ';
      if (svg) btnEl.appendChild(svg);
    }

    card.href = `./adhyay?id=${a.id}&concept=${c.id}`;
    wrap.style.display = 'block';

    return { adhyay: a, concept: c };
  }

  let currentTarget = render();

  // ── Manual "बदला" editor — set the resume pointer to any adhyay/concept ──
  const editLink   = document.getElementById('rc-edit-link');
  const overlay    = document.getElementById('pm-overlay');
  const adhyaySel  = document.getElementById('pm-adhyay-select');
  const conceptSel = document.getElementById('pm-concept-select');
  const saveBtn    = document.getElementById('pm-save-btn');
  const cancelBtn  = document.getElementById('pm-cancel-btn');
  const resetBtn   = document.getElementById('pm-reset-btn');
  if (!editLink || !overlay || !adhyaySel || !conceptSel || !saveBtn || !cancelBtn || !resetBtn) return;

  function fillConceptOptions(adhyayId, selectedConceptId) {
    const adhyay = avail.find(a => a.id === Number(adhyayId));
    conceptSel.innerHTML = '';
    if (!adhyay) return;
    adhyay.concepts.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.id;
      opt.textContent = `संकल्पना ${toDevNum(c.id)} · ${c.emoji || ''} ${c.name}`;
      conceptSel.appendChild(opt);
    });
    conceptSel.value = selectedConceptId != null && adhyay.concepts.some(c => c.id === selectedConceptId)
      ? selectedConceptId
      : adhyay.concepts[0].id;
  }

  function fillAdhyayOptions(selectedAdhyayId) {
    adhyaySel.innerHTML = '';
    avail.forEach(a => {
      const opt = document.createElement('option');
      opt.value = a.id;
      opt.textContent = `अध्याय ${a.number} · ${a.name}`;
      adhyaySel.appendChild(opt);
    });
    adhyaySel.value = selectedAdhyayId;
  }

  function openModal() {
    fillAdhyayOptions(currentTarget.adhyay.id);
    fillConceptOptions(currentTarget.adhyay.id, currentTarget.concept.id);
    overlay.classList.add('open');
    overlay.setAttribute('aria-hidden', 'false');
  }
  function closeModal() {
    overlay.classList.remove('open');
    overlay.setAttribute('aria-hidden', 'true');
  }

  // Sets the resume pointer so that the NEXT concept computed by render() is
  // exactly (adhyayId, conceptId) — i.e. stores the concept just before it.
  function setResumeTarget(adhyayId, conceptId) {
    const aIdx = avail.findIndex(a => a.id === Number(adhyayId));
    if (aIdx === -1) return;
    const adhyay = avail[aIdx];
    const cIdx = adhyay.concepts.findIndex(c => c.id === Number(conceptId));
    if (cIdx === -1) return;

    let prevAdhyay, prevConcept;
    if (cIdx > 0) {
      prevAdhyay = adhyay;
      prevConcept = adhyay.concepts[cIdx - 1];
    } else if (aIdx > 0) {
      prevAdhyay = avail[aIdx - 1];
      prevConcept = prevAdhyay.concepts[prevAdhyay.concepts.length - 1];
    } else {
      // Very first concept of the very first adhyay — no "previous" exists.
      try { localStorage.removeItem('gita-last-read'); } catch (e) { /* ignore */ }
      currentTarget = render();
      return;
    }
    try {
      localStorage.setItem('gita-last-read', JSON.stringify({
        adhyayId: prevAdhyay.id, conceptId: prevConcept.id, ts: Date.now()
      }));
    } catch (e) { /* localStorage unavailable — ignore */ }
    currentTarget = render();
  }

  editLink.addEventListener('click', openModal);
  cancelBtn.addEventListener('click', closeModal);
  overlay.addEventListener('click', (e) => { if (e.target === overlay) closeModal(); });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && overlay.classList.contains('open')) closeModal();
  });
  adhyaySel.addEventListener('change', () => fillConceptOptions(adhyaySel.value, null));
  saveBtn.addEventListener('click', () => {
    setResumeTarget(adhyaySel.value, conceptSel.value);
    closeModal();
  });
  resetBtn.addEventListener('click', () => {
    setResumeTarget(avail[0].id, avail[0].concepts[0].id);
    closeModal();
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
  const conceptUrl = `./adhyay?id=${adhyay.id}&concept=${concept.id}`;
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
