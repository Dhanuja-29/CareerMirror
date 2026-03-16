/* ─────────────────────────────────────────────
   CareerMirror  –  main.js
───────────────────────────────────────────── */

// ── Scroll reveal ──────────────────────────
const revealObserver = new IntersectionObserver(
  entries => entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add('visible');
      revealObserver.unobserve(e.target);
    }
  }),
  { threshold: 0.1 }
);
document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

// ── Nav shadow on scroll ──────────────────
window.addEventListener('scroll', () => {
  const nav = document.getElementById('mainNav');
  if (nav) {
    nav.style.boxShadow = window.scrollY > 30
      ? '0 4px 30px rgba(0,0,0,.08)' : 'none';
  }
});

// ── Auto-dismiss flash messages ───────────
document.querySelectorAll('.flash').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity .4s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 400);
  }, 3500);
});
