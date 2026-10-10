// ============================================================
// توابع کامپوننت‌ها (وضعیت‌ها، نمودار، تمرین تنفس، تاریخچه)
// ============================================================

// ============================================================
// 1. وضعیت‌های روزانه
// ============================================================

const STATUS_MAP = {
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
// ============================================================
// توابع ذخیره‌سازی محلی
// ============================================================

function loadHistory() {
    try {
        return JSON.parse(localStorage.getItem('history') || '[]');
    } catch (e) {
        return [];
    }
}

function clearHistory() {
    localStorage.removeItem('history');
    localStorage.removeItem('dailyMoods');
}
let statusValues = { mood: null, energy: null, sleep: null };

function toggleStatus(type) {
    const container = document.getElementById(type + 'Options');
    const group = document.getElementById('status' + capitalize(type));

    if (container.style.display === 'block') {
        container.style.display = 'none';
        group.classList.remove('active');
        return;
    }

    ['mood', 'energy', 'sleep'].forEach(t => {
        if (t !== type) {
            const otherContainer = document.getElementById(t + 'Options');
            const otherGroup = document.getElementById('status' + capitalize(t));
            if (otherContainer) {
                otherContainer.style.display = 'none';
                otherGroup.classList.remove('active');
            }
        }
    });

    container.style.display = 'block';
    group.classList.add('active');

    setTimeout(() => {
        group.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);
}

function toggleAllStatuses() {
    let allOpen = true;
    ['mood', 'energy', 'sleep'].forEach(t => {
        const container = document.getElementById(t + 'Options');
        if (container.style.display !== 'block') allOpen = false;
    });

    if (allOpen) {
        ['mood', 'energy', 'sleep'].forEach(t => {
            const container = document.getElementById(t + 'Options');
            const group = document.getElementById('status' + capitalize(t));
            container.style.display = 'none';
            group.classList.remove('active');
        });
    } else {
        ['mood', 'energy', 'sleep'].forEach(t => {
            const container = document.getElementById(t + 'Options');
            const group = document.getElementById('status' + capitalize(t));
            container.style.display = 'block';
            group.classList.add('active');
        });
    }
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function selectStatus(type, value) {
    statusValues[type] = value;

    // ===== ذخیره در localStorage =====
    saveDailyStatus(statusValues);

    // ===== به‌روزرسانی نمایش =====
    updateAllStatusDisplay();

    // ===== پیام موفقیت =====
    showToast('وضعیت ' + STATUS_MAP[type][value].label + ' ثبت شد', STATUS_MAP[type][value].icon, 'success');
}

// ============================================================
// به‌روزرسانی نمایش وضعیت‌ها
// ============================================================

function updateAllStatusDisplay() {
    ['mood', 'energy', 'sleep'].forEach(type => {
        const value = statusValues[type];
        const displayEl = document.getElementById(type + 'Label');

        if (displayEl && value && STATUS_MAP[type] && STATUS_MAP[type][value]) {
            const data = STATUS_MAP[type][value];
            displayEl.textContent = data.icon + ' ' + data.label;
            displayEl.style.color = '#8B5CF6';
            displayEl.style.fontWeight = '600';
        } else if (displayEl) {
            displayEl.textContent = '';
        }
    });

    // ===== به‌روزرسانی دکمه‌ها =====
    ['mood', 'energy', 'sleep'].forEach(type => {
        const value = statusValues[type];
        const buttons = document.querySelectorAll('.' + type + '-btn');
        buttons.forEach(btn => {
            if (btn.dataset.value === value) {
                btn.classList.add('active');
                btn.style.opacity = '1';
                btn.style.borderColor = '#8B5CF6';
                btn.style.transform = 'scale(1.1)';
            } else {
                btn.classList.remove('active');
                btn.style.opacity = '0.4';
                btn.style.borderColor = '#e2e8f0';
                btn.style.transform = 'scale(1)';
            }
        });
    });
}
function updateStatusSummary() {
    var moodVal = statusValues.mood;
    var energyVal = statusValues.energy;
    var sleepVal = statusValues.sleep;

    var moodEl = document.getElementById('summaryMood');
    var energyEl = document.getElementById('summaryEnergy');
    var sleepEl = document.getElementById('summarySleep');
    var dateEl = document.getElementById('summaryDate');

    if (moodEl) {
        moodEl.textContent = (moodVal && STATUS_MAP.mood[moodVal]) ? STATUS_MAP.mood[moodVal].label : '--';
    }
    if (energyEl) {
        energyEl.textContent = (energyVal && STATUS_MAP.energy[energyVal]) ? STATUS_MAP.energy[energyVal].label : '--';
    }
    if (sleepEl) {
        sleepEl.textContent = (sleepVal && STATUS_MAP.sleep[sleepVal]) ? STATUS_MAP.sleep[sleepVal].label : '--';
    }
    if (dateEl) {
        dateEl.textContent = getPersianDate();
    }
}

// ============================================================
// 3. نمودار خلقی
// ============================================================

function getWeekMoods() {
    const moods = loadDailyMoods();
    const weekDays = [];
    const today = new Date();
    const dayNames = getPersianShortDayNames();
    const fullDayNames = getPersianDayNames();
    const emojis = ['😊', '🙂', '😐', '😢'];

    for (let i = 6; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        const key = date.toISOString().split('T')[0];
        const mood = moods[key];

        weekDays.push({
            day: dayNames[i],
            fullDay: fullDayNames[i],
            icon: (mood !== undefined && mood >= 0 && mood <= 3) ? emojis[mood] : '❓',
            fullDate: key,
            value: mood,
            hasData: mood !== undefined && mood >= 0 && mood <= 3
        });
    }

    return weekDays;
}

function updateMoodChart() {
    const weekMoods = getWeekMoods();
    const container = document.getElementById('chartPoints');
    const polyline = document.getElementById('trendPolyline');
    const area = document.getElementById('trendArea');

    if (!container) return;

    const numericMap = { '😊': 3, '🙂': 2, '😐': 1, '😢': 0, '❓': -1 };
    const labelMap = {
        '😊': 'خوب',
        '🙂': 'نسبتاً خوب',
        '😐': 'معمولی',
        '😢': 'بد',
        '❓': 'ثبت نشده'
    };

    let html = '';
    let hasData = false;

    weekMoods.forEach(item => {
        const value = numericMap[item.icon] !== undefined ? numericMap[item.icon] : -1;
        const isData = item.hasData;
        if (isData) hasData = true;

        let statusClass = 'empty';
        if (isData) {
            if (value >= 2.5) statusClass = 'good';
            else if (value >= 1.5) statusClass = 'neutral';
            else if (value >= 0) statusClass = 'bad';
        }

        html += `
            <div class="chart-point">
                <div class="point-tooltip">${item.fullDay}: ${labelMap[item.icon] || 'ثبت نشده'}</div>
                <span class="point-emoji" style="${!isData ? 'opacity:0.2;' : ''}">${item.icon}</span>
                <div class="point-dot ${statusClass}"></div>
                <span class="point-day">${item.day}</span>
                <span class="point-value">${isData ? labelMap[item.icon].slice(0, 3) : '--'}</span>
            </div>
        `;
    });

    container.innerHTML = html;
    drawTrendLine(weekMoods, polyline, area);
    updateChartStats(weekMoods);
}

function drawTrendLine(points, polyline, area) {
    const width = 700;
    const height = 170;
    const padding = 20;
    const hasData = points.some(p => p.hasData);

    if (!hasData || points.length === 0) {
        polyline.setAttribute('points', '');
        area.setAttribute('points', '');
        return;
    }

    const numericMap = { '😊': 3, '🙂': 2, '😐': 1, '😢': 0 };
    let pointsStr = '';
    let areaStr = '';
    const spacing = (width - padding * 2) / (points.length - 1);

    points.forEach((p, i) => {
        const x = padding + (i * spacing);
        let y;

        if (p.hasData) {
            const val = numericMap[p.icon] || 0;
            const normalized = val / 3;
            y = height - padding - (normalized * (height - padding * 2));
        } else {
            let leftVal = null, rightVal = null;
            for (let j = i - 1; j >= 0; j--) {
                if (points[j].hasData) { leftVal = numericMap[points[j].icon] || 0; break; }
            }
            for (let k = i + 1; k < points.length; k++) {
                if (points[k].hasData) { rightVal = numericMap[points[k].icon] || 0; break; }
            }

            if (leftVal !== null && rightVal !== null) {
                const avg = (leftVal + rightVal) / 2;
                const norm = avg / 3;
                y = height - padding - (norm * (height - padding * 2));
            } else if (leftVal !== null) {
                const normL = leftVal / 3;
                y = height - padding - (normL * (height - padding * 2));
            } else if (rightVal !== null) {
                const normR = rightVal / 3;
                y = height - padding - (normR * (height - padding * 2));
            } else {
                y = height / 2;
            }
        }

        pointsStr += (i === 0 ? '' : ' ') + x + ',' + y;
        areaStr += (i === 0 ? '' : ' ') + x + ',' + y;
    });

    const lastX = padding + ((points.length - 1) * spacing);
    areaStr += ' ' + lastX + ',' + (height - padding);
    areaStr += ' ' + padding + ',' + (height - padding);

    polyline.setAttribute('points', pointsStr);
    area.setAttribute('points', areaStr);

    const length = polyline.getTotalLength ? polyline.getTotalLength() : 1000;
    polyline.style.strokeDasharray = length;
    polyline.style.strokeDashoffset = length;

    polyline.style.animation = 'none';
    setTimeout(() => {
        polyline.style.animation = 'drawLine 0.8s ease forwards';
    }, 10);
}

function updateChartStats(weekMoods) {
    const validMoods = weekMoods.filter(m => m.hasData);
    const avgEl = document.getElementById('weekAvg');
    const trendEl = document.getElementById('weekTrend');
    const bestEl = document.getElementById('bestDay');

    const numericMap = { '😊': 3, '🙂': 2, '😐': 1, '😢': 0 };

    if (validMoods.length === 0) {
        avgEl.textContent = '--';
        avgEl.className = 'stat-number no-data';
        trendEl.textContent = '--';
        trendEl.className = 'stat-number no-data';
        bestEl.textContent = '--';
        bestEl.className = 'stat-number no-data';
        return;
    }

    const total = validMoods.reduce((sum, m) => sum + (numericMap[m.icon] || 0), 0);
    const avg = total / validMoods.length;
    avgEl.textContent = avg.toFixed(1);
    avgEl.className = 'stat-number has-data';

    if (validMoods.length >= 2) {
        const first = numericMap[validMoods[0].icon] || 0;
        const last = numericMap[validMoods[validMoods.length - 1].icon] || 0;
        const diff = last - first;
        let trendText = '';
        if (diff > 0.5) trendText = '📈 رو به بهبود';
        else if (diff < -0.5) trendText = '📉 رو به کاهش';
        else trendText = '➖ پایدار';
        trendEl.textContent = trendText;
        trendEl.className = 'stat-number has-data';
    } else {
        trendEl.textContent = '🔍 کافی نیست';
        trendEl.className = 'stat-number no-data';
    }

    const best = validMoods.reduce((best, m) => {
        const val = numericMap[m.icon] || 0;
        return val > (numericMap[best.icon] || 0) ? m : best;
    }, validMoods[0]);

    bestEl.textContent = best.fullDay + ' ' + best.icon;
    bestEl.className = 'stat-number has-data';
}

// ============================================================
// 4. استریک و سطح
// ============================================================
function updateStreakAndLevel() {
    const moods = loadDailyMoods();
    let streak = 0;
    const checkDate = new Date();

    for (let i = 0; i < 30; i++) {
        const dateStr = checkDate.toISOString().split('T')[0];
        if (moods[dateStr] !== undefined && moods[dateStr] >= 0) {
            streak++;
        } else {
            break;
        }
        checkDate.setDate(checkDate.getDate() - 1);
    }

    const streakEl = document.getElementById('streakCount');
    if (streakEl) streakEl.textContent = streak;

    const totalEntries = Object.keys(moods).length;
    const level = Math.floor(totalEntries / 5) + 1;

    const levelEl = document.getElementById('levelCount');
    if (levelEl) levelEl.textContent = level;
}

// ============================================================
// 5. تاریخچه
// ============================================================
function loadHistoryDisplay() {
    const container = document.getElementById('historyContainer');
    if (!container) return;

    fetch('/api/history')
        .then(response => response.json())
        .then(data => {
            // ===== اگر خطا یا داده‌ای نبود =====
            if (data.error) {
                container.innerHTML = '<div class="history-empty">📭 خطا در دریافت تاریخچه</div>';
                return;
            }

            // ===== اگر داده خالی یا undefined بود =====
            if (!data || data.length === 0) {
                container.innerHTML = '<div class="history-empty">📭 هیچ داده‌ای ثبت نشده</div>';
                return;
            }

            let html = '<div class="history-list">';
            data.forEach(item => {
                const persianDate = new Date(item.date).toLocaleDateString('fa-IR');
                const emojis = ['😊', '🙂', '😐', '😢'];
                const emoji = emojis[item.prediction] || '❓';
                const labels = ['سالم', 'خفیف', 'متوسط', 'شدید'];
                const label = labels[item.prediction] || 'نامشخص';
                const score = item.final_score || item.score || 0;

                html += `
                    <div class="history-item">
                        <span class="history-date">${persianDate}</span>
                        <span class="history-mood">${emoji} ${label}</span>
                        <span class="history-score">${Math.round(score)}%</span>
                    </div>
                `;
            });
            html += '</div>';

            // ===== آمار =====
            const stats = { total: data.length, healthy: 0, mild: 0, moderate: 0, severe: 0 };
            data.forEach(item => {
                const pred = item.prediction;
                if (pred === 0) stats.healthy++;
                else if (pred === 1) stats.mild++;
                else if (pred === 2) stats.moderate++;
                else if (pred === 3) stats.severe++;
            });

            html += `
                <div style="margin-top:16px;padding:12px;background:#f8fafc;border-radius:12px;display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;text-align:center;">
                    <div><span style="font-size:20px;">😊</span><br><span style="font-weight:700;color:#22c55e;">${stats.healthy}</span></div>
                    <div><span style="font-size:20px;">🙂</span><br><span style="font-weight:700;color:#f59e0b;">${stats.mild}</span></div>
                    <div><span style="font-size:20px;">😐</span><br><span style="font-weight:700;color:#f97316;">${stats.moderate}</span></div>
                    <div><span style="font-size:20px;">😢</span><br><span style="font-weight:700;color:#ef4444;">${stats.severe}</span></div>
                </div>
            `;

            container.innerHTML = html;
        })
        .catch(error => {
            console.error('❌ خطا در دریافت تاریخچه:', error);
            container.innerHTML = '<div class="history-empty">📭 خطا در دریافت تاریخچه</div>';
        });
}

function updateHistoryCount() {
    const history = loadHistory();
    const moods = loadDailyMoods();
    const count = history.length + Object.keys(moods).length;

    document.getElementById('historyCount').textContent = count + ' ثبت';

    const badge = document.getElementById('historyBadge');
    if (count > 0) {
        badge.style.display = 'inline';
        badge.textContent = count;
    } else {
        badge.style.display = 'none';
    }
}

function showHistory() {
    goToPage('pageHistory');
    loadHistoryDisplay();
}
function clearAllHistory() {
    if (!confirm('⚠️ آیا مطمئنی می‌خواهی تمام تاریخچه را پاک کنی؟')) return;

    fetch('/api/history', {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('🗑️ تاریخچه پاک شد', '✅', 'warning');
            loadHistoryDisplay();
            updateMoodChart();
            updateStreakAndLevel();
            updateHistoryCount();
        } else {
            showToast('❌ خطا در پاک کردن تاریخچه', '❌', 'error');
        }
    })
    .catch(error => {
        console.error('❌ خطا:', error);
        showToast('❌ خطا در ارتباط با سرور', '❌', 'error');
    });
}
// ============================================================
// تابع باز و بسته کردن منوی وضعیت
// ============================================================

function toggleOptions(type) {
    var options = document.getElementById(type + 'Options');
    if (!options) return;

    // بستن بقیه منوها
    ['mood', 'energy', 'sleep'].forEach(function(t) {
        if (t !== type) {
            var other = document.getElementById(t + 'Options');
            if (other) other.style.display = 'none';
        }
    });

    // باز یا بسته کردن منو
    options.style.display = (options.style.display === 'block') ? 'none' : 'block';
}
// ============================================================
// روند درمان هفتگی
// ============================================================

function updateTreatmentProgress() {
    const breathEl = document.getElementById('breathCount');
    const dailyEl = document.getElementById('dailyCheckCount');
    const percentEl = document.getElementById('treatmentPercent');
    const barEl = document.getElementById('treatmentBar');

    if (!breathEl && !dailyEl && !percentEl && !barEl) return;

    fetch('/api/weekly-progress')
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                console.error('❌ خطا:', data.error);
                return;
            }

            if (breathEl) breathEl.textContent = data.breath_count || 0;
            if (dailyEl) dailyEl.textContent = data.daily_count || 0;

            const percent = Math.round(data.progress || 0);
            if (percentEl) percentEl.textContent = percent + '%';
            if (barEl) barEl.style.width = percent + '%';
        })
        .catch(err => console.error('❌ خطا در دریافت روند درمان:', err));
}
// ============================================================
// صادر کردن توابع به صورت Global
// ============================================================
// وضعیت‌ها
window.toggleStatus = toggleStatus;
window.toggleOptions=toggleOptions;
window.toggleAllStatuses = toggleAllStatuses;
window.selectStatus = selectStatus;
window.updateAllStatusDisplay = updateAllStatusDisplay;
// نمودار
window.updateMoodChart = updateMoodChart;
window.getWeekMoods = getWeekMoods;
window.updateStreakAndLevel = updateStreakAndLevel;
// تاریخچه
window.loadHistoryDisplay = loadHistoryDisplay;
window.updateHistoryCount = updateHistoryCount;
window.showHistory = showHistory;
window.clearAllHistory = clearAllHistory;
window.updateTreatmentProgress=updateTreatmentProgress;
window.statusValues=statusValues;