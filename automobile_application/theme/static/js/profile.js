<script>
  (function () {
    const btn  = document.getElementById('userMenuButton');
    const menu = document.getElementById('userMenu');
    if (!btn || !menu) return;

    function closeMenu() {
      menu.classList.add('hidden');
      btn.setAttribute('aria-expanded', 'false');
    }
    function toggleMenu(e) {
      e.stopPropagation();
      menu.classList.toggle('hidden');
      btn.setAttribute('aria-expanded', menu.classList.contains('hidden') ? 'false' : 'true');
    }

    btn.addEventListener('click', toggleMenu);
    document.addEventListener('click', () => { if (!menu.classList.contains('hidden')) closeMenu(); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeMenu(); });
  })();
</script>
