/**
 * AchievementNotification - Sistema de notificações de conquistas
 * Exibe notificações visuais quando conquistas são desbloqueadas
 */
class AchievementNotification {
    constructor() {
        this.queue = [];
        this.isShowing = false;
        this.currentNotification = null;
    }

    /**
     * Exibe uma notificação de conquista
     * @param {Object} achievement - Dados da conquista desbloqueada
     */
    show(achievement) {
        this.queue.push(achievement);
        if (!this.isShowing) {
            this.showNext();
        }
    }

    /**
     * Exibe a próxima notificação da fila
     */
    showNext() {
        if (this.queue.length === 0) {
            this.isShowing = false;
            return;
        }

        this.isShowing = true;
        const achievement = this.queue.shift();
        this.displayNotification(achievement);
    }

    /**
     * Cria e exibe o elemento de notificação
     * @param {Object} achievement - Dados da conquista
     */
    displayNotification(achievement) {
        // Criar elemento de notificação
        const notification = document.createElement('div');
        notification.className = 'achievement-notification';
        notification.innerHTML = `
            <div class="achievement-notification-content">
                <div class="achievement-notification-icon">${achievement.icon}</div>
                <div class="achievement-notification-text">
                    <div class="achievement-notification-title">Conquista Desbloqueada!</div>
                    <div class="achievement-notification-name">${achievement.name}</div>
                    <div class="achievement-notification-description">${achievement.description}</div>
                </div>
            </div>
        `;

        // Adicionar ao container
        const container = document.getElementById('achievement-toast-container');
        if (container) {
            container.appendChild(notification);
            this.currentNotification = notification;

            // Animar entrada
            setTimeout(() => {
                notification.classList.add('show');
            }, 100);

            // Auto-dismiss após 5 segundos
            setTimeout(() => {
                this.hideNotification(notification);
            }, 5000);
        }
    }

    /**
     * Esconde e remove a notificação
     * @param {HTMLElement} notification - Elemento da notificação
     */
    hideNotification(notification) {
        notification.classList.remove('show');
        notification.classList.add('hide');

        // Remover do DOM após animação
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }

            // Mostrar próxima notificação após delay
            setTimeout(() => {
                this.showNext();
            }, 500);
        }, 300);
    }

    /**
     * Verifica novas conquistas e exibe notificações
     */
    async checkNewAchievements() {
        try {
            const response = await fetch('/api/achievements/check', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: 'default'
                }),
            });

            if (response.ok) {
                const data = await response.json();

                if (data.success && data.newly_unlocked && data.newly_unlocked.length > 0) {
                    data.newly_unlocked.forEach(achievement => {
                        this.show(achievement);
                    });

                    // Atualizar contador de badges
                    if (window.badgeCounter) {
                        window.badgeCounter.forceUpdate();
                    }
                }
            }
        } catch (error) {
            console.error('Erro ao verificar conquistas:', error);
        }
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.achievementNotifier = new AchievementNotification();
});
