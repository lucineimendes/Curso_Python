/**
 * BadgeCounter - Gerencia o contador de badges na navegação
 * Exibe o número de conquistas desbloqueadas e tooltip com conquistas recentes
 */
class BadgeCounter {
    constructor() {
        this.badgeElement = null;
        this.tooltipElement = null;
        this.unlockedCount = 0;
        this.recentAchievements = [];
        this.init();
    }

    /**
     * Inicializa o contador de badges
     */
    init() {
        this.createBadgeElement();
        this.updateCount();

        // Atualizar a cada 30 segundos
        setInterval(() => this.updateCount(), 30000);
    }

    /**
     * Cria o elemento do contador de badges na navegação
     */
    createBadgeElement() {
        const achievementsLink = document.querySelector('a[href*="achievements"]');
        if (!achievementsLink) {
            console.warn('Link de conquistas não encontrado na navegação');
            return;
        }

        // Adicionar badge counter ao link existente
        const badge = document.createElement('span');
        badge.className = 'badge bg-primary ms-1';
        badge.id = 'badge-counter';
        badge.textContent = '0';
        badge.style.cursor = 'pointer';

        achievementsLink.appendChild(badge);
        this.badgeElement = badge;

        // Criar tooltip
        this.createTooltip();

        // Event listeners
        badge.addEventListener('mouseenter', () => this.showTooltip());
        badge.addEventListener('mouseleave', () => this.hideTooltip());
    }

    /**
     * Cria o elemento de tooltip
     */
    createTooltip() {
        const tooltip = document.createElement('div');
        tooltip.className = 'badge-tooltip';
        tooltip.id = 'badge-tooltip';
        tooltip.style.display = 'none';
        document.body.appendChild(tooltip);
        this.tooltipElement = tooltip;
    }

    /**
     * Busca e atualiza a contagem de conquistas desbloqueadas
     */
    async updateCount() {
        try {
            const response = await fetch('/api/achievements/unlocked?user_id=default');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.success && data.unlocked) {
                this.unlockedCount = data.unlocked.length;
                this.recentAchievements = data.unlocked
                    .sort((a, b) => new Date(b.unlocked_at) - new Date(a.unlocked_at))
                    .slice(0, 3);

                this.render();
            }
        } catch (error) {
            console.error('Erro ao buscar conquistas:', error);
        }
    }

    /**
     * Renderiza o contador com a contagem atual
     */
    render() {
        if (this.badgeElement) {
            this.badgeElement.textContent = this.unlockedCount;

            // Adicionar animação de pulso quando houver conquistas
            if (this.unlockedCount > 0) {
                this.badgeElement.classList.add('pulse');
                setTimeout(() => {
                    this.badgeElement.classList.remove('pulse');
                }, 1000);
            }
        }
    }

    /**
     * Exibe tooltip com conquistas recentes
     */
    showTooltip() {
        if (!this.tooltipElement || this.unlockedCount === 0) {
            return;
        }

        let tooltipContent = '<div class="tooltip-header">Conquistas Recentes</div>';

        if (this.recentAchievements.length === 0) {
            tooltipContent += '<div class="tooltip-empty">Nenhuma conquista ainda. Comece a aprender!</div>';
        } else {
            tooltipContent += '<div class="tooltip-achievements">';
            this.recentAchievements.forEach(achievement => {
                const date = new Date(achievement.unlocked_at);
                const formattedDate = date.toLocaleDateString('pt-BR', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric'
                });

                tooltipContent += `
                    <div class="tooltip-achievement">
                        <span class="tooltip-icon">${achievement.icon}</span>
                        <div class="tooltip-info">
                            <div class="tooltip-name">${achievement.name}</div>
                            <div class="tooltip-date">${formattedDate}</div>
                        </div>
                    </div>
                `;
            });
            tooltipContent += '</div>';
        }

        this.tooltipElement.innerHTML = tooltipContent;
        this.positionTooltip();
        this.tooltipElement.style.display = 'block';
    }

    /**
     * Posiciona o tooltip próximo ao badge
     */
    positionTooltip() {
        if (!this.badgeElement || !this.tooltipElement) {
            return;
        }

        const badgeRect = this.badgeElement.getBoundingClientRect();
        const tooltipRect = this.tooltipElement.getBoundingClientRect();

        // Posicionar abaixo do badge, centralizado
        let left = badgeRect.left + (badgeRect.width / 2) - (tooltipRect.width / 2);
        let top = badgeRect.bottom + 10;

        // Ajustar se sair da tela
        if (left < 10) {
            left = 10;
        }
        if (left + tooltipRect.width > window.innerWidth - 10) {
            left = window.innerWidth - tooltipRect.width - 10;
        }

        this.tooltipElement.style.left = `${left}px`;
        this.tooltipElement.style.top = `${top}px`;
    }

    /**
     * Esconde o tooltip
     */
    hideTooltip() {
        if (this.tooltipElement) {
            this.tooltipElement.style.display = 'none';
        }
    }

    /**
     * Força atualização do contador (chamado após desbloquear conquista)
     */
    forceUpdate() {
        this.updateCount();
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.badgeCounter = new BadgeCounter();
});
