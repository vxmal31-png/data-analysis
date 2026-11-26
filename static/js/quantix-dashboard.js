(function () {
  'use strict';
  const root = document.documentElement;
  const sidebar = document.getElementById('sidebar');
  const collapse = document.getElementById('collapseSidebar');
  const menu = document.getElementById('menuButton');
  const overlay = document.getElementById('sidebarOverlay');
  const theme = document.getElementById('themeToggle');

  if (collapse && sidebar) collapse.addEventListener('click', () => sidebar.classList.toggle('collapsed'));
  if (menu && sidebar) menu.addEventListener('click', () => { sidebar.classList.add('mobile-open'); if (overlay) overlay.classList.add('show'); });
  if (overlay && sidebar) overlay.addEventListener('click', () => { sidebar.classList.remove('mobile-open'); overlay.classList.remove('show'); });
  if (theme) theme.addEventListener('click', () => { root.dataset.theme = root.dataset.theme === 'light' ? 'dark' : 'light'; });

  // The Quantix landing dashboard intentionally uses illustrative sample figures,
  // matching the supplied reference image rather than representing live revenue data.
  const revenueCanvas = document.getElementById('quantixRevenueChart');
  if (revenueCanvas && window.Chart) {
    new Chart(revenueCanvas, {
      type: 'doughnut',
      data: {
        labels: ['API Access', 'Subscription', 'Consulting'],
        datasets: [{ data: [42, 35, 23], backgroundColor: ['#4bcfc5', '#4c8fe8', '#e5c36c'], borderColor: ['#19162b', '#19162b', '#19162b'], borderWidth: 2, hoverOffset: 5 }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '62%',
        plugins: { legend: { display: false }, tooltip: { backgroundColor: '#211d36', titleColor: '#fff', bodyColor: '#d9d3eb', borderColor: 'rgba(174,156,223,.25)', borderWidth: 1 } }
      }
    });
  }

  // Search filters visible navigation items without requiring a backend endpoint.
  const search = document.getElementById('globalSearch');
  if (search && sidebar) search.addEventListener('input', () => {
    const term = search.value.trim().toLowerCase();
    sidebar.querySelectorAll('.side-nav a').forEach(link => {
      link.style.opacity = !term || link.textContent.toLowerCase().includes(term) ? '1' : '.35';
    });
  });
})();
