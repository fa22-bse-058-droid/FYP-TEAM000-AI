(function () {
  'use strict';

  const navbar = document.querySelector('.navbar');
  const hamburger = document.querySelector('.hamburger');
  const mobileMenu = document.querySelector('.mobile-menu');
  const mobileClose = document.querySelector('.mobile-menu-close');

  const setNavbarState = () => {
    if (!navbar) return;
    navbar.classList.toggle('scrolled', window.scrollY > 40);
  };

  const closeMenu = () => {
    if (!hamburger || !mobileMenu) return;
    hamburger.classList.remove('open');
    hamburger.setAttribute('aria-expanded', 'false');
    mobileMenu.classList.remove('open');
    document.body.classList.remove('menu-open');
  };

  const openMenu = () => {
    if (!hamburger || !mobileMenu) return;
    hamburger.classList.add('open');
    hamburger.setAttribute('aria-expanded', 'true');
    mobileMenu.classList.add('open');
    document.body.classList.add('menu-open');
  };

  setNavbarState();
  window.addEventListener('scroll', setNavbarState, { passive: true });

  if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', () => {
      const isOpen = mobileMenu.classList.contains('open');
      if (isOpen) closeMenu(); else openMenu();
    });
    mobileMenu.querySelectorAll('a').forEach((a) => a.addEventListener('click', closeMenu));
    if (mobileClose) mobileClose.addEventListener('click', closeMenu);
    window.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeMenu(); });
  }

  document.querySelectorAll('.field-toggle').forEach((button) => {
    button.addEventListener('click', () => {
      const wrap = button.closest('.field-wrapper');
      const input = wrap ? wrap.querySelector('input') : null;
      if (!input) return;
      const show = input.type === 'password';
      input.type = show ? 'text' : 'password';
      button.textContent = show ? 'Hide' : 'Show';
      button.setAttribute('aria-label', show ? 'Hide password' : 'Show password');
    });
  });

  const currentPath = window.location.pathname;
  document.querySelectorAll('.navbar-links a, .mobile-menu a').forEach((link) => {
    const href = link.getAttribute('href');
    if (!href) return;
    const exact = href === '/' && currentPath === '/';
    const starts = href !== '/' && currentPath.startsWith(href);
    if (exact || starts) link.classList.add('active');
  });

  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener('click', (e) => {
      const target = document.querySelector(link.getAttribute('href'));
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  const uploadZone = document.querySelector('.upload-zone');
  if (uploadZone) {
    const input = uploadZone.querySelector('input[type="file"]');
    ['dragenter', 'dragover'].forEach((evt) => uploadZone.addEventListener(evt, (e) => {
      e.preventDefault();
      uploadZone.classList.add('dragover');
    }));
    ['dragleave', 'drop'].forEach((evt) => uploadZone.addEventListener(evt, (e) => {
      e.preventDefault();
      uploadZone.classList.remove('dragover');
    }));
    uploadZone.addEventListener('drop', (e) => {
      const droppedFiles = e.dataTransfer && e.dataTransfer.files ? e.dataTransfer.files : null;
      if (!input || !droppedFiles || !droppedFiles.length) return;
      input.files = droppedFiles;
      input.dispatchEvent(new Event('change', { bubbles: true }));
    });
    if (input) {
      input.addEventListener('change', () => {
        const label = document.querySelector('.upload-file-label');
        if (label) label.textContent = input.files && input.files[0] ? input.files[0].name : '';
      });
    }
  }

  const initCountUp = () => {
    const animateStat = (el) => {
      const target = parseFloat(el.dataset.target || el.dataset.count);
      if (Number.isNaN(target)) return;
      const unit = el.dataset.unit || '';

      if (typeof ScrollTrigger !== 'undefined' && typeof gsap !== 'undefined') {
        ScrollTrigger.create({
          trigger: el,
          start: 'top 85%',
          once: true,
          onEnter: () => {
            gsap.fromTo({ val: 0 }, { val: 0 }, { val: target, duration: 1.8, ease: 'power2.out', onUpdate() {
              const value = Math.round(this.targets()[0].val);
              el.textContent = `${value}${unit}`;
            } });
          },
        });
        return;
      }

      const duration = 1800;
      let started = false;
      const trigger = () => {
        if (started) return;
        started = true;
        const startTime = performance.now();
        const frame = (now) => {
          const p = Math.min((now - startTime) / duration, 1);
          el.textContent = `${Math.round(target * p)}${unit}`;
          if (p < 1) requestAnimationFrame(frame);
        };
        requestAnimationFrame(frame);
      };
      if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              trigger();
              observer.disconnect();
            }
          });
        }, { threshold: 0.25 });
        observer.observe(el);
      } else {
        trigger();
      }
    };

    document.querySelectorAll('.count-up, .stat-number').forEach(animateStat);
  };

  const markHighProgressBars = () => {
    document.querySelectorAll('.bar span, .mini-bars span, .bench-bar span').forEach((el) => {
      const width = parseFloat((el.style.width || '').replace('%', ''));
      if (!Number.isNaN(width) && width >= 80) el.classList.add('high-progress');
    });
  };

  const initCardHoverEffects = () => {
    if (typeof gsap === 'undefined') return;
    document.querySelectorAll('.card, .module-cell').forEach((card) => {
      card.addEventListener('mouseenter', () => gsap.to(card, { y: -4, duration: 0.25, ease: 'power2.out' }));
      card.addEventListener('mouseleave', () => gsap.to(card, { y: 0, duration: 0.25, ease: 'power2.out' }));
    });
  };

  const initGSAP = () => {
    if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') return;
    gsap.registerPlugin(ScrollTrigger);

    gsap.fromTo('.hero-glow',
      { opacity: 0.3, scale: 0.95 },
      { opacity: 0.6, scale: 1.05, duration: 4, ease: 'sine.inOut', yoyo: true, repeat: -1 });

    gsap.fromTo('.hero-content > *',
      { opacity: 0, y: 28 },
      { opacity: 1, y: 0, duration: 0.9, ease: 'power2.out', stagger: 0.18, delay: 0.2 });

    gsap.utils.toArray('.animate-in').forEach((el) => {
      gsap.fromTo(el,
        { opacity: 0, y: 40 },
        { opacity: 1, y: 0, duration: 0.8, ease: 'power2.out', scrollTrigger: { trigger: el, start: 'top 88%' } });
    });

    gsap.utils.toArray('.stagger-children').forEach((container) => {
      const children = Array.from(container.children);
      if (!children.length) return;
      gsap.fromTo(children,
        { opacity: 0, y: 24 },
        { opacity: 1, y: 0, duration: 0.6, ease: 'power2.out', stagger: 0.09, scrollTrigger: { trigger: container, start: 'top 82%' } });
    });

  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      markHighProgressBars();
      initGSAP();
      initCountUp();
      initCardHoverEffects();
    });
  } else {
    markHighProgressBars();
    initGSAP();
    initCountUp();
    initCardHoverEffects();
  }
})();
