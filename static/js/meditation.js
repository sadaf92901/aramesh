// ============================================================
// تمرین مدیتیشن
// ============================================================

const MEDITATIONS = {
    morning: {
        name: 'مدیتیشن صبحگاهی',
        icon: '🌅',
        duration: 300,
        desc: 'شروع روز با آرامش',
        texts: [
            'راحت بشین و چشمانت رو ببند...',
            'سه نفس عمیق بکش...',
            'دم... نگه دار... بازدم...',
            'هوای تازه صبح رو حس کن...',
            'نور خورشید رو روی صورتت تصور کن...',
            'این نور داره وجودت رو گرم می‌کنه...',
            'بدنت رو از نوک انگشتای پا حس کن...',
            'کم‌کم این حس رو به بالای بدن ببر...',
            'شونه‌هات رو شل کن...',
            'گردنت رو آزاد بذار...',
            'حالا یه لبخند کوچیک بزن...',
            'امروز یه روز تازه‌ست...',
            'یه صفحه سفید که خودت می‌نویسی...',
            'با آرامش شروع کن...',
            'تو قوی‌تر از چیزی هستی که فکر می‌کنی...',
            'آرامش رو انتخاب کن...'
        ]
    },
    breathing: {
        name: 'مدیتیشن تنفس عمیق',
        icon: '🌬️',
        duration: 600,
        desc: 'کاهش استرس و اضطراب',
        texts: [
            'راحت بشین، پشتت صاف باشه...',
            'چشمانت رو ببند...',
            'دستات رو روی شکمت بذار...',
            'حالا فقط نفس...',
            'دم... یک... دو... سه... چهار...',
            'نگه دار... یک... دو...',
            'بازدم... یک... دو... سه... چهار...',
            'حس کن شکمت بالا و پایین میره...',
            'به هوایی که وارد بینی‌ات میشه توجه کن...',
            'سردی هوا رو حس کن...',
            'حالا گرمای بازدم رو...',
            'هر فکری که میاد، بذار بره...',
            'دوباره برگرد به نفس...',
            'دم... نگه دار... بازدم...',
            'تو این لحظه، هیچ کاری نداری...',
            'فقط نفس...',
            'آرامش در همین لحظه‌ست...',
            'تنش رو با هر بازدم بیرون بده...',
            'تو کنترل داری...',
            'همین‌جا باش، همین الان...'
        ]
    },
    night: {
        name: 'مدیتیشن شبانه',
        icon: '🌙',
        duration: 420,
        desc: 'آرامش قبل از خواب',
        texts: [
            'امروز رو رها کن...',
            'هر چی بود، تموم شد...',
            'چشمانت رو ببند...',
            'بدنت رو روی تخت حس کن...',
            'پاهات رو شل کن...',
            'دستات رو شل کن...',
            'نفس عمیق بکش...',
            'با هر بازدم، تنش رو بیرون بده...',
            'فکرها میان و میرن...',
            'تو فقط نگاه‌کننده باش...',
            'بذار فکرها برن...',
            'بدنت داره سنگین میشه...',
            'کم‌کم داره به خواب میری...',
            'هیچ کاری برای انجام دادن نیست...',
            'فردا روز جدیدیه...',
            'تو کارت رو انجام دادی...',
            'حالا وقت استراحته...',
            'خواب آرومی داشته باش...',
            'شب بخیر...'
        ]
    }
};
let currentSession = null;
let sessionInterval = null;
let sessionTimer = null;
let sessionSeconds = 0;
let currentTextIndex = 0;

document.addEventListener('DOMContentLoaded', function() {
    loadMeditationStats();
});

function loadMeditationStats() {
    fetch('/api/meditation/stats')
        .then(res => res.json())
        .then(data => {
            if (!data.error) {
                document.getElementById('todayMinutes').textContent = data.today_minutes || 0;
                document.getElementById('weekMinutes').textContent = data.week_minutes || 0;
                document.getElementById('todayCount').textContent = data.today_count || 0;
                document.getElementById('weekCount').textContent = data.week_count || 0;
            }
        })
        .catch(err => console.error('❌ خطا:', err));
}

function startMeditation(type) {
    const meditation = MEDITATIONS[type];
    if (!meditation) return;

    currentSession = {
        type: type,
        totalSeconds: meditation.duration,
        elapsedSeconds: 0
    };
    sessionSeconds = meditation.duration;
    currentTextIndex = 0;

    const mainContent = document.getElementById('meditationMain');
    mainContent.innerHTML = `
        <div class="meditation-session">
            <div class="session-icon">${meditation.icon}</div>
            <div class="session-title">${meditation.name}</div>
            <div class="session-timer" id="sessionTimer">${formatTime(sessionSeconds)}</div>
            <div class="session-text" id="sessionText">${meditation.texts[0]}</div>
            <div class="session-progress">
                <div class="session-progress-fill" id="sessionProgress"></div>
            </div>
            <div class="session-controls">
                <button class="session-btn stop" onclick="stopMeditation()">⏹ پایان</button>
            </div>
        </div>
    `;

    sessionTimer = setInterval(() => {
        sessionSeconds--;
        const elapsed = meditation.duration - sessionSeconds;
        const progress = (elapsed / meditation.duration) * 100;

        const timerEl = document.getElementById('sessionTimer');
        if (timerEl) timerEl.textContent = formatTime(sessionSeconds);

        const progressEl = document.getElementById('sessionProgress');
        if (progressEl) progressEl.style.width = progress + '%';

        const textInterval = Math.floor(meditation.duration / meditation.texts.length);
        const newTextIndex = Math.min(
            Math.floor(elapsed / textInterval),
            meditation.texts.length - 1
        );

        if (newTextIndex !== currentTextIndex) {
            currentTextIndex = newTextIndex;
            const textEl = document.getElementById('sessionText');
            if (textEl) {
                textEl.style.opacity = '0';
                setTimeout(() => {
                    textEl.textContent = meditation.texts[currentTextIndex];
                    textEl.style.opacity = '1';
                    textEl.style.transition = 'opacity 0.5s ease';
                }, 300);
            }
        }

        if (sessionSeconds <= 0) {
            completeMeditation();
        }
    }, 1000);

    showToast('🧘 مدیتیشن شروع شد!', '✨', 'success');
}

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return String(mins).padStart(2, '0') + ':' + String(secs).padStart(2, '0');
}

function stopMeditation() {
    if (sessionTimer) clearInterval(sessionTimer);
    sessionTimer = null;

    // ===== ذخیره تمرین ناقص (بیش از ۶۰ ثانیه) =====
    if (currentSession) {
        const elapsed = currentSession.totalSeconds - sessionSeconds;

        if (elapsed >= 60) {
            fetch('/api/meditation/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: currentSession.type,
                    duration: elapsed,
                    completed: false
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showToast('⏸ تمرین ناقص ذخیره شد', '💾', 'info');
                }
            })
            .catch(err => console.error('❌ خطا:', err));
        } else {
            showToast('⏹ تمرین خیلی کوتاه بود، ذخیره نشد', '⏹', 'warning');
        }
    }

    currentSession = null;
    setTimeout(reloadMeditationPage, 800);
}
function completeMeditation() {
    if (sessionTimer) clearInterval(sessionTimer);
    sessionTimer = null;

    if (!currentSession) return;

    fetch('/api/meditation/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            type: currentSession.type,
            duration: currentSession.totalSeconds
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            showToast('🎉 آفرین! تمرین تکمیل شد', '✨', 'success');
        }
        currentSession = null;
        setTimeout(reloadMeditationPage, 1500);
    })
    .catch(err => {
        console.error('❌ خطا:', err);
        currentSession = null;
        reloadMeditationPage();
    });
}

function reloadMeditationPage() {
    window.location.reload();
}
