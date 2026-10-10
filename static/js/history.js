// ============================================================
// صفحه‌ی تاریخچه
// ============================================================

let currentFilter = 'all';
let allHistoryItems = [];
let currentChartRange = 7;
let progressChart = null;

document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ صفحه تاریخچه بارگذاری شد');
    loadStats();
    loadTimeline();
    loadWeeklySummary();
    loadProgressChart();
});

function loadStats() {
    fetch('/api/history/stats')
        .then(res => res.json())
        .then(data => {
            if (data.error) return;
            document.getElementById('statDiagnoses').textContent = data.total_diagnoses || 0;
            document.getElementById('statAvg').textContent = (data.avg_score || 0) + '%';
            document.getElementById('statNotes').textContent = data.total_notes || 0;
            document.getElementById('statBreaths').textContent = data.total_breaths || 0;
        })
        .catch(err => console.error('❌ خطا در آمار:', err));
}

function loadTimeline() {
    const container = document.getElementById('historyTimeline');
    container.innerHTML = '<div class="history-loading">🔄 در حال بارگذاری...</div>';

    fetch('/api/history/timeline')
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                container.innerHTML = '<div class="history-empty">❌ خطا در بارگذاری</div>';
                return;
            }
            allHistoryItems = data.items || [];
            renderTimeline();
        })
        .catch(err => {
            console.error('❌ خطا:', err);
            container.innerHTML = '<div class="history-empty">❌ خطا در ارتباط با سرور</div>';
        });
}

function renderTimeline() {
    const container = document.getElementById('historyTimeline');

    let items = allHistoryItems;
    if (currentFilter !== 'all') {
        items = items.filter(i => i.type === currentFilter);
    }

    if (items.length === 0) {
        container.innerHTML = '<div class="history-empty">📭 هنوز فعالیتی ثبت نشده</div>';
        return;
    }

    const groups = {};
    items.forEach(item => {
        const date = item.date;
        if (!groups[date]) groups[date] = [];
        groups[date].push(item);
    });

    const sortedDates = Object.keys(groups).sort().reverse();

    let html = '';
    sortedDates.forEach(date => {
        const dayItems = groups[date].sort((a, b) =>
            (b.timestamp || '').localeCompare(a.timestamp || '')
        );

        html += '<div class="history-day-group">';
        html += '<div class="day-header">' + formatDate(date) + '</div>';

        dayItems.forEach((item) => {
            html += renderItemRow(item);
        });

        html += '</div>';
    });

    container.innerHTML = html;
}

function renderItemRow(item) {
    const icon = getTypeIcon(item.type);
    const title = getItemTitle(item);
    const time = getItemTime(item);
    const meta = getItemMeta(item);

    const id = item.type + '::' + (item.data.id || Math.random());

    return `
        <div class="history-item-row" onclick="showItemDetail('${item.type}', ${item.data.id || 0})">
            <span class="item-icon">${icon}</span>
            <div class="item-info">
                <div class="item-title">${escapeHtml(title)}</div>
                <div class="item-time">${time}</div>
            </div>
            ${meta ? '<span class="item-meta">' + meta + '</span>' : ''}
        </div>
    `;
}

function getTypeIcon(type) {
    const icons = {
        'diagnosis': '🧠',
        'note': '📝',
        'meditation': '🧘',
        'breathing': '🌬️',
        'weekly_plan': '📋'
    };
    return icons[type] || '📌';
}

function getItemTitle(item) {
    const d = item.data;
    switch (item.type) {
        case 'diagnosis': {
            const labels = ['سالم', 'خفیف', 'متوسط', 'شدید'];
            const emojis = ['😊', '🙂', '😐', '😢'];
            return `${emojis[d.prediction] || '❓'} تشخیص: ${labels[d.prediction] || 'نامشخص'}`;
        }
        case 'note':
            return d.title ? `📝 ${d.title}` : '📝 یاداشت';
        case 'meditation': {
            const types = { 'morning': 'صبحگاهی', 'breathing': 'تنفس عمیق', 'night': 'شبانه' };
            const minutes = Math.round((d.duration || 0) / 60);
            return `🧘 مدیتیشن ${types[d.type] || ''} (${minutes} دقیقه)`;
        }
        case 'breathing':
            return `🌬️ تمرین تنفس (${d.duration || 30} ثانیه)`;
        case 'weekly_plan':
            return `📋 برنامه هفتگی - سطح ${d.level}`;
        default:
            return 'فعالیت';
    }
}

function getItemTime(item) {
    if (item.timestamp && item.timestamp.includes('T')) {
        const d = new Date(item.timestamp);
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        return `⏰ ${hours}:${minutes}`;
    }
    return '';
}

function getItemMeta(item) {
    if (item.type === 'diagnosis') {
        return Math.round(item.data.score || 0) + '%';
    }
    return '';
}

function formatDate(dateStr) {
    try {
        const d = new Date(dateStr);
        const today = new Date();
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);

        const isToday = d.toDateString() === today.toDateString();
        const isYesterday = d.toDateString() === yesterday.toDateString();

        const persian = d.toLocaleDateString('fa-IR');

        if (isToday) return '📅 امروز — ' + persian;
        if (isYesterday) return '📅 دیروز — ' + persian;
        return '📅 ' + persian;
    } catch {
        return dateStr;
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function filterHistory(type) {
    currentFilter = type;
    document.querySelectorAll('.filter-chip').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.type === type);
    });
    renderTimeline();
}

// ============================================================
// مودال
// ============================================================

function showItemDetail(type, id) {
    // پیدا کردن آیتم
    const item = allHistoryItems.find(i => i.type === type && i.data.id === id);
    if (!item) return;

    const modal = document.getElementById('detailModal');
    const content = document.getElementById('detailContent');

    content.innerHTML = renderDetailContent(item);
    modal.style.display = 'flex';
}

function renderDetailContent(item) {
    const icon = getTypeIcon(item.type);
    const d = item.data;

    let body = '';

    if (item.type === 'diagnosis') {
        const labels = ['سالم', 'خفیف', 'متوسط', 'شدید'];
        body = `
            <div style="text-align:center;margin-bottom:16px;">
                <div style="font-size:48px;">${['😊','🙂','😐','😢'][d.prediction] || '❓'}</div>
                <h2 style="margin:8px 0;color:#1e293b;">${labels[d.prediction] || 'نامشخص'}</h2>
                <div style="font-size:32px;font-weight:700;color:#8B5CF6;">${Math.round(d.score)}%</div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:16px 0;">
                <div style="text-align:center;padding:10px;background:#f0fdf4;border-radius:10px;">
                    <div style="font-size:12px;color:#64748b;">🧠 MCQ</div>
                    <div style="font-size:18px;font-weight:700;color:#22c55e;">${Math.round(d.mcq_score || 0)}%</div>
                </div>
                <div style="text-align:center;padding:10px;background:#eff6ff;border-radius:10px;">
                    <div style="font-size:12px;color:#64748b;">🤖 LLM</div>
                    <div style="font-size:18px;font-weight:700;color:#3B82F6;">${Math.round(d.llm_score || 0)}%</div>
                </div>
            </div>
            ${d.treatment ? '<div style="background:#f8fafc;padding:12px;border-radius:10px;border-right:4px solid #8B5CF6;margin-top:12px;"><p style="margin:0;font-size:14px;line-height:1.6;">' + escapeHtml(d.treatment) + '</p></div>' : ''}
        `;
    } else if (item.type === 'note') {
        body = `
            ${d.title ? '<h3 style="margin:0 0 8px 0;">' + escapeHtml(d.title) + '</h3>' : ''}
            <p style="line-height:1.8;white-space:pre-wrap;color:#475569;">${escapeHtml(d.content)}</p>
            ${d.tags && d.tags.length ? '<div style="margin-top:12px;">' + d.tags.map(t => '<span style="display:inline-block;padding:2px 10px;background:#f1f5f9;border-radius:12px;font-size:12px;color:#475569;margin-left:4px;">#' + escapeHtml(t) + '</span>').join('') + '</div>' : ''}
        `;
    } else if (item.type === 'meditation') {
        const minutes = Math.round((d.duration || 0) / 60);
        const types = { 'morning': 'صبحگاهی', 'breathing': 'تنفس عمیق', 'night': 'شبانه' };
        body = `
            <div style="text-align:center;padding:20px;">
                <div style="font-size:48px;">🧘</div>
                <h3 style="margin:12px 0;">مدیتیشن ${types[d.type] || ''}</h3>
                <p style="font-size:24px;font-weight:700;color:#8B5CF6;margin:0;">${minutes} دقیقه</p>
                <p style="font-size:13px;color:#94a3b8;margin-top:8px;">${d.completed ? '✅ تکمیل شده' : '⏸ ناقص'}</p>
            </div>
        `;
    } else if (item.type === 'breathing') {
        body = `
            <div style="text-align:center;padding:20px;">
                <div style="font-size:48px;">🌬️</div>
                <h3 style="margin:12px 0;">تمرین تنفس</h3>
                <p style="font-size:24px;font-weight:700;color:#8B5CF6;margin:0;">${d.duration || 30} ثانیه</p>
            </div>
        `;
    } else if (item.type === 'weekly_plan') {
        body = `
            <div style="text-align:center;padding:20px;">
                <div style="font-size:48px;">📋</div>
                <h3 style="margin:12px 0;">برنامه هفتگی</h3>
                <p style="font-size:14px;color:#64748b;">سطح ${d.level}</p>
                <p style="font-size:13px;color:#94a3b8;">${d.week_start} تا ${d.week_end}</p>
            </div>
        `;
    }

    const titles = {
        'diagnosis': 'تشخیص',
        'note': 'یاداشت',
        'meditation': 'مدیتیشن',
        'breathing': 'تمرین تنفس',
        'weekly_plan': 'برنامه هفتگی'
    };

    return `
        <div class="modal-header">
            <h3>${icon} ${titles[item.type] || 'فعالیت'}</h3>
            <button class="modal-close" onclick="closeDetailModal()">✕</button>
        </div>
        <div>${body}</div>
    `;
}

function closeDetailModal() {
    document.getElementById('detailModal').style.display = 'none';
}
// ============================================================
// گزارش هفتگی
// ============================================================

function loadWeeklySummary() {
    const container = document.getElementById('weeklySummary');
    if (!container) return;

    fetch('/api/history/weekly-summary')
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                document.getElementById('weeklyText').textContent =
                    '❌ خطا در بارگذاری گزارش';
                return;
            }

            renderWeeklySummary(data);
        })
        .catch(err => {
            console.error('❌ خطا:', err);
            document.getElementById('weeklyText').textContent =
                '❌ خطا در ارتباط با سرور';
        });
}
function renderWeeklySummary(data) {
    // ===== بازه‌ی تاریخ =====
    const rangeEl = document.getElementById('weekRange');
    if (rangeEl) {
        const start = new Date(data.week_start).toLocaleDateString('fa-IR', {
            month: 'short', day: 'numeric'
        });
        const end = new Date(data.week_end).toLocaleDateString('fa-IR', {
            month: 'short', day: 'numeric'
        });
        rangeEl.textContent = `${start} تا ${end}`;
    }

    // ===== آمار =====
    const statsEl = document.getElementById('weeklyStats');
    const s = data.stats;

    const trendMap = {
        'improving': { icon: '📈', text: 'رو به بهبود', class: 'improving' },
        'declining': { icon: '📉', text: 'رو به کاهش', class: 'declining' },
        'stable': { icon: '➖', text: 'پایدار', class: 'stable' },
        'نامشخص': { icon: '🔍', text: 'کافی نیست', class: 'unknown' }
    };

    const trend = trendMap[s.trend] || trendMap['نامشخص'];

    statsEl.innerHTML = `
        <div class="weekly-stat">
            <div class="weekly-stat-value">${s.total_activities}</div>
            <div class="weekly-stat-label">📊 فعالیت</div>
        </div>
        <div class="weekly-stat">
            <div class="weekly-stat-value">${s.total_diagnoses}</div>
            <div class="weekly-stat-label">🧠 تشخیص</div>
        </div>
        <div class="weekly-stat">
            <div class="weekly-stat-value">${s.total_notes}</div>
            <div class="weekly-stat-label">📝 یاداشت</div>
        </div>
        <div class="weekly-stat">
            <div class="weekly-stat-value">${s.total_breathings + s.total_meditations}</div>
            <div class="weekly-stat-label">🧘 تمرین</div>
        </div>
    `;

    // ===== روند =====
    const trendEl = document.createElement('div');
    trendEl.className = 'weekly-trend ' + trend.class;
    trendEl.innerHTML = `
        <span>${trend.icon} روند: ${trend.text}</span>
        ${s.avg_score > 0 ? `<span class="weekly-avg">میانگین: ${s.avg_score}%</span>` : ''}
    `;
    statsEl.parentNode.insertBefore(trendEl, statsEl.nextSibling);

    // ===== متن گزارش =====
    const textEl = document.getElementById('weeklyText');
    textEl.innerHTML = `
        <div class="summary-icon">${data.llm_used ? '🤖' : '💚'}</div>
        <div class="summary-content">${escapeHtml(data.summary)}</div>
    `;
}
// ============================================================
// نمودار پیشرفت
// ============================================================

function loadProgressChart() {
    const canvas = document.getElementById('progressChart');
    if (!canvas) return;

    // ===== تشخیص‌ها رو از allHistoryItems بگیر =====
    const diagnoses = allHistoryItems
        .filter(item => item.type === 'diagnosis')
        .sort((a, b) => new Date(a.date) - new Date(b.date));

    if (diagnoses.length < 2) {
        document.querySelector('.progress-chart-wrapper').style.display = 'none';
        document.getElementById('chartEmpty').style.display = 'block';
        return;
    }

    // ===== فیلتر بر اساس بازه =====
    let filteredDiagnoses = diagnoses;
    if (currentChartRange !== 'all') {
        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() - currentChartRange);
        filteredDiagnoses = diagnoses.filter(d => new Date(d.date) >= cutoffDate);
    }

    if (filteredDiagnoses.length < 2) {
        document.querySelector('.progress-chart-wrapper').style.display = 'none';
        document.getElementById('chartEmpty').style.display = 'block';
        document.getElementById('chartEmpty').querySelector('p').textContent =
            `برای این بازه، حداقل ۲ تشخیص لازمه`;
        return;
    }

    // ===== ساخت داده‌ها =====
    const labels = filteredDiagnoses.map(d => formatShortDate(d.date));
    const scores = filteredDiagnoses.map(d => Math.round(d.data.score || 0));
    const colors = scores.map(s => getScoreColor(s));

    // ===== آمار =====
    renderChartStats(scores, filteredDiagnoses);

    // ===== ساخت نمودار =====
    if (progressChart) progressChart.destroy();

    const ctx = canvas.getContext('2d');

    progressChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'امتیاز',
                data: scores,
                borderColor: '#8B5CF6',
                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: colors,
                pointBorderColor: 'white',
                pointBorderWidth: 2,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#1e293b',
                    titleColor: 'white',
                    bodyColor: 'white',
                    padding: 12,
                    cornerRadius: 10,
                    titleFont: { family: 'Vazirmatn' },
                    bodyFont: { family: 'Vazirmatn' },
                    callbacks: {
                        title: function(context) {
                            return '📅 ' + context[0].label;
                        },
                        label: function(context) {
                            const score = context.parsed.y;
                            const level = getLevelFromScore(score);
                            return `${level.icon} ${level.label}: ${score}%`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) { return value + '%'; },
                        color: '#94a3b8',
                        font: { family: 'Vazirmatn' }
                    },
                    grid: {
                        color: 'rgba(148, 163, 184, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: '#94a3b8',
                        font: { family: 'Vazirmatn', size: 11 }
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });

    document.querySelector('.progress-chart-wrapper').style.display = 'block';
    document.getElementById('chartEmpty').style.display = 'none';
}

function renderChartStats(scores, diagnoses) {
    const container = document.getElementById('chartStats');
    if (!container) return;

    const avg = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
    const best = Math.max(...scores);
    const worst = Math.min(...scores);

    // ===== روند =====
    let trend = '➖ پایدار';
    let trendClass = 'stable';
    if (scores.length >= 2) {
        const diff = scores[scores.length - 1] - scores[0];
        if (diff > 5) {
            trend = '📈 بهبود';
            trendClass = 'improving';
        } else if (diff < -5) {
            trend = '📉 کاهش';
            trendClass = 'declining';
        }
    }

    container.innerHTML = `
        <div class="chart-stat-item">
            <div class="chart-stat-icon">📊</div>
            <div class="chart-stat-value">${avg}%</div>
            <div class="chart-stat-label">میانگین</div>
        </div>
        <div class="chart-stat-item">
            <div class="chart-stat-icon">🏆</div>
            <div class="chart-stat-value">${best}%</div>
            <div class="chart-stat-label">بهترین</div>
        </div>
        <div class="chart-stat-item">
            <div class="chart-stat-icon">📉</div>
            <div class="chart-stat-value">${worst}%</div>
            <div class="chart-stat-label">بدترین</div>
        </div>
        <div class="chart-stat-item">
            <div class="chart-stat-icon">${trend.split(' ')[0]}</div>
            <div class="chart-stat-value" style="font-size: 12px;">${trend.split(' ')[1]}</div>
            <div class="chart-stat-label">روند</div>
        </div>
    `;
}

function changeChartRange(range) {
    currentChartRange = range;
    document.querySelectorAll('.chart-filter-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.range == range);
    });
    loadProgressChart();
}

function getScoreColor(score) {
    if (score >= 65) return '#22c55e';    // سالم
    if (score >= 45) return '#f59e0b';    // خفیف
    if (score >= 25) return '#f97316';    // متوسط
    return '#ef4444';                      // شدید
}

function getLevelFromScore(score) {
    if (score >= 65) return { icon: '😊', label: 'سالم' };
    if (score >= 45) return { icon: '🙂', label: 'خفیف' };
    if (score >= 25) return { icon: '😐', label: 'متوسط' };
    return { icon: '😢', label: 'شدید' };
}

function formatShortDate(dateStr) {
    try {
        const d = new Date(dateStr);
        return d.toLocaleDateString('fa-IR', {
            month: 'short',
            day: 'numeric'
        });
    } catch {
        return dateStr;
    }
}

// ============================================================
// صادر کردن
// ============================================================
window.loadProgressChart = loadProgressChart;
window.changeChartRange = changeChartRange;
window.loadWeeklySummary=loadWeeklySummary;
window.filterHistory = filterHistory;
window.showItemDetail = showItemDetail;
window.closeDetailModal = closeDetailModal;
