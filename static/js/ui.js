// ============================================================
// توابع رابط کاربری (UI)
// ============================================================

// ===== Toast =====

let toastTimeout = null;

function showToast(message, icon = '✅', type = 'info') {
    const toast = document.getElementById('toast');
    const toastIcon = document.getElementById('toastIcon');
    const toastMessage = document.getElementById('toastMessage');

    if (!toast) return;

    toastIcon.textContent = icon;
    toastMessage.textContent = message;

    toast.className = 'toast ' + (type || 'info');
    toast.classList.add('show');

    if (toastTimeout) clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

function hideToast() {
    const toast = document.getElementById('toast');
    if (toast) toast.classList.remove('show');
    if (toastTimeout) clearTimeout(toastTimeout);
}

// ===== تم =====

// ===== وضعیت اتصال =====

function updateConnectionStatus() {
    const el = document.getElementById('connectionStatus');
    if (!el) return;

    if (navigator.onLine) {
        el.textContent = '🟢 آنلاین';
        el.className = 'connection-status online';
    } else {
        el.textContent = '🔴 آفلاین';
        el.className = 'connection-status offline';
    }
}

// ===== تاریخ =====

function getPersianDate() {
    return new Intl.DateTimeFormat('fa-IR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(new Date());
}

function getPersianDayNames() {
    return ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه'];
}

function getPersianShortDayNames() {
    return ['ش', 'ی', 'د', 'س', 'چ', 'پ', 'ج'];
}

// ===== نقل قول =====

const QUOTES = [
    '"آرامش را در درون خودت پیدا کن، نه در دنیای بیرون."',
    '"تنها راهی که می‌تونی از پسش بربیای اینه که از توش عبور کنی."',
    '"هر روز یک شروع تازه است. نگذار گذشته‌ات امروز تو را تعیین کند."',
    '"قدرت تو در افکارت نهفته است. افکارت را تغییر بده تا زندگیت تغییر کند."',
    '"مهربانی با خودت، اولین قدم برای مهربانی با دیگران است."',
    '"گاهی بهترین کاری که می‌تونی انجام بدی، نفس کشیدن عمیق است."'
];

function updateDailyQuote() {
    const today = new Date().toISOString().split('T')[0];
    const stored = loadData(KEYS.DAILY_QUOTE);
    const storedDate = loadData(KEYS.DAILY_QUOTE_DATE);

    const quoteEl = document.getElementById('dailyQuote');
    if (!quoteEl) return;

    if (stored && storedDate === today) {
        quoteEl.textContent = stored;
        return stored;
    }

    const randomQuote = QUOTES[Math.floor(Math.random() * QUOTES.length)];
    quoteEl.textContent = randomQuote;
    saveData(KEYS.DAILY_QUOTE, randomQuote);
    saveData(KEYS.DAILY_QUOTE_DATE, today);
    return randomQuote;
}

// ===== آواتار =====

function changeAvatar(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('avatarImage').src = e.target.result;
            saveData(KEYS.USER_AVATAR, e.target.result);
            showToast('🖼️ آواتار به‌روزرسانی شد', '✅', 'success');
        };
        reader.readAsDataURL(file);
    }
}
function loadAvatar() {
    const saved = loadData(KEYS.USER_AVATAR, null);
    if (saved) {
        const img = document.getElementById('avatarImage');
        if (img) img.src = saved;
    }
}

// ===== نوار پیشرفت =====

function updateProgress() {
    const total = 20;
    let answered = 0;

    for (let i = 0; i < total; i++) {
        if (document.querySelector(`input[name="mc${i}"]:checked`)) {
            answered++;
        }
    }

    const percent = Math.round((answered / total) * 100);

    const bars = document.querySelectorAll('.progress-bar:not(#resultProgress)');
    const texts = document.querySelectorAll('.progress-text');

    bars.forEach(bar => {
        bar.style.width = percent + '%';
    });

    texts.forEach(text => {
        text.textContent = `پیشرفت: ${percent}% (${answered} از ${total})`;
    });

    return percent;
}

// ===== اسکرول به بالا =====

function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}
// ============================================================
// Loading States
// ============================================================

/**
 * فعال‌سازی حالت لودینگ روی دکمه
 * @param {HTMLElement} btn - دکمه
 */
function setButtonLoading(btn) {
    if (!btn) return;
    btn.classList.add('loading');
    btn.disabled = true;
}

/**
 * غیرفعال‌سازی حالت لودینگ
 */
function unsetButtonLoading(btn) {
    if (!btn) return;
    btn.classList.remove('loading');
    btn.disabled = false;
}

/**
 * نمایش لودینگ سراسری
 */
function showGlobalLoading() {
    let overlay = document.getElementById('globalLoading');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'globalLoading';
        overlay.className = 'global-loading';
        overlay.innerHTML = '<div class="global-loading-spinner"></div>';
        document.body.appendChild(overlay);
    }
    overlay.classList.add('active');
}

/**
 * مخفی کردن لودینگ سراسری
 */
function hideGlobalLoading() {
    const overlay = document.getElementById('globalLoading');
    if (overlay) {
        overlay.classList.remove('active');
    }
}
// ============================================================
// چک مهمان — قبل از ورود به ابزارها
// ============================================================

function checkGuestAndGo(url) {
    var username = localStorage.getItem('username');
    var isGuest = localStorage.getItem('isGuest');

    if (username === 'مهمان' || isGuest === 'true') {
        showGuestLockModal();
        return;
    }

    window.location.href = url;
}

function showGuestLockModal() {
    var existing = document.getElementById('guestLockModal');
    if (existing) existing.remove();

    var modal = document.createElement('div');
    modal.id = 'guestLockModal';
    modal.className = 'guest-lock-overlay';
    var html = '';
    html += '<div class="guest-lock-box" onclick="event.stopPropagation()">';
    html += '<div class="guest-lock-icon">🔒</div>';
    html += '<h3 class="guest-lock-title">این بخش نیاز به ثبت‌نام داره</h3>';
    html += '<p class="guest-lock-text">برای استفاده از ابزارها، لطفاً اول ثبت‌نام کن یا وارد حساب کاربری‌ت بشو.</p>';
    html += '<div class="guest-lock-buttons">';
    html += '<button class="guest-lock-btn primary" onclick="goToLoginFromGuest()">📝 ثبت‌نام / ورود</button>';
    html += '<button class="guest-lock-btn" onclick="closeGuestLockModal()">انصراف</button>';
    html += '</div>';
    html += '</div>';
    modal.innerHTML = html;


    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeGuestLockModal();
        }
    });

    document.body.appendChild(modal);
}

function closeGuestLockModal() {
    var modal = document.getElementById('guestLockModal');
    if (modal) modal.remove();
}

// ============================================================
// خروج از حساب مهمان + رفتن به صفحه‌ی ورود
// ============================================================

function goToLoginFromGuest() {
    // ===== پاک کردن localStorage =====
    localStorage.removeItem('username');
    localStorage.removeItem('displayName');
    localStorage.removeItem('isGuest');
    localStorage.removeItem('userAvatar');
    localStorage.removeItem('mcq_answers');
    localStorage.removeItem('open_answers');
    localStorage.removeItem('questionnaire_progress');
    localStorage.removeItem('dailyStatus');
    localStorage.removeItem('dailyMoods');
    localStorage.removeItem('history');

    // ===== پاک کردن IndexedDB =====
    try {
        indexedDB.deleteDatabase('ArameshDB');
    } catch (e) {}

    // ===== درخواست خروج از سرور + رفتن به /login =====
    fetch('/api/logout', { method: 'POST' })
        .then(function() {
            window.location.href = '/login';
        })
        .catch(function() {
            window.location.href = '/login';
        });
}
// ============================================================
// تنظیمات صدا
// ============================================================

function isSoundEnabled() {
    const saved = localStorage.getItem('aramesh_sound_enabled');
    return saved === null ? true : saved === 'true';  // پیش‌فرض: روشن
}

function setSoundEnabled(enabled) {
    localStorage.setItem('aramesh_sound_enabled', enabled ? 'true' : 'false');
}
// ============================================================
// 🆕 جلوگیری از تایپ حروف انگلیسی
// ============================================================

function enforcePersianInput(inputElement) {
    if (!inputElement) return;

    inputElement.addEventListener('input', function(e) {
        // الگوی حروف انگلیسی (a-z, A-Z)
        var englishRegex = /[a-zA-Z]/g;

        // اگر متن شامل حروف انگلیسی بود، اون‌ها رو حذف کن
        if (englishRegex.test(this.value)) {
            this.value = this.value.replace(englishRegex, '');

            // اگر می‌خوای به کاربر پیام هم بدی:
            if (typeof showToast === 'function') {
                showToast('⚠️ لطفاً فقط فارسی تایپ کنید', '⚠️', 'warning');
            }
        }
    });
}

// ============================================================
// صادر کردن
// ============================================================

window.isSoundEnabled = isSoundEnabled;
window.setSoundEnabled = setSoundEnabled;
window.checkGuestAndGo = checkGuestAndGo;
window.showGuestLockModal = showGuestLockModal;
window.closeGuestLockModal = closeGuestLockModal;
window.goToLoginFromGuest = goToLoginFromGuest;
window.setButtonLoading = setButtonLoading;
window.unsetButtonLoading = unsetButtonLoading;
window.showGlobalLoading = showGlobalLoading;
window.hideGlobalLoading = hideGlobalLoading;
window.showToast = showToast;
window.hideToast = hideToast;
window.updateConnectionStatus = updateConnectionStatus;
window.getPersianDate = getPersianDate;
window.getPersianDayNames = getPersianDayNames;
window.getPersianShortDayNames = getPersianShortDayNames;
window.updateDailyQuote = updateDailyQuote;
window.changeAvatar = changeAvatar;
window.loadAvatar = loadAvatar;
window.updateProgress = updateProgress;
window.scrollToTop = scrollToTop;
