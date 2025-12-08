// Funções gerais para a aplicação
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips do Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Gerenciamento de tema escuro/claro
    initThemeToggle();
});

function initThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');

    if (!themeToggle || !themeIcon) return;

    // Carregar tema salvo ou usar preferência do sistema
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const currentTheme = savedTheme || (prefersDark ? 'dark' : 'light');

    // Aplicar tema inicial
    setTheme(currentTheme);

    // Listener para alternância de tema
    themeToggle.addEventListener('click', function() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
        localStorage.setItem('theme', newTheme);
    });

    // Listener para mudanças na preferência do sistema
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
        if (!localStorage.getItem('theme')) {
            setTheme(e.matches ? 'dark' : 'light');
        }
    });
}

function setTheme(theme) {
    const themeIcon = document.getElementById('themeIcon');

    document.documentElement.setAttribute('data-theme', theme);

    if (themeIcon) {
        themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
    }

    // Atualizar tema do CodeMirror se existir
    if (typeof updateEditorTheme === 'function') {
        updateEditorTheme(theme);
    }
}

/**
 * Exibe um toast de notificação para uma nova conquista desbloqueada.
 * @param {Object} achievement - Objeto de conquista {name, icon, description}.
 */
function showAchievementToast(achievement) {
    const container = document.getElementById('achievement-toast-container');
    if (!container) return;

    const toastEl = document.createElement('div');
    toastEl.className = 'toast align-items-center text-white bg-success border-0 mb-2';
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');

    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body d-flex align-items-center">
                <span class="fs-2 me-3">${achievement.icon}</span>
                <div>
                    <h6 class="mb-0 fw-bold">Conquista Desbloqueada!</h6>
                    <p class="mb-0 small">${achievement.name}</p>
                </div>
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    container.appendChild(toastEl);

    const toast = new bootstrap.Toast(toastEl, { delay: 5000 });
    toast.show();

    // Remover do DOM após fechar
    toastEl.addEventListener('hidden.bs.toast', () => {
        toastEl.remove();
    });
}

/**
 * Processa novas conquistas retornadas pela API e exibe toasts.
 * @param {Array} newAchievements - Lista de novas conquistas.
 */
function handleNewAchievements(newAchievements) {
    if (newAchievements && newAchievements.length > 0) {
        newAchievements.forEach((ach, index) => {
            // Pequeno delay entre notificações múltiplas
            setTimeout(() => {
                showAchievementToast(ach);
            }, index * 1000);
        });
    }
}
