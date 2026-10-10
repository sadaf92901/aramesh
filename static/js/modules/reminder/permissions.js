// ============================================================
// مدیریت مجوز اعلان
// ============================================================

export function requestNotificationPermission() {
    if (!('Notification' in window)) {
        console.log('❌ مرورگر از Notification پشتیبانی نمیکند');
        return Promise.resolve(false);
    }

    if (Notification.permission === 'granted') {
        console.log('✅ مجوز اعلان قبلاً داده شده');
        return Promise.resolve(true);
    }

    if (Notification.permission === 'denied') {
        console.log('❌ مجوز اعلان رد شده');
        return Promise.resolve(false);
    }

    return Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
            console.log('✅ مجوز اعلان داده شد');
            return true;
        } else {
            console.log('❌ مجوز اعلان داده نشد');
            return false;
        }
    });
}

export function getNotificationPermission() {
    if (!('Notification' in window)) return 'unsupported';
    return Notification.permission;
}