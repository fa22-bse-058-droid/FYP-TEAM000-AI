/* CareerAI — main.js
   Vanilla JS (ES2022): navbar scroll, mobile menu,
   GSAP scroll animations, password toggles, active nav
*/

// Mark document as JS-enabled so CSS can conditionally hide animated elements
document.documentElement.classList.add('js-enabled');

(function () {
  'use strict';

  /* ── Navbar scroll effect ── */
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    const onScroll = () => {
      if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* ── Mobile hamburger menu ── */
  const hamburger = document.querySelector('.hamburger');
  const mobileMenu = document.querySelector('.mobile-menu');
  if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', () => {
      const isOpen = hamburger.classList.toggle('open');
      mobileMenu.classList.toggle('open', isOpen);
      hamburger.setAttribute('aria-expanded', String(isOpen));
      document.body.style.overflow = isOpen ? 'hidden' : '';
    });

    // Close on link click
    mobileMenu.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        hamburger.classList.remove('open');
        mobileMenu.classList.remove('open');
        hamburger.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
      });
    });
  }

  /* ── Active nav link highlight ── */
  const currentPath = window.location.pathname;
  document.querySelectorAll('.navbar-links a, .mobile-menu a').forEach((link) => {
    const href = link.getAttribute('href');
    if (href && href !== '/' && currentPath.startsWith(href)) {
      link.classList.add('active');
    } else if (href === '/' && currentPath === '/') {
      link.classList.add('active');
    }
  });

  /* ── Password show/hide toggle ── */
  document.querySelectorAll('.field-toggle').forEach((btn) => {
    btn.addEventListener('click', () => {
      const wrapper = btn.closest('.field-wrapper');
      if (!wrapper) return;
      const input = wrapper.querySelector('input');
      if (!input) return;
      const isPassword = input.type === 'password';
      input.type = isPassword ? 'text' : 'password';
      // Swap icon
      const eyeOpen = btn.querySelector('.eye-open');
      const eyeClosed = btn.querySelector('.eye-closed');
      if (eyeOpen) eyeOpen.style.display = isPassword ? 'none' : 'block';
      if (eyeClosed) eyeClosed.style.display = isPassword ? 'block' : 'none';
    });
  });

  /* ── Upload zone drag events ── */
  const uploadZone = document.querySelector('.upload-zone');
  if (uploadZone) {
    ['dragenter', 'dragover'].forEach((evt) => {
      uploadZone.addEventListener(evt, (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
      });
    });
    ['dragleave', 'drop'].forEach((evt) => {
      uploadZone.addEventListener(evt, (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
      });
    });

    // Show selected filename
    const fileInput = uploadZone.querySelector('input[type="file"]');
    const fileLabel = uploadZone.querySelector('.upload-file-label');
    if (fileInput && fileLabel) {
      fileInput.addEventListener('change', () => {
        const file = fileInput.files && fileInput.files[0];
        fileLabel.textContent = file ? file.name : '';
      });
    }
  }

  /* ── Smooth scroll for anchor links ── */
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', (e) => {
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  /* ── GSAP animations (loaded via CDN in base.html) ── */
  function initGSAP() {
    if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') return;

    gsap.registerPlugin(ScrollTrigger);

    // Hero content entrance
    const heroContent = document.querySelector('.hero-content');
    if (heroContent) {
      const children = heroContent.children;
      gsap.from(children, {
        opacity: 0,
        y: 30,
        duration: 0.8,
        stagger: 0.12,
        ease: 'power3.out',
        delay: 0.1,
      });
    }

    // Generic scroll-triggered sections
    gsap.utils.toArray('.animate-on-scroll').forEach((el) => {
      gsap.to(el, {
        opacity: 1,
        y: 0,
        duration: 0.7,
        ease: 'power3.out',
        scrollTrigger: {
          trigger: el,
          start: 'top 85%',
          once: true,
        },
      });
    });

    // Feature cards stagger
    gsap.utils.toArray('.features-grid .feature-card').forEach((card, i) => {
      gsap.fromTo(card,
        { opacity: 0, y: 24 },
        {
          opacity: 1,
          y: 0,
          duration: 0.6,
          delay: i * 0.1,
          ease: 'power3.out',
          overwrite: true,
          scrollTrigger: {
            trigger: card,
            start: 'top 88%',
            once: true,
          },
        }
      );
    });

    // Stats cards stagger
    gsap.utils.toArray('.stat-card').forEach((card, i) => {
      gsap.fromTo(card,
        { opacity: 0, y: 20 },
        {
          opacity: 1,
          y: 0,
          duration: 0.5,
          delay: i * 0.08,
          ease: 'power3.out',
          overwrite: true,
          scrollTrigger: {
            trigger: card,
            start: 'top 90%',
            once: true,
          },
        }
      );
    });

    // How-it-works steps
    gsap.utils.toArray('.howto-step').forEach((step, i) => {
      gsap.fromTo(step,
        { opacity: 0, y: 20 },
        {
          opacity: 1,
          y: 0,
          duration: 0.6,
          delay: i * 0.15,
          ease: 'power3.out',
          overwrite: true,
          scrollTrigger: {
            trigger: step,
            start: 'top 88%',
            once: true,
          },
        }
      );
    });
  }

  // Delay allows inline GSAP bundle (served from static) to finish evaluating before we register plugins
  const GSAP_INIT_DELAY = 100;
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => setTimeout(initGSAP, GSAP_INIT_DELAY));
  } else {
    setTimeout(initGSAP, GSAP_INIT_DELAY);
  }
})();
