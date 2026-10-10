// ============================================================
// صفحه‌ی پروفایل
// ============================================================

let currentUser = null;

document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ صفحه پروفایل بارگذاری شد');
    loadProfile();
    loadStats();
    updateSettingsDisplay();
});


// ============================================================
// بارگذاری
// ============================================================

function loadProfile() {
    fetch('/api/profile')
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                showToast('❌ ' + data.error, '❌', 'error');
                return;
            }
            currentUser = data;

            document.getElementById('displayNameField').textContent = data.display_name || data.username;
            document.getElementById('usernameField').textContent = data.username;
            document.getElementById('emailField').textContent = data.email;
            document.getElementById('joinedField').textContent = formatDate(data.created_at);

            // ===== آواتار =====
            if (data.avatar_url) {
                const avatarEl = document.getElementById('avatarDisplay');
                avatarEl.style.backgroundImage = `url('${data.avatar_url}')`;
                avatarEl.textContent = '';
            }
        })
        .catch(err => {
            console.error('❌ خطا:', err);
            showToast('❌ خطا در بارگذاری پروفایل', '❌', 'error');
        });
}

function loadStats() {
    fetch('/api/profile/stats')
        .then(res => res.json())
        .then(data => {
            if (data.error) return;
            document.getElementById('statDiagnoses').textContent = data.total_diagnoses || 0;
            document.getElementById('statNotes').textContent = data.total_notes || 0;
            document.getElementById('statBreaths').textContent = data.total_breaths || 0;
            document.getElementById('statMeditations').textContent = data.total_meditations || 0;
            document.getElementById('statStreak').textContent = data.streak || 0;
        })
        .catch(err => console.error('❌ خطا:', err));
}

function updateSettingsDisplay() {
    // ===== تم =====
    const theme = localStorage.getItem('theme') || 'light';
    const themeEl = document.getElementById('themeValue');
    if (themeEl) {
        themeEl.textContent = theme === 'dark' ? 'تاریک' : 'روشن';
    }

    // ===== یادآوری =====
    const reminderSettings = JSON.parse(localStorage.getItem('aramesh_reminder_settings') || '{}');
    const enabled = reminderSettings.enabled !== false;
    const reminderEl = document.getElementById('reminderValue');
    if (reminderEl) {
        reminderEl.textContent = enabled ? 'فعال' : 'غیرفعال';
    }

    // ===== ✨ صدا (جدید) =====
    const soundEl = document.getElementById('soundValue');
    if (soundEl) {
        soundEl.textContent = isSoundEnabled() ? 'روشن' : 'خاموش';
    }
}


// ============================================================
// آواتار
// ============================================================

function uploadAvatar(event) {
    const file = event.target.files[0];
    if (!file) return;

    if (file.size > 2 * 1024 * 1024) {
        showToast('⚠️ حجم فایل باید کمتر از ۲ مگابایت باشه', '⚠️', 'warning');
        return;
    }

    const formData = new FormData();
    formData.append('avatar', file);

    fetch('/api/profile/avatar', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            showToast('❌ ' + data.error, '❌', 'error');
            return;
        }

        const avatarEl = document.getElementById('avatarDisplay');
        avatarEl.style.backgroundImage = `url('${data.avatar_url}')`;
        avatarEl.textContent = '';

        showToast('✅ آواتار به‌روزرسانی شد', '📷', 'success');
    })
    .catch(err => {
        console.error('❌ خطا:', err);
        showToast('❌ خطا در آپلود', '❌', 'error');
    });
}


// ============================================================
// ویرایش پروفایل
// ============================================================

function openEditModal() {
    if (!currentUser) return;
    document.getElementById('editDisplayName').value = currentUser.display_name || '';
    document.getElementById('editEmail').value = currentUser.email || '';
    document.getElementById('editError').textContent = '';
    document.getElementById('editModal').style.display = 'flex';
}

function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
}

function saveProfile() {
    const displayName = document.getElementById('editDisplayName').value.trim();
    const email = document.getElementById('editEmail').value.trim();
    const errorEl = document.getElementById('editError');

    errorEl.textContent = '';

    if (!displayName || !email) {
        errorEl.textContent = '⚠️ همه‌ی فیلدها را پر کنید';
        return;
    }

    fetch('/api/profile/update', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ display_name: displayName, email })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            errorEl.textContent = '❌ ' + data.error;
            return;
        }

        localStorage.setItem('displayName', data.user.display_name);
        currentUser = data.user;
        loadProfile();
        closeEditModal();
        showToast('✅ اطلاعات به‌روزرسانی شد', '✅', 'success');
    })
    .catch(err => {
        console.error('❌ خطا:', err);
        errorEl.textContent = '❌ خطا در ارتباط با سرور';
    });
}


// ============================================================
// تغییر رمز
// ============================================================

function openPasswordModal() {
    document.getElementById('currentPassword').value = '';
    document.getElementById('newPassword').value = '';
    document.getElementById('confirmPassword').value = '';
    document.getElementById('passwordError').textContent = '';
    document.getElementById('passwordModal').style.display = 'flex';
}

function closePasswordModal() {
    document.getElementById('passwordModal').style.display = 'none';
}

function savePassword() {
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const errorEl = document.getElementById('passwordError');

    errorEl.textContent = '';

    if (!currentPassword || !newPassword || !confirmPassword) {
        errorEl.textContent = '⚠️ همه‌ی فیلدها را پر کنید';
        return;
    }

    if (newPassword !== confirmPassword) {
        errorEl.textContent = '⚠️ رمز جدید و تکرارش یکسان نیستن';
        return;
    }

    if (newPassword.length < 8) {
        errorEl.textContent = '⚠️ رمز جدید باید حداقل ۸ کاراکتر باشه';
        return;
    }

    fetch('/api/profile/change-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            current_password: currentPassword,
            new_password: newPassword
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            errorEl.textContent = '❌ ' + data.error;
            return;
        }

        closePasswordModal();
        showToast('✅ رمز عبور تغییر کرد', '🔒', 'success');
    })
    .catch(err => {
        console.error('❌ خطا:', err);
        errorEl.textContent = '❌ خطا در ارتباط با سرور';
    });
}


// ============================================================
// دانلود داده‌ها
// ============================================================

function downloadData() {
    Promise.all([
        fetch('/api/profile').then(r => r.json()),
        fetch('/api/history/timeline').then(r => r.json()),
        fetch('/api/notes').then(r => r.json())
    ])
    .then(([profile, timeline, notes]) => {
        const data = {
            profile,
            timeline: timeline.items || [],
            notes: notes || [],
            exported_at: new Date().toISOString()
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `aramesh_data_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);

        showToast('📥 داده‌ها دانلود شد', '✅', 'success');
    })
    .catch(err => {
        console.error('❌ خطا:', err);
        showToast('❌ خطا در دانلود', '❌', 'error');
    });
}


// ============================================================
// پاک کردن حساب
// ============================================================

function deleteAccount() {
    const confirm1 = confirm('⚠️ آیا مطمئنی می‌خوای حسابت رو پاک کنی؟\n\nهمه‌ی داده‌ها پاک میشن و قابل برگشت نیستن!');
    if (!confirm1) return;

    const confirm2 = prompt('برای تأیید نهایی، کلمه‌ی «حذف» رو بنویس:');
    if (confirm2 !== 'حذف') {
        showToast('لغو شد', '↩️', 'info');
        return;
    }

    fetch('/api/profile/delete', { method: 'DELETE' })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                localStorage.clear();
                showToast('🗑️ حساب پاک شد', '✅', 'warning');
                setTimeout(() => {
                    window.location.href = '/';
                }, 1500);
            }
        })
        .catch(err => {
            console.error('❌ خطا:', err);
            showToast('❌ خطا در پاک کردن حساب', '❌', 'error');
        });
}


// ============================================================
// تنظیمات
// ============================================================

function toggleThemeFromProfile() {
    if (typeof toggleTheme === 'function') {
        toggleTheme();
    } else {
        document.body.classList.toggle('dark-theme');
        const isDark = document.body.classList.contains('dark-theme');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    }
    updateSettingsDisplay();
}


// ============================================================
// ✨ صدا (جدید)
// ============================================================

function toggleSoundFromProfile() {
    const current = isSoundEnabled();
    setSoundEnabled(!current);

    // ===== به‌روزرسانی UI =====
    updateSettingsDisplay();

    // ===== Toast =====
    if (typeof showToast === 'function') {
        showToast(
            !current ? '🔊 صدا روشن شد' : '🔇 صدا خاموش شد',
            !current ? '🔊' : '🔇',
            'success'
        );
    }
}


// ============================================================
// توابع کمکی
// ============================================================

function formatDate(isoString) {
    if (!isoString) return '-';
    try {
        const d = new Date(isoString);
        return d.toLocaleDateString('fa-IR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    } catch {
        return isoString;
    }
}


// ============================================================
// صادر کردن
// ============================================================

window.uploadAvatar = uploadAvatar;
window.openEditModal = openEditModal;
window.closeEditModal = closeEditModal;
window.saveProfile = saveProfile;
window.openPasswordModal = openPasswordModal;
window.closePasswordModal = closePasswordModal;
window.savePassword = savePassword;
window.downloadData = downloadData;
window.deleteAccount = deleteAccount;
window.toggleThemeFromProfile = toggleThemeFromProfile;
window.toggleSoundFromProfile = toggleSoundFromProfile;
