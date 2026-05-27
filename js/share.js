(function () {
  'use strict';

  const TOAST_TEXT = 'लिंक कॉपी झाली';
  const WHATSAPP_LABEL = 'व्हॉट्सॲप';
  const COPY_LABEL = 'लिंक कॉपी करा';

  let activePopover = null;

  function buildText(title, url) {
    return title ? title + '\n' + url : url;
  }

  function showToast(msg) {
    let el = document.querySelector('.share-toast');
    if (!el) {
      el = document.createElement('div');
      el.className = 'share-toast';
      document.body.appendChild(el);
    }
    el.textContent = msg;
    requestAnimationFrame(() => el.classList.add('show'));
    clearTimeout(el._t);
    el._t = setTimeout(() => el.classList.remove('show'), 1800);
  }

  function legacyCopy(text) {
    return new Promise((resolve, reject) => {
      try {
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.setAttribute('readonly', '');
        ta.style.position = 'fixed';
        ta.style.top = '-1000px';
        document.body.appendChild(ta);
        ta.select();
        const ok = document.execCommand('copy');
        document.body.removeChild(ta);
        ok ? resolve() : reject(new Error('execCommand returned false'));
      } catch (e) { reject(e); }
    });
  }

  function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text).catch(() => legacyCopy(text));
    }
    return legacyCopy(text);
  }

  function closePopover() {
    if (activePopover) {
      activePopover.remove();
      activePopover = null;
      document.removeEventListener('click', onDocClick, true);
      document.removeEventListener('keydown', onKeyDown, true);
    }
  }

  function onDocClick(e) {
    if (activePopover && !activePopover.contains(e.target) && e.target !== activePopover._anchor) {
      closePopover();
    }
  }

  function onKeyDown(e) {
    if (e.key === 'Escape') closePopover();
  }

  function openPopover(anchorBtn, title, url, shareText) {
    closePopover();
    const text = buildText(shareText || title, url);
    const pop = document.createElement('div');
    pop.className = 'share-popover';
    pop.setAttribute('role', 'menu');

    const wa = document.createElement('a');
    wa.className = 'share-popover-item';
    wa.href = 'https://wa.me/?text=' + encodeURIComponent(text);
    wa.target = '_blank';
    wa.rel = 'noopener noreferrer';
    wa.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.5 3.5A11 11 0 0 0 3.6 17.3L2 22l4.8-1.5A11 11 0 1 0 20.5 3.5zM12 20a8 8 0 0 1-4.1-1.1l-.3-.2-2.9.9.9-2.8-.2-.3A8 8 0 1 1 12 20zm4.5-5.6c-.2-.1-1.4-.7-1.7-.8-.2-.1-.3-.1-.5.1-.1.2-.6.7-.7.9-.1.1-.3.2-.5 0a6.4 6.4 0 0 1-3.2-2.8c-.2-.4.2-.4.6-1.2.1-.2 0-.3 0-.5l-.7-1.7c-.2-.4-.4-.4-.5-.4h-.5c-.2 0-.4.1-.6.3a2.4 2.4 0 0 0-.7 1.7c0 1 .7 2 .8 2.1.1.2 1.4 2.2 3.5 3.1 1.3.5 1.8.6 2.4.5.4 0 1.4-.5 1.6-1.1.2-.5.2-1 .1-1.1 0-.1-.2-.2-.4-.3z"/></svg><span>' + WHATSAPP_LABEL + '</span>';

    const copyBtn = document.createElement('button');
    copyBtn.type = 'button';
    copyBtn.className = 'share-popover-item';
    copyBtn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg><span>' + COPY_LABEL + '</span>';
    copyBtn.addEventListener('click', () => {
      copyToClipboard(url).then(() => {
        showToast(TOAST_TEXT);
      }).catch(() => {
        showToast('कॉपी अयशस्वी');
      }).finally(closePopover);
    });

    pop.appendChild(wa);
    pop.appendChild(copyBtn);
    pop._anchor = anchorBtn;

    const wrap = document.createElement('span');
    wrap.className = 'share-anchor-wrap';
    anchorBtn.parentNode.insertBefore(wrap, anchorBtn);
    wrap.appendChild(anchorBtn);
    wrap.appendChild(pop);

    activePopover = pop;
    setTimeout(() => {
      document.addEventListener('click', onDocClick, true);
      document.addEventListener('keydown', onKeyDown, true);
    }, 0);
  }

  function getTitleFromDocument() {
    const t = (document.title || '').trim();
    return t.replace(/\s*[·\|]\s*गीता-ज्ञानेश्वरी\s*$/, '').trim() || t;
  }

  function handleShare(buttonEl, getShareData) {
    const data = getShareData();
    if (!data || !data.url) return;
    const title    = data.title || getTitleFromDocument();
    const url      = data.url;
    const shareText = data.text || title;  // optional rich body (e.g. install instructions)

    if (navigator.share) {
      // shareText as body so the URL (carried by `url`) appears only once
      navigator.share({ title, text: shareText, url }).catch(() => {});
      return;
    }
    openPopover(buttonEl, title, url, shareText);
  }

  window.initShareButton = function (buttonEl, getShareData) {
    if (!buttonEl || typeof getShareData !== 'function') return;
    if (buttonEl._shareBound) return;
    buttonEl._shareBound = true;
    buttonEl.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      handleShare(buttonEl, getShareData);
    });
  };

  window.autoInitSankalpanaShare = function () {
    const btn = document.getElementById('share-btn');
    if (!btn) return;
    window.initShareButton(btn, () => ({
      title: getTitleFromDocument(),
      url: window.location.href.split('#')[0]
    }));
  };
})();
