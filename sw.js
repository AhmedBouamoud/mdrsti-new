// خدمة عاملة بسيطة: تفعيل فوري وتمرير الطلبات إلى الشبكة مباشرة.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', event => event.waitUntil(self.clients.claim()));
self.addEventListener('fetch', () => {});
