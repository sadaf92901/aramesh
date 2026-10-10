// ============================================================
// صفحه‌ی اشتراک
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('⭐ صفحه اشتراک بارگذاری شد');
    loadSubscription();
    loadUsage();
});


// ============================================================
// بارگذاری اطلاعات اشتراک
// ============================================================

function loadSubscription() {
    fetch('/api/subscription/status')
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                console.error('❌ خطا:', data.error);
                return;
            }
            renderPlan(data);
            renderFeatures(data.features || {});
        })
        .catch(err => console.error('❌ خطا:', err));
}


// ============================================================
// نمایش پلن فعلی
// ============================================================

function renderPlan(data) {
    const iconEl = document.getElementById('planIcon');
    const nameEl = document.getElementById('planName');
    const descEl = document.getElementById('planDesc');

    if (iconEl) iconEl.textContent = data.plan_icon || '🆓';
    if (nameEl) nameEl.textContent = data.plan_name || 'رایگان';

    if (descEl) {
        if (data.is_premium) {
            descEl.textContent = 'از تمام امکانات لذت ببر! ⭐';
        } else {
            descEl.textContent = 'همه‌ی امکانات پایه برای همه';
        }
    }
}


// ============================================================
// نمایش ویژگی‌ها
// ============================================================

function renderFeatures(features) {
    const container = document.getElementById('featuresGrid');
    if (!container) return;

    const featuresList = [
        { key: 'rag_enabled', icon: '🤖', name: 'تحلیل هوشمند' },
        { key: 'llm_summary', icon: '📊', name: 'گزارش هفتگی' },
        { key: 'pdf_export', icon: '📄', name: 'خروجی PDF' },
        { key: 'premium_themes', icon: '🎨', name: 'تم‌های ویژه' },
        { key: 'cloud_backup', icon: '☁️', name: 'بکاپ ابری' },
        { key: 'rag_enabled_2', icon: '💬', name: 'چت هوشمند' },
    ];

    let html = '';
    featuresList.forEach(f => {
        const enabled = features[f.key] === true;
        html += `
            <div class="feature-item ${enabled ? 'enabled' : 'disabled'}">
                <span class="feature-icon">${enabled ? '✅' : '❌'}</span>
                <span>${f.icon} ${f.name}</span>
            </div>
        `;
    });

    container.innerHTML = html;
}


// ============================================================
// بارگذاری وضعیت استفاده
// ============================================================

function loadUsage() {
    Promise.all([
        fetch('/api/subscription/usage').then(r => r.json()).catch(() => ({})),
        fetch('/api/subscription/status').then(r => r.json()).catch(() => ({}))
    ])
    .then(([usage, status]) => {
        const limits = status.limits || {};

        // ===== تشخیص =====
        updateUsageBar(
            'usageBarDiagnosis',
            'usageCountDiagnosis',
            usage.diagnosis_today || 0,
            limits.diagnosis_per_day || 5
        );

        // ===== چت =====
        updateUsageBar(
            'usageBarChat',
            'usageCountChat',
            usage.chat_today || 0,
            limits.chat_per_day || 50
        );

        // ===== یاداشت =====
        updateUsageBar(
            'usageBarNotes',
            'usageCountNotes',
            usage.notes_today || 0,
            limits.notes_per_day || 20
        );

        // ===== تاریخچه =====
        const historyEl = document.getElementById('usageCountHistory');
        if (historyEl) {
            historyEl.textContent = toPersian(limits.history_days || 365) + ' روز';
        }
    })
    .catch(err => console.error('❌ خطا در بارگذاری usage:', err));
}


// ============================================================
// به‌روزرسانی نوار استفاده
// ============================================================

function updateUsageBar(barId, countId, used, limit) {
    const barEl = document.getElementById(barId);
    const countEl = document.getElementById(countId);

    if (!barEl || !countEl) return;

    // ===== نامحدود =====
    if (limit === -1) {
        barEl.style.width = '100%';
        barEl.classList.remove('warning', 'danger');
        countEl.textContent = toPersian(used) + ' ♾️';
        return;
    }

    // ===== متن =====
    countEl.textContent = toPersian(used) + ' از ' + toPersian(limit);

    // ===== درصد =====
    const percent = limit > 0 ? Math.min(100, (used / limit) * 100) : 0;
    barEl.style.width = percent + '%';

    // ===== رنگ =====
    barEl.classList.remove('warning', 'danger');
    if (percent >= 90) {
        barEl.classList.add('danger');
    } else if (percent >= 70) {
        barEl.classList.add('warning');
    }
}


// ============================================================
// FAQ
// ============================================================

function toggleFaq(element) {
    element.classList.toggle('open');
}


// ============================================================
// اطلاع‌رسانی پریمیوم
// ============================================================

function notifyPremiumInterest() {
    const btn = document.querySelector('.premium-notify-btn');
    if (!btn) return;

    // ===== بررسی اینکه کاربر قبلاً ثبت کرده یا نه =====
    const key = 'premium_interest_registered';
    if (localStorage.getItem(key) === 'true') {
        showToast('قبلاً ثبت کردی! بهت خبر می‌دیم ✅', '🔔', 'info');
        return;
    }

    // ===== ثبت در localStorage (به‌عنوان راه‌حل موقت) =====
    localStorage.setItem(key, 'true');
    localStorage.setItem('premium_interest_date', new Date().toISOString());

    // ===== ظاهر =====
    btn.textContent = '✅ ثبت شد! بهت خبر می‌دیم';
    btn.disabled = true;

    // ===== Toast =====
    if (typeof showToast === 'function') {
        showToast('✅ ثبت شد! وقتی پریمیوم فعال شد، خبرت می‌کنیم', '🔔', 'success');
    }

    console.log('🔔 علاقه‌مندی به پریمیوم ثبت شد');
}


// ============================================================
// تبدیل عدد به فارسی
// ============================================================

function toPersian(num) {
    const persianDigits = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
    return String(num).split('').map(d => persianDigits[parseInt(d)] || d).join('');
}


// ============================================================
// صادر کردن
// ============================================================

window.toggleFaq = toggleFaq;
window.notifyPremiumInterest = notifyPremiumInterest;
