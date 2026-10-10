// ============================================================
// تنظیمات یادآوری
// ============================================================

const STORAGE_KEY = 'aramesh_reminder_settings';

const defaultSettings = {
    enabled: true,
    journalReminder: true,
    journalTime: '21:00',
    breathingReminder: true,
    breathingMorning: '08:00',
    breathingEvening: '18:00'
};

export function loadSettings() {
    try {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved) {
            const parsed = JSON.parse(saved);
            return { ...defaultSettings, ...parsed };
        }
    } catch (e) {
        console.error('❌ خطا در خواندن تنظیمات:', e);
    }
    return { ...defaultSettings };
}

export function saveSettings(settings) {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
        return true;
    } catch (e) {
        console.error('❌ خطا در ذخیره تنظیمات:', e);
        return false;
    }
}

export function toggleReminders(enabled) {
    const settings = loadSettings();
    settings.enabled = enabled;
    saveSettings(settings);
    return settings;
}