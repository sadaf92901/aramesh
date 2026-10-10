// ============================================================
// باغ آرامش
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🌸 صفحه‌ی باغ بارگذاری شد');
    loadGarden();
    updateSoundIcon();
});


// ============================================================
// Cache Helpers
// ============================================================

const GARDEN_CACHE_KEY = 'garden_cache';
const GARDEN_CACHE_TIME_KEY = 'garden_cache_time';
const GARDEN_CACHE_TTL = 30 * 1000; // ۳۰ ثانیه


function getGardenCache() {
    try {
        const cached = localStorage.getItem(GARDEN_CACHE_KEY);
        const cacheTime = localStorage.getItem(GARDEN_CACHE_TIME_KEY);

        if (!cached || !cacheTime) return null;

        // ===== چک TTL =====
        const age = Date.now() - parseInt(cacheTime);
        if (age > GARDEN_CACHE_TTL) {
            clearGardenCache();
            return null;
        }

        return JSON.parse(cached);
    } catch (e) {
        console.warn('⚠️ خطا در خواندن cache:', e);
        return null;
    }
}


function setGardenCache(data) {
    try {
        localStorage.setItem(GARDEN_CACHE_KEY, JSON.stringify(data));
        localStorage.setItem(GARDEN_CACHE_TIME_KEY, Date.now().toString());
    } catch (e) {
        console.warn('⚠️ خطا در ذخیره‌ی cache:', e);
    }
}


function clearGardenCache() {
    localStorage.removeItem(GARDEN_CACHE_KEY);
    localStorage.removeItem(GARDEN_CACHE_TIME_KEY);
}


// ============================================================
// بارگذاری باغ (با Cache)
// ============================================================

function loadGarden(forceRefresh = false) {
    // ===== ۱. چک cache =====
    if (!forceRefresh) {
        const cached = getGardenCache();
        if (cached) {
            console.log('⚡ باغ از cache لود شد');
            renderGarden(cached);
            return;
        }
    }

    // ===== ۲. fetch از سرور =====
    fetch('/api/garden')
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                console.error('❌ خطا:', data.error);
                return;
            }

            // ===== ذخیره در cache =====
            setGardenCache(data);

            // ===== نمایش =====
            renderGarden(data);
        })
        .catch(err => console.error('❌ خطا:', err));
}


// ============================================================
// نمایش باغ
// ============================================================

function renderGarden(data) {
    // ===== ذخیره در window =====
    window.gardenData = data;

    // ===== چک: باغ خالیه؟ =====
    const isEmpty = (
        data.stats.total_flowers === 0 &&
        data.stats.total_seeds === 0
    );

    const emptyState = document.getElementById('gardenEmptyState');
    const mainContent = document.getElementById('gardenMain');

    if (isEmpty) {
        if (emptyState) emptyState.style.display = 'block';
        if (mainContent) mainContent.style.display = 'none';
        return;
    }

    // ===== مخفی کردن Empty State =====
    if (emptyState) emptyState.style.display = 'none';
    if (mainContent) mainContent.style.display = 'block';

    // ===== آمار =====
    document.getElementById('totalFlowers').textContent = toPersian(data.stats.total_flowers);
    document.getElementById('uniqueDays').textContent = toPersian(data.stats.unique_days);
    document.getElementById('streakDays').textContent = toPersian(data.stats.streak);

    // ===== کیف دانه =====
    renderSeedsBag(data.seeds);

    // ===== خوشه‌بندی گل‌ها =====
    const clusters = groupFlowers(data.flowers);
    renderClusters(clusters);

    // ===== چک بوته‌ی جدید =====
    checkPendingCluster(clusters);
}


// ============================================================
// گروه‌بندی گل‌ها به خوشه‌ها (۳ سطح)
// ============================================================

function groupFlowers(flowers) {
    if (!flowers || flowers.length === 0) return [];

    const flowerLabels = {
        '🌸': 'تشخیص',
        '🌷': 'یاداشت',
        '🌿': 'تنفس',
        '🪷': 'مدیتیشن',
        '🌻': 'وضعیت روزانه'
    };

    const sorted = [...flowers].sort((a, b) =>
        new Date(a.planted_at || a.date) - new Date(b.planted_at || b.date)
    );

    // ===== گروه‌بندی بر اساس نوع =====
    const byType = {};
    sorted.forEach(f => {
        if (!byType[f.flower_type]) byType[f.flower_type] = [];
        byType[f.flower_type].push(f);
    });

    const clusters = [];
    Object.keys(byType).forEach(type => {
        const typeFlowers = byType[type];
        const total = typeFlowers.length;

        // ===== سطح ۳: باغچه (هر ۱۰۰ گل) =====
        const gardenCount = Math.floor(total / 100);
        const afterGardens = total % 100;

        // ===== سطح ۲: بوته (هر ۱۰ گل) =====
        const clusterCount = Math.floor(afterGardens / 10);
        const remainder = afterGardens % 10;

        // ===== باغچه‌ها (×۱۰۰) =====
        for (let i = 0; i < gardenCount; i++) {
            const sampleFlower = typeFlowers[i * 100];
            clusters.push({
                type: type,
                count: 100,
                isCluster: true,
                isGarden: true,
                isMega: true,
                sampleId: sampleFlower.id,
                date: sampleFlower.planted_at || sampleFlower.date,
                label: flowerLabels[type] || 'فعالیت',
                position_x: sampleFlower.position_x,
                position_y: sampleFlower.position_y
            });
        }

        // ===== بوته‌ها (×۱۰) =====
        for (let i = 0; i < clusterCount; i++) {
            const sampleFlower = typeFlowers[gardenCount * 100 + i * 10];
            clusters.push({
                type: type,
                count: 10,
                isCluster: true,
                isGarden: false,
                isMega: clusterCount >= 2,
                sampleId: sampleFlower.id,
                date: sampleFlower.planted_at || sampleFlower.date,
                label: flowerLabels[type] || 'فعالیت',
                position_x: sampleFlower.position_x,
                position_y: sampleFlower.position_y
            });
        }

        // ===== گل‌های تکی =====
        for (let i = 0; i < remainder; i++) {
            const flower = typeFlowers[gardenCount * 100 + clusterCount * 10 + i];
            clusters.push({
                type: type,
                count: 1,
                isCluster: false,
                isGarden: false,
                isMega: false,
                sampleId: flower.id,
                date: flower.planted_at || flower.date,
                label: flowerLabels[type] || 'فعالیت',
                position_x: flower.position_x,
                position_y: flower.position_y
            });
        }
    });

    return clusters;
}


// ============================================================
// نمایش خوشه‌ها (با aria-label)
// ============================================================

function renderClusters(clusters) {
    const container = document.getElementById('flowersContainer');
    if (!container) return;

    if (!clusters || clusters.length === 0) {
        container.innerHTML = '';
        return;
    }

    let html = '';
    clusters.forEach((cluster, index) => {
        // ===== استفاده از موقعیت DB یا محاسبه‌ی جدید =====
        let x, y, rotate;

        if (
            cluster.position_x !== null && cluster.position_x !== undefined &&
            cluster.position_y !== null && cluster.position_y !== undefined
        ) {
            x = cluster.position_x;
            y = cluster.position_y;

            const seedRotate = (cluster.sampleId * 3571 + 1013) % 233280;
            rotate = -12 + (seedRotate / 233280) * 24;
        } else {
            const seed1 = (cluster.sampleId * 9301 + 49297) % 233280;
            const random1 = seed1 / 233280;

            const seed2 = (cluster.sampleId * 4523 + 7919) % 233280;
            const random2 = seed2 / 233280;

            const seed3 = (cluster.sampleId * 3571 + 1013) % 233280;
            const random3 = seed3 / 233280;

            x = 8 + random1 * 80;
            y = 45 + random2 * 45;
            rotate = -12 + random3 * 24;
        }

        // ===== اندازه و کلاس =====
        let size, badge = '', extraClass = '';

        if (cluster.isGarden) {
            size = 75;
            badge = '<span class="flower-badge garden-badge" aria-hidden="true">×۱۰۰</span>';
            extraClass = 'cluster mega-cluster garden-cluster';
        } else if (cluster.isCluster) {
            size = 58;
            badge = '<span class="flower-badge" aria-hidden="true">×۱۰</span>';
            extraClass = cluster.isMega ? 'cluster mega-cluster' : 'cluster';
        } else {
            size = 30;
        }

        const date = formatPersianDate(cluster.date);

        // ===== 🆕 ساخت aria-label =====
        let ariaLabel;
        if (cluster.count === 1) {
            ariaLabel = `گل ${cluster.label}`;
        } else if (cluster.count === 10) {
            ariaLabel = `بوته‌ی ${cluster.label}، ساخته‌شده از ۱۰ گل`;
        } else {
            ariaLabel = `باغچه‌ی ${cluster.label}، ساخته‌شده از ۱۰۰ گل`;
        }

        html += `
            <div class="garden-flower ${extraClass}"
                 style="left: ${x}%; top: ${y}%; font-size: ${size}px; transform: rotate(${rotate}deg); animation-delay: ${index * 0.05}s;"
                 onclick="openFlowerModal('${cluster.type}', '${cluster.label}', '${date}', ${cluster.count})"
                 role="button"
                 tabindex="0"
                 aria-label="${ariaLabel}">
                <span aria-hidden="true">${cluster.type}</span>
                ${badge}
            </div>
        `;
    });

    container.innerHTML = html;
}


// ============================================================
// چک: خوشه‌ی جدید ساخته شد؟ (جشن)
// ============================================================

function checkPendingCluster(clusters) {
    const clusterCounts = {};
    clusters.forEach(c => {
        if (c.isCluster) {
            if (!clusterCounts[c.type]) clusterCounts[c.type] = 0;
            clusterCounts[c.type]++;
        }
    });

    const isFirstTime = localStorage.getItem('garden_clusters_initialized') !== 'true';

    if (isFirstTime) {
        Object.keys(clusterCounts).forEach(type => {
            localStorage.setItem('garden_last_clusters_' + type, clusterCounts[type]);
        });
        localStorage.setItem('garden_clusters_initialized', 'true');
        return;
    }

    let newCluster = false;

    Object.keys(clusterCounts).forEach(type => {
        const key = 'garden_last_clusters_' + type;
        const lastCount = parseInt(localStorage.getItem(key) || '0');

        if (clusterCounts[type] > lastCount) {
            newCluster = true;
            localStorage.setItem(key, clusterCounts[type]);
        }
    });

    if (newCluster) {
        setTimeout(() => {
            createConfetti();
            playCelebrationSound();

            if (typeof showToast === 'function') {
                showToast('🌳 تبریک! بوته‌ی جدید ساختی!', '🎉', 'success');
            }
        }, 800);
    }
}


// ============================================================
// کیف دانه (با aria-label)
// ============================================================

function renderSeedsBag(seeds) {
    const bag = document.getElementById('seedsBag');
    const count = document.getElementById('seedsCount');
    const list = document.getElementById('seedsList');
    const hint = document.getElementById('seedsHint');

    if (!bag || !count || !list) {
        console.error('❌ عناصر کیف دانه پیدا نشدن!');
        return;
    }

    if (!seeds || seeds.length === 0) {
        bag.style.display = 'none';
        console.log('📦 کیف دانه: خالی');
        return;
    }

    bag.style.display = 'block';
    count.textContent = toPersian(seeds.length);

    const seedLabels = {
        '🌸': 'تشخیص',
        '🌷': 'یاداشت',
        '🌿': 'تنفس',
        '🪷': 'مدیتیشن',
        '🌻': 'وضعیت'
    };

    let html = '';
    seeds.forEach(seed => {
        const seedLabel = seedLabels[seed.flower_type] || 'گل';
        html += `
            <div class="seed-item"
                 onclick="plantSeed(${seed.id})"
                 role="button"
                 tabindex="0"
                 aria-label="کاشتن دانه‌ی ${seedLabel}"
                 title="بکار">
                <span class="seed-emoji" aria-hidden="true">${seed.flower_type}</span>
                <span class="seed-label">${seedLabel}</span>
            </div>
        `;
    });

    list.innerHTML = html;

    if (hint) hint.style.display = 'block';
}


// ============================================================
// کاشتن دانه
// ============================================================

function plantSeed(seedId) {
    fetch('/api/garden/plant', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ seed_id: seedId })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert('❌ ' + data.error);
            return;
        }

        // ===== پاک کردن cache =====
        clearGardenCache();

        // ===== صدا =====
        playPlantSound();

        // ===== ذرات نور =====
        createSparkles();

        // ===== Toast =====
        if (typeof showToast === 'function') {
            showToast('🌸 گل کاشته شد!', '✨', 'success');
        }

        // ===== بارگذاری مجدد =====
        setTimeout(() => loadGarden(true), 800);
    })
    .catch(err => {
        console.error('❌ خطا:', err);
        alert('❌ خطا در کاشتن');
    });
}


// ============================================================
// مودال پیشرفت
// ============================================================

function openProgressModal() {
    const modal = document.getElementById('progressModal');
    if (!modal) return;

    modal.style.display = 'flex';

    const data = window.gardenData;

    if (!data) {
        fetch('/api/garden')
            .then(res => res.json())
            .then(freshData => {
                if (freshData.error) return;
                window.gardenData = freshData;

                renderLevel(freshData.stats.total_flowers);
                renderGrowth(freshData.flowers);
                renderAchievements(freshData.stats);
            })
            .catch(err => console.error('❌ خطا:', err));
        return;
    }

    renderLevel(data.stats.total_flowers);
    renderGrowth(data.flowers);
    renderAchievements(data.stats);
}

function closeProgressModal() {
    const modal = document.getElementById('progressModal');
    if (modal) modal.style.display = 'none';
}


// ============================================================
// سطح باغ (۹ سطح)
// ============================================================

function renderLevel(totalFlowers) {
    const levels = [
        { min: 0,     max: 10,       name: 'تازه‌کار',          icon: '🌱', next: 10 },
        { min: 10,    max: 35,       name: 'باغبون',            icon: '🌿', next: 35 },
        { min: 35,    max: 70,       name: 'باغبون ماهر',       icon: '🌳', next: 70 },
        { min: 70,    max: 150,      name: 'استاد باغبون',      icon: '🌲', next: 150 },
        { min: 150,   max: 300,      name: 'باغ‌بهشت',          icon: '🏆', next: 300 },
        { min: 300,   max: 600,      name: 'باغبون افسانه‌ای',  icon: '👑', next: 600 },
        { min: 600,   max: 1000,     name: 'باغبون جاودانه',    icon: '💎', next: 1000 },
        { min: 1000,  max: 2000,     name: 'اسطوره‌ی باغ',      icon: '🌟', next: 2000 },
        { min: 2000,  max: Infinity, name: 'خدای باغ',          icon: '🌌', next: null }
    ];

    let current = levels[0];
    for (const level of levels) {
        if (totalFlowers >= level.min && totalFlowers < level.max) {
            current = level;
            break;
        }
    }

    document.getElementById('levelIcon').textContent = current.icon;
    document.getElementById('levelName').textContent = current.name;

    if (current.next) {
        const progress = totalFlowers - current.min;
        const total = current.next - current.min;
        const percent = (progress / total) * 100;

        document.getElementById('levelProgress').textContent = toPersian(progress) + '/' + toPersian(total);
        document.getElementById('levelBar').style.width = percent + '%';
        document.getElementById('levelNext').textContent =
            toPersian(total - progress) + ' گل دیگه تا سطح بعدی ' + current.icon;
    } else {
        document.getElementById('levelProgress').textContent = '🌌';
        document.getElementById('levelBar').style.width = '100%';
        document.getElementById('levelNext').textContent = 'به بالاترین سطح رسیدی! 🌌';
    }
}


// ============================================================
// نمودار رشد
// ============================================================

function renderGrowth(flowers) {
    const container = document.getElementById('growthBars');
    if (!container) return;

    const counts = {
        '🌸': 0,
        '🌷': 0,
        '🌿': 0,
        '🪷': 0,
        '🌻': 0
    };

    flowers.forEach(f => {
        if (counts[f.flower_type] !== undefined) {
            counts[f.flower_type]++;
        }
    });

    const max = Math.max(...Object.values(counts), 10);

    const labels = {
        '🌸': 'تشخیص',
        '🌷': 'یاداشت',
        '🌿': 'تنفس',
        '🪷': 'مدیتیشن',
        '🌻': 'وضعیت'
    };

    const flowerIndex = {
        '🌸': 1,
        '🌷': 2,
        '🌿': 3,
        '🪷': 4,
        '🌻': 5
    };

    let html = '';
    Object.keys(counts).forEach(type => {
        const count = counts[type];
        const percent = count > 0 ? (count / max) * 100 : 0;
        const hasCluster = count >= 10;
        const clusterCount = Math.floor(count / 10);

        html += `
            <div class="growth-row" role="group" aria-label="${labels[type]}: ${count} گل">
                <span class="growth-emoji" aria-hidden="true">${type}</span>
                <span class="growth-label">${labels[type]}</span>
                <div class="growth-bar-container">
                    <div class="growth-bar-fill flower-${flowerIndex[type]}"
                         style="width: ${percent}%;">
                    </div>
                </div>
                <span class="growth-count ${hasCluster ? 'has-cluster' : ''}">
                    ${toPersian(count)}${hasCluster ? ' 🌳' + toPersian(clusterCount) : ''}
                </span>
            </div>
        `;
    });

    container.innerHTML = html;
}


// ============================================================
// دستاوردها (۱۱ دستاورد)
// ============================================================

function renderAchievements(stats) {
    const container = document.getElementById('achievementsGrid');
    if (!container) return;

    const total = stats.total_flowers;

    const achievements = [
        { icon: '🌱', name: 'اولین قدم',        target: 1 },
        { icon: '🌸', name: '۱۰ گل',             target: 10 },
        { icon: '🌿', name: '۳۵ گل',             target: 35 },
        { icon: '🌳', name: '۷۰ گل',             target: 70 },
        { icon: '🌲', name: '۱۵۰ گل',            target: 150 },
        { icon: '🏆', name: '۳۰۰ گل',            target: 300 },
        { icon: '👑', name: '۶۰۰ گل',            target: 600 },
        { icon: '💎', name: '۱۰۰۰ گل',           target: 1000 },
        { icon: '🔥', name: 'استریک ۷ روزه',     target: 7,   value: stats.streak },
        { icon: '⚡', name: 'استریک ۳۰ روزه',    target: 30,  value: stats.streak },
        { icon: '🌪️', name: 'استریک ۱۰۰ روزه',  target: 100, value: stats.streak },
    ];

    let html = '';
    achievements.forEach(a => {
        const value = a.value !== undefined ? a.value : total;
        const unlocked = value >= a.target;

        html += `
            <div class="achievement ${unlocked ? 'unlocked' : 'locked'}"
                 aria-label="${a.name}${unlocked ? '، باز شده' : '، قفل'}">
                <span class="achievement-icon" aria-hidden="true">${a.icon}</span>
                <div class="achievement-info">
                    <div class="achievement-name">${a.name}</div>
                    <div class="achievement-progress">
                        ${unlocked ? '✅ باز شد' : toPersian(value) + '/' + toPersian(a.target)}
                    </div>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}


// ============================================================
// صدا (کاشتن)
// ============================================================

function playPlantSound() {
    if (!isSoundEnabled()) return;

    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

        const osc1 = audioCtx.createOscillator();
        const gain1 = audioCtx.createGain();

        osc1.type = 'sine';
        osc1.frequency.setValueAtTime(880, audioCtx.currentTime);
        osc1.frequency.exponentialRampToValueAtTime(1320, audioCtx.currentTime + 0.1);

        gain1.gain.setValueAtTime(0.1, audioCtx.currentTime);
        gain1.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.3);

        osc1.connect(gain1);
        gain1.connect(audioCtx.destination);
        osc1.start(audioCtx.currentTime);
        osc1.stop(audioCtx.currentTime + 0.3);

        const osc2 = audioCtx.createOscillator();
        const gain2 = audioCtx.createGain();

        osc2.type = 'sine';
        osc2.frequency.setValueAtTime(1320, audioCtx.currentTime + 0.1);
        osc2.frequency.exponentialRampToValueAtTime(1760, audioCtx.currentTime + 0.2);

        gain2.gain.setValueAtTime(0, audioCtx.currentTime + 0.1);
        gain2.gain.linearRampToValueAtTime(0.08, audioCtx.currentTime + 0.15);
        gain2.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.5);

        osc2.connect(gain2);
        gain2.connect(audioCtx.destination);
        osc2.start(audioCtx.currentTime + 0.1);
        osc2.stop(audioCtx.currentTime + 0.5);

    } catch (e) {
        console.log('🔇 صدا پخش نشد:', e);
    }
}


// ============================================================
// صدا (جشن)
// ============================================================

function playCelebrationSound() {
    if (!isSoundEnabled()) return;

    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

        const notes = [523.25, 659.25, 783.99, 1046.50];

        notes.forEach((freq, i) => {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();

            osc.type = 'sine';
            osc.frequency.setValueAtTime(freq, audioCtx.currentTime + i * 0.1);

            gain.gain.setValueAtTime(0, audioCtx.currentTime + i * 0.1);
            gain.gain.linearRampToValueAtTime(0.08, audioCtx.currentTime + i * 0.1 + 0.05);
            gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + i * 0.1 + 0.5);

            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start(audioCtx.currentTime + i * 0.1);
            osc.stop(audioCtx.currentTime + i * 0.1 + 0.5);
        });

    } catch (e) {
        console.log('🔇 صدا پخش نشد:', e);
    }
}


// ============================================================
// Toggle صدا
// ============================================================

function toggleGardenSound() {
    const current = isSoundEnabled();
    setSoundEnabled(!current);

    updateSoundIcon();

    if (typeof showToast === 'function') {
        showToast(
            !current ? '🔊 صدا روشن شد' : '🔇 صدا خاموش شد',
            !current ? '🔊' : '🔇',
            'success'
        );
    }
}

function updateSoundIcon() {
    const btn = document.getElementById('soundToggleBtn');
    if (!btn) return;
    btn.textContent = isSoundEnabled() ? '🔊' : '🔇';
    btn.title = isSoundEnabled() ? 'خاموش کردن صدا' : 'روشن کردن صدا';
    btn.setAttribute('aria-label', isSoundEnabled() ? 'خاموش کردن صدای باغ' : 'روشن کردن صدای باغ');
}


// ============================================================
// ذرات نور
// ============================================================

function createSparkles() {
    const container = document.getElementById('sparkles');
    if (!container) return;

    const rect = container.getBoundingClientRect();
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    for (let i = 0; i < 16; i++) {
        const sparkle = document.createElement('div');
        sparkle.className = 'sparkle';
        sparkle.setAttribute('aria-hidden', 'true');

        const angle = (Math.PI * 2 * i) / 16;
        const distance = 60 + Math.random() * 80;

        sparkle.style.left = centerX + 'px';
        sparkle.style.top = centerY + 'px';

        const targetX = centerX + Math.cos(angle) * distance;
        const targetY = centerY + Math.sin(angle) * distance;

        sparkle.animate([
            { transform: 'translate(0, 0) scale(1)', opacity: 1 },
            { transform: `translate(${targetX - centerX}px, ${targetY - centerY}px) scale(0)`, opacity: 0 }
        ], {
            duration: 1200,
            easing: 'cubic-bezier(0.4, 0, 0.2, 1)'
        });

        container.appendChild(sparkle);
        setTimeout(() => sparkle.remove(), 1200);
    }
}


// ============================================================
// کانفتی (جشن)
// ============================================================

function createConfetti() {
    const container = document.getElementById('confetti');
    if (!container) return;

    const colors = ['#f59e0b', '#10b981', '#8b5cf6', '#ec4899', '#3b82f6', '#ef4444', '#fbbf24'];
    const shapes = ['square', 'circle'];

    for (let i = 0; i < 50; i++) {
        const piece = document.createElement('div');
        piece.className = 'confetti-piece';
        piece.setAttribute('aria-hidden', 'true');

        const color = colors[Math.floor(Math.random() * colors.length)];
        const shape = shapes[Math.floor(Math.random() * shapes.length)];

        piece.style.left = Math.random() * 100 + '%';
        piece.style.background = color;
        piece.style.animationDelay = (Math.random() * 0.5) + 's';
        piece.style.animationDuration = (2 + Math.random() * 2) + 's';

        if (shape === 'circle') {
            piece.style.borderRadius = '50%';
        }

        const size = 6 + Math.random() * 8;
        piece.style.width = size + 'px';
        piece.style.height = size + 'px';

        container.appendChild(piece);
        setTimeout(() => piece.remove(), 5000);
    }
}


// ============================================================
// مودال گل
// ============================================================

function openFlowerModal(flowerType, label, date, count) {
    count = count || 1;

    const flowerInfo = {
        '🌸': {
            title: 'تشخیص وضعیت روانی',
            desc: 'این گل رو وقتی کاشتی که یه تشخیص انجام دادی',
            quote: '💚 هر تشخیص، یه قدم به سمت خودشناسی',
            color: '#EC4899'
        },
        '🌷': {
            title: 'یاداشت امروز',
            desc: 'این گل رو وقتی کاشتی که احساست رو نوشتی',
            quote: '💜 نوشتن، نیمی از درمانه',
            color: '#A855F7'
        },
        '🌿': {
            title: 'تمرین تنفس',
            desc: 'این گل رو وقتی کاشتی که با نفست آروم شدی',
            quote: '💚 یه نفس عمیق، بهترین داروی آرامشه',
            color: '#10B981'
        },
        '🪷': {
            title: 'مدیتیشن',
            desc: 'این گل رو وقتی کاشتی که با خودت خلوت کردی',
            quote: '💙 سکوت، بهترین معلمه',
            color: '#3B82F6'
        },
        '🌻': {
            title: 'وضعیت روزانه',
            desc: 'این گل رو وقتی کاشتی که حالت رو ثبت کردی',
            quote: '💛 آگاهی از حال، اولین قدم به سمت آرامشه',
            color: '#F59E0B'
        }
    };

    const info = flowerInfo[flowerType] || {
        title: label,
        desc: 'این گل رو کاشتی',
        quote: '💚 هر فعالیت، یه قدم به سمت آرامش',
        color: '#8B5CF6'
    };

    const modalFlower = document.getElementById('flowerModalFlower');
    const modalTitle = document.getElementById('flowerModalTitle');
    const modalDate = document.getElementById('flowerModalDate');

    if (count === 100) {
        modalFlower.innerHTML = flowerType + '<span class="flower-badge-modal garden-badge" aria-hidden="true">×۱۰۰</span>';
        modalTitle.textContent = '🏞️ باغچه‌ی ' + info.title;
    } else if (count === 10) {
        modalFlower.innerHTML = flowerType + '<span class="flower-badge-modal" aria-hidden="true">×۱۰</span>';
        modalTitle.textContent = '🌳 بوته‌ی ' + info.title;
    } else {
        modalFlower.textContent = flowerType;
        modalTitle.textContent = info.title;
    }

    modalDate.innerHTML = `
        <div style="margin-bottom:12px;">📅 ${date}</div>
        ${count === 100 ? '<div style="margin-bottom:12px;font-size:14px;font-weight:700;color:#F59E0B;">🏞️ این باغچه از ۱۰۰ گل ساخته شده!</div>' : ''}
        ${count === 10 ? '<div style="margin-bottom:12px;font-size:14px;font-weight:700;color:#10B981;">🌳 این بوته از ۱۰ گل ساخته شده!</div>' : ''}
        <div style="font-size:13px;color:#64748b;margin-bottom:12px;line-height:1.8;">${info.desc}</div>
        <div style="background:${info.color}20;color:${info.color};padding:10px 14px;border-radius:12px;font-size:13px;font-weight:700;border-right:3px solid ${info.color};">
            ${info.quote}
        </div>
    `;

    document.getElementById('flowerModal').style.display = 'flex';
}

function closeFlowerModal() {
    document.getElementById('flowerModal').style.display = 'none';
}


// ============================================================
// توابع کمکی
// ============================================================

function toPersian(num) {
    const persianDigits = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
    return String(num).split('').map(d => persianDigits[parseInt(d)] || d).join('');
}

function formatPersianDate(dateStr) {
    try {
        if (!dateStr) return '';
        const d = new Date(dateStr);
        return d.toLocaleDateString('fa-IR', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    } catch {
        return dateStr;
    }
}


// ============================================================
// صادر کردن
// ============================================================

window.plantSeed = plantSeed;
window.openFlowerModal = openFlowerModal;
window.closeFlowerModal = closeFlowerModal;
window.openProgressModal = openProgressModal;
window.closeProgressModal = closeProgressModal;
window.toggleGardenSound = toggleGardenSound;
window.updateSoundIcon = updateSoundIcon;
