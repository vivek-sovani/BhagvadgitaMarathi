const CACHE = 'gita-v2';

const PRECACHE = [
  '/index.html',
  '/adhyay.html',
  '/css/style.css',
  '/js/data.js',
  '/js/home.js',
  '/js/adhyay.js',
  '/js/content.js',
  '/js/stories.js',
  '/js/triggers.js',
  '/js/pdf-carousel.js',
  '/js/pdf.worker.min.js',
  '/assets/home-banner-landscape.jpg',
  '/assets/home-banner-potrait.jpg',
  '/assets/icons/icon-192.png',
  '/assets/icons/icon-512.png',
  '/manifest.json'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(PRECACHE)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const { request } = e;
  const url = new URL(request.url);

  // Only handle same-origin requests
  if (url.origin !== location.origin) return;

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

  // Everything else: cache-first
  e.respondWith(
    caches.match(request).then(cached => {
      if (cached) return cached;
      return fetch(request).then(res => {
        if (res.ok) {
          const clone = res.clone();
          caches.open(CACHE).then(c => c.put(request, clone));
        }
        return res;
      });
    })
  );
});
