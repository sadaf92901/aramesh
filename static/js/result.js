
// ============================================================
// صفحه‌ی نتیجه
// ============================================================

function showResult(result) {
    console.log('📊 نمایش نتیجه:', result);

    const labels = ['سالم', 'خفیف', 'متوسط', 'شدید'];
    const classes = ['healthy', 'mild', 'moderate', 'severe'];
    const pred = result.prediction || 0;
    const score = result.score || 50;

    // ===== دایره =====
    const circle = document.getElementById('resultCircle');
    if (circle) circle.className = 'result-circle ' + classes[pred];

    const scoreEl = document.getElementById('resultScore');
    if (scoreEl) scoreEl.textContent = Math.round(score) + '%';

    const statusEl = document.getElementById('resultStatus');
    if (statusEl) statusEl.textContent = 'وضعیت: ' + labels[pred];

    // ===== جزئیات =====
    let detail = '';
    if (score >= 65) detail = 'احساسات شما نشان‌دهنده‌ی سلامت کامل است.';
    else if (score >= 45) detail = 'احساسات شما نشان‌دهنده‌ی خفیف‌ترین سطح افسردگی است.';
    else if (score >= 25) detail = 'احساسات شما نشان‌دهنده‌ی افسردگی متوسط است.';
    else detail = 'احساسات شما نشان‌دهنده‌ی افسردگی شدید است.';

    const detailEl = document.getElementById('resultDetail');
    if (detailEl) detailEl.textContent = detail;

    // ===== امتیاز MCQ =====
    const mcqEl = document.getElementById('mcqScoreDisplay');
    if (mcqEl) mcqEl.textContent = Math.round(result.mcqScore || 0) + '%';

    // ===== امتیاز LLM =====
    const llmEl = document.getElementById('llmScoreDisplay');
    if (llmEl) llmEl.textContent = Math.round(result.llmScore || 0) + '%';

    const llmStatusEl = document.getElementById('llmStatusDisplay');
    if (llmStatusEl) {
        const statusColors = {
            'موفق': '#22c55e',
            'مثبت': '#22c55e',
            'منفی': '#ef4444',
            'خنثی': '#f59e0b',
            'غیرفعال': '#94a3b8',
            'نامعتبر': '#ef4444'
        };
        llmStatusEl.textContent = 'وضعیت: ' + (result.llmStatus || '-');
        llmStatusEl.style.color = statusColors[result.llmStatus] || '#64748b';
    }

    // ===== درمان =====
    const treatmentEl = document.getElementById('resultTreatment');
    if (treatmentEl) treatmentEl.textContent = result.treatment || '';

    // ===== توصیه‌ها =====
    renderRecommendations(pred);
        // ===== نمایش کمک فوری (اگه شدید بود) =====
    const emergencyCard = document.getElementById('emergencyCard');
    if (emergencyCard) {
        if (pred === 3) {
            emergencyCard.style.display = 'block';
        } else {
            emergencyCard.style.display = 'none';
        }
    }
    // ===== مقایسه =====
    loadComparison();
}

// ============================================================
// توصیه‌های عملی
// ============================================================

function renderRecommendations(prediction) {
    const container = document.getElementById('recommendationsBody');
    if (!container) return;

    const recommendations = {
        0: [ // سالم
            'روزانه ۵ دقیقه تمرین تنفس',
            'یاداشت روزانه برای ثبت حالات',
            'معاشرت با دوستان و خانواده',
            'خواب منظم (۷-۸ ساعت)'
        ],
        1: [ // خفیف
            'روزانه ۱۰ دقیقه مدیتیشن',
            'ورزش سبک (پیاده‌روی ۲۰ دقیقه)',
            'با دوستانت صحبت کن',
            'از الکل و کافئین زیاد پرهیز کن',
            'تمرین تنفس قبل از خواب'
        ],
        2: [ // متوسط
            'مشاوره با روانشناس',
            'روزانه ۱۵ دقیقه مدیتیشن',
            'ورزش منظم (۳۰ دقیقه)',
            'دفترچه‌ی افکار منفی بنویس',
            'با افراد مورد اعتماد صحبت کن'
        ],
        3: [ // شدید
            'حتماً با روانشناس متخصص مشورت کن',
            'با اورژانس اجتماعی (۱۲۳) تماس بگیر',
            'روزانه تمرین تنفس عمیق',
            'از تنها موندن پرهیز کن',
            'الان با یه نفر مورد اعتماد صحبت کن'
        ]
    };

    const items = recommendations[prediction] || recommendations[0];

    container.innerHTML = `
        <ul>
            ${items.map(item => `<li>${item}</li>`).join('')}
        </ul>
    `;
}

// ============================================================
// مقایسه با تشخیص قبلی
// ============================================================

function loadComparison() {
    fetch('/api/history/compare')
        .then(res => res.json())
        .then(data => {
            if (!data.has_comparison) return;

            const card = document.getElementById('comparisonCard');
            const body = document.getElementById('comparisonBody');

            if (!card || !body) return;

            const latest = data.latest;
            const previous = data.previous;

            body.innerHTML = `
                <div class="comparison-item">
                    <div class="comparison-item-label">قبلی</div>
                    <div class="comparison-item-value">${Math.round(previous.score)}%</div>
                </div>
                <div class="comparison-arrow">→</div>
                <div class="comparison-item">
                    <div class="comparison-item-label">الان</div>
                    <div class="comparison-item-value">${Math.round(latest.score)}%</div>
                </div>
                <div class="comparison-trend ${data.trend}">
                    ${data.trend_icon} ${data.trend_text} (${data.diff > 0 ? '+' : ''}${data.diff}%)
                </div>
            `;

            card.style.display = 'block';
        })
        .catch(err => console.error('❌ خطا در مقایسه:', err));
}

// ============================================================
// اشتراک‌گذاری
// ============================================================

function shareResult() {
    const statusEl = document.getElementById('resultStatus');
    const scoreEl = document.getElementById('resultScore');

    const text = '🧠 نتیجه تحلیل سلامت روان من:\n\n' +
        (statusEl ? statusEl.textContent : '') + '\n' +
        'امتیاز: ' + (scoreEl ? scoreEl.textContent : '') + '\n\n' +
        '#همراه_آرامش #سلامت_روان';

    if (navigator.share) {
        navigator.share({
            title: 'نتیجه تحلیل سلامت روان',
            text: text,
            url: window.location.href
        }).catch(err => {
            if (err.name !== 'AbortError') copyToClipboard(text);
        });
    } else {
        copyToClipboard(text);
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        if (typeof showToast === 'function') {
            showToast('📋 متن کپی شد!', '✅', 'success');
        }
    }).catch(() => {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        if (typeof showToast === 'function') {
            showToast('📋 متن کپی شد!', '✅', 'success');
        }
    });
}

// ============================================================
// صادر کردن
// ============================================================

window.showResult = showResult;
window.shareResult = shareResult;
