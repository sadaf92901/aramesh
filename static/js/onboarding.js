// ============================================================
// Onboarding
// ============================================================

let currentSlide = 0;
const totalSlides = 5;

// ============================================================
// ناوبری
// ============================================================

function showSlide(index) {
    if (index < 0 || index >= totalSlides) return;

    const slides = document.querySelectorAll('.slide');
    const dots = document.querySelectorAll('.dot');

    slides.forEach((slide, i) => {
        slide.classList.remove('active', 'prev');
        if (i === index) {
            slide.classList.add('active');
        } else if (i < index) {
            slide.classList.add('prev');
        }
    });

    dots.forEach((dot, i) => {
        dot.classList.toggle('active', i === index);
    });

    // ===== دکمه‌ها =====
    document.getElementById('prevBtn').style.display = index > 0 ? 'block' : 'none';
    document.getElementById('nextBtn').style.display = index < totalSlides - 1 ? 'block' : 'none';
    document.getElementById('startBtn').style.display = index === totalSlides - 1 ? 'block' : 'none';

    currentSlide = index;
}

function nextSlide() {
    if (currentSlide < totalSlides - 1) {
        showSlide(currentSlide + 1);
    }
}

function prevSlide() {
    if (currentSlide > 0) {
        showSlide(currentSlide - 1);
    }
}

// ============================================================
// اتمام
// ============================================================

function finishOnboarding() {
    // ===== ذخیره در localStorage =====
    localStorage.setItem('onboarding_done', 'true');

    // ===== انیمیشن خروج =====
    document.querySelector('.onboarding-container').style.opacity = '0';
    document.querySelector('.onboarding-container').style.transform = 'scale(0.95)';

    setTimeout(() => {
        window.location.href = '/';
    }, 300);
}

function skipOnboarding() {
    // ===== ذخیره =====
    localStorage.setItem('onboarding_done', 'true');

    // ===== رفتن به خانه =====
    window.location.href = '/';
}

// ============================================================
// کلیک روی نقطه‌ها
// ============================================================

document.querySelectorAll('.dot').forEach(dot => {
    dot.addEventListener('click', function() {
        const index = parseInt(this.dataset.dot);
        showSlide(index);
    });
});

// ============================================================
// کیبورد
// ============================================================

document.addEventListener('keydown', function(e) {
    if (e.key === 'ArrowRight') prevSlide();
    if (e.key === 'ArrowLeft') nextSlide();
    if (e.key === 'Escape') skipOnboarding();
});

// ============================================================
// صادر کردن
// ============================================================

window.nextSlide = nextSlide;
window.prevSlide = prevSlide;
window.skipOnboarding = skipOnboarding;
window.finishOnboarding = finishOnboarding;

// ============================================================
// راه‌اندازی
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    showSlide(0);
});