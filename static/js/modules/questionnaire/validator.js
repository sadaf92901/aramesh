// ============================================================
// اعتبارسنجی پرسشنامه
// ============================================================

import { saveCurrentAnswers } from './submitter.js';

export function validateAndGo(pageId) {
    const currentPage = document.querySelector('.page.active');
    const radios = currentPage.querySelectorAll('input[type="radio"]');
    const questionNames = {};
    let allAnswered = true;

    radios.forEach(radio => {
        const name = radio.name;
        if (!questionNames[name]) questionNames[name] = false;
        if (radio.checked) questionNames[name] = true;
    });

    for (const key in questionNames) {
        if (!questionNames[key]) {
            allAnswered = false;
            break;
        }
    }

    if (!allAnswered) {
        window.showToast('⚠️ لطفاً به همه سوالات این صفحه پاسخ دهید.', '⚠️', 'warning');
        return;
    }

    saveCurrentAnswers();
    window.updateProgress();
    window.goToPage(pageId);
}

export function goToPage(pageId) {
    document.querySelectorAll('.page').forEach(p => {
        p.classList.remove('active');
        p.style.display = 'none';
    });

    const target = document.getElementById(pageId);
    if (target) {
        target.style.display = 'flex';
        target.classList.add('active');
        if (typeof window.scrollToTop === 'function') {
            window.scrollToTop();
        }
    }

    setTimeout(() => {
        if (typeof window.updateProgress === 'function') {
            window.updateProgress();
        }
    }, 100);
}

export function getCurrentPageId() {
    const active = document.querySelector('.page.active');
    return active ? active.id : 'pageWelcome';
}

export function getMcqProgress() {
    let answered = 0;
    for (let i = 0; i < 20; i++) {
        if (document.querySelector(`input[name="mc${i}"]:checked`)) {
            answered++;
        }
    }
    return answered;
}

export function updateContinueBadge() {
    const progress = JSON.parse(localStorage.getItem('questionnaire_progress') || 'null');
    const badge = document.getElementById('continueBadge');
    const title = document.getElementById('actionTitle');
    const subtitle = document.getElementById('actionSubtitle');
    const time = document.getElementById('actionTime');

    if (progress && progress.mcqCompleted > 0 && progress.mcqCompleted < 20) {
        if (badge) badge.textContent = `ادامه ${progress.mcqCompleted}/20`;
        if (title) title.textContent = 'ادامه تشخیص';
        if (subtitle) subtitle.textContent = 'از جایی که متوقف شدی ادامه بده';
        if (time) time.textContent = `⏱️ ${Math.round((20 - progress.mcqCompleted) / 2)} دقیقه باقی‌مانده`;
    } else {
        if (badge) badge.textContent = 'جدید';
        if (title) title.textContent = 'تشخیص کامل';
        if (subtitle) subtitle.textContent = 'ارزیابی دقیق وضعیت روان';
        if (time) time.textContent = '⏱️ حدود ۱۰ دقیقه';
    }
}

export function updateProgress() {
    const total = 20;
    const answered = document.querySelectorAll('input[type="radio"]:checked').length;
    const progress = Math.round((answered / total) * 100);

    document.querySelectorAll('.progress-bar').forEach(bar => {
        bar.style.width = progress + '%';
    });

    document.querySelectorAll('.progress-text').forEach(text => {
        if (text) text.textContent = progress + '%';
    });
}
