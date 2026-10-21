// ============================================================
// فایل اصلی - راه‌اندازی و رویدادها
// ============================================================

// ============================================================
// Service Worker (PWA) — فقط در production
// ============================================================
if ('serviceWorker' in navigator) {
    const isLocalhost = (
        location.hostname === 'localhost' ||
        location.hostname === '127.0.0.1' ||
        location.hostname === ''
    );

    if (isLocalhost) {
        // ===== Development: پاک کردن SW و cache =====
        console.log('🔧 Development mode: پاک کردن Service Worker');

        navigator.serviceWorker.getRegistrations().then(function(registrations) {
            registrations.forEach(function(registration) {
                registration.unregister().then(function() {
                    console.log('🗑️ Service Worker پاک شد');
                });
            });
        });

        if ('caches' in window) {
            caches.keys().then(function(names) {
                names.forEach(function(name) {
                    caches.delete(name);
                    console.log('🗑️ کش پاک شد:', name);
                });
            });
        }
    } else {
        // ===== Production: ثبت SW =====
        console.log('🚀 Production mode: ثبت Service Worker');

        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/static/service-worker.js')
                .then(function(registration) {
                    console.log('✅ Service Worker ثبت شد:', registration.scope);
                })
                .catch(function(error) {
                    console.error('❌ خطا در ثبت Service Worker:', error);
                });
        });
    }
}


// ============================================================
// راه‌اندازی اپلیکیشن
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 راه‌اندازی اپلیکیشن...');

    // ===== توابع عمومی (همیشه اجرا میشن) =====

    loadAvatar();
    loadUser();
    updateConnectionStatus();

    // ===== بارگذاری وضعیت روزانه از سرور =====
    fetch('/api/daily-status')
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            var dates = Object.keys(data).sort().reverse();
            if (dates.length > 0) {
                var latest = data[dates[0]];
                localStorage.setItem('dailyStatus', JSON.stringify(latest));
                if (typeof window.statusValues !== 'undefined') {
                    Object.assign(window.statusValues, latest);
                    updateAllStatusDisplay();
                }
            }
        })
        .catch(function(error) {
            console.error('❌ خطا در دریافت وضعیت:', error);
        });

    // ===== فقط در صفحه اصلی (index.html) =====
    if (document.getElementById('pageWelcome')) {
        console.log('📍 صفحه اصلی');

        const dateEl = document.getElementById('summaryDate');
        if (dateEl) dateEl.textContent = getPersianDate();

        updateDailyQuote();
        updateAllStatusDisplay();
        updateMoodChart();
        updateStreakAndLevel();
        updateHistoryCount();
        updateContinueBadge();
        updateProgress();

        // رویدادهای اتصال
        window.addEventListener('online', function() {
            updateConnectionStatus();
            showToast('🟢 به اینترنت متصل شدید!', '🌐', 'success');
            syncPendingData();
        });

        window.addEventListener('offline', function() {
            updateConnectionStatus();
            showToast('🔴 آفلاین شدید! داده‌ها ذخیره می‌شوند.', '📱', 'warning');
        });
    }

    // ===== فقط در صفحه پرسشنامه (questionnaire.html) =====
    if (document.getElementById('qGroup1')) {
        console.log('📍 صفحه پرسشنامه');

        if (typeof window.buildQuestions === 'function') {
            console.log('✅ توابع پرسشنامه در دسترس هستند!');
            window.buildQuestions();
            setTimeout(window.loadSavedAnswers, 100);
        } else {
            console.error('❌ توابع پرسشنامه در دسترس نیستند!');
            setTimeout(function() {
                if (typeof window.buildQuestions === 'function') {
                    console.log('✅ توابع پرسشنامه در تلاش مجدد در دسترس هستند!');
                    window.buildQuestions();
                    setTimeout(window.loadSavedAnswers, 100);
                }
            }, 500);
        }

        if (typeof window.loadAllAudioFiles === 'function') {
            window.loadAllAudioFiles();
        }
        if (typeof window.updateProgress === 'function') {
            window.updateProgress();
        }
    }

    console.log('✅ اپلیکیشن آماده است!');
});


// ============================================================
// همگام‌سازی داده‌های آفلاین
// ============================================================

function syncPendingData() {
    getAllAnswers().then(function(answers) {
        if (answers && answers.length > 0) {
            showToast('🔄 در حال همگام‌سازی ' + answers.length + ' داده...', '🔄', 'info');
            answers.forEach(function(answer) {
                var formData = new FormData();
                formData.append('mc_answers[]', answer.mcq || []);
                formData.append('text_answers[]', answer.open || []);
                fetch('/api/predict', {
                    method: 'POST',
                    body: formData
                }).then(function(response) {
                    return response.json();
                }).then(function(result) {
                    if (!result.error) {
                        saveDailyMood(result.prediction);
                        saveHistory({
                            date: new Date().toISOString().split('T')[0],
                            prediction: result.prediction,
                            score: result.score,
                            label: ['سالم', 'خفیف', 'متوسط', 'شدید'][result.prediction]
                        });
                    }
                });
            });
            deleteAllAnswers();
        }
    });

    var pendingResult = localStorage.getItem('pendingResult');
    if (pendingResult) {
        try {
            var result = JSON.parse(pendingResult);
            showToast('📊 نتیجه تحلیل شما آماده است!', '📊', 'success');
            goToPage('pageResult');
            showResult(result);
            localStorage.removeItem('pendingResult');
        } catch (e) {
            localStorage.removeItem('pendingResult');
        }
    }
}


// ============================================================
// تاریخچه
// ============================================================

function loadHistory() {
    var container = document.getElementById('historyContainer');
    if (!container) return;

    fetch('/api/history')
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            if (data.error) {
                container.innerHTML = '<div class="history-empty">📭 خطا در دریافت تاریخچه</div>';
                return;
            }

            if (data.length === 0) {
                container.innerHTML = '<div class="history-empty">📭 هیچ داده‌ای ثبت نشده</div>';
                return;
            }

            var html = '<div class="history-list">';
            data.forEach(function(item) {
                var persianDate = new Date(item.date).toLocaleDateString('fa-IR');
                var emojis = ['😊', '🙂', '😐', '😢'];
                var emoji = emojis[item.prediction] || '❓';
                var labels = ['سالم', 'خفیف', 'متوسط', 'شدید'];
                var label = labels[item.prediction] || 'نامشخص';
                var score = item.final_score || item.score || 0;

                html += '<div class="history-item">';
                html += '<span class="history-date">' + persianDate + '</span>';
                html += '<span class="history-mood">' + emoji + ' ' + label + '</span>';
                html += '<span class="history-score">' + Math.round(score) + '%</span>';
                html += '</div>';
            });
            html += '</div>';

            // ===== آمار =====
            var stats = { total: data.length, healthy: 0, mild: 0, moderate: 0, severe: 0 };
            data.forEach(function(item) {
                var pred = item.prediction;
                if (pred === 0) stats.healthy++;
                else if (pred === 1) stats.mild++;
                else if (pred === 2) stats.moderate++;
                else if (pred === 3) stats.severe++;
            });

            html += '<div style="margin-top:16px;padding:12px;background:#f8fafc;border-radius:12px;display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;text-align:center;">';
            html += '<div><span style="font-size:20px;">😊</span><br><span style="font-weight:700;color:#22c55e;">' + stats.healthy + '</span></div>';
            html += '<div><span style="font-size:20px;">🙂</span><br><span style="font-weight:700;color:#f59e0b;">' + stats.mild + '</span></div>';
            html += '<div><span style="font-size:20px;">😐</span><br><span style="font-weight:700;color:#f97316;">' + stats.moderate + '</span></div>';
            html += '<div><span style="font-size:20px;">😢</span><br><span style="font-weight:700;color:#ef4444;">' + stats.severe + '</span></div>';
            html += '</div>';

            container.innerHTML = html;
        })
        .catch(function(error) {
            console.error('❌ خطا در دریافت تاریخچه:', error);
            container.innerHTML = '<div class="history-empty">📭 خطا در دریافت تاریخچه</div>';
        });
}

function showHistory() {
    goToPage('pageHistory');
    loadHistory();
}

function updateHistoryCount() {
    var historyData = loadHistoryFromStorage();
    var moods = loadDailyMoods();
    var count = historyData.length + Object.keys(moods).length;
    var countEl = document.getElementById('historyCount');
    if (countEl) countEl.textContent = count + ' ثبت';
    var badge = document.getElementById('historyBadge');
    if (badge) {
        if (count > 0) {
            badge.style.display = 'inline';
            badge.textContent = count;
        } else {
            badge.style.display = 'none';
        }
    }
}

function clearHistory() {
    if (confirm('⚠️ آیا مطمئنی می‌خواهی تمام تاریخچه را پاک کنی؟')) {
        localStorage.removeItem('history');
        showToast('🗑️ تاریخچه پاک شد', '✅', 'warning');
        loadHistory();
        updateMoodChart();
        updateStreakAndLevel();
        updateHistoryCount();
    }
}


// ============================================================
// پیگیری روزانه
// ============================================================

function dailyCheckIn() {
    if (localStorage.getItem('username') === 'مهمان') {
        alert('⚠️ برای استفاده از پیگیری روزانه، لطفاً ثبت‌نام کنید.');
        return;
    }

    fetch('/api/daily-status')
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            var dates = Object.keys(data).sort().reverse();
            var statuses = { mood: null, energy: null, sleep: null };

            if (dates.length > 0) {
                var latest = data[dates[0]];
                statuses = latest;
            }

            var persianDate = getPersianDate();
            var msg = '📅 پیگیری روزانه - ' + persianDate + '\n\n';
            msg += 'خلق: ' + (statuses.mood ? ({ good: '😊 خوب', neutral: '😐 متوسط', bad: '😢 بد' })[statuses.mood] : 'ثبت نشده') + '\n';
            msg += 'انرژی: ' + (statuses.energy ? ({ high: '⚡⚡⚡ زیاد', medium: '⚡⚡ متوسط', low: '⚡ کم' })[statuses.energy] : 'ثبت نشده') + '\n';
            msg += 'خواب: ' + (statuses.sleep ? ({ great: '😴😴😴 عالی', good: '😴😴 خوب', bad: '😴 بد' })[statuses.sleep] : 'ثبت نشده');

            showToast('📋 خلاصه وضعیت امروز نمایش داده شد', '📅', 'info');
            alert(msg);
        })
        .catch(function(error) {
            console.error('❌ خطا در دریافت وضعیت:', error);
            alert('⚠️ خطا در دریافت وضعیت روزانه');
        });
}


// ============================================================
// خروجی گرفتن از داده‌ها
// ============================================================

function exportData() {
    var data = exportAllData();
    var blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = 'aramesh_data_' + new Date().toISOString().split('T')[0] + '.json';
    a.click();
    URL.revokeObjectURL(url);
    showToast('📤 داده‌ها با موفقیت خروجی گرفته شد', '✅', 'success');
}


// ============================================================
// اشتراک‌گذاری نتیجه
// ============================================================

function shareResult() {
    var resultStatusEl = document.getElementById('resultStatus');
    var resultText = resultStatusEl ? resultStatusEl.textContent : 'نامشخص';
    var scoreEl = document.getElementById('resultScore');
    var scoreText = scoreEl ? scoreEl.textContent : '0%';

    var text = '🧠 نتیجه تحلیل سلامت روان من:\n\n' +
        'وضعیت: ' + resultText + '\n' +
        'امتیاز: ' + scoreText + '\n\n' +
        '#همراه_آرامش #سلامت_روان';

    if (navigator.share) {
        navigator.share({
            title: 'نتیجه تحلیل سلامت روان',
            text: text,
            url: window.location.href
        }).catch(function(err) {
            if (err.name !== 'AbortError') {
                copyToClipboard(text);
            }
        });
    } else {
        copyToClipboard(text);
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('📋 متن کپی شد!', '✅', 'success');
    }).catch(function() {
        var textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        showToast('📋 متن کپی شد!', '✅', 'success');
    });
}


// ============================================================
// پاک کردن داده‌ها و رفتن به پرسشنامه
// ============================================================

function clearOldDataAndGo() {
    localStorage.removeItem('mcq_answers');
    localStorage.removeItem('open_answers');
    localStorage.removeItem('questionnaire_progress');
    window.location.href = '/questionnaire';
}

// ============================================================
// بارگذاری کاربر و آواتار
// ============================================================
function loadUser() {
    var username = localStorage.getItem('username');
    var displayName = localStorage.getItem('displayName');
    var greeting = document.getElementById('userGreeting');

    if (username && username !== 'مهمان') {
        if (greeting) greeting.innerHTML = 'سلام، ' + (displayName || username) + '! 👋';
    } else {
        if (greeting) greeting.innerHTML = 'سلام، مهمان! 👋';
    }

    // 🆕 گرفتن آواتار از سرور
    fetch('/api/profile')
        .then(res => res.json())
        .then(data => {
            if (data.avatar_url) {
                var mainAvatar = document.getElementById('avatarContainer');
                if (mainAvatar) {
                    mainAvatar.innerHTML = `<img src="${data.avatar_url}" style="width:100%; height:100%; border-radius:50%; object-fit:cover;">`;
                }

                var sidebarAvatar = document.getElementById('sidebarAvatar');
                if (sidebarAvatar) {
                    sidebarAvatar.innerHTML = `<img src="${data.avatar_url}" style="width:100%; height:100%; border-radius:50%; object-fit:cover;">`;
                }
            }
        })
        .catch(err => console.log('⚠️ خطا در دریافت آواتار:', err));
}

// ============================================================
// خروج از حساب
// ============================================================
function logoutUser() {
    if (!confirm('آیا می‌خوای از حسابت خارج شی؟')) return;

    // ===== پاک کردن IndexedDB =====
    try {
        indexedDB.deleteDatabase('ArameshDB');
        console.log('✅ IndexedDB پاک شد');
    } catch (e) {
        console.error('❌ خطا در پاک کردن IndexedDB:', e);
    }

    fetch('/api/logout', { method: 'POST' })
        .then(res => res.json())
        .then(() => {
            // ===== پاک کردن localStorage =====
            localStorage.removeItem('username');
            localStorage.removeItem('displayName');
            localStorage.removeItem('isGuest');
            localStorage.removeItem('userAvatar');
            localStorage.removeItem('mcq_answers');
            localStorage.removeItem('open_answers');
            localStorage.removeItem('questionnaire_progress');

            window.location.href = '/';
        })
        .catch(() => {
            localStorage.removeItem('username');
            localStorage.removeItem('displayName');
            localStorage.removeItem('isGuest');
            localStorage.removeItem('userAvatar');
            localStorage.removeItem('mcq_answers');
            localStorage.removeItem('open_answers');
            localStorage.removeItem('questionnaire_progress');

            window.location.href = '/';
        });
}


// ============================================================
// صادر کردن توابع
// ============================================================
window.logoutUser = logoutUser;
window.syncPendingData = syncPendingData;
window.showHistory = showHistory;
window.loadHistory = loadHistory;
window.clearHistory = clearHistory;
window.dailyCheckIn = dailyCheckIn;
window.exportData = exportData;
window.shareResult = shareResult;
window.copyToClipboard = copyToClipboard;
window.clearOldDataAndGo = clearOldDataAndGo;
