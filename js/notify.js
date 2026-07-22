// Daily sankalpana notification engine.
// No push server: while the app is open (foreground or backgrounded-but-alive),
// this checks whether it's past the user's chosen time and today's notification
// hasn't fired yet, then shows one via the service worker. Settings are reachable
// from the hamburger menu on every page that loads this script.
//
// Inside the installed Android app (TWA), that "only while open" check isn't good
// enough, so saved settings are also handed off to a native AlarmManager-based
// scheduler (see GitaMarathiTWA's ScheduleBridgeActivity/DailyAlarmReceiver) via a
// gitamarathi://schedule deep link — native code then owns actually firing the
// notification there, and this file's own showNotification call is skipped in that
// context to avoid double notifications. Plain-browser/non-TWA installs are
// unaffected and keep the original best-effort behavior.
(function () {
  'use strict';

  var SETTINGS_KEY = 'gita-notify-settings';
  var LAST_KEY = 'gita-notify-last';
  var START_DATE = new Date(2026, 3, 20); // 2026-04-20 — same epoch as the daily email's day index

  function isTWA() {
    return document.referrer.indexOf('android-app://') === 0;
  }

  // Hands the enabled/hour/minute choice to the native scheduler inside the TWA.
  // Must be a direct top-level navigation (not a hidden iframe) — Chrome blocks
  // intent:// activation from iframes as an anti-abuse measure. A user gesture
  // (this only ever runs from the Save button's click handler) is required too.
  // Chrome intercepts the matching intent:// before any real navigation happens,
  // so the page itself doesn't actually change.
  function bridgeToNative(enabled, hour, minute) {
    if (!isTWA()) return;
    try {
      var uri = 'intent://schedule?enabled=' + (enabled ? '1' : '0') +
        '&hour=' + hour + '&minute=' + minute +
        '#Intent;scheme=gitamarathi;package=io.github.viveksovani.gitamarathi;end';
      window.location.href = uri;
    } catch (e) {}
  }

  function loadSettings() {
    var fallback = { enabled: false, hour: 7, minute: 0 };
    try {
      var raw = localStorage.getItem(SETTINGS_KEY);
      if (!raw) return fallback;
      var p = JSON.parse(raw);
      return {
        enabled: !!p.enabled,
        hour: Number.isInteger(p.hour) && p.hour >= 0 && p.hour <= 23 ? p.hour : fallback.hour,
        minute: Number.isInteger(p.minute) && p.minute >= 0 && p.minute <= 59 ? p.minute : fallback.minute
      };
    } catch (e) {
      return fallback;
    }
  }

  function saveSettings(s) {
    try { localStorage.setItem(SETTINGS_KEY, JSON.stringify(s)); } catch (e) {}
  }

  function pad2(n) { return n < 10 ? '0' + n : '' + n; }

  function todayStr(d) {
    return d.getFullYear() + '-' + pad2(d.getMonth() + 1) + '-' + pad2(d.getDate());
  }

  function getLastNotified() {
    try { return localStorage.getItem(LAST_KEY) || ''; } catch (e) { return ''; }
  }

  function setLastNotified(str) {
    try { localStorage.setItem(LAST_KEY, str); } catch (e) {}
  }

  function isInSankalpana() {
    return /\/sankalpana\//.test(location.pathname);
  }

  function assetPath(p) {
    return (isInSankalpana() ? '../' : '') + p;
  }

  function sankalpanaUrl(slug) {
    return new URL(assetPath('sankalpana/' + slug + '.html'), location.href).href;
  }

  function todaysSankalpana() {
    var list = window.SANKALPANA_LIST;
    if (!list || !list.length) return null;
    var now = new Date();
    var start = new Date(START_DATE.getFullYear(), START_DATE.getMonth(), START_DATE.getDate());
    var today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    var days = Math.round((today - start) / 86400000);
    var idx = ((days % list.length) + list.length) % list.length;
    return list[idx];
  }

  function registerSW() {
    if (!('serviceWorker' in navigator)) return;
    try {
      if (isInSankalpana()) {
        navigator.serviceWorker.register('../sw.js', { scope: '../' });
      } else {
        navigator.serviceWorker.register('./sw.js');
      }
    } catch (e) {}
  }

  function maybeNotify() {
    if (isTWA()) return; // native AlarmManager-based scheduler owns delivery here
    if (!('Notification' in window) || Notification.permission !== 'granted') return;
    var settings = loadSettings();
    if (!settings.enabled) return;

    var now = new Date();
    var nowMinutes = now.getHours() * 60 + now.getMinutes();
    var targetMinutes = settings.hour * 60 + settings.minute;
    if (nowMinutes < targetMinutes) return;

    var today = todayStr(now);
    if (getLastNotified() === today) return;

    var item = todaysSankalpana();
    if (!item) return;

    setLastNotified(today); // set before showing so a rapid double-fire (interval + visibilitychange) can't double-notify

    var title = 'गीता-ज्ञानेश्वरी';
    var options = {
      body: 'आजची संकल्पना: ' + item.title,
      icon: assetPath('assets/icons/icon-192.png'),
      tag: 'daily-sankalpana',
      data: { url: sankalpanaUrl(item.slug) }
    };

    if (navigator.serviceWorker && navigator.serviceWorker.ready) {
      navigator.serviceWorker.ready.then(function (reg) {
        reg.showNotification(title, options);
      }).catch(function () {});
    } else if (typeof Notification === 'function') {
      var n = new Notification(title, options);
      n.onclick = function () { window.open(options.data.url, '_blank'); };
    }
  }

  // ---------- Settings UI (built inline, no extra CSS file dependency) ----------

  var modalEl = null;

  function closeModal() {
    if (modalEl && modalEl.parentNode) modalEl.parentNode.removeChild(modalEl);
    modalEl = null;
  }

  function permissionNote() {
    if (!('Notification' in window)) return 'या ब्राउझरमध्ये सूचना सुविधा उपलब्ध नाही.';
    if (Notification.permission === 'denied') return '⚠️ सूचना परवानगी नाकारली आहे — फोनच्या अ‍ॅप सेटिंग्जमधून सूचना सुरू करा.';
    return '';
  }

  function openModal() {
    closeModal();

    var settings = loadSettings();
    var item = todaysSankalpana();

    var backdrop = document.createElement('div');
    backdrop.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.55);z-index:9998;';

    var card = document.createElement('div');
    card.setAttribute('role', 'dialog');
    card.setAttribute('aria-modal', 'true');
    card.setAttribute('aria-label', 'दैनंदिन सूचना सेटिंग्ज');
    card.style.cssText = [
      'position:fixed', 'top:50%', 'left:50%', 'transform:translate(-50%,-50%)',
      'z-index:9999', 'width:min(360px, calc(100vw - 40px))', 'max-height:calc(100vh - 40px)',
      'overflow:auto', 'background:var(--surface,#fbf6ea)', 'color:var(--ink,#1f1812)',
      'border-radius:var(--radius,10px)', 'box-shadow:var(--shadow-lg,0 10px 25px rgba(0,0,0,0.2))',
      'padding:22px', 'font-family:var(--sans-dev,sans-serif)'
    ].join(';');

    var noteHtml = permissionNote();
    var previewHtml = item
      ? '<div style="margin-top:4px;font-size:13px;color:var(--ink-soft,#4a3d31);">आजची संकल्पना: <strong>' + item.title + '</strong></div>'
      : '';

    card.innerHTML =
      '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">' +
        '<span style="font-weight:700;font-size:16px;">🔔 दैनंदिन सूचना</span>' +
        '<button type="button" id="notify-modal-close" aria-label="बंद करा" style="background:none;border:none;font-size:18px;cursor:pointer;color:inherit;width:32px;height:32px;border-radius:50%;">✕</button>' +
      '</div>' +
      '<label style="display:flex;align-items:center;gap:10px;font-size:14.5px;cursor:pointer;margin-bottom:14px;">' +
        '<input type="checkbox" id="notify-enabled" style="width:18px;height:18px;accent-color:var(--saffron-deep,#9c4a10);"' + (settings.enabled ? ' checked' : '') + ' />' +
        '<span>रोज एक नवीन संकल्पना सूचना म्हणून पाठवा</span>' +
      '</label>' +
      '<label style="display:flex;align-items:center;justify-content:space-between;gap:10px;font-size:14.5px;margin-bottom:6px;">' +
        '<span>वेळ</span>' +
        '<input type="time" id="notify-time" value="' + pad2(settings.hour) + ':' + pad2(settings.minute) + '" style="font-family:inherit;font-size:14.5px;padding:6px 8px;border:1px solid var(--rule,#d9cdb4);border-radius:6px;background:var(--surface-2,#f3ead4);color:inherit;" />' +
      '</label>' +
      previewHtml +
      (noteHtml ? '<div style="margin-top:12px;font-size:13px;color:var(--saffron-deep,#9c4a10);">' + noteHtml + '</div>' : '') +
      '<div id="notify-status" style="margin-top:10px;font-size:13px;color:var(--ink-soft,#4a3d31);min-height:18px;"></div>' +
      '<div style="display:flex;gap:10px;margin-top:18px;">' +
        '<button type="button" id="notify-save" style="flex:1;background:var(--saffron-deep,#9c4a10);color:#fff;border:none;border-radius:999px;padding:10px 0;font-size:14.5px;font-weight:600;cursor:pointer;font-family:inherit;">जतन करा</button>' +
        '<button type="button" id="notify-cancel" style="flex:0 0 auto;background:none;border:1px solid var(--rule,#d9cdb4);color:inherit;border-radius:999px;padding:10px 18px;font-size:14.5px;cursor:pointer;font-family:inherit;">रद्द करा</button>' +
      '</div>';

    modalEl = document.createElement('div');
    modalEl.appendChild(backdrop);
    modalEl.appendChild(card);
    document.body.appendChild(modalEl);

    var statusEl = card.querySelector('#notify-status');
    backdrop.addEventListener('click', closeModal);
    card.querySelector('#notify-modal-close').addEventListener('click', closeModal);
    card.querySelector('#notify-cancel').addEventListener('click', closeModal);

    card.querySelector('#notify-save').addEventListener('click', function () {
      var enabled = card.querySelector('#notify-enabled').checked;
      var timeVal = card.querySelector('#notify-time').value || '07:00';
      var parts = timeVal.split(':');
      var hour = parseInt(parts[0], 10);
      var minute = parseInt(parts[1], 10);
      if (isNaN(hour) || isNaN(minute)) { hour = 7; minute = 0; }

      function persist(finalEnabled) {
        saveSettings({ enabled: finalEnabled, hour: hour, minute: minute });
        bridgeToNative(finalEnabled, hour, minute);
        registerSW();
        statusEl.textContent = finalEnabled ? '✓ जतन झाले — दररोज ' + pad2(hour) + ':' + pad2(minute) + ' नंतर सूचना मिळेल.' : '✓ जतन झाले — सूचना बंद आहे.';
        setTimeout(closeModal, 900);
      }

      if (enabled && 'Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission().then(function (result) {
          persist(result === 'granted');
          if (result !== 'granted') statusEl.textContent = 'सूचना परवानगी मिळाली नाही, त्यामुळे सूचना बंद ठेवली आहे.';
        });
      } else if (enabled && 'Notification' in window && Notification.permission === 'denied') {
        statusEl.textContent = permissionNote();
        persist(false);
      } else {
        persist(enabled);
      }
    });
  }

  function injectMenuEntry() {
    var containers = document.querySelectorAll('#mobile-nav .wrap');
    containers.forEach(function (wrap) {
      if (wrap.querySelector('#notify-menu-btn')) return;
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.id = 'notify-menu-btn';
      btn.className = 'header-suchi-btn';
      btn.style.cssText = 'background:none;border:none;cursor:pointer;font-family:inherit;font-size:15px;color:var(--ink-soft);padding:12px 4px;text-align:left;width:100%;';
      btn.textContent = '🔔 दैनंदिन सूचना';
      btn.addEventListener('click', function () {
        var nav = wrap.closest('.nav');
        if (nav) nav.classList.remove('menu-open');
        var menuBtn = document.getElementById('menu-btn');
        if (menuBtn) menuBtn.setAttribute('aria-expanded', 'false');
        openModal();
      });
      wrap.appendChild(btn);
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    injectMenuEntry();
    registerSW();
    maybeNotify();
    // Keeps the native alarm in sync on every open — covers users who enabled
    // notifications before this native bridge existed, and reinstalls/updates.
    var s = loadSettings();
    bridgeToNative(s.enabled, s.hour, s.minute);
  });
  document.addEventListener('visibilitychange', function () {
    if (!document.hidden) maybeNotify();
  });
  setInterval(maybeNotify, 60000);
})();
