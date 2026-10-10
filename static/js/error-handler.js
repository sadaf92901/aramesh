// ============================================================
// مدیریت خطاها در Frontend
// ============================================================

const ERROR_MESSAGES = {
    400: '⚠️ اطلاعات ارسالی نامعتبر است',
    401: '🔒 لطفاً وارد شوید',
    403: '🚫 دسترسی غیرمجاز',
    404: '🔍 صفحه‌ای که می‌خوای پیدا نشد',
    405: '❌ این عملیات مجاز نیست',
    500: '💥 خطای داخلی سرور. لطفاً دوباره تلاش کن',
    503: '🔌 سرور در دسترس نیست. لطفاً بعداً تلاش کن'
};

const NETWORK_ERROR = '📡 اتصال به اینترنت قطع است. لطفاً چک کن';
const TIMEOUT_ERROR = '⏱️ درخواست طول کشید. لطفاً دوباره تلاش کن';

function _showErrorToast(message, icon, type) {
    if (typeof window.showToast === 'function') {
        window.showToast(message, icon, type);
    } else {
        console.warn('[Error]', message);
    }
}

async function safeFetch(url, options = {}) {
    const {
        timeout = 120000,
        showError = true,
        ...fetchOptions
    } = options;

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        const response = await fetch(url, {
            ...fetchOptions,
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        let data;
        const contentType = response.headers.get('content-type');

        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            data = await response.text();
        }

        if (!response.ok) {
            const errorMessage = data?.error ||
                                ERROR_MESSAGES[response.status] ||
                                `خطای ${response.status}`;

            if (showError) {
                _showErrorToast(errorMessage, '❌', 'error');
            }

            return {
                success: false,
                status: response.status,
                error: errorMessage,
                data: null
            };
        }

        return {
            success: true,
            status: response.status,
            data: data
        };

    } catch (error) {
        if (error.name === 'AbortError') {
            if (showError) {
                _showErrorToast(TIMEOUT_ERROR, '⏱️', 'warning');
            }
            return { success: false, status: 0, error: TIMEOUT_ERROR, data: null };
        }

        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            if (showError) {
                _showErrorToast(NETWORK_ERROR, '📡', 'warning');
            }
            return { success: false, status: 0, error: NETWORK_ERROR, data: null };
        }

        if (showError) {
            _showErrorToast('❌ خطای غیرمنتظره. لطفاً دوباره تلاش کن', '❌', 'error');
        }
        console.error('❌ خطای غیرمنتظره:', error);

        return { success: false, status: 0, error: error.message, data: null };
    }
}

window.addEventListener('error', function(event) {
    console.error('❌ خطای JavaScript:', event.error);
});

window.addEventListener('unhandledrejection', function(event) {
    console.error('❌ Promise رد شده:', event.reason);
});

window.safeFetch = safeFetch;
