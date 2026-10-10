// ============================================================
// ثبت و ذخیره‌سازی پرسشنامه
// ============================================================

import { mcQuestions } from '../../data/questions.js';
import { getMcqProgress, getCurrentPageId } from './validator.js';

// ============================================================
// متغیرها
// ============================================================

let isSubmitting = false;

// ============================================================
// توابع صادر شده
// ============================================================

export function selectOption(el) {
    const parent = el.parentElement;
    parent.querySelectorAll('label').forEach(label => {
        label.classList.remove('selected');
    });
    el.classList.add('selected');
    el.querySelector('input[type="radio"]').checked = true;
    saveCurrentAnswers();
    if (typeof window.updateProgress === 'function') {
        window.updateProgress();
    }
}

export function saveCurrentAnswers() {
    const mcqAnswers = {};
    for (let i = 0; i < 20; i++) {
        const selected = document.querySelector(`input[name="mc${i}"]:checked`);
        mcqAnswers[i] = selected ? selected.value : null;
    }
    localStorage.setItem('mcq_answers', JSON.stringify(mcqAnswers));

    const openAnswers = {};
    for (let j = 0; j < 3; j++) {
        const textarea = document.getElementById(`openText${j}`);
        openAnswers[j] = textarea ? textarea.value : '';
    }
    localStorage.setItem('open_answers', JSON.stringify(openAnswers));

    const progress = {
        mcqCompleted: getMcqProgress(),
        currentPage: getCurrentPageId(),
        timestamp: new Date().toISOString()
    };
    localStorage.setItem('questionnaire_progress', JSON.stringify(progress));

    if (typeof window.updateContinueBadge === 'function') {
        window.updateContinueBadge();
    }
}

export function startQuestionnaire() {
    const progress = JSON.parse(localStorage.getItem('questionnaire_progress') || 'null');
    if (progress && progress.mcqCompleted > 0 && progress.mcqCompleted < 20) {
        if (typeof window.goToPage === 'function') {
            window.goToPage(progress.currentPage);
        }
    } else {
        window.location.href = '/questionnaire';
    }
}

export function submitAll() {
    if (isSubmitting) return;

    // ===== چک سوالات MCQ =====
    for (let i = 0; i < 20; i++) {
        const checked = document.querySelector(`input[name="mc${i}"]:checked`);
        if (!checked) {
            window.showToast('⚠️ لطفاً به همه سوالات متنی پاسخ دهید.', '⚠️', 'warning');
            return;
        }
    }

    // ===== چک سوالات باز =====
    for (let j = 0; j < 3; j++) {
        const textarea = document.getElementById(`openText${j}`);
        const text = textarea ? textarea.value.trim() : '';
        const blob = window.getAudioBlob ? window.getAudioBlob(j) : null;

        if (!text && !blob) {
            window.showToast(`⚠️ لطفاً به سوال باز شماره ${j + 1} پاسخ دهید.`, '⚠️', 'warning');
            return;
        }

        if (text && text.length < 10) {
            window.showToast(`⚠️ پاسخ سوال ${j + 1} باید حداقل ۱۰ کاراکتر باشه`, '⚠️', 'warning');
            return;
        }
    }

    // ===== رفتن به صفحه لودینگ =====
    if (typeof window.goToPage === 'function') {
        window.goToPage('pageLoading');
    }
    isSubmitting = true;

    // ===== جمع‌آوری داده =====
    const mcAnswers = [];
    const textAnswers = [];
    const audioFiles = [];

    for (let m = 0; m < 20; m++) {
        const selected = document.querySelector(`input[name="mc${m}"]:checked`);
        mcAnswers.push(selected ? selected.value : '');
    }

    for (let k = 0; k < 3; k++) {
        const textarea = document.getElementById(`openText${k}`);
        textAnswers.push(textarea ? textarea.value : '');
    }

    for (let l = 0; l < 3; l++) {
        const blob = window.getAudioBlob ? window.getAudioBlob(l) : null;
        if (blob) {
            audioFiles.push(new File([blob], `recording_${l}.wav`, { type: 'audio/wav' }));
        }
    }

    // ===== ارسال به سرور =====
    const formData = new FormData();
    for (let m = 0; m < 20; m++) {
        formData.append('mc_answers[]', mcAnswers[m] || '');
    }
    for (let k = 0; k < 3; k++) {
        formData.append('text_answers[]', textAnswers[k] || '');
    }
    audioFiles.forEach(file => {
        formData.append('audio_files[]', file);
    });

    fetch('/api/predict', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            window.showToast('❌ ' + data.error, '❌', 'error');
            isSubmitting = false;
            return;
        }

        const result = {
            prediction: data.prediction,
            score: data.score,
            mcqScore: data.mcqScore,
            llmScore: data.llmScore,
            llmStatus: data.llmStatus,
            treatment: data.treatment,
            llmEnabled: data.llmEnabled
        };

        localStorage.setItem('pendingResult', JSON.stringify(result));
        window.location.href = '/result';
    })
    .catch(error => {
        console.error('❌ خطا:', error);
        window.showToast('❌ خطا در ارتباط با سرور', '❌', 'error');
        isSubmitting = false;
    });
}

export function resetApp() {
    document.querySelectorAll('input[type="radio"]').forEach(i => { i.checked = false; });
    document.querySelectorAll('textarea').forEach(t => { t.value = ''; });
    document.querySelectorAll('audio').forEach(a => { a.style.display = 'none'; });
    document.querySelectorAll('.options label').forEach(label => { label.classList.remove('selected'); });
    document.querySelectorAll('.recording-status').forEach(s => {
        s.textContent = 'وضعیت: آماده';
        s.className = 'recording-status';
    });
    document.querySelectorAll('.btn-circle').forEach(btn => { btn.classList.remove('btn-recording'); });

    for (let i = 0; i < 3; i++) {
        window.audioBlobs = window.audioBlobs || {};
        window.audioBlobs[i] = null;
        if (window.recordingTimers && window.recordingTimers[i]) {
            clearInterval(window.recordingTimers[i]);
            window.recordingTimers[i] = null;
        }
    }

    isSubmitting = false;

    localStorage.removeItem('mcq_answers');
    localStorage.removeItem('open_answers');
    localStorage.removeItem('questionnaire_progress');

    window.location.href = '/';
    window.showToast('🔄 برنامه ریست شد', '🔄', 'info');
}
