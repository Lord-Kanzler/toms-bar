// api.js - JavaScript API client using Axios

const API_BASE_URL = 'http://localhost:8000/api';

// Utility function for error handling
function handleApiError(error, defaultMessage = 'An error occurred') {
    console.error('API Error:', error);
    if (error.response?.data?.detail) {
        return error.response.data.detail;
    }
    return defaultMessage;
}

// Orders API
const ordersAPI = {
    async getAll() {
        try {
            const response = await axios.get(`${API_BASE_URL}/orders/`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to fetch orders'));
        }
    },

    async getById(orderId) {
        try {
            const response = await axios.get(`${API_BASE_URL}/orders/${orderId}`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to fetch order'));
        }
    },

    async create(orderData) {
        try {
            const response = await axios.post(`${API_BASE_URL}/orders/`, orderData);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to create order'));
        }
    },

    async update(orderId, orderData) {
        try {
            const response = await axios.put(`${API_BASE_URL}/orders/${orderId}`, orderData);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to update order'));
        }
    },

    async delete(orderId) {
        try {
            const response = await axios.delete(`${API_BASE_URL}/orders/${orderId}`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to delete order'));
        }
    },

    async updateStatus(orderId, status) {
        try {
            const response = await axios.patch(`${API_BASE_URL}/orders/${orderId}/status?status=${status}`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to update order status'));
        }
    }
};

// Menu API
const menuAPI = {
    async getAll(params = {}) {
        try {
            const queryParams = new URLSearchParams();
            if (params.category) queryParams.append('category', params.category);
            if (params.active_only !== undefined) queryParams.append('active_only', params.active_only);
            
            const response = await axios.get(`${API_BASE_URL}/menu/?${queryParams}`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to fetch menu items'));
        }
    },

    async getById(itemId) {
        try {
            const response = await axios.get(`${API_BASE_URL}/menu/${itemId}`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to fetch menu item'));
        }
    },

    async create(itemData) {
        try {
            const response = await axios.post(`${API_BASE_URL}/menu/`, itemData);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to create menu item'));
        }
    },

    async update(itemId, itemData) {
        try {
            const response = await axios.put(`${API_BASE_URL}/menu/${itemId}`, itemData);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to update menu item'));
        }
    },

    async delete(itemId) {
        try {
            const response = await axios.delete(`${API_BASE_URL}/menu/${itemId}`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to delete menu item'));
        }
    },

    async getCategories() {
        try {
            const response = await axios.get(`${API_BASE_URL}/menu/categories/list`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to fetch categories'));
        }
    },

    async toggleActive(itemId) {
        try {
            const response = await axios.patch(`${API_BASE_URL}/menu/${itemId}/toggle-active`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to toggle menu item status'));
        }
    }
};

// Inventory API
const inventoryAPI = {
    async getAll(params = {}) {
        try {
            const queryParams = new URLSearchParams();
            if (params.category) queryParams.append('category', params.category);
            if (params.low_stock_only) queryParams.append('low_stock_only', params.low_stock_only);
            if (params.alcohol_only) queryParams.append('alcohol_only', params.alcohol_only);
            
            const response = await axios.get(`${API_BASE_URL}/inventory/?${queryParams}`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to fetch inventory items'));
        }
    },

    async getLowStock() {
        try {
            const response = await axios.get(`${API_BASE_URL}/inventory/low-stock`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to fetch low stock items'));
        }
    },

    async getOutOfStock() {
        try {
            const response = await axios.get(`${API_BASE_URL}/inventory/out-of-stock`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to fetch out of stock items'));
        }
    },

    async getById(itemId) {
        try {
            const response = await axios.get(`${API_BASE_URL}/inventory/${itemId}`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to fetch inventory item'));
        }
    },

    async create(itemData) {
        try {
            const response = await axios.post(`${API_BASE_URL}/inventory/`, itemData);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to create inventory item'));
        }
    },

    async update(itemId, itemData) {
        try {
            const response = await axios.put(`${API_BASE_URL}/inventory/${itemId}`, itemData);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to update inventory item'));
        }
    },

    async delete(itemId) {
        try {
            const response = await axios.delete(`${API_BASE_URL}/inventory/${itemId}`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to delete inventory item'));
        }
    },

    async updateStock(itemId, stockChange) {
        try {
            const response = await axios.patch(`${API_BASE_URL}/inventory/${itemId}/stock?stock_change=${stockChange}`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to update stock'));
        }
    },

    async getCategories() {
        try {
            const response = await axios.get(`${API_BASE_URL}/inventory/categories/list`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to fetch categories'));
        }
    },

    async getSummary() {
        try {
            const response = await axios.get(`${API_BASE_URL}/inventory/summary/stats`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to fetch inventory summary'));
        }
    }
};

// Staff API
const staffAPI = {
    async getAll(params = {}) {
        try {
            const queryParams = new URLSearchParams();
            if (params.position) queryParams.append('position', params.position);
            if (params.active_only !== undefined) queryParams.append('active_only', params.active_only);
            
            const response = await axios.get(`${API_BASE_URL}/staff/?${queryParams}`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to fetch staff members'));
        }
    },

    async getById(staffId) {
        try {
            const response = await axios.get(`${API_BASE_URL}/staff/${staffId}`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to fetch staff member'));
        }
    },

    async create(staffData) {
        try {
            const response = await axios.post(`${API_BASE_URL}/staff/`, staffData);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to create staff member'));
        }
    },

    async update(staffId, staffData) {
        try {
            const response = await axios.put(`${API_BASE_URL}/staff/${staffId}`, staffData);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to update staff member'));
        }
    },

    async delete(staffId) {
        try {
            const response = await axios.delete(`${API_BASE_URL}/staff/${staffId}`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to delete staff member'));
        }
    },

    async toggleActive(staffId) {
        try {
            const response = await axios.patch(`${API_BASE_URL}/staff/${staffId}/toggle-active`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to toggle staff member status'));
        }
    },

    async getPositions() {
        try {
            const response = await axios.get(`${API_BASE_URL}/staff/positions/list`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to fetch positions'));
        }
    },

    async getSummary() {
        try {
            const response = await axios.get(`${API_BASE_URL}/staff/summary/stats`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to fetch staff summary'));
        }
    }
};

// Notifications API
const notificationsAPI = {
    async getAll(filters = {}) {
        try {
            const params = new URLSearchParams();
            if (filters.unread_only) params.append('unread_only', 'true');
            if (filters.category) params.append('category', filters.category);
            if (filters.priority) params.append('priority', filters.priority);
            if (filters.user_id) params.append('user_id', filters.user_id);
            if (filters.limit) params.append('limit', filters.limit);
            
            const response = await axios.get(`${API_BASE_URL}/notifications/?${params}`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to fetch notifications'));
        }
    },

    async getStats(userId = null) {
        try {
            const params = userId ? `?user_id=${userId}` : '';
            const response = await axios.get(`${API_BASE_URL}/notifications/stats${params}`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to fetch notification stats'));
        }
    },

    async getUnreadCount(userId = null) {
        try {
            const params = userId ? `?user_id=${userId}` : '';
            const response = await axios.get(`${API_BASE_URL}/notifications/unread-count${params}`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to fetch unread count'));
        }
    },

    async create(notificationData) {
        try {
            const response = await axios.post(`${API_BASE_URL}/notifications/`, notificationData);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to create notification'));
        }
    },

    async markAsRead(notificationId) {
        try {
            const response = await axios.put(`${API_BASE_URL}/notifications/${notificationId}`, {
                is_read: true
            });
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to mark notification as read'));
        }
    },

    async markAsDismissed(notificationId) {
        try {
            const response = await axios.put(`${API_BASE_URL}/notifications/${notificationId}`, {
                is_dismissed: true
            });
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to dismiss notification'));
        }
    },

    async markAllAsRead(userId = null, category = null) {
        try {
            const params = new URLSearchParams();
            if (userId) params.append('user_id', userId);
            if (category) params.append('category', category);
            
            const response = await axios.post(`${API_BASE_URL}/notifications/mark-all-read?${params}`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to mark all notifications as read'));
        }
    },

    async delete(notificationId) {
        try {
            const response = await axios.delete(`${API_BASE_URL}/notifications/${notificationId}`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to delete notification'));
        }
    },

    async cleanupExpired() {
        try {
            const response = await axios.post(`${API_BASE_URL}/notifications/cleanup-expired`);
            return response.data;
        } catch (error) {
            throw new Error(handleApiError(error, 'Failed to cleanup expired notifications'));
        }
    }
};

// Legacy functions for backward compatibility
async function fetchOrders() {
    return ordersAPI.getAll();
}

async function createOrder(orderData) {
    return ordersAPI.create(orderData);
}

// Make APIs available globally
window.ordersAPI = ordersAPI;
window.menuAPI = menuAPI;
window.inventoryAPI = inventoryAPI;
window.staffAPI = staffAPI;
window.notificationsAPI = notificationsAPI;
window.fetchOrders = fetchOrders;
window.createOrder = createOrder;

console.log('APIs loaded successfully');
