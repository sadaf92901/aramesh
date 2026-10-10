// ============================================================
// زمان‌بندی یادآوری‌ها
// ============================================================

let reminderTimeouts = [];
let reminderIntervals = [];

export function scheduleReminders() {
    clearAllReminders();

    // ===== ۱. یادآوری روزنگار (ساعت ۲۱:۰۰) =====
    scheduleDailyReminder(21, 0, '📝 وقت نوشتن یاداشت!', 'روزت رو توی روزنگار آرامش ثبت کن ✍️', '/journal');

    // ===== ۲. یادآوری تمرین تنفس صبح (ساعت ۰۸:۰۰) =====
    scheduleDailyReminder(8, 0, '🧘 تمرین تنفس صبحگاهی!', 'با یه تمرین تنفس روزت رو شروع کن 🌊', null, 'breathing');

    // ===== ۳. یادآوری تمرین تنفس عصر (ساعت ۱۸:۰۰) =====
    scheduleDailyReminder(18, 0, '🧘 تمرین تنفس عصر!', 'یه تمرین تنفس آرامش‌بخش انجام بده 🌊', null, 'breathing');
}

function scheduleDailyReminder(hours, minutes, title, body, link, action) {
    const now = new Date();
    const target = new Date();
    target.setHours(hours, minutes, 0, 0);

    if (now > target) target.setDate(target.getDate() + 1);
    const delay = target - now;

    const timeoutId = setTimeout(() => {
        sendNotification(title, body, link, action);

        // تکرار هر ۲۴ ساعت
        const intervalId = setInterval(() => {
            sendNotification(title, body, link, action);
        }, 24 * 60 * 60 * 1000);

        reminderIntervals.push(intervalId);
    }, delay);

    reminderTimeouts.push(timeoutId);
    console.log(⏰ یادآوری "${title}" برای ساعت ${hours}:${minutes} تنظیم شد);
}

function sendNotification(title, body, link, action) {
    if (!('Notification' in window) || Notification.permission !== 'granted') return;

    const notification = new Notification(title, {
        body: body,
        icon: '/static/images/logo.png',
        vibrate: [200, 100, 200],
        silent: false
    });

    notification.onclick = function() {
        window.focus();
        if (link) {
            window.location.href = link;
        } else if (action === 'breathing') {
            // پیدا کردن دکمه تمرین تنفس
            const breathBtn = document.getElementById('breathStartBtn');
            if (breathBtn) breathBtn.click();
        }
        notification.close();
    };

    setTimeout(() => notification.close(), 30000);
}

function clearAllReminders() {
    reminderTimeouts.forEach(id => clearTimeout(id));
    reminderIntervals.forEach(id => clearInterval(id));
    reminderTimeouts = [];
    reminderIntervals = [];
}

export function getReminderStatus() {
    return {
        enabled: reminderTimeouts.length > 0,
        count: reminderTimeouts.length
    };
}