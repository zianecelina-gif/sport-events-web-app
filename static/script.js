/* ═══════════════════════════════════════════════════════════════════
   KALOS-main.js - Main JavaScript for Kalos website
   ═══════════════════════════════════════════════════════════════════ */

/* ── Page Loader ─────────────────────────────────────────────────── */
(function() {
    const loader = document.createElement('div');
    loader.id = 'kalos-loader';
    loader.innerHTML = `
        <div class="loader-inner">
            <div class="loader-logo">K</div>
            <div class="loader-bar"><div class="loader-fill"></div></div>
        </div>`;
    document.body.appendChild(loader);

    window.addEventListener('load', () => {
        loader.classList.add('fade-out');
        setTimeout(() => loader.remove(), 500);
    });
})();

document.addEventListener('DOMContentLoaded', () => {

    /* ── Header scroll ───────────────────────────────────────────── */
    const header = document.getElementById('main-header');
    if (header) {
        window.addEventListener('scroll', () => {
            header.classList.toggle('scrolled', window.scrollY > 20);
        }, { passive: true });
    }

    /* ── Mobile menu toggle ──────────────────────────────────────── */
    const mobileToggle = document.getElementById('mobile-toggle');
    const headerNav    = document.getElementById('header-nav');
    if (mobileToggle && headerNav) {
        mobileToggle.addEventListener('click', () => {
            headerNav.classList.toggle('open');
            const icon = mobileToggle.querySelector('i');
            icon.classList.toggle('fa-bars');
            icon.classList.toggle('fa-times');
        });
    }

    /* ── User dropdown ───────────────────────────────────────────── */
    const avatarBtn    = document.getElementById('user-avatar-btn');
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

    /* ── Flash messages auto-dismiss ────────────────────────────── */
    document.querySelectorAll('.flash-msg').forEach((msg, index) => {
        msg.addEventListener('click', () => dismissFlash(msg));
        setTimeout(() => dismissFlash(msg), 4500 + index * 500);
    });

    function dismissFlash(msg) {
        if (!msg.parentElement) return;
        msg.style.opacity = '0';
        msg.style.transform = 'translateX(80px)';
        msg.style.transition = 'all 0.3s ease';
        setTimeout(() => msg.remove(), 320);
    }

    /* ── Hero rotating words ─────────────────────────────────────── */
    const rotatingContainer = document.querySelector('.rotating-word');
    if (rotatingContainer) {
        const words = rotatingContainer.querySelectorAll('span');
        if (words.length > 0) {
            let currentIndex = 0;

            words.forEach((word, i) => {
                word.style.cssText = `
                    position: absolute;
                    width: 100%;
                    transition: all 0.55s cubic-bezier(0.4, 0, 0.2, 1);
                `;
                if (i !== 0) {
                    word.style.opacity = '0';
                    word.style.transform = 'translateY(24px)';
                }
            });
            rotatingContainer.style.cssText = 'position: relative; display: inline-block;';

            setInterval(() => {
                words[currentIndex].style.opacity = '0';
                words[currentIndex].style.transform = 'translateY(-24px)';
                currentIndex = (currentIndex + 1) % words.length;
                words[currentIndex].style.opacity = '1';
                words[currentIndex].style.transform = 'translateY(0)';
            }, 2500);
        }
    }

    /* ── Animated counters ───────────────────────────────────────── */
    function animateCounter(el) {
        const target   = parseInt(el.getAttribute('data-target'));
        const duration = 1800;
        const startTime = performance.now();

        function easeOut(t) { return 1 - Math.pow(1 - t, 3); }

        function tick(now) {
            const elapsed  = now - startTime;
            const progress = Math.min(elapsed / duration, 1);
            el.textContent = Math.floor(easeOut(progress) * target);
            if (progress < 1) requestAnimationFrame(tick);
            else el.textContent = target;
        }
        requestAnimationFrame(tick);
    }

    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                counterObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.3 });

    document.querySelectorAll('.stat-number[data-target]').forEach(el => {
        counterObserver.observe(el);
    });

    /* ── Scroll reveal animations ────────────────────────────────── */
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, i) => {
            if (entry.isIntersecting) {
                const delay = entry.target.dataset.delay || 0;
                setTimeout(() => {
                    entry.target.classList.add('revealed');
                }, delay);
                revealObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

    // Stagger cards in grids
    document.querySelectorAll('.feature-card, .event-card').forEach((el, i) => {
        el.classList.add('reveal-item');
        el.dataset.delay = (i % 3) * 80;
        revealObserver.observe(el);
    });

    document.querySelectorAll('.stat-item, .step-item, .glass-card').forEach(el => {
        if (!el.classList.contains('reveal-item')) {
            el.classList.add('reveal-item');
            revealObserver.observe(el);
        }
    });

    /* ── Hero text entrance animation ───────────────────────────── */
    const heroText = document.querySelector('.hero-text');
    if (heroText) {
        heroText.style.opacity = '0';
        heroText.style.transform = 'translateY(32px)';
        heroText.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
        requestAnimationFrame(() => {
            heroText.style.opacity = '1';
            heroText.style.transform = 'translateY(0)';
        });
    }

    const heroMockup = document.querySelector('.hero-mockup, .hero-image');
    if (heroMockup) {
        heroMockup.style.opacity = '0';
        heroMockup.style.transform = 'translateY(24px)';
        heroMockup.style.transition = 'opacity 0.8s ease 0.2s, transform 0.8s ease 0.2s';
        requestAnimationFrame(() => {
            heroMockup.style.opacity = '1';
            heroMockup.style.transform = 'translateY(0)';
        });
    }

    /* ── 3D tilt on event cards ──────────────────────────────────── */
    document.querySelectorAll('.event-card').forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect   = card.getBoundingClientRect();
            const x      = (e.clientX - rect.left) / rect.width  - 0.5;
            const y      = (e.clientY - rect.top)  / rect.height - 0.5;
            const tiltX  = y * -6;
            const tiltY  = x *  6;
            card.style.transform = `translateY(-8px) rotateX(${tiltX}deg) rotateY(${tiltY}deg)`;
            card.style.transition = 'transform 0.1s ease';
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0) rotateX(0) rotateY(0)';
            card.style.transition = 'all 0.4s cubic-bezier(0.4,0,0.2,1)';
        });
    });

    /* ── Scroll-to-top button ────────────────────────────────────── */
    const scrollBtn = document.createElement('button');
    scrollBtn.id = 'scroll-top';
    scrollBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    scrollBtn.setAttribute('aria-label', 'Retour en haut');
    scrollBtn.title = 'Retour en haut';
    document.body.appendChild(scrollBtn);

    window.addEventListener('scroll', () => {
        scrollBtn.classList.toggle('visible', window.scrollY > 400);
    }, { passive: true });

    scrollBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    /* ── "Nouveau" badge on recent events ───────────────────────── */
    document.querySelectorAll('.event-card').forEach(card => {
        const dateEl = card.querySelector('.event-card-meta span');
        if (!dateEl) return;
        const text = dateEl.textContent;
        const match = text.match(/(\d{2})\/(\d{2})\/(\d{4})/);
        if (!match) return;
        const eventDate = new Date(`${match[3]}-${match[2]}-${match[1]}`);
        const now = new Date();
        const diffDays = (eventDate - now) / (1000 * 60 * 60 * 24);
        if (diffDays >= 0 && diffDays <= 7) {
            const badge = document.createElement('span');
            badge.className = 'new-badge';
            badge.textContent = 'Nouveau';
            const img = card.querySelector('.event-card-image');
            if (img) img.appendChild(badge);
        }
    });

    /* ── Smooth page transitions ─────────────────────────────────── */
    document.querySelectorAll('a[href]').forEach(link => {
        if (link.href.startsWith(window.location.origin) &&
            !link.href.includes('#') &&
            !link.target &&
            link.getAttribute('href') !== '#') {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                document.body.style.opacity = '0';
                document.body.style.transition = 'opacity 0.2s ease';
                setTimeout(() => { window.location.href = link.href; }, 200);
            });
        }
    });

    // Fade in on load
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.3s ease';
    requestAnimationFrame(() => { document.body.style.opacity = '1'; });

});