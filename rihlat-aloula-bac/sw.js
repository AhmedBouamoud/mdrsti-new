// تطبيق «رحلة الأولى باك»: يحفظ الصفحة الرئيسية والدروس الـ17 للقراءة دون إنترنت.
// الصور الكبيرة (الإنفوغرافيا) لا تُحمَّل مسبقًا رفقًا بباقة الهاتف، بل تُحفَظ عند أول فتح لها.
const CACHE_NAME = 'rihlat-aloula-bac-app-v4';
const LESSONS = [
  'dughut-istiimariya', 'geo-iidad-turab', 'geo-ittihad-urubbi', 'geo-ma-tasahhur',
  'geo-mawarid-maghrib', 'geo-sin', 'geo-tahyia-hadariya', 'geo-tanmiya', 'geo-usa',
  'harb-alamiya-thaniya', 'nidal-maghrib', 'nidham-himaya', 'tahawwulat-iqtisadiya',
  'tahawwulat-kubra', 'tanafus-imbiriyali', 'urubba-bayna-harbayn', 'yaqada-fikriya'
];
const CORE = [
  './',
  './manifest.webmanifest',
  './assets/css/lesson.css',
  './assets/img/ab-logo.png',
  './assets/img/ab-icon.png',
  './assets/img/favicon-32.png',
  './assets/img/icon-192.png',
  ...LESSONS.map(s => './lessons/' + s + '.html')
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache =>
      Promise.all(CORE.map(u => cache.add(u).catch(() => null)))
    )
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

async function fromCache(request) {
  const cache = await caches.open(CACHE_NAME);
  let hit = await cache.match(request, { ignoreSearch: true });
  if (hit) return hit;
  const url = new URL(request.url);
  if (!url.pathname.endsWith('/') && !/\.[a-z0-9]+$/i.test(url.pathname)) {
    hit = await cache.match(url.origin + url.pathname + '.html');
    if (hit) return hit;
  }
  if (request.mode === 'navigate') return cache.match('./');
  return undefined;
}

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin !== location.origin) return;

  // الصفحات: الشبكة أولًا (ليرى التلميذ آخر تحديث)، ثم النسخة المحفوظة دون إنترنت.
  if (request.mode === 'navigate' || request.destination === 'document') {
    event.respondWith(
      fetch(request)
        .then(async res => {
          if (res.ok) { const copy = res.clone(); caches.open(CACHE_NAME).then(c => c.put(request, copy)); return res; }
          return (await fromCache(request)) || res;
        })
        .catch(() => fromCache(request))
    );
    return;
  }

  // الملفات الأخرى (تنسيق، صور، ملفات التحميل): المحفوظ أولًا، ثم الشبكة مع الحفظ.
  event.respondWith(
    fromCache(request).then(hit => hit || fetch(request).then(res => {
      if (res.ok && res.type === 'basic') { const copy = res.clone(); caches.open(CACHE_NAME).then(c => c.put(request, copy)); }
      return res;
    }))
  );
});
