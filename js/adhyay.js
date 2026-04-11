(function () {
  // ── Parse URL params ─────────────────────────────────────────
  const params     = new URLSearchParams(window.location.search);
  const adhyayId   = parseInt(params.get('id'), 10);
  const conceptId  = parseInt(params.get('concept'), 10) || null;

  const adhyay = GITA_DATA.adhyays.find(a => a.id === adhyayId);
  if (!adhyay || !adhyay.available) {
    window.location.replace('index.html');
    return;
  }

  // ── Prev / Next available chapter ────────────────────────────
  const availableAdhyays = GITA_DATA.adhyays.filter(a => a.available);
  const currentAdhyayIdx = availableAdhyays.findIndex(a => a.id === adhyayId);
  const prevAdhyay = currentAdhyayIdx > 0 ? availableAdhyays[currentAdhyayIdx - 1] : null;
  const nextAdhyay = currentAdhyayIdx < availableAdhyays.length - 1 ? availableAdhyays[currentAdhyayIdx + 1] : null;

  // ── Element refs ─────────────────────────────────────────────
  const headerLabel      = document.getElementById('header-adhyay-label');
  const summarySection   = document.getElementById('summary-img-section');
  const summaryImg       = document.getElementById('summary-img');
  const summaryPH        = document.getElementById('summary-placeholder');
  const summaryPHText    = document.getElementById('summary-placeholder-text');
  const summaryTextEl    = document.getElementById('adhyay-summary-text');
  const summaryLabelEl   = document.getElementById('summary-adhyay-label');
  const summaryDescEl    = document.getElementById('summary-adhyay-desc');
  const summaryConceptListEl = document.getElementById('summary-concept-list');
  const bnavEl           = document.getElementById('bottom-concept-nav');
  const bnavPrevName     = document.getElementById('bnav-prev-name');
  const bnavNextName     = document.getElementById('bnav-next-name');
  const conceptTitleBar  = document.getElementById('concept-title-bar');
  const ctbMeta          = document.getElementById('ctb-meta');
  const ctbName          = document.getElementById('ctb-name');
  const conceptView      = document.getElementById('concept-view');
  const conceptImg       = document.getElementById('concept-img');
  const conceptPH        = document.getElementById('concept-placeholder');
  const conceptPHEmoji   = document.getElementById('concept-placeholder-emoji');
  const conceptInfoEmoji   = document.getElementById('concept-info-emoji');
  const conceptInfoName    = document.getElementById('concept-info-name');
  const conceptInfoMeta    = document.getElementById('concept-info-meta');
  const conceptTextContent = document.getElementById('concept-text-content');
  const pdfLabel         = document.getElementById('pdf-label');
  const pdfContainer     = document.getElementById('pdf-carousel-container');
  const pdfOpenBtn       = document.getElementById('pdf-open-btn');
  const pdfModal         = document.getElementById('pdf-modal');
  const pdfModalTitle    = document.getElementById('pdf-modal-title');
  const pdfModalClose    = document.getElementById('pdf-modal-close');
  const pdfModalBackdrop = document.getElementById('pdf-modal-backdrop');
  const pdfIframe        = document.getElementById('pdf-iframe');

  // ── PDF thumbnail ─────────────────────────────────────────────
  let pendingPdfUrl = null;
  const thumbCanvas = document.getElementById('pdf-thumb-canvas');
  const thumbPH     = document.getElementById('pdf-thumb-placeholder');

  async function renderThumb(url) {
    if (!url || !thumbCanvas) return;
    try {
      const pdf      = await pdfjsLib.getDocument({ url }).promise;
      const page     = await pdf.getPage(1);
      const vp0      = page.getViewport({ scale: 1 });
      const scale    = thumbCanvas.parentElement.clientWidth / vp0.width || 1;
      const vp       = page.getViewport({ scale });
      thumbCanvas.width  = vp.width;
      thumbCanvas.height = vp.height;
      await page.render({ canvasContext: thumbCanvas.getContext('2d'), viewport: vp }).promise;
      thumbCanvas.style.display = 'block';
      thumbPH.style.display = 'none';
    } catch (e) {
      thumbCanvas.style.display = 'none';
      thumbPH.style.display = '';
    }
  }

  // ── Modal open/close ──────────────────────────────────────────

  function openPdfModal(title) {
    if (!pendingPdfUrl) return;
    // Mobile: open in new tab using native PDF viewer
    if (window.innerWidth < 768) {
      window.open(pendingPdfUrl, '_blank');
      return;
    }
    // Desktop: show in iframe modal
    pdfModalTitle.textContent = title;
    pdfIframe.src = pendingPdfUrl;
    pdfModal.classList.add('open');
    pdfModalBackdrop.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closePdfModal() {
    pdfModal.classList.remove('open');
    pdfModalBackdrop.classList.remove('open');
    document.body.style.overflow = '';
    pdfIframe.src = ''; // stop loading PDF when closed
  }

  pdfOpenBtn.addEventListener('click', () => openPdfModal(pdfModalTitle.textContent));
  pdfModalClose.addEventListener('click', closePdfModal);
  pdfModalBackdrop.addEventListener('click', closePdfModal);



  // ── Helpers ───────────────────────────────────────────────────
  function assetPath(file) {
    return `assets/adhyay-${adhyay.id}/${file}`;
  }

  function setImg(imgEl, phEl, src, fallbackEmoji) {
    imgEl.style.display = '';
    imgEl.src = src;
    phEl.style.display = 'none';
    imgEl.onerror = function () {
      this.style.display = 'none';
      phEl.style.display = '';
      if (fallbackEmoji && phEl.querySelector('.ph-icon-inner')) {
        phEl.querySelector('.ph-icon-inner').textContent = fallbackEmoji;
      }
    };
  }

  // ── Render header ─────────────────────────────────────────────
  document.title = `गीता-ज्ञानेश्वरी — अध्याय ${adhyay.number} | ${adhyay.name}`;
  // Cover page: show chapter name as informational label
  headerLabel.textContent = `अध्याय ${adhyay.number} · ${adhyay.name}`;

  // ── Render cover title overlay ────────────────────────────────
  const actNum = document.getElementById('act-num');
  const actName = document.getElementById('act-name');
  if (actNum) actNum.textContent = `अध्याय ${adhyay.number}`;
  if (actName) actName.textContent = adhyay.name;

  // Header adhyay label → go back to cover page
  headerLabel.addEventListener('click', goToCoverPage);

  // Header सूची button → go to cover page and scroll to concept list
  const suchiBtn = document.getElementById('header-suchi-btn');
  if (suchiBtn) {
    suchiBtn.addEventListener('click', () => {
      if (currentConceptId !== null) goToCoverPage();
      setTimeout(() => {
        const conceptList = document.getElementById('summary-concept-list');
        if (!conceptList) return;
        const header = document.querySelector('.site-header');
        const headerH = header ? header.offsetHeight : 70;
        const rect = conceptList.getBoundingClientRect();
        window.scrollTo({ top: window.scrollY + rect.top - headerH - 8, behavior: 'smooth' });
      }, 100);
    });
  }

  // Concept title bar back button → go back to cover page
  const ctbBackBtn = document.getElementById('ctb-back-btn');
  if (ctbBackBtn) ctbBackBtn.addEventListener('click', goToCoverPage);

  // ── Render adhyay summary image ───────────────────────────────
  summaryPHText.textContent = `अध्याय ${adhyay.number} — ${adhyay.name}`;
  summaryImg.alt = `अध्याय ${adhyay.number} सारांश`;
  summaryImg.style.display = '';
  summaryPH.style.display = 'none';
  const summaryExts = ['jpg', 'jpeg', 'png'];
  let summaryExtIdx = 0;
  summaryImg.src = assetPath(`summary.${summaryExts[summaryExtIdx]}`);
  summaryImg.onerror = function () {
    summaryExtIdx++;
    if (summaryExtIdx < summaryExts.length) {
      this.src = assetPath(`summary.${summaryExts[summaryExtIdx]}`);
    } else {
      this.style.display = 'none';
      summaryPH.style.display = '';
    }
  };

  // ── Render summary text + concept list ───────────────────────
  if (adhyay.summary && summaryTextEl) {
    summaryLabelEl.textContent = `अध्याय ${adhyay.number} — ${adhyay.name}`;
    summaryDescEl.textContent  = adhyay.summary;
    summaryConceptListEl.innerHTML = '';
    adhyay.concepts.forEach(concept => {
      const item = document.createElement('div');
      item.className = 'summary-concept-item';
      item.innerHTML = `
        <span class="sci-num">${concept.id}.</span>
        <span class="sci-emoji">${concept.emoji}</span>
        <span class="sci-name">${concept.name}</span>
      `;
      item.addEventListener('click', () => selectConcept(concept.id));
      summaryConceptListEl.appendChild(item);
    });
    summaryTextEl.style.display = '';
  }

  // ── Show bottom nav (cover page: chapter navigation) ─────────
  if (bnavEl) {
    bnavEl.style.display = '';
    const prevBtn = document.getElementById('prev-concept-btn');
    const nextBtn = document.getElementById('next-concept-btn');
    if (bnavPrevName) bnavPrevName.textContent = prevAdhyay ? `अध्याय ${prevAdhyay.number} — ${prevAdhyay.name}` : '';
    if (bnavNextName) bnavNextName.textContent = nextAdhyay ? `अध्याय ${nextAdhyay.number} — ${nextAdhyay.name}` : '';
    if (prevBtn) prevBtn.disabled = !prevAdhyay;
    if (nextBtn) nextBtn.disabled = !nextAdhyay;
  }

  // ── Adhyay-level PDF (default view) ──────────────────────────
  pdfLabel.textContent = `अध्याय ${adhyay.number} PDF`;
  pdfModalTitle.textContent = `अध्याय ${adhyay.number} PDF`;
  pendingPdfUrl = assetPath('adhyay.pdf');
  renderThumb(pendingPdfUrl);

  // ── Render concept text ────────────────────────────────────────
  function renderConceptText(adhyayIdStr, conceptIdStr) {
    const el = conceptTextContent;
    if (!el) return;
    const adhyayContent = (typeof GITA_CONTENT !== 'undefined') && GITA_CONTENT[adhyayIdStr];
    const raw = adhyayContent && adhyayContent[conceptIdStr];
    if (!raw) { el.innerHTML = ''; return; }

    // Parse the raw text into structured HTML
    const lines = raw.split('\n');
    let html = '<div>';
    let i = 0;

    // Skip header line (first line with 🕉️ भगवद्गीता | ...)
    if (lines[0] && lines[0].includes('भगवद्गीता |')) i = 1;

    let inShlok    = false;
    let inDnyan    = false;
    let inSankalp  = false;
    let inQuestion = false;
    let shlokLines = [];
    let dnyanLines = [];

    const flush = () => {
      if (inShlok && shlokLines.length) {
        html += `<div class="ct-shlok-block">${shlokLines.join('<br>')}</div>`;
        shlokLines = []; inShlok = false;
      }
      if (inDnyan && dnyanLines.length) {
        html += `<div class="ct-dnyananeshwari"><span class="ct-dnyananeshwari-label">🟧 ज्ञानेश्वरी</span>${dnyanLines.join('<br>')}</div>`;
        dnyanLines = []; inDnyan = false;
      }
    };

    while (i < lines.length) {
      const line = lines[i].trim();

      if (!line) { i++; continue; }

      // Shlok section start
      if (/^📖/.test(line)) {
        flush();
        const label = line.replace(/^📖\s*/, '').trim();
        shlokLines = [`<span class="ct-shlok-label">📖 ${label || 'श्लोक'}</span>`];
        inShlok = true; inDnyan = false; inSankalp = false; inQuestion = false;
        i++; continue;
      }

      // Dnyaneshwari section
      if (/^🟧/.test(line)) {
        flush();
        inDnyan = true; inShlok = false; inSankalp = false; inQuestion = false;
        i++; continue;
      }

      // Question section
      if (/^💡/.test(line)) {
        flush();
        inQuestion = true; inSankalp = false;
        html += `<div class="ct-highlight"><span class="ct-section-icon">💡</span><strong>${line.replace(/^💡\s*/, '')}</strong></div>`;
        i++; continue;
      }

      // Sankalp section
      if (/^🌱/.test(line)) {
        flush();
        if (inSankalp) { html += '</div>'; }
        inSankalp = true; inQuestion = false;
        const rest = line.replace(/^🌱\s*/, '');
        html += `<div class="ct-sankalp"><span class="ct-label">🌱 आजचा संकल्प</span>`;
        if (rest) html += `<div>${rest}</div>`;
        i++; continue;
      }

      // Title line (emoji + name pattern — first non-header bold line)
      if (/^[🌅⚡🔍🔥✨💎🌊👁🌈🌟⚖️🔗🌿🌸🛠️🏰☀️️🌅⚔️🕉️]/.test(line) && !inShlok && !inDnyan) {
        flush();
        inSankalp = false; inQuestion = false;
        html += `<div class="ct-header">${line}</div>`;
        i++; continue;
      }

      // Quoted text lines (lines wrapped in " ")
      if (line.startsWith('"') || line.startsWith('\u201C')) {
        flush();
        if (inSankalp) { html += `<div>${line}</div>`; }
        else { html += `<div class="ct-highlight">${line}</div>`; }
        i++; continue;
      }

      // Accumulate into current block
      if (inShlok) { shlokLines.push(line); }
      else if (inDnyan) { dnyanLines.push(line); }
      else if (inSankalp) { html += `<div class="ct-para">${line}</div>`; }
      else { html += `<div class="ct-para">${line}</div>`; }

      i++;
    }

    flush();
    if (inSankalp) html += '</div>'; // close ct-sankalp
    html += '</div>';
    el.innerHTML = html;
    // Scroll text panel to top on new concept
    const body = el.closest('.concept-info-body');
    if (body) body.scrollTop = 0;
  }

  // ── Go to cover page ──────────────────────────────────────────
  function goToCoverPage() {
    currentConceptId = null;
    const adhyayBodyEl = document.getElementById('adhyay-body');
    if (adhyayBodyEl) adhyayBodyEl.scrollTop = 0;
    window.scrollTo(0, 0);
    conceptView.classList.remove('visible');
    if (conceptTitleBar) conceptTitleBar.style.display = 'none';
    summarySection.style.display = '';
    if (suchiBtn) suchiBtn.style.display = '';
    // Restore chapter nav in bottom nav
    const prevBtn = document.getElementById('prev-concept-btn');
    const nextBtn = document.getElementById('next-concept-btn');
    if (bnavPrevName) bnavPrevName.textContent = prevAdhyay ? `अध्याय ${prevAdhyay.number} — ${prevAdhyay.name}` : '';
    if (bnavNextName) bnavNextName.textContent = nextAdhyay ? `अध्याय ${nextAdhyay.number} — ${nextAdhyay.name}` : '';
    if (prevBtn) prevBtn.disabled = !prevAdhyay;
    if (nextBtn) nextBtn.disabled = !nextAdhyay;
    pdfLabel.textContent = `अध्याय ${adhyay.number} PDF`;
    pdfModalTitle.textContent = `अध्याय ${adhyay.number} PDF`;
    pendingPdfUrl = assetPath('adhyay.pdf');
    renderThumb(pendingPdfUrl);
    // Restore header label to chapter name (no back arrow)
    headerLabel.textContent = `अध्याय ${adhyay.number} · ${adhyay.name}`;
    const url = new URL(window.location.href);
    url.searchParams.delete('concept');
    history.pushState({ adhyayId }, '', url);
  }

  // ── Prev / Next concept ────────────────────────────────────────
  const prevConceptBtn = document.getElementById('prev-concept-btn');
  const nextConceptBtn = document.getElementById('next-concept-btn');
  if (prevConceptBtn) prevConceptBtn.addEventListener('click', () => {
    if (currentConceptId === null) {
      // Cover page → navigate to prev chapter
      if (prevAdhyay) window.location.href = `adhyay.html?id=${prevAdhyay.id}`;
    } else {
      // Concept page → prev concept (or prev adhyay, or cover)
      const idx = adhyay.concepts.findIndex(c => c.id === currentConceptId);
      if (idx > 0) selectConcept(adhyay.concepts[idx - 1].id);
      else if (prevAdhyay) window.location.href = `adhyay.html?id=${prevAdhyay.id}`;
      else goToCoverPage();
    }
  });
  if (nextConceptBtn) nextConceptBtn.addEventListener('click', () => {
    if (currentConceptId === null) {
      // Cover page → navigate to next chapter
      if (nextAdhyay) window.location.href = `adhyay.html?id=${nextAdhyay.id}`;
    } else {
      // Concept page → next concept (or next adhyay)
      const idx = adhyay.concepts.findIndex(c => c.id === currentConceptId);
      if (idx < adhyay.concepts.length - 1) selectConcept(adhyay.concepts[idx + 1].id);
      else if (nextAdhyay) window.location.href = `adhyay.html?id=${nextAdhyay.id}`;
    }
  });

  // ── Select concept ─────────────────────────────────────────────
  let currentConceptId = null;
  function selectConcept(cid) {
    const concept = adhyay.concepts.find(c => c.id === cid);
    if (!concept) return;
    const adhyayBodyEl = document.getElementById('adhyay-body');
    if (adhyayBodyEl) adhyayBodyEl.scrollTop = 0;
    window.scrollTo(0, 0);
    if (suchiBtn) suchiBtn.style.display = 'none';

    // Update URL without full page reload
    const url = new URL(window.location.href);
    url.searchParams.set('concept', cid);
    history.pushState({ adhyayId, conceptId: cid }, '', url);

    // Update header label to show back-to-chapter affordance
    headerLabel.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="width:12px;height:12px;flex-shrink:0"><polyline points="15 18 9 12 15 6"/></svg> अध्याय ${adhyay.number} · ${adhyay.name}`;

    // Update concept title bar
    const idx = adhyay.concepts.findIndex(c => c.id === cid);
    if (conceptTitleBar) {
      conceptTitleBar.style.display = '';
      ctbMeta.textContent = `${concept.emoji}  संकल्पना ${concept.id}`;
      ctbName.textContent = concept.name;
    }

    // Update bottom nav with prev/next concept names
    const prevConcept = idx > 0 ? adhyay.concepts[idx - 1] : null;
    const nextConcept = idx < adhyay.concepts.length - 1 ? adhyay.concepts[idx + 1] : null;
    const prevBtn = document.getElementById('prev-concept-btn');
    const nextBtn = document.getElementById('next-concept-btn');
    if (prevBtn) {
      prevBtn.disabled = false;
      if (bnavPrevName) bnavPrevName.textContent = prevConcept
        ? `${prevConcept.emoji} ${prevConcept.name}`
        : prevAdhyay ? `${prevAdhyay.emoji} ${prevAdhyay.name}` : `अध्याय ${adhyay.number}`;
    }
    if (nextBtn) {
      nextBtn.disabled = !nextConcept && !nextAdhyay;
      if (bnavNextName) bnavNextName.textContent = nextConcept
        ? `${nextConcept.emoji} ${nextConcept.name}`
        : nextAdhyay ? `${nextAdhyay.emoji} ${nextAdhyay.name}` : '';
    }

    summarySection.style.display = 'none';
    conceptView.classList.add('visible');

    // Concept image — try .jpg → .jpeg → .png
    conceptPHEmoji.textContent = concept.emoji;
    conceptImg.style.display = '';
    conceptImg.alt = concept.name;

    // Set handlers BEFORE src so cached images still trigger onload
    conceptImg.onload = function () {
      // Only adjust columns on desktop — mobile uses CSS single-column layout
      if (window.innerWidth <= 767) return;
      const availH   = conceptView.offsetHeight;
      if (!availH || !this.naturalWidth || !this.naturalHeight) return;
      const aspect   = this.naturalWidth / this.naturalHeight;
      const idealW   = Math.round(availH * aspect);
      const minW     = 280;
      const maxW     = Math.round(window.innerWidth * 0.55);
      const colW     = Math.max(minW, Math.min(idealW, maxW));
      conceptView.style.gridTemplateColumns = `${colW}px 1fr`;
    };
    conceptImg.onerror = function () {
      if (!this.src.endsWith('.jpeg')) {
        this.src = assetPath(`concept-${concept.id}.jpeg`);
      } else if (!this.src.endsWith('.png')) {
        this.src = assetPath(`concept-${concept.id}.png`);
      } else {
        this.style.display = 'none';
        conceptPH.style.display = '';
        if (window.innerWidth > 767) {
          conceptView.style.gridTemplateColumns = '50% 1fr';
        }
      }
    };
    conceptImg.src = assetPath(`concept-${concept.id}.jpg`);
    conceptPH.style.display = 'none';

    currentConceptId = cid;

    // Concept info panel
    conceptInfoEmoji.textContent = concept.emoji;
    conceptInfoName.textContent  = concept.name;
    conceptInfoMeta.textContent  = `अध्याय ${adhyay.number} · संकल्पना ${concept.id}`;
    renderConceptText(String(adhyay.id), String(concept.id));

    // Store concept PDF url — loaded when modal opens
    pdfLabel.textContent = `संकल्पना ${concept.id} PDF`;
    pdfModalTitle.textContent = `संकल्पना ${concept.id} — ${concept.name}`;
    pendingPdfUrl = assetPath(`concept-${concept.id}.pdf`);
    renderThumb(pendingPdfUrl);
  }

  // ── Recalculate column width on window resize ─────────────────
  window.addEventListener('resize', () => {
    if (window.innerWidth <= 767) {
      conceptView.style.gridTemplateColumns = '';  // let CSS media query take over
      return;
    }
    if (conceptImg.naturalWidth && conceptImg.naturalHeight && conceptView.classList.contains('visible')) {
      const availH   = conceptView.offsetHeight;
      const aspect   = conceptImg.naturalWidth / conceptImg.naturalHeight;
      const idealW   = Math.round(availH * aspect);
      const minW     = 280;
      const maxW     = Math.round(window.innerWidth * 0.55);
      const colW     = Math.max(minW, Math.min(idealW, maxW));
      conceptView.style.gridTemplateColumns = `${colW}px 1fr`;
    }
  });

  // ── Handle browser back/forward ───────────────────────────────
  window.addEventListener('popstate', (e) => {
    const s = e.state;
    if (s && s.conceptId) {
      selectConcept(s.conceptId);
    } else {
      goToCoverPage();
    }
  });

  // ── Auto-select concept from URL ──────────────────────────────
  if (conceptId && adhyay.concepts.find(c => c.id === conceptId)) {
    selectConcept(conceptId);
  }

})();
