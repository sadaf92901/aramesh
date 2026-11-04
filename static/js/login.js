// ============================================================
// اعتبارسنجی
// ============================================================

const VALIDATION = {
    username: {
        regex: /^[a-zA-Z][a-zA-Z0-9_]{2,19}$/,
        message: '⚠️ نام کاربری باید ۳ تا ۲۰ کاراکتر، با حرف انگلیسی شروع شه و فقط شامل حروف، عدد و _ باشه'
    },
    displayName: {
        minLength: 2,
        maxLength: 50,
        message: '⚠️ نام نمایشی باید ۲ تا ۵۰ کاراکتر باشه'
    },
    email: {
        regex: /^[^\s@]+@[^\s@]+\.[a-zA-Z]{2,}$/,
        message: '⚠️ ایمیل معتبر وارد کنید (مثلاً: ali@example.com)'
    },
    password: {
        minLength: 8,
        message: '⚠️ رمز عبور باید حداقل ۸ کاراکتر، شامل حرف بزرگ، کوچک و عدد باشه'
    }
};

const COMMON_PASSWORDS = [
    '12345678', 'password', 'qwerty123', '11111111',
    '123456789', 'password1', 'abc12345'
];

function validateUsername(value) {
    if (!VALIDATION.username.regex.test(value)) {
        return VALIDATION.username.message;
    }
    return null;
}

function validateDisplayName(value) {
    if (value.length < VALIDATION.displayName.minLength ||
        value.length > VALIDATION.displayName.maxLength) {
        return VALIDATION.displayName.message;
    }
    return null;
}

function validateEmail(value) {
    if (!VALIDATION.email.regex.test(value)) {
        return VALIDATION.email.message;
    }
    return null;
}

function validatePassword(value) {
    if (value.length < VALIDATION.password.minLength) {
        return VALIDATION.password.message;
    }
    if (!/[A-Z]/.test(value)) {
        return VALIDATION.password.message;
    }
    if (!/[a-z]/.test(value)) {
        return VALIDATION.password.message;
    }
    if (!/[0-9]/.test(value)) {
        return VALIDATION.password.message;
    }
    if (COMMON_PASSWORDS.includes(value.toLowerCase())) {
        return '⚠️ این رمز عبور خیلی رایجه، یه رمز قوی‌تر انتخاب کن';
    }
    return null;
}

// ============================================================
// نمایش فرم‌ها
// ============================================================
function showLoginForm() {
    document.getElementById('loginForm').classList.add('active');
    document.getElementById('registerForm').classList.remove('active');
    document.getElementById('tabLogin').classList.add('active');
    document.getElementById('tabRegister').classList.remove('active');

    // ===== خالی کردن فیلدها =====
    document.getElementById('loginUsername').value = '';
    document.getElementById('loginPassword').value = '';

    // ===== پاک کردن خطا =====
    var errorEl = document.getElementById('loginError');
    errorEl.textContent = '';
    errorEl.className = 'form-error';

    // ===== تلاش مجدد بعد از تأخیر (برای Chrome) =====
    setTimeout(function() {
        document.getElementById('loginUsername').value = '';
        document.getElementById('loginPassword').value = '';
    }, 100);
}
function hideLoginForm() {
    document.getElementById('loginForm').classList.remove('active');
    document.getElementById('loginError').textContent = '';
}

function showRegisterForm() {
    document.getElementById('registerForm').classList.add('active');
    document.getElementById('loginForm').classList.remove('active');
    document.getElementById('registerError').textContent = '';
    document.getElementById('registerError').className = 'form-error';
    document.getElementById('registerDisplayName').value = '';
    document.getElementById('registerUsername').value = '';
    document.getElementById('registerEmail').value = '';
    document.getElementById('registerPassword').value = '';
}

function hideRegisterForm() {
    document.getElementById('registerForm').classList.remove('active');
    document.getElementById('registerError').textContent = '';
}

// ============================================================
// ورود
// ============================================================
function loginUserSubmit() {
    var username = document.getElementById('loginUsername');
    var password = document.getElementById('loginPassword');
    var errorEl = document.getElementById('loginError');
    var submitBtn = document.getElementById('loginSubmitBtn');

    if (!username || !password) {
        alert('❌ فیلدهای ورود پیدا نشدند!');
        return;
    }

    var usernameValue = username.value.trim();
    var passwordValue = password.value.trim();

    errorEl.textContent = '';
    errorEl.className = 'form-error';

    // ===== مهمان =====
    if (usernameValue === 'مهمان') {
        localStorage.setItem('username', 'مهمان');
        localStorage.setItem('isGuest', 'true');
        window.location.href = '/';
        return;
    }

    if (!usernameValue || !passwordValue) {
        errorEl.textContent = '⚠️ نام کاربری و رمز عبور را وارد کنید';
        errorEl.className = 'form-error error';
        return;
    }

    // ===== چک: آیا در حالت انتظار هستیم؟ =====
    var lockoutUntil = localStorage.getItem('login_lockout_until');
    if (lockoutUntil) {
        var remaining = Math.ceil((parseInt(lockoutUntil) - Date.now()) / 1000);
        if (remaining > 0) {
            showLockoutCountdown(remaining, submitBtn, errorEl);
            return;
        } else {
            // انتظار تموم شد
            localStorage.removeItem('login_lockout_until');
        }
    }

    errorEl.textContent = '🔄 در حال بررسی...';
    errorEl.style.color = '#8B5CF6';

    submitBtn.disabled = true;
    submitBtn.textContent = '⏳ در حال ورود...';
    // ===== قفل کردن inputها =========
    document.getElementById('loginUsername').disabled = true;
    document.getElementById('loginPassword').disabled = true;

    fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: usernameValue, password: passwordValue })
    })
    .then(function(response) {
        // ===== چک Rate Limit =====
        if (response.status === 429) {
            return response.json().then(function(data) {
                return { rateLimited: true, error: data.error };
            });
        }
        return response.json();
    })
    .then(function(data) {
        // ===== اگه Rate Limit خورد =====
        if (data.rateLimited) {
            handleFailedLogin(submitBtn, errorEl);
            return;
        }

        // ===== خطاهای معمولی (رمز اشتباه یا کاربر نبود) =====
        if (data.error) {
            errorEl.textContent = '❌ ' + data.error;
            errorEl.className = 'form-error error';
            username.value = '';
            password.value = '';
            username.focus();

            // ===== ثبت خطا و محاسبه‌ی تأخیر =====
            handleFailedLogin(submitBtn, errorEl);
            return;
        }

        // ===== موفقیت =====
        localStorage.setItem('username', data.username);
        localStorage.setItem('displayName', data.display_name || data.username);
        localStorage.removeItem('isGuest');

        // ===== پاک کردن تاریخچه‌ی خطاها =====
        localStorage.removeItem('login_fail_count');
        localStorage.removeItem('login_lockout_until');

        window.location.href = '/';
    })
    .catch(function() {
        errorEl.textContent = '❌ خطا در ارتباط با سرور';
        errorEl.className = 'form-error error';
        submitBtn.disabled = false;
        submitBtn.textContent = '✅ ورود';
    });
}


// ============================================================
// مدیریت خطا و تأخیر تدریجی
// ============================================================
function handleFailedLogin(submitBtn, errorEl) {
    // ===== تعداد خطاها =====
    var failCount = parseInt(localStorage.getItem('login_fail_count') || '0') + 1;
    localStorage.setItem('login_fail_count', failCount);

    console.log('🔴 تعداد خطا:', failCount);

    // ===== تأخیر تدریجی =====
    var delays = [0, 0, 0, 0, 10, 20, 30, 60, 100];  // 0 = بدون قفل
    var delay = failCount < delays.length ? delays[failCount] : 300;

    // ===== اگه تأخیر داریم =====
    if (delay > 0) {
        showLockoutCountdown(delay, submitBtn, errorEl);
    } else {
        // ===== بدون قفل، فقط پیام خطا =====
        submitBtn.disabled = false;
        submitBtn.textContent = '✅ ورود';

        var usernameInput = document.getElementById('loginUsername');
        var passwordInput = document.getElementById('loginPassword');
        if (usernameInput) usernameInput.disabled = false;
        if (passwordInput) passwordInput.disabled = false;
    }
}
// ============================================================
// نمایش شمارش معکوس
// ============================================================
function showLockoutCountdown(seconds, submitBtn, errorEl) {
    var usernameInput = document.getElementById('loginUsername');
    var passwordInput = document.getElementById('loginPassword');

    // ===== قفل کردن همه =====
    submitBtn.disabled = true;
    if (usernameInput) usernameInput.disabled = true;
    if (passwordInput) passwordInput.disabled = true;
    submitBtn.style.opacity = '0.5';
    submitBtn.style.cursor = 'not-allowed';

    submitBtn.textContent = '🚫 ' + seconds + ' ثانیه صبر کن';

    var interval = setInterval(function() {
        seconds--;

        if (seconds <= 0) {
            clearInterval(interval);

            // ===== باز کردن قفل =====
            submitBtn.disabled = false;
            if (usernameInput) usernameInput.disabled = false;
            if (passwordInput) passwordInput.disabled = false;
            submitBtn.style.opacity = '1';
            submitBtn.style.cursor = 'pointer';
            submitBtn.textContent = '✅ ورود';

            errorEl.textContent = 'می‌تونی دوباره تلاش کنی';
            errorEl.className = 'form-error';
            errorEl.style.color = '#8B5CF6';

            localStorage.removeItem('login_lockout_until');
        } else {
            submitBtn.textContent = '🚫 ' + seconds + ' ثانیه صبر کن';
        }
    }, 1000);

    if (seconds >= 60) {
        var mins = Math.ceil(seconds / 60);
        errorEl.textContent = '🚫 تعداد تلاش‌های ناموفق زیاد شده. ' + mins + ' دقیقه صبر کن.';
    } else {
        errorEl.textContent = '🚫 تعداد تلاش‌های ناموفق زیاد شده. ' + seconds + ' ثانیه صبر کن.';
    }
    errorEl.className = 'form-error error';
}
// ============================================================
// ثبت‌نام
// ============================================================

function registerUserSubmit() {
    var displayNameField = document.getElementById('registerDisplayName');
    var usernameField = document.getElementById('registerUsername');
    var emailField = document.getElementById('registerEmail');
    var passwordField = document.getElementById('registerPassword');
    var errorEl = document.getElementById('registerError');

    var displayNameValue = displayNameField.value.trim();
    var usernameValue = usernameField.value.trim();
    var emailValue = emailField.value.trim();
    var passwordValue = passwordField.value.trim();

    errorEl.textContent = '';
    errorEl.className = 'form-error';

    // ===== چک خالی بودن =====
    if (!displayNameValue || !usernameValue || !emailValue || !passwordValue) {
        errorEl.textContent = '⚠️ تمام فیلدها را پر کنید';
        errorEl.className = 'form-error error';
        return;
    }

    // ===== اعتبارسنجی نام نمایشی =====
    var error = validateDisplayName(displayNameValue);
    if (error) {
        errorEl.textContent = error;
        errorEl.className = 'form-error error';
        return;
    }

    // ===== اعتبارسنجی نام کاربری =====
    error = validateUsername(usernameValue);
    if (error) {
        errorEl.textContent = error;
        errorEl.className = 'form-error error';
        return;
    }

    // ===== اعتبارسنجی ایمیل =====
    error = validateEmail(emailValue);
    if (error) {
        errorEl.textContent = error;
        errorEl.className = 'form-error error';
        return;
    }

    // ===== اعتبارسنجی رمز عبور =====
    error = validatePassword(passwordValue);
    if (error) {
        errorEl.textContent = error;
        errorEl.className = 'form-error error';
        return;
    }

    errorEl.textContent = '🔄 در حال ثبت‌نام...';
    errorEl.style.color = '#8B5CF6';
    const consentChecked = document.getElementById('registerConsent')?.checked || false;
    fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            username: usernameValue,
            display_name: displayNameValue,
            email: emailValue,
            password: passwordValue,
            consent_audio:consentChecked

        })
    })
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (data.error) {
            errorEl.textContent = '❌ ' + data.error;
            errorEl.className = 'form-error error';
            return;
        }

        localStorage.setItem('username', data.username);
        localStorage.setItem('displayName', data.display_name || data.username);
        localStorage.removeItem('isGuest');
        localStorage.removeItem('onboarding_done')
        window.location.href = '/';
    })
    .catch(function() {
        errorEl.textContent = '❌ خطا در ارتباط با سرور';
        errorEl.className = 'form-error error';
    });
}

// ============================================================
// مهمان
// ============================================================

function guestLogin() {
    // ===== پاک کردن data‌های قبلی =====
    localStorage.removeItem('displayName');

    // ===== ذخیره مهمان =====
    localStorage.setItem('username', 'مهمان');
    localStorage.setItem('isGuest', 'true');

    // ===== به سرور بگو مهمان اومده =====
    fetch('/api/guest-login', { method: 'POST' })
        .then(() => {
            window.location.href = '/';
        })
        .catch(() => {
            window.location.href = '/';
        });
}
// ============================================================
// نمایش/مخفی کردن رمز
// ============================================================

function togglePassword(inputId, btn) {
    var input = document.getElementById(inputId);
    if (!input) return;

    if (input.type === 'password') {
        input.type = 'text';
        btn.textContent = '🙈';
    } else {
        input.type = 'password';
        btn.textContent = '👁️';
    }
}
function showLoginForm() {
    document.getElementById('loginForm').classList.add('active');
    document.getElementById('registerForm').classList.remove('active');
    document.getElementById('tabLogin').classList.add('active');
    document.getElementById('tabRegister').classList.remove('active');
    document.getElementById('loginError').textContent = '';
    document.getElementById('loginError').className = 'form-error';
    document.getElementById('loginUsername').value = '';
    document.getElementById('loginPassword').value = '';
}

function showRegisterForm() {
    document.getElementById('registerForm').classList.add('active');
    document.getElementById('loginForm').classList.remove('active');
    document.getElementById('tabRegister').classList.add('active');
    document.getElementById('tabLogin').classList.remove('active');
    document.getElementById('registerError').textContent = '';
    document.getElementById('registerError').className = 'form-error';
    document.getElementById('registerDisplayName').value = '';
    document.getElementById('registerUsername').value = '';
    document.getElementById('registerEmail').value = '';
    document.getElementById('registerPassword').value = '';
}
// ============================================================
// صادر کردن توابع
// ============================================================

window.showLoginForm = showLoginForm;
window.hideLoginForm = hideLoginForm;
window.showRegisterForm = showRegisterForm;
window.hideRegisterForm = hideRegisterForm;
window.loginUserSubmit = loginUserSubmit;
window.registerUserSubmit = registerUserSubmit;
window.guestLogin = guestLogin;
window.togglePassword=togglePassword;
// ============================================================
// پاک کردن فیلدها هنگام لود صفحه
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    // ===== کدهای قبلی (پاک کردن فیلدها) =====
    var clearLoginFields = function() {
        var u = document.getElementById('loginUsername');
        var p = document.getElementById('loginPassword');
        if (u) u.value = '';
        if (p) p.value = '';
    };

    clearLoginFields();
    setTimeout(clearLoginFields, 50);
    setTimeout(clearLoginFields, 200);
    setTimeout(clearLoginFields, 500);

    // ============================================================
    // 🆕 جلوگیری از تایپ فارسی در فیلدهای انگلیسی
    // ============================================================

    function blockPersianInput(inputId) {
        var input = document.getElementById(inputId);
        if (!input) return;

        input.addEventListener('input', function() {
            var persianRegex = /[\u0600-\u06FF]/g;
            if (persianRegex.test(this.value)) {
                this.value = this.value.replace(persianRegex, '');
                if (typeof showToast === 'function') {
                    showToast('⚠️ این فیلد باید به انگلیسی پر شود', '⚠️', 'warning');
                }
            }
        });
    }

    // ===== فرم ورود =====
    blockPersianInput('loginUsername');
    blockPersianInput('loginPassword');

    // ===== فرم ثبت‌نام =====
    blockPersianInput('registerUsername');
    blockPersianInput('registerEmail');
    blockPersianInput('registerPassword');

    // ⚠️ نام نمایشی (Display Name) رو بلاک نمی‌کنیم، چون می‌تونه فارسی یا انگلیسی باشه.
});