(function () {
  const LANG_KEY = 'gita-lang';
  const DEFAULT = 'mr';

  function applyLang(lang, dispatch) {
    document.documentElement.lang = lang;
    if (typeof GITA_I18N !== 'undefined') {
      document.querySelectorAll('[data-i18n]').forEach(function (el) {
        const val = (GITA_I18N[lang] || GITA_I18N.mr)[el.dataset.i18n];
        if (val !== undefined) el.textContent = val;
      });
    }
    document.querySelectorAll('.lang-toggle').forEach(function (btn) {
      const en = btn.querySelector('.lt-en');
      const mr = btn.querySelector('.lt-mr');
      if (en) en.classList.toggle('lt-active', lang === 'en');
      if (mr) mr.classList.toggle('lt-active', lang === 'mr');
    });
    if (dispatch) {
      document.dispatchEvent(new CustomEvent('langchange', { detail: { lang: lang } }));
    }
  }

  function makeBtn() {
    const btn = document.createElement('button');
    btn.className = 'lang-toggle';
    btn.setAttribute('aria-label', 'भाषा बदला / Change language');
    btn.innerHTML =
      '<span class="lt-en">EN</span>' +
      '<span class="lt-sep"> | </span>' +
      '<span class="lt-mr">मर</span>';
    btn.addEventListener('click', function () {
      const next = document.documentElement.lang === 'en' ? 'mr' : 'en';
      localStorage.setItem(LANG_KEY, next);
      applyLang(next, true);
    });
    return btn;
  }

  function init() {
    const lang = localStorage.getItem(LANG_KEY) || DEFAULT;
    applyLang(lang, false);

    ['nav-lang-slot', 'mobile-nav-lang-slot'].forEach(function (id) {
      const slot = document.getElementById(id);
      if (slot) slot.appendChild(makeBtn());
    });

    // Re-apply so newly created buttons get their active class
    applyLang(lang, false);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
