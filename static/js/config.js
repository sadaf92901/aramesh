// ============================================================
// تنظیمات و مقادیر ثابت پروژه
// ============================================================

export const CONFIG = {
    APP_NAME: 'همراه آرامش',
    APP_VERSION: '2.0.0',
    DB_NAME: 'ArameshDB',
    DB_VERSION: 2,
    MAX_AUDIO_SIZE: 5 * 1024 * 1024, // 5MB
    MAX_TEXT_LENGTH: 1000,
    BREATHING_DURATION: 30,
    HISTORY_LIMIT: 100
};

export const KEYS = {
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

export const STATUS_MAP = {
    mood: {
        good: { label: 'خوب', icon: '😊' },
        neutral: { label: 'معمولی', icon: '😐' },
        bad: { label: 'بد', icon: '😢' }
    },
    energy: {
        high: { label: 'زیاد', icon: '⚡⚡⚡' },
        medium: { label: 'متوسط', icon: '⚡⚡' },
        low: { label: 'کم', icon: '⚡' }
    },
    sleep: {
        great: { label: 'عالی', icon: '😴😴😴' },
        good: { label: 'خوب', icon: '😴😴' },
        bad: { label: 'بد', icon: '😴' }
    }
};

export const LABELS = {
    healthy: ['سالم', 'خفیف', 'متوسط', 'شدید'],
    classes: ['healthy', 'mild', 'moderate', 'severe'],
    emojis: ['😊', '🙂', '😐', '😢']
};

export const QUOTES = [
    '"آرامش را در درون خودت پیدا کن، نه در دنیای بیرون."',
    '"تنها راهی که می‌تونی از پسش بربیای اینه که از توش عبور کنی."',
    '"هر روز یک شروع تازه است. نگذار گذشته‌ات امروز تو را تعیین کند."',
    '"قدرت تو در افکارت نهفته است. افکارت را تغییر بده تا زندگیت تغییر کند."',
    '"مهربانی با خودت، اولین قدم برای مهربانی با دیگران است."',
    '"گاهی بهترین کاری که می‌تونی انجام بدی، نفس کشیدن عمیق است."'
];