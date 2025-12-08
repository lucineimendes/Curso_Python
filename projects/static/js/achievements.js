/**
 * Achievement Notification System
 * Handles displaying achievement unlock notifications with animations and queueing
 */

class AchievementNotification {
    constructor() {
        this.queue = [];
        this.isShowing = false;
        this.notificationElement = null;
        this.AUTO_DISMISS_DELAY = 5000; // 5 seconds
        this.FADE_IN_DURATION = 300; // ms
        this.FADE_OUT_DURATION = 300; // ms
        this.QUEUE_DELAY = 500; // ms between notifications
    }

    /**
     * Show a notification for an unlocked achievement
     * @param {Object} achievement - Achievement data with id, name, description, icon
     */
    show(achievement) {
        // Add to queue
        this.queue.push(achievement);

        // Process queue if not already showing
        if (!this.isShowing) {
            this._processQueue();
        }
    }

    /**
     * Process the notification queue sequentially
     */
    async _processQueue() {
        while (this.queue.length > 0) {
            this.isShowing = true;
            const achievement = this.queue.shift();
            await this._displayNotification(achievement);

            // Delay before next notification
            if (this.queue.length > 0) {
                await this._delay(this.QUEUE_DELAY);
            }
        }
        this.isShowing = false;
    }

    /**
     * Display a single notification with animations
     * @param {Object} achievement - Achievement data
     */
    async _displayNotification(achievement) {
        // Create notification element
        this.notificationElement = this._createNotificationElement(achievement);
        document.body.appendChild(this.notificationElement);

        // Fade in
        await this._delay(10); // Small delay for DOM to update
        this.notificationElement.classList.add('show');

        // Auto-dismiss after delay
        await this._delay(this.AUTO_DISMISS_DELAY);

        // Fade out
        await this._dismissNotification();
    }

    /**
     * Create the notification DOM element
     * @param {Object} achievement - Achievement data
     * @returns {HTMLElement} Notification element
     */
    _createNotificationElement(achievement) {
        const notification = document.createElement('div');
        notification.className = 'achievement-notification';

        notification.innerHTML = `
            <div class="achievement-notification-content">
                <div class="achievement-notification-icon">${achievement.icon || '🏆'}</div>
                <div class="achievement-notification-text">
                    <div class="achievement-notification-title">Conquista Desbloqueada!</div>
                    <div class="achievement-notification-name">${achievement.name}</div>
                </div>
            </div>
        `;

        // Add click to dismiss
        notification.addEventListener('click', () => {
            this._dismissNotification();
        });

        return notification;
    }

    /**
     * Dismiss the current notification with fade out animation
     */
    async _dismissNotification() {
        if (!this.notificationElement) return;

        this.notificationElement.classList.remove('show');
        await this._delay(this.FADE_OUT_DURATION);

        if (this.notificationElement && this.notificationElement.parentNode) {
            this.notificationElement.parentNode.removeChild(this.notificationElement);
        }
        this.notificationElement = null;
    }

    /**
     * Check for newly unlocked achievements and show notifications
     * @param {string} userId - User ID (default: 'default')
     */
    async checkNewAchievements(userId = 'default') {
        try {
            const response = await fetch('/api/achievements/check', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ user_id: userId })
            });

            if (!response.ok) {
                console.error('Failed to check achievements:', response.statusText);
                return;
            }

            const data = await response.json();

            if (data.success && data.newly_unlocked && data.newly_unlocked.length > 0) {
                // Show notifications for each newly unlocked achievement
                data.newly_unlocked.forEach(achievement => {
                    this.show(achievement);
                });
            }
        } catch (error) {
            console.error('Error checking achievements:', error);
        }
    }

    /**
     * Utility function to create a delay promise
     * @param {number} ms - Milliseconds to delay
     * @returns {Promise} Promise that resolves after delay
     */
    _delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Create global instance
window.achievementNotification = new AchievementNotification();
