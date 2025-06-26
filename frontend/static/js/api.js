// api.js - JavaScript API client using Axios

const API_BASE_URL = 'http://localhost:8001/api';

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

// Legacy functions for backward compatibility
async function fetchOrders() {
    return ordersAPI.getAll();
}

async function createOrder(orderData) {
    return ordersAPI.create(orderData);
}

// Export APIs
export { 
    ordersAPI, 
    menuAPI, 
    inventoryAPI, 
    staffAPI,
    fetchOrders, 
    createOrder 
};
