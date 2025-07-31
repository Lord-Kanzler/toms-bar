// notifications.js - Notification system UI components

class NotificationManager {
    constructor() {
        this.notifications = [];
        this.unreadCount = 0;
        this.isPolling = false;
        this.pollInterval = 30000; // 30 seconds
        this.maxDisplayedNotifications = 5;
        
        this.init();
    }

    async init() {
        try {
            // Create notification elements if they don't exist
            this.createNotificationElements();
            
            // Load initial notifications
            await this.loadNotifications();
            
            // Start polling for new notifications
            this.startPolling();
            
            // Setup event listeners
            this.setupEventListeners();
            
            console.log('Notification manager initialized');
        } catch (error) {
            console.error('Failed to initialize notification manager:', error);
        }
    }

    createNotificationElements() {
        // Check if notification elements already exist
        if (document.getElementById('notificationBell')) {
            return;
        }

        // Find the header or create one if it doesn't exist
        let header = document.querySelector('header');
        if (!header) {
            // Create a simple header for notifications
            header = document.createElement('div');
            header.className = 'notification-header bg-white shadow-sm border-b px-4 py-2 flex justify-between items-center';
            header.innerHTML = `
                <div class="flex items-center space-x-4">
                    <h1 class="text-lg font-semibold text-gray-900">GastroPro Dashboard</h1>
                </div>
                <div class="flex items-center space-x-4">
                    <div class="notification-container relative">
                        <button id="notificationBell" class="relative p-2 text-gray-600 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded-lg transition-colors">
                            <i class="fas fa-bell text-xl"></i>
                            <span id="notificationBadge" class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center hidden">0</span>
                        </button>
                        <div id="notificationDropdown" class="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50 hidden">
                            <div class="p-4 border-b border-gray-200">
                                <div class="flex items-center justify-between">
                                    <h3 class="text-lg font-semibold text-gray-900">Notifications</h3>
                                    <button id="markAllRead" class="text-sm text-indigo-600 hover:text-indigo-800">Mark all read</button>
                                </div>
                            </div>
                            <div id="notificationList" class="max-h-96 overflow-y-auto">
                                <!-- Notifications will be inserted here -->
                            </div>
                            <div class="p-4 border-t border-gray-200">
                                <button id="viewAllNotifications" class="w-full text-center text-sm text-indigo-600 hover:text-indigo-800">View all notifications</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Insert at the beginning of the page
            const mainContainer = document.querySelector('main') || document.body;
            mainContainer.insertBefore(header, mainContainer.firstChild);
        }

        // Create toast notification container
        if (!document.getElementById('toastContainer')) {
            const toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'fixed top-4 right-4 z-50 space-y-2';
            document.body.appendChild(toastContainer);
        }
    }

    setupEventListeners() {
        const notificationBell = document.getElementById('notificationBell');
        const notificationDropdown = document.getElementById('notificationDropdown');
        const markAllRead = document.getElementById('markAllRead');
        const viewAllNotifications = document.getElementById('viewAllNotifications');

        if (notificationBell) {
            notificationBell.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleDropdown();
            });
        }

        if (markAllRead) {
            markAllRead.addEventListener('click', () => {
                this.markAllAsRead();
            });
        }

        if (viewAllNotifications) {
            viewAllNotifications.addEventListener('click', () => {
                this.showAllNotifications();
            });
        }

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (notificationDropdown && !notificationDropdown.contains(e.target) && !notificationBell.contains(e.target)) {
                notificationDropdown.classList.add('hidden');
            }
        });
    }

    async loadNotifications() {
        try {
            const [notifications, stats] = await Promise.all([
                notificationsAPI.getAll({ limit: this.maxDisplayedNotifications }),
                notificationsAPI.getStats()
            ]);

            this.notifications = notifications;
            this.unreadCount = stats.unread_count;

            this.updateUI();
        } catch (error) {
            console.error('Failed to load notifications:', error);
        }
    }

    updateUI() {
        this.updateBadge();
        this.updateNotificationList();
    }

    updateBadge() {
        const badge = document.getElementById('notificationBadge');
        if (badge) {
            if (this.unreadCount > 0) {
                badge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
                badge.classList.remove('hidden');
            } else {
                badge.classList.add('hidden');
            }
        }
    }

    updateNotificationList() {
        const notificationList = document.getElementById('notificationList');
        if (!notificationList) return;

        if (this.notifications.length === 0) {
            notificationList.innerHTML = `
                <div class="p-4 text-center text-gray-500">
                    <i class="fas fa-bell-slash text-2xl mb-2"></i>
                    <p>No notifications</p>
                </div>
            `;
            return;
        }

        notificationList.innerHTML = this.notifications.map(notification => 
            this.createNotificationHTML(notification)
        ).join('');

        // Add event listeners to notification items
        notificationList.querySelectorAll('.notification-item').forEach(item => {
            const notificationId = item.dataset.notificationId;
            const actionBtn = item.querySelector('.notification-action');
            const dismissBtn = item.querySelector('.notification-dismiss');

            item.addEventListener('click', () => {
                this.markAsRead(notificationId);
            });

            if (actionBtn) {
                actionBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const actionUrl = actionBtn.dataset.actionUrl;
                    if (actionUrl) {
                        // Navigate to the action URL
                        window.location.hash = actionUrl;
                        this.markAsRead(notificationId);
                    }
                });
            }

            if (dismissBtn) {
                dismissBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.dismissNotification(notificationId);
                });
            }
        });
    }

    createNotificationHTML(notification) {
        const timeAgo = this.getTimeAgo(notification.created_at);
        const isUnread = !notification.is_read;
        const typeIcon = this.getTypeIcon(notification.notification_type);
        const priorityClass = this.getPriorityClass(notification.priority);

        return `
            <div class="notification-item p-3 border-b border-gray-100 hover:bg-gray-50 cursor-pointer ${isUnread ? 'bg-blue-50' : ''}" 
                 data-notification-id="${notification.id}">
                <div class="flex items-start space-x-3">
                    <div class="flex-shrink-0">
                        <div class="w-8 h-8 rounded-full ${priorityClass} flex items-center justify-center">
                            <i class="${typeIcon} text-white text-sm"></i>
                        </div>
                    </div>
                    <div class="flex-1 min-w-0">
                        <div class="flex items-center justify-between">
                            <p class="text-sm font-medium text-gray-900 ${isUnread ? 'font-semibold' : ''}">${notification.title}</p>
                            ${isUnread ? '<div class="w-2 h-2 bg-blue-500 rounded-full"></div>' : ''}
                        </div>
                        <p class="text-sm text-gray-600 mt-1">${notification.message}</p>
                        <div class="flex items-center justify-between mt-2">
                            <span class="text-xs text-gray-500">${timeAgo}</span>
                            <div class="flex space-x-2">
                                ${notification.action_url ? `
                                    <button class="notification-action text-xs text-indigo-600 hover:text-indigo-800" 
                                            data-action-url="${notification.action_url}">
                                        ${notification.action_label || 'View'}
                                    </button>
                                ` : ''}
                                <button class="notification-dismiss text-xs text-gray-500 hover:text-gray-700">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    getTypeIcon(type) {
        const icons = {
            'info': 'fas fa-info',
            'warning': 'fas fa-exclamation-triangle',
            'error': 'fas fa-exclamation-circle',
            'success': 'fas fa-check-circle'
        };
        return icons[type] || icons.info;
    }

    getPriorityClass(priority) {
        const classes = {
            'low': 'bg-gray-500',
            'normal': 'bg-blue-500',
            'high': 'bg-orange-500',
            'urgent': 'bg-red-500'
        };
        return classes[priority] || classes.normal;
    }

    getTimeAgo(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);

        if (diffInSeconds < 60) return 'Just now';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
        return `${Math.floor(diffInSeconds / 86400)}d ago`;
    }

    toggleDropdown() {
        const dropdown = document.getElementById('notificationDropdown');
        if (dropdown) {
            dropdown.classList.toggle('hidden');
            if (!dropdown.classList.contains('hidden')) {
                // Refresh notifications when opening dropdown
                this.loadNotifications();
            }
        }
    }

    async markAsRead(notificationId) {
        try {
            await notificationsAPI.markAsRead(notificationId);
            
            // Update local notification
            const notification = this.notifications.find(n => n.id == notificationId);
            if (notification && !notification.is_read) {
                notification.is_read = true;
                this.unreadCount = Math.max(0, this.unreadCount - 1);
                this.updateUI();
            }
        } catch (error) {
            console.error('Failed to mark notification as read:', error);
        }
    }

    async dismissNotification(notificationId) {
        try {
            await notificationsAPI.markAsDismissed(notificationId);
            
            // Remove from local notifications
            this.notifications = this.notifications.filter(n => n.id != notificationId);
            const notification = this.notifications.find(n => n.id == notificationId);
            if (notification && !notification.is_read) {
                this.unreadCount = Math.max(0, this.unreadCount - 1);
            }
            
            this.updateUI();
        } catch (error) {
            console.error('Failed to dismiss notification:', error);
        }
    }

    async markAllAsRead() {
        try {
            await notificationsAPI.markAllAsRead();
            
            // Update all local notifications
            this.notifications.forEach(notification => {
                notification.is_read = true;
            });
            this.unreadCount = 0;
            
            this.updateUI();
        } catch (error) {
            console.error('Failed to mark all notifications as read:', error);
        }
    }

    showAllNotifications() {
        // Navigate to notifications page or open modal
        // For now, we'll just close the dropdown
        const dropdown = document.getElementById('notificationDropdown');
        if (dropdown) {
            dropdown.classList.add('hidden');
        }
        
        // TODO: Implement full notifications page
        console.log('Show all notifications - TODO: Implement full page');
    }

    startPolling() {
        if (this.isPolling) return;
        
        this.isPolling = true;
        this.pollIntervalId = setInterval(() => {
            this.loadNotifications();
        }, this.pollInterval);
    }

    stopPolling() {
        if (this.pollIntervalId) {
            clearInterval(this.pollIntervalId);
            this.isPolling = false;
        }
    }

    // Show toast notification for real-time updates
    showToast(notification) {
        const toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) return;

        const toast = document.createElement('div');
        toast.className = `notification-toast max-w-sm bg-white shadow-lg rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5 overflow-hidden transform transition-all duration-300 translate-x-full`;
        
        const typeClass = this.getPriorityClass(notification.priority);
        const typeIcon = this.getTypeIcon(notification.notification_type);

        toast.innerHTML = `
            <div class="p-4">
                <div class="flex items-start">
                    <div class="flex-shrink-0">
                        <div class="w-8 h-8 rounded-full ${typeClass} flex items-center justify-center">
                            <i class="${typeIcon} text-white text-sm"></i>
                        </div>
                    </div>
                    <div class="ml-3 w-0 flex-1 pt-0.5">
                        <p class="text-sm font-medium text-gray-900">${notification.title}</p>
                        <p class="mt-1 text-sm text-gray-500">${notification.message}</p>
                        ${notification.action_url ? `
                            <div class="mt-3">
                                <button class="bg-indigo-600 text-white px-3 py-1 rounded-md text-sm hover:bg-indigo-700" 
                                        onclick="window.location.hash='${notification.action_url}'">
                                    ${notification.action_label || 'View'}
                                </button>
                            </div>
                        ` : ''}
                    </div>
                    <div class="ml-4 flex-shrink-0 flex">
                        <button class="bg-white rounded-md inline-flex text-gray-400 hover:text-gray-500" 
                                onclick="this.closest('.notification-toast').remove()">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;

        toastContainer.appendChild(toast);

        // Animate in
        setTimeout(() => {
            toast.classList.remove('translate-x-full');
        }, 100);

        // Auto remove after 5 seconds
        setTimeout(() => {
            toast.classList.add('translate-x-full');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 5000);
    }

    // Method to manually create notifications (for testing or system events)
    async createNotification(notificationData) {
        try {
            const notification = await notificationsAPI.create(notificationData);
            
            // Show toast for new notification
            this.showToast(notification);
            
            // Refresh notifications
            await this.loadNotifications();
            
            return notification;
        } catch (error) {
            console.error('Failed to create notification:', error);
            throw error;
        }
    }
}

// Make NotificationManager available globally
window.NotificationManager = NotificationManager;

// Auto-initialize when notifications API is available
document.addEventListener('DOMContentLoaded', () => {
    // Wait for APIs to load
    const checkAPIs = () => {
        if (window.notificationsAPI) {
            window.notificationManager = new NotificationManager();
        } else {
            setTimeout(checkAPIs, 100);
        }
    };
    checkAPIs();
});
