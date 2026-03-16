/* ═══════════════════════════════════════════════════════════════════
   KALOS — Main JavaScript
   ═══════════════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

    // ─── Header scroll effect ────────────────────────────────────
    const header = document.getElementById('main-header');
    if (header) {
        window.addEventListener('scroll', () => {
            header.classList.toggle('scrolled', window.scrollY > 20);
        });
    }

    // ─── Mobile menu toggle ──────────────────────────────────────
    const mobileToggle = document.getElementById('mobile-toggle');
    const headerNav = document.getElementById('header-nav');
    if (mobileToggle && headerNav) {
        mobileToggle.addEventListener('click', () => {
            headerNav.classList.toggle('open');
            const icon = mobileToggle.querySelector('i');
            icon.classList.toggle('fa-bars');
            icon.classList.toggle('fa-times');
        });
    }

    // ─── User dropdown ───────────────────────────────────────────
    const avatarBtn = document.getElementById('user-avatar-btn');
    const dropdownMenu = document.getElementById('dropdown-menu');
    if (avatarBtn && dropdownMenu) {
        avatarBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdownMenu.classList.toggle('active');
        });
        document.addEventListener('click', (e) => {
            if (!dropdownMenu.contains(e.target) && e.target !== avatarBtn) {
                dropdownMenu.classList.remove('active');
            }
        });
    }

    // ─── Flash message auto-dismiss ──────────────────────────────
    const flashMessages = document.querySelectorAll('.flash-msg');
    flashMessages.forEach((msg, index) => {
        // Click to dismiss
        msg.addEventListener('click', () => {
            msg.style.opacity = '0';
            msg.style.transform = 'translateX(100px)';
            setTimeout(() => msg.remove(), 300);
        });
        // Auto-dismiss after 4s
        setTimeout(() => {
            if (msg.parentElement) {
                msg.style.opacity = '0';
                msg.style.transform = 'translateX(100px)';
                setTimeout(() => msg.remove(), 300);
            }
        }, 4000 + (index * 500));
    });

    // ─── Animate elements on scroll ──────────────────────────────
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.glass-card, .feature-card, .stat-item').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });

    // ─── Hero rotating words ─────────────────────────────────────
    const rotatingContainer = document.querySelector('.rotating-word');
    if (rotatingContainer) {
        const words = rotatingContainer.querySelectorAll('span');
        if (words.length > 0) {
            let currentIndex = 0;
            setInterval(() => {
                words[currentIndex].style.opacity = '0';
                words[currentIndex].style.transform = 'translateY(-20px)';
                currentIndex = (currentIndex + 1) % words.length;
                words[currentIndex].style.opacity = '1';
                words[currentIndex].style.transform = 'translateY(0)';
            }, 2500);

            words.forEach((word, i) => {
                word.style.position = 'absolute';
                word.style.transition = 'all 0.5s ease';
                word.style.width = '100%';
                if (i !== 0) {
                    word.style.opacity = '0';
                    word.style.transform = 'translateY(20px)';
                }
            });
            rotatingContainer.style.position = 'relative';
            rotatingContainer.style.display = 'inline-block';
        }
    }

    // ─── Hero image carousel ─────────────────────────────────────
    const heroImages = document.querySelectorAll('.hero-carousel-img');
    if (heroImages.length > 1) {
        let imgIndex = 0;
        setInterval(() => {
            heroImages[imgIndex].style.opacity = '0';
            imgIndex = (imgIndex + 1) % heroImages.length;
            heroImages[imgIndex].style.opacity = '1';
        }, 3000);
    }

    // ─── Animated counter ────────────────────────────────────────
    document.querySelectorAll('.stat-number[data-target]').forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target'));
        const duration = 2000;
        const step = target / (duration / 16);
        let current = 0;

        const updateCounter = () => {
            current += step;
            if (current < target) {
                counter.textContent = Math.floor(current);
                requestAnimationFrame(updateCounter);
            } else {
                counter.textContent = target;
            }
        };

        const counterObserver = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                updateCounter();
                counterObserver.unobserve(counter);
            }
        });
        counterObserver.observe(counter);
    });
});