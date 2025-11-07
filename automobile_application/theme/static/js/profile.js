// Чекаємо, поки вся сторінка завантажиться
document.addEventListener('DOMContentLoaded', () => {
    
    // Знаходимо кнопку (аватар) та саме меню за їх ID
    const menuButton = document.getElementById('userMenuButton');
    const userMenu = document.getElementById('userMenu');

    // Перевіряємо, чи обидва елементи існують на сторінці
    if (menuButton && userMenu) {
        
        // 1. Обробник кліку на кнопку (аватар)
        menuButton.addEventListener('click', (event) => {
            // Зупиняємо "спливання" події, щоб клік не передався документу
            event.stopPropagation(); 
            
            // Перемикаємо клас 'hidden', щоб показати або приховати меню
            userMenu.classList.toggle('hidden');
            
            // Оновлюємо атрибут aria-expanded для доступності (для скрін-рідерів)
            const isExpanded = !userMenu.classList.contains('hidden');
            menuButton.setAttribute('aria-expanded', isExpanded.toString());
        });

        // 2. Обробник кліку на будь-яке місце в документі
        document.addEventListener('click', () => {
            // Якщо меню *не* приховане, ми його приховуємо
            if (!userMenu.classList.contains('hidden')) {
                userMenu.classList.add('hidden');
                menuButton.setAttribute('aria-expanded', 'false');
            }
        });

        // 3. Обробник кліку на саме меню
        // (Потрібно, щоб клік по посиланню "Профіль" не закривав меню)
        userMenu.addEventListener('click', (event) => {
            // Зупиняємо "спливання" події, щоб документ не отримав цей клік
            event.stopPropagation();
        });
    }
});