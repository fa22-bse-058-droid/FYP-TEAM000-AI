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
      if (!input || !e.dataTransfer || !e.dataTransfer.files || !e.dataTransfer.files.length) return;
      input.files = e.dataTransfer.files;
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
    document.querySelectorAll('.count-up').forEach((el) => {
      const end = Number(el.dataset.count || '0');
      if (Number.isNaN(end)) return;
      const duration = 1200;
      const trigger = () => {
        const startTime = performance.now();
        const frame = (now) => {
          const p = Math.min((now - startTime) / duration, 1);
          el.textContent = String(Math.floor(end * p));
          if (p < 1) requestAnimationFrame(frame);
        };
        requestAnimationFrame(frame);
      };
      if (typeof ScrollTrigger !== 'undefined' && typeof gsap !== 'undefined') {
        ScrollTrigger.create({ trigger: el, start: 'top 85%', once: true, onEnter: trigger });
      } else {
        trigger();
      }
    });
  };

  const initGSAP = () => {
    if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') return;
    gsap.registerPlugin(ScrollTrigger);

    const heroChildren = document.querySelectorAll('.hero-content > *');
    if (heroChildren.length) {
      gsap.fromTo(heroChildren, { opacity: 0, y: 30 }, {
        opacity: 1,
        y: 0,
        duration: 0.7,
        ease: 'power2.out',
        stagger: 0.15,
        delay: 0.3,
      });
    }

    gsap.utils.toArray('.animate-in, .animate-on-scroll').forEach((el) => {
      gsap.fromTo(el, { opacity: 0, y: 30 }, {
        opacity: 1,
        y: 0,
        duration: 0.7,
        ease: 'power2.out',
        scrollTrigger: { trigger: el, start: 'top 85%', once: true },
      });
    });

    gsap.utils.toArray('.stagger-children').forEach((container) => {
      const children = Array.from(container.children);
      if (!children.length) return;
      gsap.fromTo(children, { opacity: 0, y: 30 }, {
        opacity: 1,
        y: 0,
        duration: 0.7,
        ease: 'power2.out',
        stagger: 0.08,
        scrollTrigger: { trigger: container, start: 'top 85%', once: true },
      });
    });

    initCountUp();
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initGSAP);
  } else {
    initGSAP();
  }
})();
