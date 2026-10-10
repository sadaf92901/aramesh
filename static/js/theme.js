// ============================================================
// همراه آرامش — Theme Manager
// ============================================================
// مدیریت تم رنگی + حالت تیره/روشن
// ============================================================

(function() {
    'use strict';

    // ============================================================
    // کلیدهای ذخیره‌سازی
    // ============================================================
    const THEME_COLOR_KEY = 'aramesh_color_theme';
    const THEME_MODE_KEY = 'aramesh_display_mode';

    // ============================================================
    // مقادیر پیش‌فرض
    // ============================================================
    const DEFAULT_COLOR = 'purple';
    const DEFAULT_MODE = 'light';

    // ============================================================
    // تم‌های معتبر
    // ============================================================
    const VALID_COLORS = ['purple', 'blue', 'green', 'pink', 'orange', 'gray'];
    const VALID_MODES = ['light', 'dark'];


    // ============================================================
    // خواندن تم فعلی
    // ============================================================
    function getColorTheme() {
        const saved = localStorage.getItem(THEME_COLOR_KEY);
        return VALID_COLORS.includes(saved) ? saved : DEFAULT_COLOR;
    }

    function getDisplayMode() {
        const saved = localStorage.getItem(THEME_MODE_KEY);
        return VALID_MODES.includes(saved) ? saved : DEFAULT_MODE;
    }


    // ============================================================
    // اعمال تم رنگی
    // ============================================================
    function applyColorTheme(color) {
        if (!VALID_COLORS.includes(color)) return;

        // ===== ست کردن data-theme روی <html> =====
        document.documentElement.setAttribute('data-theme', color);

        // ===== ذخیره در localStorage =====
        localStorage.setItem(THEME_COLOR_KEY, color);

        // ===== به‌روزرسانی دکمه‌های فعال در مودال =====
        updateActiveButtons();

        // ===== Toast =====
        if (typeof showToast === 'function') {
            showToast('🎨 تم عوض شد', '✅', 'success');
        }

        console.log('🎨 Color theme applied:', color);
    }


    // ============================================================
    // اعمال حالت تیره/روشن
    // ============================================================
    function applyDisplayMode(mode) {
        if (!VALID_MODES.includes(mode)) return;

        // ===== اضافه/حذف کلاس dark-theme روی <body> =====
        if (mode === 'dark') {
            document.body.classList.add('dark-theme');
        } else {
            document.body.classList.remove('dark-theme');
        }

        // ===== ذخیره در localStorage =====
        localStorage.setItem(THEME_MODE_KEY, mode);

        // ===== به‌روزرسانی دکمه‌های فعال =====
        updateActiveButtons();

        // ===== به‌روزرسانی theme-color مرورگر =====
        updateBrowserThemeColor(mode);

        // ===== Toast =====
        if (typeof showToast === 'function') {
            showToast(mode === 'dark' ? '🌙 حالت تیره' : '☀️ حالت روشن', '✅', 'success');
        }

        console.log('🌓 Display mode applied:', mode);
    }


    // ============================================================
    // به‌روزرسانی دکمه‌های فعال در مودال
    // ============================================================
    function updateActiveButtons() {
        const currentColor = getColorTheme();
        const currentMode = getDisplayMode();

        // ===== دکمه‌های رنگی =====
        document.querySelectorAll('.theme-color-btn').forEach(btn => {
            if (btn.dataset.theme === currentColor) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    // ===== دکمه‌های حالت =====
        document.querySelectorAll('.theme-mode-btn').forEach(btn => {
            if (btn.dataset.mode === currentMode) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }


    // ============================================================
    // به‌روزرسانی theme-color مرورگر
    // ============================================================
    function updateBrowserThemeColor(mode) {
        const metaTheme = document.querySelector('meta[name="theme-color"]');
        if (!metaTheme) return;

        if (mode === 'dark') {
            metaTheme.setAttribute('content', '#0f172a');
        } else {
            // رنگ اصلی تم رو می‌گیریم
            const colorMap = {
                purple: '#8B5CF6',
                blue:   '#3B82F6',
                green:  '#10B981',
                pink:   '#EC4899',
                orange: '#F59E0B',
                gray:   '#64748B',
            };
            const color = colorMap[getColorTheme()] || '#8B5CF6';
            metaTheme.setAttribute('content', color);
        }
    }


    // ============================================================
    // باز/بسته کردن مودال
    // ============================================================
    function openThemeModal() {
        const modal = document.getElementById('themeModal');
        if (!modal) return;

        modal.style.display = 'flex';
        updateActiveButtons();

        console.log('🎨 Theme modal opened');
    }

    function closeThemeModal() {
        const modal = document.getElementById('themeModal');
        if (!modal) return;

        modal.style.display = 'none';

        console.log('🎨 Theme modal closed');
    }


    // ============================================================
    // بستن مودال با کلیک روی پس‌زمینه
    // ============================================================
    function setupModalClickOutside() {
        const modal = document.getElementById('themeModal');
        if (!modal) return;

        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeThemeModal();
            }
        });
    }


    // ============================================================
    // راه‌اندازی
    // ============================================================
    function initTheme() {
        // ===== اعمال تم رنگی =====
        const color = getColorTheme();
        document.documentElement.setAttribute('data-theme', color);

        // ===== اعمال حالت نمایش =====
        const mode = getDisplayMode();
        if (mode === 'dark') {
            document.body.classList.add('dark-theme');
        } else {
            document.body.classList.remove('dark-theme');
        }

        // ===== theme-color مرورگر =====
        updateBrowserThemeColor(mode);

        // ===== Setup بستن با کلیک بیرون =====
        setupModalClickOutside();

        // ===== به‌روزرسانی دکمه‌های فعال =====
        updateActiveButtons();

        console.log('✅ Theme initialized:', { color, mode });
    }


    // ============================================================
    // اجرا: قبل از DOMContentLoaded برای جلوگیری از FOUC
    // ============================================================
    initTheme();


    // ============================================================
    // صادر کردن به window
    // ============================================================
    window.openThemeModal   = openThemeModal;
    window.closeThemeModal  = closeThemeModal;
    window.applyColorTheme  = applyColorTheme;
    window.applyDisplayMode = applyDisplayMode;
    window.getColorTheme    = getColorTheme;
    window.getDisplayMode   = getDisplayMode;

    // ===== برای سازگاری با کد قدیمی =====
    window.toggleTheme = function() {
        const current = getDisplayMode();
        const next = current === 'dark' ? 'light' : 'dark';
        applyDisplayMode(next);
    };

    console.log('✅ Theme module loaded');

})();