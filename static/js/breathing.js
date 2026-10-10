// ============================================================
// تمرین تنفس - صفحه اختصاصی
// ============================================================

let pageBreathInterval = null;
let pageBreathTimer = null;
let pageBreathSeconds = 30;
let pageBreathRunning = false;

document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ صفحه تنفس بارگذاری شد');
    loadBreathingStats();
    setTimeout(function() {
        console.log('🚀 شروع خودکار تمرین');
        startPageBreathing();
    }, 500);
});

function loadBreathingStats() {
    fetch('/api/breathing')
        .then(res => res.json())
        .then(data => {
            if (data.count !== undefined) {
                const todayEl = document.getElementById('todayCount');
                const weekEl = document.getElementById('weekCount');
                if (todayEl) todayEl.textContent = data.count || 0;
                if (weekEl) weekEl.textContent = data.count || 0;
            }
        })
        .catch(err => console.error('❌ خطا:', err));
}

function startPageBreathing() {
    if (pageBreathRunning) return;
    pageBreathRunning = true;

    const exercise = document.getElementById('breathingExercise');
    const circle = document.getElementById('breathCircle');
    const text = document.getElementById('breathText');
    const timer = document.getElementById('breathTimer');
    const progress = document.getElementById('breathProgress');
    const icon = document.getElementById('breathIcon');

    if (!exercise) {
        console.error('❌ breathingExercise پیدا نشد!');
        return;
    }

    exercise.style.display = 'block';
    pageBreathSeconds = 30;

    const steps = [
        { action: 'inhale', text: '🌬️ دم... (۴ ثانیه)', icon: '🌊' },
        { action: 'hold', text: '😌 نگه دار... (۴ ثانیه)', icon: '🌊' },
        { action: 'exhale', text: '🌊 بازدم... (۴ ثانیه)', icon: '🌊' }
    ];

    let stepIndex = 0;

    // ===== فعال‌سازی اولیه‌ی راهنما =====
    document.querySelectorAll('.breathing-guide .guide-item').forEach((el, i) => {
        el.classList.toggle('active', i === 0);
    });

    pageBreathInterval = setInterval(function() {
        const step = steps[stepIndex];
        if (circle) circle.className = 'breath-circle ' + step.action;
        if (text) text.textContent = step.text;
        if (icon) icon.textContent = step.icon;

        // ===== راهنمای زنده =====
        document.querySelectorAll('.breathing-guide .guide-item').forEach((el, i) => {
            el.classList.toggle('active', i === stepIndex);
        });

        stepIndex = (stepIndex + 1) % steps.length;
    }, 4000);

    pageBreathTimer = setInterval(function() {
        pageBreathSeconds--;
        if (timer) timer.textContent = '۰:' + (pageBreathSeconds < 10 ? '0' : '') + pageBreathSeconds;
        if (progress) progress.style.width = ((30 - pageBreathSeconds) / 30 * 100) + '%';

        if (pageBreathSeconds <= 0) {
            completePageBreathing();
        }
    }, 1000);

    showToast('🌬️ تمرین تنفس شروع شد!', '🧘', 'info');
}

function stopPageBreathing() {
    if (pageBreathTimer) clearInterval(pageBreathTimer);
    if (pageBreathInterval) clearInterval(pageBreathInterval);
    pageBreathRunning = false;
    pageBreathSeconds = 30;

    // ===== خاموش کردن راهنما =====
    document.querySelectorAll('.breathing-guide .guide-item').forEach(el => {
        el.classList.remove('active');
    });
}

function resetPageBreathing() {
    stopPageBreathing();
    setTimeout(startPageBreathing, 500);
}

function completePageBreathing() {
    if (pageBreathTimer) clearInterval(pageBreathTimer);
    if (pageBreathInterval) clearInterval(pageBreathInterval);
    pageBreathRunning = false;

    fetch('/api/breathing')
        .then(res => res.json())
        .then(data => {
            const newCount = (data.count || 0) + 1;
            return fetch('/api/breathing', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ count: newCount })
            });
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                console.log('✅ تمرین تنفس ذخیره شد');
                loadBreathingStats();
            }
        })
        .catch(err => console.error('❌ خطا:', err));

    showToast('🧘 تمرین تنفس تمام شد!', '✨', 'success');

    setTimeout(function() {
        window.location.href = '/';
    }, 1500);
}

// ============================================================
// صادر کردن به window برای onclick در HTML
// ============================================================
window.startPageBreathing = startPageBreathing;
window.stopPageBreathing = stopPageBreathing;
window.resetPageBreathing = resetPageBreathing;
