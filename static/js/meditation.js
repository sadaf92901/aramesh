// ============================================================
// تمرین مدیتیشن
// ============================================================

const MEDITATIONS = {
    breathing: {
        name: 'مدیتیشن تنفس آرام',
        icon: '🌬️',
        duration: 300, // ۵ دقیقه
        desc: 'آرامش از طریق نفس',
        audio: '/static/audio/meditation/breathing.mp3',
        texts: [
            'سلام. به این لحظه خوش آمدی.',
            'همین حالا، هر جا که هستی، کمی راحت‌تر بنشین.',
            'شانه‌هایت را رها کن. دست‌هایت را روی زانو یا شکمت بگذار.',
            'چشم‌هایت را آرام ببند... یا به یک نقطه روبرو نگاه کن.',
            'توجهت را ببر به نفس‌هایت. لازم نیست تغییرش بدهی.',
            'فقط تماشا کن که چطور وارد می‌شود... و چطور بیرون می‌رود.',
            'با هر دم، آرامش را به بدنت دعوت کن.',
            'با هر بازدم، هر تنشی را رها کن.',
            'اگر فکری آمد، اشکالی ندارد.',
            'فقط مثل ابری در آسمان، تماشایش کن و بگذار برود.',
            'و دوباره برگرد به نفس.',
            'تو همین حالا، همین جا، کامل هستی. هیچ چیزی کم نداری.',
            'فقط نفس بکش... و آرام باش.',
            'کم‌کم توجهت را به بدنت برگردان. انگشت‌های دستت را حرکت بده.',
            'و هر وقت آماده بودی، چشم‌هایت را باز کن.',
            'ممنون که این چند دقیقه را به خودت هدیه دادی.'
        ]
    },
    release: {
        name: 'مدیتیشن رهاسازی تنش',
        icon: '🍃',
        duration: 420, // ۷ دقیقه
        desc: 'آزاد کردن تنش‌های بدن',
        audio: '/static/audio/meditation/release.mp3',
        texts: [
            'بنشین یا دراز بکش، به شکلی که کاملاً راحت باشی.',
            'اگر دراز کشیده‌ای، دست‌هایت را کنار بدنت بگذار. چشم‌هایت را ببند.',
            'یک نفس عمیق بکش... و با بازدم، رها کن.',
            'توجهت را ببر به پیشانی‌ات. اگر اخمی هست، بازش کن.',
            'پیشانی‌ات را کاملاً صاف و آرام کن.',
            'برو سراغ فک و دهانت. فک را کمی باز کن، زبانت را رها کن.',
            'بگذار دهانت کاملاً شل شود.',
            'توجهت را ببر به گردنت. هر تنشی داری، با بازدم بیرون بریز.',
            'شانه‌هایت را بالا ببر... و با بازدم، رها کن.',
            'دوباره... بالا ببر... و رها کن.',
            'برو سراغ دست‌هایت. از شانه تا آرنج... از آرنج تا مچ... و نوک انگشتان.',
            'همه را رها کن.',
            'قفسه سینه‌ات را آرام کن. با هر دم، هوا وارد ریه‌هایت می‌شود.',
            'با هر بازدم، سنگینی از روی سینه‌ات برداشته می‌شود.',
            'شکمت را رها کن. بگذار نفس‌هایت آرام و طبیعی باشند.',
            'برو سراغ پاهایت. ران‌ها... زانوها... ساق‌ها... و کف پاها.',
            'همه را رها کن.',
            'تمام بدنت حالا سبک‌تر است. آرام‌تر است.',
            'و تو در این آرامش، امن هستی.',
            'کم‌کم نفس عمیقی بکش. بدنت را کمی حرکت بده.',
            'و هر وقت آماده بودی، چشم‌هایت را باز کن.'
        ]
    },
    gratitude: {
        name: 'مدیتیشن شکرگزاری',
        icon: '✨',
        duration: 300, // ۵ دقیقه
        desc: 'تمرکز بر چیزهای خوب زندگی',
        audio: '/static/audio/meditation/gratitude.mp3',
        texts: [
            'به این لحظه خوش آمدی.',
            'چشم‌هایت را ببند و چند نفس آرام بکش.',
            'حالا از خودت بپرس: امروز برای چه چیزی می‌توانم شکرگزار باشم؟',
            'شاید یک چیز کوچک باشد. یک لبخند. یک نفس راحت. یک لحظه آرامش.',
            'شکرگزاری یعنی دیدن چیزهایی که همیشه هستند، اما ما آن‌ها را نمی‌بینیم.',
            'به بدنت فکر کن. به قلبت که بی‌وقفه می‌تپد.',
            'به ریه‌هایت که نفس می‌کشند. به چشمانت که می‌بینند.',
            'به آدم‌هایی فکر کن که در زندگی‌ات هستند.',
            'حتی اگر همه‌شان کامل نباشند.',
            'و حالا، یک «ممنونم» از ته دل بگو.',
            'به خودت... به زندگی... به هر چیزی که هست.',
            'این حس شکرگزاری را در قلبت نگه دار.',
            'و هر وقت آماده بودی، چشم‌هایت را باز کن.'
        ]
    },
    sleep: {
        name: 'مدیتیشن قبل از خواب',
        icon: '🌙',
        duration: 600, // ۱۰ دقیقه
        desc: 'آرامش عمیق برای خواب',
        audio: '/static/audio/meditation/sleep.mp3',
        texts: [
            'دراز بکش. سرت را روی بالش بگذار.',
            'دست‌هایت را کنار بدنت رها کن. چشم‌هایت را ببند.',
            'امشب، قرار نیست به هیچ چیز فکر کنی. قرار نیست هیچ مشکلی را حل کنی.',
            'فقط می‌خواهی آرام باشی.',
            'یک نفس عمیق بکش... و با بازدم، تمام روزت را رها کن.',
            'تمام کارهایی که امروز انجام دادی. تمام حرف‌هایی که زدی.',
            'تمام فکرهایی که از سرت گذشت. همه را رها کن.',
            'حالا توجهت را ببر به پاهایت. از نوک انگشتان پا شروع کن.',
            'حس کن که چقدر سنگین‌اند. چقدر خسته‌اند. بگذار کاملاً رها شوند.',
            'این رهایی را آرام آرام بالا بیاور. ساق‌ها... زانوها... ران‌ها.',
            'بگذار شکمت با هر نفس، آرام بالا و پایین برود.',
            'سینه‌ات را رها کن. شانه‌هایت را رها کن. گردنت را رها کن.',
            'و حالا صورتت. پیشانی‌ات را صاف کن. فکت را شل کن. زبانت را رها کن.',
            'تمام بدنت حالا سنگین و آرام است. مثل اینکه روی ابری نرم دراز کشیده‌ای.',
            'هیچ چیز مهم نیست. فقط خواب... و آرامش.',
            'کم‌کم به خواب می‌روی. بدنت را رها کن. ذهنت را رها کن.',
            'و بگذار خواب بیاید.',
            'شب بخیر.'
        ]
    }
};

let currentSession = null;
let sessionInterval = null;
let sessionTimer = null;
let sessionSeconds = 0;
let currentTextIndex = 0;
let currentAudio = null;

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

    // ===== پخش فایل صوتی =====
    if (meditation.audio) {
        try {
            currentAudio = new Audio(meditation.audio);
            currentAudio.volume = 0.8;
            currentAudio.play().catch(err => {
                console.warn('⚠️ فایل صوتی پخش نشد:', err);
            });
        } catch (err) {
            console.warn('⚠️ خطا در ایجاد صدا:', err);
        }
    }

    sessionTimer = setInterval(() => {
        sessionSeconds--;
        const elapsed = meditation.duration - sessionSeconds;
        const progress = (elapsed / meditation.duration) * 100;

        const timerEl = document.getElementById('sessionTimer');
        if (timerEl) timerEl.textContent = formatTime(sessionSeconds);

        const progressEl = document.getElementById('sessionProgress');
        if (progressEl) progressEl.style.width = progress + '%';

        // ===== تغییر متن بر اساس زمان =====
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

    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        currentAudio = null;
    }

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
                if (data.success) showToast('⏸ تمرین ناقص ذخیره شد', '💾', 'info');
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

    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        currentAudio = null;
    }

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
        if (data.success) showToast('🎉 آفرین! تمرین تکمیل شد', '✨', 'success');
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
