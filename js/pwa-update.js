(function () {
  'use strict';
  if (!('serviceWorker' in navigator)) return;

  function showUpdateBar() {
    if (document.getElementById('pwa-update-bar')) return; // already visible

    var bar = document.createElement('div');
    bar.id = 'pwa-update-bar';
    bar.setAttribute('role', 'alert');
    bar.setAttribute('aria-live', 'polite');

    // Inline styles so no CSS file dependency
    bar.style.cssText = [
      'position:fixed', 'bottom:0', 'left:0', 'right:0', 'z-index:9999',
      'background:var(--ink,#1f1812)', 'color:var(--bg,#f6efe2)',
      'padding:14px clamp(16px,4vw,32px)',
      'display:flex', 'align-items:center', 'justify-content:space-between',
      'gap:12px', 'flex-wrap:wrap',
      'font-family:var(--serif-dev,sans-serif)', 'font-size:14.5px',
      'box-shadow:0 -2px 20px rgba(0,0,0,0.25)',
      'transform:translateY(110%)',
      'transition:transform 0.35s cubic-bezier(.4,0,.2,1)'
    ].join(';');

    var msg = document.createElement('span');
    msg.textContent = '🔄 नवीन आवृत्ती उपलब्ध आहे';

    var refreshBtn = document.createElement('button');
    refreshBtn.textContent = 'अपडेट करा';
    refreshBtn.style.cssText = [
      'background:var(--saffron-deep,#9c4a10)', 'color:#fff',
      'border:none', 'border-radius:999px',
      'padding:7px 20px', 'font-size:14px', 'font-weight:600',
      'cursor:pointer', 'font-family:inherit', 'white-space:nowrap',
      'flex-shrink:0'
    ].join(';');
    refreshBtn.addEventListener('click', function () {
      window.location.reload();
    });

    var closeBtn = document.createElement('button');
    closeBtn.setAttribute('aria-label', 'बंद करा');
    closeBtn.innerHTML = '&times;';
    closeBtn.style.cssText = [
      'background:none', 'border:none', 'color:inherit',
      'font-size:20px', 'line-height:1', 'cursor:pointer',
      'padding:4px 8px', 'opacity:0.65', 'flex-shrink:0'
    ].join(';');
    closeBtn.addEventListener('click', function () {
      bar.style.transform = 'translateY(110%)';
      setTimeout(function () { if (bar.parentNode) bar.remove(); }, 400);
    });

    bar.appendChild(msg);
    bar.appendChild(refreshBtn);
    bar.appendChild(closeBtn);
    document.body.appendChild(bar);

    // Slide in
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        bar.style.transform = 'translateY(0)';
      });
    });

    // Auto-dismiss after 60 seconds if user ignores it
    setTimeout(function () {
      if (!bar.parentNode) return;
      bar.style.transform = 'translateY(110%)';
      setTimeout(function () { if (bar.parentNode) bar.remove(); }, 400);
    }, 60000);
  }

  // When a new SW activates (skipWaiting + clients.claim already done in sw.js),
  // the browser fires 'controllerchange' on every open tab. Show the banner.
  navigator.serviceWorker.addEventListener('controllerchange', function () {
    showUpdateBar();
  });

  // Edge case: if the page loaded while a new SW was already waiting
  // (e.g. opened from a cached link), check on registration
  navigator.serviceWorker.getRegistration().then(function (reg) {
    if (reg && reg.waiting) showUpdateBar();
  }).catch(function () {});
})();
