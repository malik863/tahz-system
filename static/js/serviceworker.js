var staticCacheName = "django-pwa-v1";
var filesToCache = [
    '/',
    '/static/css/bootstrap.min.css', // Adjust paths to match your actual CSS/JS asset locations
    '/static/js/bootstrap.bundle.min.js',
];

// Cache on install
self.addEventListener("install", event => {
    this.skipWaiting();
    event.waitUntil(
        caches.open(staticCacheName)
            .then(cache => {
                return cache.addAll(filesToCache);
            })
    );
});

// Clear old caches on activate
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.filter(cacheName => cacheName !== staticCacheName)
                    .map(cacheName => caches.delete(cacheName))
            );
        })
    );
});

// Serve from Cache / Network Fallback
self.addEventListener("fetch", event => {
    event.respondWith(
        caches.match(event.request).then(response => {
            return response || fetch(event.request);
        }).catch(() => {
            // Optional: return a fallback offline HTML page if offline completely
        })
    );
});