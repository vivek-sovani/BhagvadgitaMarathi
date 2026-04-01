/**
 * PDFCarousel — renders a PDF as a navigable page carousel using PDF.js
 * Usage:
 *   const carousel = new PDFCarousel(document.getElementById('my-carousel'));
 *   await carousel.load('assets/adhyay-4/adhyay.pdf');
 */

// PDF.js worker setup (loaded from CDN in HTML)
class PDFCarousel {
  constructor(containerEl) {
    this.container = containerEl;
    this.pdfDoc    = null;
    this.pageNum   = 1;
    this.pageCount = 0;
    this.rendering = false;
    this.currentUrl = null;
    this._touchStartX = 0;

    this._buildDOM();
    this._bindEvents();
  }

  _buildDOM() {
    this.container.innerHTML = `
      <div class="pdf-carousel-wrap">
        <div class="pdf-carousel-inner" tabindex="0" role="region" aria-label="PDF दर्शक">
          <button class="pdf-nav-btn prev" aria-label="मागील पान" disabled>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="15 18 9 12 15 6"/>
            </svg>
          </button>
          <div class="pdf-canvas-area"></div>
          <button class="pdf-nav-btn next" aria-label="पुढील पान" disabled>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="9 18 15 12 9 6"/>
            </svg>
          </button>
        </div>
        <div class="pdf-carousel-footer">
          <span class="pdf-page-counter">— / —</span>
        </div>
      </div>
    `;

    this.inner      = this.container.querySelector('.pdf-carousel-inner');
    this.canvasArea = this.container.querySelector('.pdf-canvas-area');
    this.prevBtn    = this.container.querySelector('.pdf-nav-btn.prev');
    this.nextBtn    = this.container.querySelector('.pdf-nav-btn.next');
    this.counter    = this.container.querySelector('.pdf-page-counter');

    this._showPlaceholder('📄', 'PDF लोड होत आहे…');
  }

  _bindEvents() {
    this.prevBtn.addEventListener('click', () => this.prev());
    this.nextBtn.addEventListener('click', () => this.next());

    // Keyboard navigation
    this.inner.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft')  { e.preventDefault(); this.prev(); }
      if (e.key === 'ArrowRight') { e.preventDefault(); this.next(); }
    });

    // Touch swipe
    this.inner.addEventListener('touchstart', (e) => {
      this._touchStartX = e.changedTouches[0].clientX;
    }, { passive: true });
    this.inner.addEventListener('touchend', (e) => {
      const dx = e.changedTouches[0].clientX - this._touchStartX;
      if (Math.abs(dx) > 40) {
        if (dx < 0) this.next();
        else        this.prev();
      }
    }, { passive: true });
  }

  async load(url) {
    if (!url) { this._showPlaceholder('📂', 'PDF उपलब्ध नाही'); return; }
    if (this.currentUrl === url && this.pdfDoc) return; // only skip if already loaded OK
    this.currentUrl = url;

    this._showLoading();
    this.pdfDoc  = null;
    this.pageNum = 1;

    try {
      const loadingTask = pdfjsLib.getDocument({ url, cMapPacked: true });
      this.pdfDoc    = await loadingTask.promise;
      this.pageCount = this.pdfDoc.numPages;
      // Wait for layout to be fully computed before rendering
      await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
      await this._renderPage(this.pageNum);
    } catch (err) {
      console.error('PDF load error:', url, err);
      this.currentUrl = null; // allow retry
      this._showPlaceholder('⚠️', 'PDF उघडता आला नाही');
    }
  }

  async _renderPage(num) {
    if (this.rendering || !this.pdfDoc) return;
    this.rendering = true;

    try {
      const page = await this.pdfDoc.getPage(num);

      // Scale to fit container width (nav buttons are absolute, don't subtract much)
      const btnMargin  = window.innerWidth < 480 ? 16 : 80;
      const containerW = this.inner.clientWidth - btnMargin;
      const viewport0  = page.getViewport({ scale: 1 });
      const scale      = Math.min(containerW / viewport0.width, 2.5);
      const viewport   = page.getViewport({ scale });

      let canvas = this.canvasArea.querySelector('canvas');
      if (!canvas) {
        this.canvasArea.innerHTML = '';
        canvas = document.createElement('canvas');
        this.canvasArea.appendChild(canvas);
      }
      const ctx = canvas.getContext('2d');
      canvas.width  = viewport.width;
      canvas.height = viewport.height;

      await page.render({ canvasContext: ctx, viewport }).promise;

      this.pageNum = num;
      this._updateControls();
    } catch (err) {
      console.warn('Page render error:', err);
    } finally {
      this.rendering = false;
    }
  }

  _updateControls() {
    this.counter.textContent  = `${this.pageNum} / ${this.pageCount}`;
    this.prevBtn.disabled     = this.pageNum <= 1;
    this.nextBtn.disabled     = this.pageNum >= this.pageCount;
  }

  prev() { if (this.pageNum > 1 && !this.rendering) this._renderPage(this.pageNum - 1); }
  next() { if (this.pageNum < this.pageCount && !this.rendering) this._renderPage(this.pageNum + 1); }

  _showPlaceholder(icon, msg) {
    this.canvasArea.innerHTML = `
      <div class="pdf-placeholder-msg">
        <span class="ph-icon">${icon}</span>
        <span>${msg}</span>
      </div>`;
    this.counter.textContent = '— / —';
    this.prevBtn.disabled = true;
    this.nextBtn.disabled = true;
  }

  _showLoading() {
    this.canvasArea.innerHTML = `
      <div class="pdf-loading">
        <div class="spinner"></div>
        <span>PDF लोड होत आहे…</span>
      </div>`;
    this.counter.textContent = '— / —';
    this.prevBtn.disabled = true;
    this.nextBtn.disabled = true;
  }

  reset() {
    this.currentUrl = null;
    this.pdfDoc     = null;
    this.pageNum    = 1;
    this.pageCount  = 0;
    this._showPlaceholder('📄', 'PDF निवडा');
  }
}
