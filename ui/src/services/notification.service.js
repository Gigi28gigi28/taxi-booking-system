import authService from './auth.service';

const API_BASE_URL = 'http://localhost:8001';

const notificationService = {
    /**
     * Get all notifications for current user
     */
    getNotifications: async () => {
        const response = await fetch(`${API_BASE_URL}/api/notifications/`, {
            headers: authService.getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error('Failed to fetch notifications');
        }

        return response.json();
    },

    /**
     * Get unread notifications only
     */
    getUnreadNotifications: async () => {
        const response = await fetch(`${API_BASE_URL}/api/notifications/unread/`, {
            headers: authService.getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error('Failed to fetch unread notifications');
        }

        return response.json();
    },

    /**
     * Mark notification as read
     */
    markAsRead: async (notificationId) => {
        const response = await fetch(`${API_BASE_URL}/api/notifications/${notificationId}/mark_as_read/`, {
            method: 'POST',
            headers: authService.getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error('Failed to mark notification as read');
        }

        return response.json();
    },

    /**
     * Mark all notifications as read
     */
    markAllAsRead: async () => {
        const response = await fetch(`${API_BASE_URL}/api/notifications/mark_all_as_read/`, {
            method: 'POST',
            headers: authService.getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error('Failed to mark all notifications as read');
        }

        return response.json();
    },

    /**
     * Poll for new notifications
     * @param {string} since - ISO timestamp of last poll
     */
    pollNotifications: async (since) => {
        const response = await fetch(`${API_BASE_URL}/api/notifications/poll/?since=${since}`, {
            headers: authService.getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error('Failed to poll notifications');
        }

        return response.json();
    },

    /**
     * Delete notification
     */
    deleteNotification: async (notificationId) => {
        const response = await fetch(`${API_BASE_URL}/api/notifications/${notificationId}/`, {
            method: 'DELETE',
            headers: authService.getAuthHeaders()
        });

        if (!response.ok) {
            throw new Error('Failed to delete notification');
        }

        return true;
    },

    /**
     * Get notification count
     */
    getNotificationCount: async () => {
        const data = await notificationService.getNotifications();
        return {
            total: data.count || 0,
            unread: data.unread_count || 0
        };
    },

    /**
     * Subscribe to real-time notifications (polling implementation)
     * Calls callback function when new notifications arrive
     */
    subscribe: (callback, intervalMs = 5000) => {
        let lastPollTime = new Date().toISOString();
        let isActive = true;

        const poll = async () => {
            if (!isActive) return;

            try {
                const data = await notificationService.pollNotifications(lastPollTime);

                if (data.count > 0) {
                    callback(data.notifications);
                    lastPollTime = data.timestamp;
                }
            } catch (error) {
                console.error('Notification polling error:', error);
            }

            if (isActive) {
                setTimeout(poll, intervalMs);
            }
        };

        // Start polling
        poll();

        // Return unsubscribe function
        return () => {
            isActive = false;
        };
    },

    /**
     * Format notification for display
     */
    formatNotification: (notification) => {
        const typeIcons = {
            ride_requested: '🚖',
            ride_offered: '👋',
            ride_accepted: '✅',
            ride_rejected: '❌',
            ride_completed: '🏁',
            ride_cancelled: '🚫'
        };

        return {
            ...notification,
            icon: typeIcons[notification.notification_type] || '📢',
            timeAgo: notificationService.getTimeAgo(notification.created_at)
        };
    },

    /**
     * Get human-readable time ago string
     */
    getTimeAgo: (timestamp) => {
        const now = new Date();
        const created = new Date(timestamp);
        const diffMs = now - created;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        return created.toLocaleDateString();
    },

    /**
     * Get notification priority/urgency
     */
    getNotificationPriority: (notification) => {
        const highPriority = ['ride_offered', 'ride_accepted'];
        const mediumPriority = ['ride_requested', 'ride_rejected'];
        const lowPriority = ['ride_completed', 'ride_cancelled'];

        if (highPriority.includes(notification.notification_type)) return 'high';
        if (mediumPriority.includes(notification.notification_type)) return 'medium';
        return 'low';
    },

    /**
     * Group notifications by ride
     */
    groupByRide: (notifications) => {
        const grouped = {};

        notifications.forEach(notification => {
            const rideId = notification.ride_id || notification.ride;

            if (!grouped[rideId]) {
                grouped[rideId] = [];
            }

            grouped[rideId].push(notification);
        });

        return grouped;
    },

    /**
     * Filter notifications by type
     */
    filterByType: (notifications, types) => {
        if (!Array.isArray(types)) {
            types = [types];
        }

        return notifications.filter(n => types.includes(n.notification_type));
    },

    /**
     * Get latest notification for each ride
     */
    getLatestPerRide: (notifications) => {
        const grouped = notificationService.groupByRide(notifications);
        const latest = [];

        Object.keys(grouped).forEach(rideId => {
            const rideNotifications = grouped[rideId];
            // Sort by created_at descending
            rideNotifications.sort((a, b) =>
                new Date(b.created_at) - new Date(a.created_at)
            );
            latest.push(rideNotifications[0]);
        });

        return latest;
    }
};

export default notificationService;