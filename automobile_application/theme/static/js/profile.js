document.addEventListener('DOMContentLoaded', () => {
    const menuButton = document.getElementById('userMenuButton');
    const userMenu = document.getElementById('userMenu');

    if (menuButton && userMenu) {
        menuButton.addEventListener('click', (event) => {
            event.stopPropagation();
            userMenu.classList.toggle('hidden');
            const isExpanded = !userMenu.classList.contains('hidden');
            menuButton.setAttribute('aria-expanded', isExpanded.toString());
        });

        document.addEventListener('click', () => {
            if (!userMenu.classList.contains('hidden')) {
                userMenu.classList.add('hidden');
                menuButton.setAttribute('aria-expanded', 'false');
            }
        });

        userMenu.addEventListener('click', (event) => {
            event.stopPropagation();
        });
    }
});