// ============================================================
// Service Worker — همراه آرامش
// ============================================================

const CACHE_VERSION = '100.0.0';
const CACHE_NAME = `aramesh-v${CACHE_VERSION}`;
const OFFLINE_URL = '/offline';

// ============================================================
// فایل‌های استاتیک
// ============================================================
const STATIC_ASSETS = [
    '/offline',

    // ===== CSS =====
    '/static/css/base.css',
    '/static/css/layout.css',
    '/static/css/components/switch.css',
    '/static/css/components/card.css',
    '/static/css/components/button.css',
    '/static/css/components/form.css',
    '/static/css/components/feedback.css',
    '/static/css/pages/home.css',
    '/static/css/pages/questionnaire.css',
    '/static/css/journal.css',
    '/static/css/weekly_plan.css',
    '/static/css/meditation.css',
    '/static/css/breathing.css',
    '/static/css/profile.css',
    '/static/css/history.css',
    '/static/css/legal.css',
    '/static/css/login.css',

    // ===== JS =====
    '/static/js/main.js',
    '/static/js/storage.js',
    '/static/js/ui.js',
    '/static/js/components.js',
    '/static/js/error-handler.js',
    '/static/js/login.js',
    '/static/js/modules/questionnaire/index.js',
    '/static/js/modules/questionnaire/builder.js',
    '/static/js/modules/questionnaire/validator.js',
    '/static/js/modules/questionnaire/submitter.js',
    '/static/js/modules/questionnaire/recording.js',

    // ===== Manifest + Icons =====
    '/static/manifest.json',
    '/static/images/icons/icon-192.png',
    '/static/images/icons/icon-512.png'
];
// ============================================================
// نصب
// ============================================================

self.addEventListener('install', (event) => {
    console.log('🔧 Service Worker در حال نصب...', CACHE_NAME);

    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('📦 کش کردن فایل‌ها...');
                return cache.addAll(STATIC_ASSETS).catch((err) => {
                    console.warn('⚠️ بعضی فایل‌ها کش نشدن:', err);
                });
            })
            .then(() => {
                console.log('✅ Service Worker نصب شد');
                return self.skipWaiting();
            })
    );
});

// ============================================================
// فعال‌سازی
// ============================================================

self.addEventListener('activate', (event) => {
    console.log('🚀 Service Worker فعال شد');

    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('🗑️ حذف کش قدیمی:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// ============================================================
// Fetch
// ============================================================

self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // ===== فقط GET =====
    if (event.request.method !== 'GET') {
        return;
    }

    // ===== API: Network First =====
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(networkFirst(event.request));
        return;
    }

    // ===== صفحه‌ها: Network First + Fallback =====
    if (event.request.mode === 'navigate') {
        event.respondWith(
            fetch(event.request)
                .then((response) => {
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, responseClone);
                    });
                    return response;
                })
                .catch(() => {
                    return caches.match(OFFLINE_URL);
                })
        );
        return;
    }

    // ===== استاتیک: Cache First =====
    event.respondWith(cacheFirst(event.request));
});

// ============================================================
// استراتژی‌ها
// ============================================================
async function cacheFirst(request) {
    const cached = await caches.match(request);
    if (cached) return cached;

    try {
        const response = await fetch(request);
        // ===== فقط http/https رو کش کن =====
        if (response.ok && request.url.startsWith('http')) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, response.clone());
        }
        return response;
    } catch (err) {
        return new Response('آفلاین', { status: 503 });
    }
}
async function networkFirst(request) {
    try {
        const response = await fetch(request);
        // ===== فقط http/https رو کش کن =====
        if (response.ok && request.url.startsWith('http')) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, response.clone());
        }
        return response;
    } catch (err) {
        const cached = await caches.match(request);
        if (cached) return cached;

        return new Response(
            JSON.stringify({
                error: 'آفلاین هستید',
                offline: true
            }),
            {
                status: 503,
                headers: { 'Content-Type': 'application/json' }
            }
        );
    }
}
// ============================================================
// پیام‌ها
// ============================================================

self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});

console.log('✅ Service Worker لود شد');
