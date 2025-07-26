// enhanced-api.js - Extended API client for new features

const API_BASE_URL = 'http://localhost:8000/api';

// Staff Management API
export const staffManagementAPI = {
    // Timesheet operations
    createTimesheet: async (timesheetData) => {
        const response = await fetch(`${API_BASE_URL}/staff-management/timesheets/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(timesheetData)
        });
        if (!response.ok) throw new Error('Failed to create timesheet');
        return response.json();
    },

    getTimesheets: async (staffId = null, startDate = null, endDate = null) => {
        const params = new URLSearchParams();
        if (staffId) params.append('staff_id', staffId);
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        const response = await fetch(`${API_BASE_URL}/staff-management/timesheets/?${params}`);
        if (!response.ok) throw new Error('Failed to fetch timesheets');
        return response.json();
    },

    clockIn: async (timesheetId) => {
        const response = await fetch(`${API_BASE_URL}/staff-management/timesheets/${timesheetId}/clock-in`, {
            method: 'POST'
        });
        if (!response.ok) throw new Error('Failed to clock in');
        return response.json();
    },

    clockOut: async (timesheetId) => {
        const response = await fetch(`${API_BASE_URL}/staff-management/timesheets/${timesheetId}/clock-out`, {
            method: 'POST'
        });
        if (!response.ok) throw new Error('Failed to clock out');
        return response.json();
    },

    // Salary operations
    getSalaryRecords: async (staffId) => {
        const response = await fetch(`${API_BASE_URL}/staff-management/salary/${staffId}`);
        if (!response.ok) throw new Error('Failed to fetch salary records');
        return response.json();
    },

    calculateMonthlySalary: async (staffId, month, year) => {
        const response = await fetch(`${API_BASE_URL}/staff-management/salary/calculate/${staffId}?month=${month}&year=${year}`, {
            method: 'POST'
        });
        if (!response.ok) throw new Error('Failed to calculate salary');
        return response.json();
    },

    getMonthlySalaryReport: async (month, year) => {
        const response = await fetch(`${API_BASE_URL}/staff-management/salary/monthly-report?month=${month}&year=${year}`);
        if (!response.ok) throw new Error('Failed to fetch monthly salary report');
        return response.json();
    },

    getStaffAnalytics: async (startDate = null, endDate = null) => {
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        const response = await fetch(`${API_BASE_URL}/staff-management/analytics?${params}`);
        if (!response.ok) throw new Error('Failed to fetch staff analytics');
        return response.json();
    }
};

// Sales Analytics API
export const salesAnalyticsAPI = {
    getSalesOverview: async (startDate = null, endDate = null) => {
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        const response = await fetch(`${API_BASE_URL}/sales-analytics/analytics/overview?${params}`);
        if (!response.ok) throw new Error('Failed to fetch sales overview');
        return response.json();
    },
    
    getHourlySales: async (startDate = null, endDate = null) => {
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        const response = await fetch(`${API_BASE_URL}/sales-analytics/analytics/hourly-sales?${params}`);
        if (!response.ok) throw new Error('Failed to fetch hourly sales data');
        return response.json();
    },
    
    getStaffPerformance: async (startDate = null, endDate = null) => {
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        const response = await fetch(`${API_BASE_URL}/sales-analytics/analytics/staff-performance?${params}`);
        if (!response.ok) throw new Error('Failed to fetch staff performance data');
        return response.json();
    },
    
    getCategoryPerformance: async (startDate = null, endDate = null) => {
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        const response = await fetch(`${API_BASE_URL}/sales-analytics/analytics/product-category-performance?${params}`);
        if (!response.ok) throw new Error('Failed to fetch category performance data');
        return response.json();
    },
    
    getDailyReports: async (startDate = null, endDate = null) => {
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        const response = await fetch(`${API_BASE_URL}/sales-analytics/daily-reports/?${params}`);
        if (!response.ok) throw new Error('Failed to fetch daily reports');
        return response.json();
    },
    
    generateDailyReport: async (reportDate) => {
        const response = await fetch(`${API_BASE_URL}/sales-analytics/daily-reports/generate?report_date=${reportDate}`, {
            method: 'POST'
        });
        if (!response.ok) throw new Error('Failed to generate daily report');
        return response.json();
    },
    
    getMonthlyReport: async (month, year) => {
        const response = await fetch(`${API_BASE_URL}/sales-analytics/reports/monthly?month=${month}&year=${year}`);
        if (!response.ok) throw new Error('Failed to fetch monthly report');
        return response.json();
    },
    
    exportSalesToExcel: async (startDate, endDate) => {
        const response = await fetch(`${API_BASE_URL}/sales-analytics/export/excel?start_date=${startDate}&end_date=${endDate}`);
        if (!response.ok) throw new Error('Failed to export sales data');
        return response.json();
    }
}

// Enhanced Inventory API
export const enhancedInventoryAPI = {
    getAlcoholInventory: async () => {
        const response = await fetch(`${API_BASE_URL}/inventory/alcohol`);
        if (!response.ok) throw new Error('Failed to fetch alcohol inventory');
        return response.json();
    },

    getAlcoholByType: async () => {
        const response = await fetch(`${API_BASE_URL}/inventory/alcohol/by-type`);
        if (!response.ok) throw new Error('Failed to fetch alcohol by type');
        return response.json();
    },

    createStockMovement: async (movementData) => {
        const response = await fetch(`${API_BASE_URL}/inventory/stock-movement`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(movementData)
        });
        if (!response.ok) throw new Error('Failed to create stock movement');
        return response.json();
    },

    getStockMovements: async (inventoryItemId) => {
        const response = await fetch(`${API_BASE_URL}/inventory/movements/${inventoryItemId}`);
        if (!response.ok) throw new Error('Failed to fetch stock movements');
        return response.json();
    },

    getInventoryAnalytics: async () => {
        const response = await fetch(`${API_BASE_URL}/inventory/analytics`);
        if (!response.ok) throw new Error('Failed to fetch inventory analytics');
        return response.json();
    }
};

// System Settings API
export const systemAPI = {
    getSettings: async (category = null) => {
        const params = category ? `?category=${category}` : '';
        const response = await fetch(`${API_BASE_URL}/system/settings/${params}`);
        if (!response.ok) throw new Error('Failed to fetch settings');
        return response.json();
    },

    getSetting: async (settingKey) => {
        const response = await fetch(`${API_BASE_URL}/system/settings/${settingKey}`);
        if (!response.ok) throw new Error('Failed to fetch setting');
        return response.json();
    },

    createSetting: async (settingData) => {
        const response = await fetch(`${API_BASE_URL}/system/settings/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settingData)
        });
        if (!response.ok) throw new Error('Failed to create setting');
        return response.json();
    },

    updateSetting: async (settingKey, settingData) => {
        const response = await fetch(`${API_BASE_URL}/system/settings/${settingKey}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settingData)
        });
        if (!response.ok) throw new Error('Failed to update setting');
        return response.json();
    },

    initializeDefaults: async () => {
        const response = await fetch(`${API_BASE_URL}/system/settings/initialize-defaults`, {
            method: 'POST'
        });
        if (!response.ok) throw new Error('Failed to initialize default settings');
        return response.json();
    },

    // Notifications
    getNotifications: async (recipientId = null, isRead = null, notificationType = null) => {
        const params = new URLSearchParams();
        if (recipientId) params.append('recipient_id', recipientId);
        if (isRead !== null) params.append('is_read', isRead);
        if (notificationType) params.append('notification_type', notificationType);
        
        const response = await fetch(`${API_BASE_URL}/system/notifications/?${params}`);
        if (!response.ok) throw new Error('Failed to fetch notifications');
        return response.json();
    },

    createNotification: async (notificationData) => {
        const response = await fetch(`${API_BASE_URL}/system/notifications/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(notificationData)
        });
        if (!response.ok) throw new Error('Failed to create notification');
        return response.json();
    },

    markNotificationRead: async (notificationId) => {
        const response = await fetch(`${API_BASE_URL}/system/notifications/${notificationId}/mark-read`, {
            method: 'POST'
        });
        if (!response.ok) throw new Error('Failed to mark notification as read');
        return response.json();
    },

    markAllNotificationsRead: async (recipientId = null) => {
        const params = recipientId ? `?recipient_id=${recipientId}` : '';
        const response = await fetch(`${API_BASE_URL}/system/notifications/mark-all-read${params}`, {
            method: 'POST'
        });
        if (!response.ok) throw new Error('Failed to mark all notifications as read');
        return response.json();
    },

    checkLowStockNotifications: async () => {
        const response = await fetch(`${API_BASE_URL}/system/notifications/check-low-stock`, {
            method: 'POST'
        });
        if (!response.ok) throw new Error('Failed to check low stock notifications');
        return response.json();
    },

    getDashboardSummary: async () => {
        const response = await fetch(`${API_BASE_URL}/system/dashboard/summary`);
        if (!response.ok) throw new Error('Failed to fetch dashboard summary');
        return response.json();
    }
};

// Financial Reporting API
export const financialAPI = {
    getFinancialOverview: async (startDate = null, endDate = null) => {
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        const response = await fetch(`${API_BASE_URL}/financial/overview?${params}`);
        if (!response.ok) throw new Error('Failed to fetch financial overview');
        return response.json();
    },
    
    getProfitLossStatement: async (year, month = null) => {
        const params = new URLSearchParams();
        params.append('year', year);
        if (month) params.append('month', month);
        
        const response = await fetch(`${API_BASE_URL}/financial/profit-loss?${params}`);
        if (!response.ok) throw new Error('Failed to fetch profit/loss statement');
        return response.json();
    },
    
    getExpenseReport: async (startDate = null, endDate = null, category = null) => {
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        if (category) params.append('category', category);
        
        const response = await fetch(`${API_BASE_URL}/financial/expense-report?${params}`);
        if (!response.ok) throw new Error('Failed to fetch expense report');
        return response.json();
    },
    
    getCashFlow: async (startDate = null, endDate = null) => {
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        const response = await fetch(`${API_BASE_URL}/financial/cash-flow?${params}`);
        if (!response.ok) throw new Error('Failed to fetch cash flow report');
        return response.json();
    },
    
    getTaxReport: async (year, quarter = null) => {
        const params = new URLSearchParams();
        params.append('year', year);
        if (quarter) params.append('quarter', quarter);
        
        const response = await fetch(`${API_BASE_URL}/financial/tax-report?${params}`);
        if (!response.ok) throw new Error('Failed to fetch tax report');
        return response.json();
    }
};
