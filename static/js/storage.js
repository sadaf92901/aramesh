// ============================================================
// مدیریت ذخیره‌سازی (localStorage و IndexedDB)
// ============================================================

// ===== کلیدهای ذخیره‌سازی =====
const KEYS = {
    USER_AVATAR: 'userAvatar',
    DAILY_STATUS: 'dailyStatus',
    DAILY_MOODS: 'dailyMoods',
    LAST_DIAGNOSIS: 'lastDiagnosis',
    DAILY_QUOTE: 'dailyQuote',
    DAILY_QUOTE_DATE: 'dailyQuoteDate',
    THEME: 'theme',
    MCQ_ANSWERS: 'mcq_answers',
    OPEN_ANSWERS: 'open_answers',
    PROGRESS: 'questionnaire_progress',
    HISTORY: 'history',
    PENDING_RESULT: 'pendingResult'
};

// ===== LocalStorage =====

function saveData(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
        return true;
    } catch (e) {
        console.error('Save error:', e);
        return false;
    }
}

function loadData(key, defaultValue = null) {
    try {
        const data = localStorage.getItem(key);
        if (data === null || data === undefined) return defaultValue;
        return JSON.parse(data);
    } catch (e) {
        console.warn('Load error for key:', key, e);
        localStorage.removeItem(key);
        return defaultValue;
    }
}

function removeData(key) {
    localStorage.removeItem(key);
}

function clearAllData() {
    localStorage.clear();
}

// ===== IndexedDB =====

let dbInstance = null;

function openDatabase() {
    return new Promise((resolve, reject) => {
        if (dbInstance) {
            resolve(dbInstance);
            return;
        }

        const request = indexedDB.open('ArameshDB', 2);

        request.onupgradeneeded = (event) => {
            const db = event.target.result;

            if (!db.objectStoreNames.contains('audioFiles')) {
                const store = db.createObjectStore('audioFiles', { keyPath: 'id' });
                store.createIndex('index', 'index', { unique: false });
            }

            if (!db.objectStoreNames.contains('answers')) {
                const store = db.createObjectStore('answers', { keyPath: 'id' });
                store.createIndex('timestamp', 'timestamp', { unique: false });
            }
        };

        request.onsuccess = (event) => {
            dbInstance = event.target.result;
            resolve(dbInstance);
        };

        request.onerror = (event) => {
            reject(event.target.error);
        };
    });
}

function saveAudioFile(index, blob) {
    return new Promise((resolve, reject) => {
        openDatabase().then(db => {
            const transaction = db.transaction(['audioFiles'], 'readwrite');
            const store = transaction.objectStore('audioFiles');

            const request = store.put({
                id: 'audio_' + index,
                index: index,
                blob: blob,
                timestamp: new Date().toISOString()
            });
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        }).catch(reject);
    });
}

function loadAudioFile(index) {
    return new Promise((resolve) => {
        openDatabase().then(db => {
            const transaction = db.transaction(['audioFiles'], 'readonly');
            const store = transaction.objectStore('audioFiles');
            const request = store.get('audio_' + index);
            request.onsuccess = () => resolve(request.result?.blob || null);
            request.onerror = () => resolve(null);
        }).catch(() => resolve(null));
    });
}

function saveFullAnswer(data) {
    return new Promise((resolve, reject) => {
        openDatabase().then(db => {
            const transaction = db.transaction(['answers'], 'readwrite');
            const store = transaction.objectStore('answers');

            const answerData = {
                id: 'answer_' + Date.now(),
                ...data,
                timestamp: new Date().toISOString()
            };

            const request = store.put(answerData);
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        }).catch(reject);
    });
}

function getAllAnswers() {
    return new Promise((resolve, reject) => {
        openDatabase().then(db => {
            const transaction = db.transaction(['answers'], 'readonly');
            const store = transaction.objectStore('answers');
            const request = store.getAll();
            request.onsuccess = () => resolve(request.result || []);
            request.onerror = () => reject(request.error);
        }).catch(reject);
    });
}

function deleteAllAnswers() {
    return new Promise((resolve, reject) => {
        openDatabase().then(db => {
            const transaction = db.transaction(['answers'], 'readwrite');
            const store = transaction.objectStore('answers');
            const request = store.clear();
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        }).catch(reject);
    });
}

// ===== پاسخ‌های پرسشنامه =====

function saveMcqAnswers(answers) {
    return saveData(KEYS.MCQ_ANSWERS, answers);
}

function loadMcqAnswers() {
    return loadData(KEYS.MCQ_ANSWERS, {});
}

function saveOpenAnswers(answers) {
    return saveData(KEYS.OPEN_ANSWERS, answers);
}

function loadOpenAnswers() {
    return loadData(KEYS.OPEN_ANSWERS, {});
}

function saveProgress(progress) {
    return saveData(KEYS.PROGRESS, progress);
}

function loadProgress() {
    return loadData(KEYS.PROGRESS, null);
}

// ===== وضعیت‌ها =====
function saveDailyStatus(status) {
    console.log('📤 ذخیره وضعیت:', status);  // ← دیباگ

    localStorage.setItem('dailyStatus', JSON.stringify(status));

    fetch('/api/daily-status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(status)
    })
    .then(function(response) {
        console.log('📥 پاسخ سرور:', response.status);
        return response.json();
    })
    .then(function(data) {
        console.log('📦 داده دریافتی:', data);
        if (data.success) {
            console.log('✅ وضعیت در دیتابیس ذخیره شد');
        } else {
            console.error('❌ خطا:', data);
        }
    })
    .catch(function(error) {
        console.error('❌ خطا در ارتباط:', error);
    });
}
function loadDailyStatus() {
    try {
        var data = localStorage.getItem('dailyStatus');
        if (data) {
            return JSON.parse(data);
        }
    } catch (e) {
        console.error('❌ خطا در خواندن localStorage:', e);
    }

    // ===== اگر در localStorage نبود، از سرور بخوان =====
    fetch('/api/daily-status')
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            if (Object.keys(data).length > 0) {
                var dates = Object.keys(data).sort().reverse();
                var latest = data[dates[0]];
                localStorage.setItem('dailyStatus', JSON.stringify(latest));
                return latest;
            }
            return { mood: null, energy: null, sleep: null };
        })
        .catch(function(error) {
            console.error('❌ خطا در دریافت وضعیت از سرور:', error);
            return { mood: null, energy: null, sleep: null };
        });

    return { mood: null, energy: null, sleep: null };
}
function saveDailyMood(prediction) {
    const today = new Date().toISOString().split('T')[0];
    const moods = loadData(KEYS.DAILY_MOODS, {});
    moods[today] = prediction;
    return saveData(KEYS.DAILY_MOODS, moods);
}

function loadDailyMoods() {
    return loadData(KEYS.DAILY_MOODS, {});
}

// ===== تاریخچه =====

function saveHistory(entry) {
    const history = loadData(KEYS.HISTORY, []);
    history.push({
        ...entry,
        timestamp: new Date().toISOString()
    });

    if (history.length > 100) {
        history.splice(0, history.length - 100);
    }

    return saveData(KEYS.HISTORY, history);
}

function loadHistory() {
    return loadData(KEYS.HISTORY, []);
}

function clearHistory() {
    return removeData(KEYS.HISTORY);
}

// ===== خروجی گرفتن =====

function exportAllData() {
    return {
        dailyStatus: loadDailyStatus(),
        dailyMoods: loadDailyMoods(),
        history: loadHistory(),
        lastDiagnosis: loadData(KEYS.LAST_DIAGNOSIS, ''),
        settings: {
            theme: loadData(KEYS.THEME, 'light')
        },
        exportDate: new Date().toISOString(),
        version: '1.0'
    };
}

// ===== صادر کردن به صورت global =====
window.KEYS = KEYS;
window.saveData = saveData;
window.loadData = loadData;
window.removeData = removeData;
window.clearAllData = clearAllData;
window.saveAudioFile = saveAudioFile;
window.loadAudioFile = loadAudioFile;
window.saveFullAnswer = saveFullAnswer;
window.getAllAnswers = getAllAnswers;
window.deleteAllAnswers = deleteAllAnswers;
window.saveMcqAnswers = saveMcqAnswers;
window.loadMcqAnswers = loadMcqAnswers;
window.saveOpenAnswers = saveOpenAnswers;
window.loadOpenAnswers = loadOpenAnswers;
window.saveProgress = saveProgress;
window.loadProgress = loadProgress;
window.saveDailyStatus = saveDailyStatus;
window.loadDailyStatus = loadDailyStatus;
window.saveDailyMood = saveDailyMood;
window.loadDailyMoods = loadDailyMoods;
window.saveHistory = saveHistory;
window.loadHistory = loadHistory;
window.clearHistory = clearHistory;
window.exportAllData = exportAllData;
function loadHistoryFromStorage() {
    return loadData(KEYS.HISTORY, []);
}
window.loadHistoryFromStorage = loadHistoryFromStorage;