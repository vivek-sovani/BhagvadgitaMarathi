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
  const conceptTextContent  = document.getElementById('concept-text-content');
  const conceptTabs         = document.getElementById('concept-tabs');
  const conceptStoryContent = document.getElementById('concept-story-content');
  const pdfLabel         = document.getElementById('pdf-label');
  const pdfOpenBar       = document.querySelector('.pdf-open-bar');
  const pdfModal         = document.getElementById('pdf-modal');
  const pdfModalTitle    = document.getElementById('pdf-modal-title');
  const pdfModalClose    = document.getElementById('pdf-modal-close');
  const pdfModalBackdrop = document.getElementById('pdf-modal-backdrop');
  const pdfIframe        = document.getElementById('pdf-iframe');

  // ── Adhyay PDF inline viewer ──────────────────────────────────
  let pendingPdfUrl = null;

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

  // pdf-open-btn removed — adhyay PDF now uses inline viewer (renderStoryPdfPages)
  pdfModalClose.addEventListener('click', closePdfModal);
  pdfModalBackdrop.addEventListener('click', closePdfModal);

  // Opens a story-PDF in the same modal used for vivechan PDFs
  function openStoryPdf(url, title) {
    pendingPdfUrl = url;
    pdfModalTitle.textContent = title;
    openPdfModal(title);
  }

  // Renders all pages of a PDF as horizontal canvases inside containerId
  async function renderStoryPdfPages(url, containerId) {
    const container = document.getElementById(containerId);
    if (!container || typeof pdfjsLib === 'undefined') return;
    try {
      const pdf = await pdfjsLib.getDocument({ url }).promise;
      container.innerHTML = ''; // clear loading spinner
      const dpr     = window.devicePixelRatio || 1;
      // Logical (CSS) pixel dimensions the slide is displayed at
      const targetW = container.clientWidth  > 0 ? container.clientWidth  : Math.max(300, window.innerWidth  - 32);
      const targetH = container.clientHeight > 0 ? container.clientHeight : Math.round(window.innerHeight * 0.52);
      for (let p = 1; p <= pdf.numPages; p++) {
        const page  = await pdf.getPage(p);
        const rotation = page.rotate || 0;
        const vp0   = page.getViewport({ scale: 1, rotation });
        // Logical "contain" scale — whole page fits within (targetW × targetH)
        const logicalScale = Math.min(targetW / vp0.width, targetH / vp0.height);
        // Render at dpr× for sharp text on retina/high-dpi screens
        const vp    = page.getViewport({ scale: logicalScale * dpr, rotation });
        const canvas = document.createElement('canvas');
        canvas.width  = vp.width;   // physical px (e.g. 3× on iPhone)
        canvas.height = vp.height;
        // CSS size stays at logical px so the canvas isn't displayed bigger than rendered
        canvas.style.width  = Math.round(vp.width  / dpr) + 'px';
        canvas.style.height = Math.round(vp.height / dpr) + 'px';
        canvas.className = 'story-pdf-page';
        await page.render({ canvasContext: canvas.getContext('2d'), viewport: vp }).promise;
        // Wrap in a slide div — scroll-snap snaps exactly one full page at a time
        const slide = document.createElement('div');
        slide.className = 'story-pdf-slide';
        slide.appendChild(canvas);
        container.appendChild(slide);
      }
    } catch (e) {
      container.innerHTML = '<div class="story-pdf-error">PDF लोड होऊ शकले नाही</div>';
    }
  }



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
  pdfLabel.textContent = `📄 अध्याय ${adhyay.number} सादरीकरण`;
  pendingPdfUrl = assetPath('adhyay.pdf');
  // Only render now if no concept will be selected immediately
  // (avoids racing with the concept PDF render in selectConcept)
  const initialConceptId = parseInt(params.get('concept'), 10) || null;
  if (!initialConceptId || !adhyay.concepts.find(c => c.id === initialConceptId)) {
    renderStoryPdfPages(pendingPdfUrl, 'adhyay-pdf-pages');
  }

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

  // ── Story tab helpers ─────────────────────────────────────────

  function showConceptTab(tab) {
    if (conceptTabs) {
      conceptTabs.querySelectorAll('.ctab-btn').forEach(b =>
        b.classList.toggle('ctab-active', b.dataset.tab === tab));
    }
    if (conceptTextContent)   conceptTextContent.style.display   = tab === 'vivechan' ? '' : 'none';
    if (conceptStoryContent)  conceptStoryContent.style.display  = tab === 'katha'    ? '' : 'none';
  }

  // Wire tab click events once (at init)
  if (conceptTabs) {
    conceptTabs.querySelectorAll('.ctab-btn').forEach(btn => {
      btn.addEventListener('click', () => showConceptTab(btn.dataset.tab));
    });
  }

  function renderStory(adhyayIdStr, conceptIdStr) {
    const el = conceptStoryContent;
    if (!el) return false;
    const entry = (typeof GITA_STORIES !== 'undefined')
      && GITA_STORIES[parseInt(adhyayIdStr)]
      && GITA_STORIES[parseInt(adhyayIdStr)][conceptIdStr];
    if (!entry) { el.innerHTML = ''; return false; }

    const { shloka, conceptSummary, story } = entry;
    const pdfPagesId = `spdf-${adhyayIdStr}-${conceptIdStr}`;
    let html = '';

    // ── Inline PDF viewer (horizontally scrollable pages) ─────
    if (entry.pdfUrl) {
      html += `<div class="story-pdf-viewer">
        <div class="story-pdf-viewer-label">📖 कथा</div>
        <div class="story-pdf-pages" id="${pdfPagesId}">
          <div class="story-pdf-loading">PDF लोड होत आहे…</div>
        </div>
        <div class="story-pdf-swipe-hint">← स्वाइप करून पाने पहा →</div>
      </div>`;
    }

    // ── Shloka card ───────────────────────────────────────────
    if (shloka) {
      html += `<div class="story-shloka-card">
        <div class="story-shloka-label">मूळ श्लोक · ${shloka.ref}</div>
        <div class="story-shloka-text">${shloka.text.replace(/\n/g, '<br>')}</div>
        <div class="story-shloka-meaning">${shloka.meaning}</div>
      </div>`;
    }

    // ── Concept summary ───────────────────────────────────────
    if (conceptSummary) {
      html += `<div class="story-concept-summary">${conceptSummary}</div>`;
    }

    if (entry.pdfUrl) {
      // ── PDF MODE: skip narrative; show only Gita connect + reflection/sankalp ──
      html += `<div class="story-card">`;
      html += `<div class="story-gita-connect">
        <div class="story-gc-label">🕉️ गीता संदेश · The Gita Parallel</div>
        <div class="story-gc-text">${story.gitaConnect}</div>
      </div>`;
      html += `<div class="story-reflection-sankalp">
        <div class="story-reflection">
          <div class="story-rs-label">💔 स्वतःला विचारा</div>
          <div class="story-rs-text">${story.reflection}</div>
        </div>
        <div class="story-sankalp">
          <div class="story-rs-label">🌱 आजचा संकल्प</div>
          <div class="story-rs-text">${story.sankalp}</div>
        </div>
      </div>`;
      html += `</div>`; // end .story-card
      el.innerHTML = html;
      renderStoryPdfPages(entry.pdfUrl, pdfPagesId);
      return true;
    }

    // ── HTML MODE: full story card ────────────────────────────
    html += `<div class="story-card">`;

    // Scene strip
    html += `<div class="story-scene-strip">
      <div class="story-scene-label">परिस्थिती · Setting</div>
      <div class="story-scene-title">${story.scene.title}</div>
      <div class="story-scene-subtitle">${story.scene.subtitle}</div>
    </div>`;

    // Story body
    html += `<div class="story-body">`;
    html += `<div class="story-ornament">· · ·</div>`;

    // Characters
    if (story.characters && story.characters.length) {
      html += `<div class="story-characters">`;
      story.characters.forEach(c => {
        html += `<span class="story-char-tag">${c.emoji} <strong>${c.role}</strong> — ${c.desc}</span>`;
      });
      html += `</div>`;
    }

    // Body items — para, dialogue + rich adhyay-2 types
    story.body.forEach(item => {
      if (item.type === 'para') {
        html += `<p class="story-para">${item.text}</p>`;
      } else if (item.type === 'dialogue') {
        html += `<div class="story-dialogue">
          <div class="story-dialogue-speaker">${item.speaker}</div>
          <div class="story-dialogue-text">${item.text}</div>
        </div>`;
      } else if (item.type === 'inner-thought') {
        html += `<div class="story-inner-thought">
          <div class="story-it-speaker">${item.speaker}</div>
          <div class="story-it-text">${item.text}</div>
        </div>`;
      } else if (item.type === 'hbox') {
        html += `<div class="story-hbox story-hbox-${item.variant || 'gold'}">
          <div class="story-hbox-label">${item.label}</div>
          <div class="story-hbox-text">${item.text}</div>
        </div>`;
      } else if (item.type === 'contrast') {
        html += `<div class="story-contrast">`;
        item.items.forEach(ci => {
          html += `<div class="story-contrast-item story-contrast-${ci.side}">
            <span class="story-contrast-icon">${ci.icon}</span>
            <div class="story-contrast-label">${ci.label}</div>
            <div class="story-contrast-text">${ci.text}</div>
          </div>`;
        });
        html += `</div>`;
      } else if (item.type === 'diary') {
        html += `<div class="story-diary">
          <div class="story-diary-label">${item.label}</div>
          <div class="story-diary-text">${item.text}</div>
        </div>`;
      } else if (item.type === 'layers') {
        html += `<div class="story-layers"><div class="story-layers-header">${item.header}</div>`;
        item.items.forEach(li => {
          html += `<div class="story-layer-row">
            <div class="story-layer-num">${li.num}</div>
            <div class="story-layer-content">
              <div class="story-layer-title">${li.title}</div>
              ${li.gita ? `<div class="story-layer-gita">${li.gita}</div>` : ''}
              <div class="story-layer-story">${li.story}</div>
            </div>
          </div>`;
        });
        html += `</div>`;
      } else if (item.type === 'grid') {
        html += `<div class="story-grid">`;
        if (item.header) html += `<div class="story-grid-header">${item.header}</div>`;
        html += `<div class="story-grid-cells story-grid-cols-${item.cols || 2}">`;
        item.items.forEach(gi => {
          html += `<div class="story-grid-cell">
            <span class="story-grid-icon">${gi.icon}</span>
            <div class="story-grid-label">${gi.label}</div>
            ${gi.shloka ? `<div class="story-grid-shloka">${gi.shloka}</div>` : ''}
            <div class="story-grid-text">${gi.text}</div>
          </div>`;
        });
        html += `</div></div>`;
      } else if (item.type === 'traits') {
        html += `<div class="story-traits"><div class="story-traits-header">${item.header}</div>`;
        item.items.forEach(ti => {
          html += `<div class="story-trait-row">
            <span class="story-trait-emoji">${ti.emoji}</span>
            <div class="story-trait-text">${ti.text}</div>
          </div>`;
        });
        html += `</div>`;
      } else if (item.type === 'vastra') {
        html += `<div class="story-vastra">
          <div class="story-vastra-header">${item.header}</div>
          <div class="story-vastra-grid">
            <div class="story-vastra-side">
              <span class="story-vastra-icon">${item.left.icon}</span>
              <div class="story-vastra-label story-vastra-left-label">${item.left.label}</div>
              <div class="story-vastra-text">${item.left.text}</div>
            </div>
            <div class="story-vastra-arrow">→</div>
            <div class="story-vastra-side">
              <span class="story-vastra-icon">${item.right.icon}</span>
              <div class="story-vastra-label story-vastra-right-label">${item.right.label}</div>
              <div class="story-vastra-text">${item.right.text}</div>
            </div>
          </div>
          <div class="story-vastra-footer">${item.footer}</div>
        </div>`;
      }
    });

    // Turning point
    html += `<div class="story-turning-point">
      <div class="story-tp-label">कथेचा वळणबिंदू · The Gita Moment</div>
      <div class="story-tp-text">${story.turningPoint}</div>
    </div>`;

    html += `</div>`; // end .story-body

    // Optional adhyay-end summary strip (last concept of an adhyay)
    if (story.adhyayEnd) {
      html += `<div class="story-adhyay-end"><div class="story-ae-label">${story.adhyayEnd.label}</div>`;
      story.adhyayEnd.items.forEach(ai => {
        html += `<div class="story-ae-row">
          <div class="story-ae-num">${ai.num}</div>
          <span class="story-ae-emoji">${ai.emoji}</span>
          <div class="story-ae-text">${ai.text}</div>
        </div>`;
      });
      html += `</div>`;
    }

    // Gita connect
    html += `<div class="story-gita-connect">
      <div class="story-gc-label">🕉️ गीता संदेश · The Gita Parallel</div>
      <div class="story-gc-text">${story.gitaConnect}</div>
    </div>`;

    // Reflection + sankalp
    html += `<div class="story-reflection-sankalp">
      <div class="story-reflection">
        <div class="story-rs-label">💔 स्वतःला विचारा</div>
        <div class="story-rs-text">${story.reflection}</div>
      </div>
      <div class="story-sankalp">
        <div class="story-rs-label">🌱 आजचा संकल्प</div>
        <div class="story-rs-text">${story.sankalp}</div>
      </div>
    </div>`;

    html += `</div>`; // end .story-card

    el.innerHTML = html;
    return true;
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
    pdfLabel.textContent = `📄 अध्याय ${adhyay.number} सादरीकरण`;
    pendingPdfUrl = assetPath('adhyay.pdf');
    renderStoryPdfPages(pendingPdfUrl, 'adhyay-pdf-pages');
    if (pdfOpenBar) pdfOpenBar.style.display = ''; // restore adhyay PDF viewer
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
        : prevAdhyay ? `अध्याय ${prevAdhyay.number} · ${prevAdhyay.emoji} ${prevAdhyay.name}` : `अध्याय ${adhyay.number}`;
    }
    if (nextBtn) {
      nextBtn.disabled = !nextConcept && !nextAdhyay;
      if (bnavNextName) bnavNextName.textContent = nextConcept
        ? `${nextConcept.emoji} ${nextConcept.name}`
        : nextAdhyay ? `अध्याय ${nextAdhyay.number} · ${nextAdhyay.emoji} ${nextAdhyay.name}` : '';
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

    // Inject inline PDF viewer at bottom of vivechan content
    const cpdfId = `cpdf-${adhyay.id}-${cid}`;
    const pdfViewerEl = document.createElement('div');
    pdfViewerEl.className = 'story-pdf-viewer concept-pdf-viewer';
    pdfViewerEl.innerHTML = `
      <div class="story-pdf-viewer-label">📄 संकल्पना ${concept.id} सादरीकरण</div>
      <div class="story-pdf-pages" id="${cpdfId}">
        <div class="story-pdf-loading">PDF लोड होत आहे…</div>
      </div>
      <div class="story-pdf-swipe-hint">← स्वाइप करून पाने पहा →</div>`;
    conceptTextContent.appendChild(pdfViewerEl);

    const hasStory = renderStory(String(adhyay.id), String(concept.id));
    if (conceptTabs) conceptTabs.style.display = hasStory ? '' : 'none';

    // ── कथा prompt card at bottom of विवेचन (only when story exists) ──
    if (hasStory) {
      const kathaPrompt = document.createElement('div');
      kathaPrompt.className = 'katha-prompt-card';
      kathaPrompt.innerHTML = `
        <div class="katha-prompt-icon">📖</div>
        <div class="katha-prompt-text">
          <div class="katha-prompt-title">कथा वाचा</div>
          <div class="katha-prompt-sub">या संकल्पनेशी संबंधित जीवनकथा</div>
        </div>
        <div class="katha-prompt-arrow">→</div>`;
      kathaPrompt.addEventListener('click', () => showConceptTab('katha'));
      conceptTextContent.appendChild(kathaPrompt);
    }

    showConceptTab('vivechan'); // always land on विवेचन when switching concepts

    // Concept PDF — inline viewer replaces the thumbnail card
    if (pdfOpenBar) pdfOpenBar.style.display = 'none';
    pdfLabel.textContent = `📄 संकल्पना ${concept.id} सादरीकरण`;
    pdfModalTitle.textContent = `संकल्पना ${concept.id} — ${concept.name}`;
    pendingPdfUrl = assetPath(`concept-${concept.id}.pdf`);
    renderStoryPdfPages(pendingPdfUrl, cpdfId);
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
