const CACHE = 'gita-v43';

const PRECACHE = [
  './',
  './adhyay',
  './concept',
  './prasang',
  './css/style.css',
  './js/data.js',
  './js/home.js',
  './js/adhyay.js',
  './js/content.js',
  './js/stories.js',
  './js/triggers.js',
  './js/pdf-carousel.js',
  './js/pdf.worker.min.js',
  './js/share.js',
  './js/pwa-update.js',
  './js/notify.js',
  './js/sankalpana-list.js',
  './js/prasang-list.js',
  './assets/home-banner-landscape.jpg',
  './assets/home-banner-potrait.jpg',
  './assets/icons/icon-192.png',
  './assets/icons/icon-512.png',
  './manifest.json'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(PRECACHE)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
  // controllerchange fires on all tabs — pwa-update.js listens and shows the banner
});

// Daily sankalpana notification (shown by js/notify.js via showNotification) — open/focus its page on click
self.addEventListener('notificationclick', e => {
  e.notification.close();
  const url = (e.notification.data && e.notification.data.url) || './';
  e.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(clientList => {
      for (const client of clientList) {
        if (client.url === url && 'focus' in client) return client.focus();
      }
      return self.clients.openWindow(url);
    })
  );
});

self.addEventListener('fetch', e => {
  const { request } = e;
  const url = new URL(request.url);

  // Only handle same-origin requests
  if (url.origin !== location.origin) return;

  // HTML navigation: network-first so pages are always fresh; fall back to cache offline
  if (request.mode === 'navigate') {
    e.respondWith(
      fetch(request)
        .then(res => {
          const clone = res.clone();
          caches.open(CACHE).then(c => c.put(request, clone));
          return res;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  // PDFs: network-first, fall back to cache
  if (url.pathname.endsWith('.pdf')) {
    e.respondWith(
      fetch(request)
        .then(res => {
          const clone = res.clone();
          caches.open(CACHE).then(c => c.put(request, clone));
          return res;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  // JS / CSS / images / fonts: stale-while-revalidate
  // → serve cached version instantly for fast load
  // → fetch fresh copy in background and update the cache for next visit
  e.respondWith(
    caches.open(CACHE).then(cache =>
      cache.match(request).then(cached => {
        const networkFetch = fetch(request).then(res => {
          if (res.ok) cache.put(request, res.clone());
          return res;
        }).catch(() => cached);   // offline: fall back to cached copy
        return cached || networkFetch;
      })
    )
  );
});
