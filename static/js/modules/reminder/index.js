// ============================================================
// ماژول یادآوری - ورودی اصلی
// ============================================================

import { requestNotificationPermission } from './permissions.js';
import { scheduleReminders, getReminderStatus } from './scheduler.js';
import { loadSettings, saveSettings, toggleReminders } from './settings.js';

export function initReminders() {
    const settings = loadSettings();

    if (!settings.enabled) {
        console.log('⏰ یادآوری‌ها غیرفعال هستند');
        return;
    }

    requestNotificationPermission().then(granted => {
        if (granted) {
            scheduleReminders();
        }
    });
}

export function restartReminders() {
    const settings = loadSettings();
    if (settings.enabled) {
        scheduleReminders();
    }
}

export function getStatus() {
    return {
        settings: loadSettings(),
        reminders: getReminderStatus()
    };
}

// صادر کردن به ویندوز برای استفاده در HTML
window.reminderModule = {
    init: initReminders,
    restart: restartReminders,
    getStatus: getStatus,
    loadSettings: loadSettings,
    saveSettings: saveSettings,
    toggleReminders: toggleReminders
};

console.log('✅ ماژول یادآوری بارگذاری شد');