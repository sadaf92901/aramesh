// ============================================================
// برنامه درمانی هفتگی
// ============================================================

let currentPlan = null;

document.addEventListener('DOMContentLoaded', function() {
    loadWeeklyPlan();
});

function loadWeeklyPlan() {
    fetch('/api/weekly-plan')
        .then(res => res.json())
        .then(data => {
            if (data.plan) {
                currentPlan = data.plan;
                renderPlan(currentPlan);
            } else {
                showEmptyState();
            }
        })
        .catch(err => {
            console.error('❌ خطا:', err);
            showEmptyState();
        });
}

function showEmptyState() {
    const container = document.getElementById('daysContainer');
    container.innerHTML = `
        <div class="empty-state">
            <span class="empty-icon">📋</span>
            <h3>هنوز برنامه‌ای نداری!</h3>
            <p>برای دریافت برنامه هفتگی، اول تشخیص روانشناسی بده.</p>
            <button class="btn-start" onclick="generatePlan()">🧠 ساخت برنامه</button>
        </div>
    `;
}

function generatePlan() {
    fetch('/api/weekly-plan/generate', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                currentPlan = data.plan;
                renderPlan(currentPlan);
                showToast('✅ برنامه هفتگی ساخته شد!', '📅', 'success');
            } else {
                showToast('❌ ' + (data.error || 'خطا'), '❌', 'error');
            }
        })
        .catch(err => {
            console.error('❌ خطا:', err);
            showToast('❌ خطا در ساخت برنامه', '❌', 'error');
        });
}

function renderPlan(plan) {
    const container = document.getElementById('daysContainer');
    const planData = plan.plan_data;

    if (!planData || !planData.days) {
        showEmptyState();
        return;
    }

    const today = new Date().getDay();
    const todayIndex = (today + 1) % 7;

    let totalActivities = 0;
    let doneActivities = 0;

    planData.days.forEach((day, i) => {
        day.activities.forEach(a => {
            totalActivities++;
            if (a.done) doneActivities++;
        });
    });

    const percent = totalActivities > 0 ? Math.round((doneActivities / totalActivities) * 100) : 0;

    document.getElementById('weeklyPercent').textContent = percent + '%';
    document.getElementById('weeklyBar').style.width = percent + '%';

    let completedDays = 0;
    planData.days.forEach(day => {
        if (day.activities.every(a => a.done)) completedDays++;
    });

    document.getElementById('completedDays').textContent = completedDays;
    document.getElementById('remainingDays').textContent = 7 - completedDays;

    let html = '';
    planData.days.forEach((day, dayIndex) => {
        const allDone = day.activities.every(a => a.done);
        const isToday = dayIndex === todayIndex;
        const isFuture = dayIndex > todayIndex;

        let cardClass = '';
        let statusText = '';
        let statusClass = '';

        if (allDone) {
            cardClass = 'completed';
            statusText = '✅ انجام شد';
            statusClass = 'completed';
        } else if (isToday) {
            cardClass = 'today';
            statusText = '🔵 امروز';
            statusClass = 'today';
        } else if (isFuture) {
            cardClass = 'future';
            statusText = '⏳ در انتظار';
            statusClass = 'future';
        }

        html += `
            <div class="day-card ${cardClass}">
                <div class="day-header" onclick="toggleDay(${dayIndex})">
                    <span class="day-name">${day.day}</span>
                    <span class="day-status ${statusClass}">${statusText}</span>
                </div>
                <div class="day-body ${isToday ? 'open' : ''}" id="dayBody${dayIndex}">
        `;

        day.activities.forEach((activity, actIndex) => {
            const checkClass = activity.done ? 'checked' : (isFuture ? 'locked' : '');
            const itemClass = activity.done ? 'done' : '';

            html += `
                <div class="activity-item ${itemClass}">
                    <div class="activity-check ${checkClass}" onclick="toggleActivity(${dayIndex}, ${actIndex})">
                        ${activity.done ? '✓' : (isFuture ? '🔒' : '')}
                    </div>
                    <span class="activity-icon">${activity.icon}</span>
                    <div class="activity-info">
                        <div class="activity-title">${activity.title}</div>
                        <div class="activity-duration">${activity.duration}</div>
                    </div>
                </div>
            `;
        });

        html += `
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

function toggleDay(dayIndex) {
    const body = document.getElementById('dayBody' + dayIndex);
    if (body) {
        body.classList.toggle('open');
    }
}

function toggleActivity(dayIndex, activityIndex) {
    fetch('/api/weekly-plan/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ day: dayIndex, activity: activityIndex })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            currentPlan = data.plan;
            renderPlan(currentPlan);
        }
    })
    .catch(err => console.error('❌ خطا:', err));
}
