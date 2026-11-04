import { mcQuestions, openQuestions } from '../../data/questions.js';

let _questionsBuilt = false;

// ============================================================
// توابع
// ============================================================

function buildQuestions() {
    if (_questionsBuilt) return;
    _questionsBuilt = true;
    console.log('🏗️ ساخت سوالات شروع شد...');
    buildMcqQuestions();
    buildOpenQuestions();
    loadSavedAnswers();
    console.log('✅ ساخت سوالات تمام شد!');
}

function buildMcqQuestions() {
    console.log('🏗️ ساخت سوالات MCQ...');
    const groups = [
        document.getElementById('qGroup1'),
        document.getElementById('qGroup2'),
        document.getElementById('qGroup3'),
        document.getElementById('qGroup4')
    ];
    groups.forEach(g => { if (g) g.innerHTML = ''; });

    mcQuestions.forEach((item, index) => {
        const div = document.createElement('div');
        div.className = 'question-item';
        let html = `<label>${index + 1}. ${item.q}</label><div class="options">`;
        item.opts.forEach(opt => {
            html += `<label onclick="window.selectOption(this)">
                <input type="radio" name="mc${index}" value="${opt}"> ${opt}
            </label>`;
        });
        html += '</div>';
        div.innerHTML = html;
        const gi = Math.floor(index / 5);
        if (groups[gi]) groups[gi].appendChild(div);
    });
    console.log('✅ ساخت MCQ تمام شد!');
}

function buildOpenQuestions() {
    console.log('🏗️ ساخت سوالات باز...');
    const openGroup = document.getElementById('openGroup1');
    if (!openGroup) {
        console.error('❌ openGroup1 پیدا نشد!');
        return;
    }
    openGroup.innerHTML = '';

    openQuestions.forEach((item, index) => {
        const div = document.createElement('div');
        div.className = 'question-item';
        div.innerHTML = `
            <label>${index + 1}. ${item.q}</label>
            <div class="question-hint">${item.hint || ''}</div>
            <div class="recording-area">
                <textarea
                    rows="3"
                    placeholder="پاسخ خود را بنویسید..."
                    id="openText${index}"
                    minlength="10"
                    maxlength="1000"
                ></textarea>
                <button class="btn btn-circle btn-sm" onclick="window.startRecording(${index})" id="recordBtn${index}">🎤</button>
                <button class="btn btn-circle btn-sm btn-secondary" onclick="window.stopRecording(${index})" id="stopBtn${index}" disabled>⏹️</button>
            </div>
            <div class="recording-status" id="recordingStatus${index}">وضعیت: آماده</div>
            <audio id="audioPlayback${index}" controls style="display:none;"></audio>
        `;
        openGroup.appendChild(div);

        // 🆕 جلوگیری از تایپ انگلیسی
        const textarea = document.getElementById(`openText${index}`);
        if (textarea) {
            textarea.addEventListener('input', function() {
                var englishRegex = /[a-zA-Z]/g;
                if (englishRegex.test(this.value)) {
                    this.value = this.value.replace(englishRegex, '');
                    if (typeof window.showToast === 'function') {
                        window.showToast('⚠️ لطفاً فقط فارسی تایپ کنید', '⚠️', 'warning');
                    }
                }
            });
        }
    });
    console.log('✅ ساخت سوالات باز تمام شد!');
}

function loadSavedAnswers() {
    console.log('📂 بارگذاری پاسخ‌های ذخیره شده...');

    const mcqAnswers = JSON.parse(localStorage.getItem('mcq_answers') || '{}');
    Object.keys(mcqAnswers).forEach(index => {
        const value = mcqAnswers[index];
        if (value) {
            document.querySelectorAll(`input[name="mc${index}"]`).forEach(radio => {
                if (radio.value === value) {
                    radio.checked = true;
                    const label = radio.closest('label');
                    if (label) label.classList.add('selected');
                }
            });
        }
    });

    const openAnswers = JSON.parse(localStorage.getItem('open_answers') || '{}');
    Object.keys(openAnswers).forEach(index => {
        const textarea = document.getElementById(`openText${index}`);
        if (textarea && openAnswers[index]) textarea.value = openAnswers[index];
    });

    if (typeof window.updateProgress === 'function') window.updateProgress();
    console.log('✅ بارگذاری پاسخ‌ها تمام شد!');
}

// ============================================================
// صادرات به window
// ============================================================

window.buildQuestions = buildQuestions;
window.buildMcqQuestions = buildMcqQuestions;
window.buildOpenQuestions = buildOpenQuestions;
window.loadSavedAnswers = loadSavedAnswers;

export {
    buildQuestions,
    buildMcqQuestions,
    buildOpenQuestions,
    loadSavedAnswers
};
