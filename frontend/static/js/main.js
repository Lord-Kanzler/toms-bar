// main.js - Main application logic
import { ordersAPI, menuAPI, inventoryAPI, staffAPI } from './api.js';

// Global state
let currentSection = 'dashboardSection';
let currentData = {};

// DOM elements
const pageTitle = document.getElementById('pageTitle');
const mainContent = document.getElementById('mainContent');
const sidebar = document.getElementById('sidebar');
const mobileSidebarToggle = document.getElementById('mobileSidebarToggle');

// Utility functions
function capitalizeWord(word) {
    if (!word) return '';
    return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Initialize application
document.addEventListener('DOMContentLoaded', async () => {
    setupEventListeners();
    await loadSection('dashboardSection');
});

// Setup event listeners
function setupEventListeners() {
    // Navigation links
    document.querySelectorAll('.nav-link, #dashboardLink, #ordersLink, #menuLink, #inventoryLink, #staffLink').forEach(link => {
        link.addEventListener('click', async (e) => {
            e.preventDefault();
            const section = link.dataset.section || getSectionFromId(link.id);
            if (section) {
                updateActiveNavigation(link);
                await loadSection(section);
            }
        });
    });

    // Mobile sidebar toggle
    if (mobileSidebarToggle) {
        mobileSidebarToggle.addEventListener('click', () => {
            sidebar?.classList.toggle('open');
        });
    }

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
        if (window.innerWidth < 768 && sidebar && !sidebar.contains(e.target) && !mobileSidebarToggle.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    });
}

function getSectionFromId(linkId) {
    const sectionMap = {
        'dashboardLink': 'dashboardSection',
        'ordersLink': 'ordersSection',
        'menuLink': 'menuSection',
        'inventoryLink': 'inventorySection',
        'staffLink': 'staffSection'
    };
    return sectionMap[linkId];
}

function updateActiveNavigation(activeLink) {
    document.querySelectorAll('.nav-link, #dashboardLink, #ordersLink, #menuLink, #inventoryLink, #staffLink').forEach(link => {
        link.classList.remove('active');
    });
    activeLink.classList.add('active');
}

// Main section loader
async function loadSection(section) {
    currentSection = section;
    
    // Update page title
    const title = section.replace('Section', '').replace(/([A-Z])/g, ' $1').trim();
    pageTitle.textContent = title;

    // Show loading state
    showLoading();

    try {
        switch (section) {
            case 'dashboardSection':
                await loadDashboard();
                break;
            case 'ordersSection':
                await loadOrders();
                break;
            case 'menuSection':
                await loadMenu();
                break;
            case 'inventorySection':
                await loadInventory();
                break;
            case 'staffSection':
                await loadStaff();
                break;
            default:
                showError('Section not found');
        }
    } catch (error) {
        showError(error.message);
    }
}

// Dashboard section
async function loadDashboard() {
    try {
        const [orders, lowStockItems, inventorySummary, staffSummary] = await Promise.all([
            ordersAPI.getAll(),
            inventoryAPI.getLowStock(),
            inventoryAPI.getSummary(),
            staffAPI.getSummary()
        ]);

        const dashboardHTML = generateDashboardHTML({
            orders,
            lowStockItems,
            inventorySummary,
            staffSummary
        });

        mainContent.innerHTML = dashboardHTML;
    } catch (error) {
        throw error;
    }
}

function generateDashboardHTML(data) {
    const activeOrders = data.orders.filter(order => order.status !== 'completed');
    const todaysRevenue = data.orders
        .filter(order => order.status === 'completed')
        .reduce((sum, order) => sum + order.total_amount, 0);

    return `
        <div class="space-y-6">
            <!-- Stats Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div class="bg-white p-6 rounded-lg shadow card-hover">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-500 text-sm">Today's Revenue</p>
                            <h3 class="text-2xl font-bold text-gray-900">$${todaysRevenue.toFixed(2)}</h3>
                        </div>
                        <div class="bg-indigo-100 p-3 rounded-full">
                            <i class="fas fa-dollar-sign text-indigo-600"></i>
                        </div>
                    </div>
                </div>
                
                <div class="bg-white p-6 rounded-lg shadow card-hover">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-500 text-sm">Active Orders</p>
                            <h3 class="text-2xl font-bold text-gray-900">${activeOrders.length}</h3>
                        </div>
                        <div class="bg-yellow-100 p-3 rounded-full">
                            <i class="fas fa-clipboard-list text-yellow-600"></i>
                        </div>
                    </div>
                </div>
                
                <div class="bg-white p-6 rounded-lg shadow card-hover">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-500 text-sm">Total Staff</p>
                            <h3 class="text-2xl font-bold text-gray-900">${data.staffSummary.total_staff}</h3>
                        </div>
                        <div class="bg-green-100 p-3 rounded-full">
                            <i class="fas fa-users text-green-600"></i>
                        </div>
                    </div>
                </div>
                
                <div class="bg-white p-6 rounded-lg shadow card-hover">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-500 text-sm">Low Stock Items</p>
                            <h3 class="text-2xl font-bold text-gray-900">${data.inventorySummary.low_stock_items}</h3>
                        </div>
                        <div class="bg-red-100 p-3 rounded-full">
                            <i class="fas fa-exclamation-triangle text-red-600"></i>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Recent Orders -->
            <div class="bg-white rounded-lg shadow">
                <div class="p-6 border-b border-gray-200">
                    <h2 class="text-lg font-semibold text-gray-900">Recent Orders</h2>
                </div>
                <div class="p-6">
                    ${generateRecentOrdersTable(data.orders.slice(0, 5))}
                </div>
            </div>

            <!-- Low Stock Alert -->
            ${data.lowStockItems.length > 0 ? `
            <div class="bg-white rounded-lg shadow">
                <div class="p-6 border-b border-gray-200">
                    <h2 class="text-lg font-semibold text-gray-900">Low Stock Alerts</h2>
                </div>
                <div class="p-6">
                    ${generateLowStockTable(data.lowStockItems.slice(0, 5))}
                </div>
            </div>
            ` : ''}
        </div>
    `;
}

// Orders section
async function loadOrders() {
    try {
        const orders = await ordersAPI.getAll();
        currentData.orders = orders;

        const ordersHTML = generateOrdersHTML(orders);
        mainContent.innerHTML = ordersHTML;

        // Setup order event listeners
        setupOrderEventListeners();
    } catch (error) {
        throw error;
    }
}

function generateOrdersHTML(orders) {
    return `
        <div class="space-y-6">
            <!-- Header -->
            <div class="flex justify-between items-center">
                <h2 class="text-2xl font-bold text-gray-900">Order Management</h2>
                <button onclick="openCreateOrderModal()" class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center">
                    <i class="fas fa-plus mr-2"></i> New Order
                </button>
            </div>

            <!-- Orders List -->
            <div class="bg-white rounded-lg shadow overflow-hidden">
                <div class="p-4 border-b border-gray-200">
                    <h3 class="font-semibold text-gray-900">All Orders</h3>
                </div>
                <div class="divide-y divide-gray-200">
                    ${orders.map(order => generateOrderCard(order)).join('')}
                </div>
            </div>
        </div>
    `;
}

function generateOrderCard(order) {
    const statusColors = {
        pending: 'bg-yellow-100 text-yellow-800',
        preparing: 'bg-blue-100 text-blue-800',
        ready: 'bg-green-100 text-green-800',
        served: 'bg-gray-100 text-gray-800',
        completed: 'bg-green-100 text-green-800',
        cancelled: 'bg-red-100 text-red-800'
    };

    return `
        <div class="p-4 hover:bg-gray-50 transition order-item">
            <div class="flex items-start justify-between">
                <div>
                    <div class="flex items-center mb-2">
                        <span class="font-medium text-gray-900">Order #${order.id}</span>
                        <span class="ml-2 px-2 py-1 text-xs font-semibold rounded-full ${statusColors[order.status] || 'bg-gray-100 text-gray-800'}">
                            ${order.status}
                        </span>
                    </div>
                    <p class="text-sm text-gray-600">Table ${order.table_number} • ${order.customer_name || 'Walk-in'}</p>
                    <p class="text-sm text-gray-600">${formatDate(order.created_at)}</p>
                </div>
                <div class="text-right">
                    <p class="font-medium text-gray-900">$${order.total_amount.toFixed(2)}</p>
                    <div class="mt-2 flex space-x-2">
                        ${generateOrderActions(order)}
                    </div>
                </div>
            </div>
        </div>
    `;
}

function generateOrderActions(order) {
    const actions = [];
    
    if (order.status === 'pending') {
        actions.push(`<button onclick="updateOrderStatus(${order.id}, 'preparing')" class="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded hover:bg-blue-200">Start Preparing</button>`);
    }
    
    if (order.status === 'preparing') {
        actions.push(`<button onclick="updateOrderStatus(${order.id}, 'ready')" class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded hover:bg-green-200">Mark Ready</button>`);
    }
    
    if (order.status === 'ready') {
        actions.push(`<button onclick="updateOrderStatus(${order.id}, 'served')" class="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded hover:bg-gray-200">Mark Served</button>`);
    }
    
    if (order.status === 'served') {
        actions.push(`<button onclick="updateOrderStatus(${order.id}, 'completed')" class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded hover:bg-green-200">Complete</button>`);
    }
    
    if (['pending', 'preparing'].includes(order.status)) {
        actions.push(`<button onclick="updateOrderStatus(${order.id}, 'cancelled')" class="text-xs bg-red-100 text-red-800 px-2 py-1 rounded hover:bg-red-200">Cancel</button>`);
    }
    
    return actions.join('');
}

// Menu section
async function loadMenu() {
    try {
        const [menuItems, categories] = await Promise.all([
            menuAPI.getAll({ active_only: false }),
            menuAPI.getCategories()
        ]);
        
        currentData.menuItems = menuItems;
        currentData.categories = categories;

        const menuHTML = generateMenuHTML(menuItems, categories);
        mainContent.innerHTML = menuHTML;

        setupMenuEventListeners();
    } catch (error) {
        throw error;
    }
}

function generateMenuHTML(menuItems, categories) {
    return `
        <div class="space-y-6">
            <!-- Header -->
            <div class="flex justify-between items-center">
                <h2 class="text-2xl font-bold text-gray-900">Menu Management</h2>
                <div class="flex space-x-3">
                    <button onclick="openCreateMenuItemModal()" class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center">
                        <i class="fas fa-plus mr-2"></i> Add Item
                    </button>
                    <select id="categoryFilter" class="border border-gray-300 rounded-md px-3 py-2 text-sm">
                        <option value="">All Categories</option>
                        ${categories.map(cat => `<option value="${cat}">${cat}</option>`).join('')}
                    </select>
                </div>
            </div>

            <!-- Menu Items -->
            <div class="bg-white rounded-lg shadow overflow-hidden">
                <div class="divide-y divide-gray-200" id="menuItemsList">
                    ${menuItems.map(item => generateMenuItemCard(item)).join('')}
                </div>
            </div>
        </div>
    `;
}

function generateMenuItemCard(item) {
    return `
        <div class="p-4 hover:bg-gray-50 transition menu-item">
            <div class="flex items-start space-x-4">
                <div class="w-16 h-16 bg-gray-200 rounded-md overflow-hidden flex-shrink-0">
                    ${item.image_path ? 
                        `<img src="${item.image_path}" alt="${item.name}" class="w-full h-full object-cover">` :
                        `<div class="w-full h-full flex items-center justify-center text-gray-400"><i class="fas fa-utensils"></i></div>`
                    }
                </div>
                <div class="flex-1">
                    <div class="flex items-start justify-between">
                        <div>
                            <h4 class="font-medium text-gray-900">${item.name}</h4>
                            <p class="text-sm text-gray-600">${item.description}</p>
                            <div class="mt-2 flex flex-wrap gap-2">
                                <span class="bg-gray-100 px-2 py-1 rounded text-xs text-gray-700">${item.category}</span>
                                ${item.tags ? item.tags.split(',').map(tag => 
                                    `<span class="bg-gray-100 px-2 py-1 rounded text-xs text-gray-700">${tag.trim()}</span>`
                                ).join('') : ''}
                                <span class="px-2 py-1 rounded text-xs ${item.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}">
                                    ${item.is_active ? 'Active' : 'Inactive'}
                                </span>
                            </div>
                        </div>
                        <span class="font-medium text-gray-900">$${item.price.toFixed(2)}</span>
                    </div>
                    <div class="mt-3 flex space-x-2 menu-actions opacity-0">
                        <button onclick="editMenuItem(${item.id})" class="text-xs bg-blue-100 text-blue-800 px-3 py-1 rounded hover:bg-blue-200">
                            <i class="fas fa-edit mr-1"></i> Edit
                        </button>
                        <button onclick="toggleMenuItemActive(${item.id})" class="text-xs bg-yellow-100 text-yellow-800 px-3 py-1 rounded hover:bg-yellow-200">
                            <i class="fas fa-toggle-${item.is_active ? 'on' : 'off'} mr-1"></i> Toggle
                        </button>
                        <button onclick="deleteMenuItem(${item.id})" class="text-xs bg-red-100 text-red-800 px-3 py-1 rounded hover:bg-red-200">
                            <i class="fas fa-trash mr-1"></i> Delete
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Inventory section
async function loadInventory() {
    try {
        const [inventoryItems, categories, summary] = await Promise.all([
            inventoryAPI.getAll(),
            inventoryAPI.getCategories(),
            inventoryAPI.getSummary()
        ]);
        
        currentData.inventoryItems = inventoryItems;
        currentData.inventoryCategories = categories;
        currentData.inventorySummary = summary;

        const inventoryHTML = generateInventoryHTML(inventoryItems, categories, summary);
        mainContent.innerHTML = inventoryHTML;

        setupInventoryEventListeners();
    } catch (error) {
        throw error;
    }
}

// Staff section
async function loadStaff() {
    try {
        const [staffMembers, positions, summary] = await Promise.all([
            staffAPI.getAll({ active_only: false }),
            staffAPI.getPositions(),
            staffAPI.getSummary()
        ]);
        
        currentData.staffMembers = staffMembers;
        currentData.positions = positions;
        currentData.staffSummary = summary;

        const staffHTML = generateStaffHTML(staffMembers, positions, summary);
        mainContent.innerHTML = staffHTML;

        setupStaffEventListeners();
    } catch (error) {
        throw error;
    }
}

// Utility functions
function showLoading() {
    mainContent.innerHTML = `
        <div class="flex items-center justify-center h-64">
            <div class="text-center">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
                <p class="text-gray-600">Loading...</p>
            </div>
        </div>
    `;
}

function showError(message) {
    mainContent.innerHTML = `
        <div class="flex items-center justify-center h-64">
            <div class="text-center">
                <i class="fas fa-exclamation-triangle text-red-500 text-4xl mb-4"></i>
                <p class="text-red-600 font-medium">${message}</p>
                <button onclick="loadSection(currentSection)" class="mt-4 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded">
                    Try Again
                </button>
            </div>
        </div>
    `;
}

// Table generation functions for dashboard
function generateRecentOrdersTable(orders) {
    if (!orders || orders.length === 0) {
        return '<p class="text-gray-500 text-center py-4">No recent orders</p>';
    }

    return `
        <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order ID</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Table</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                    </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                    ${orders.map(order => `
                        <tr class="hover:bg-gray-50">
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">#${order.id}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${order.customer_name || 'Walk-in'}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${order.table_number}</td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColorClass(order.status)}">
                                    ${capitalizeWord(order.status)}
                                </span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">$${order.total_amount.toFixed(2)}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${formatDate(order.created_at)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function generateLowStockTable(items) {
    if (!items || items.length === 0) {
        return '<p class="text-gray-500 text-center py-4">No low stock items</p>';
    }

    return `
        <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Item</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Current Stock</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Minimum Stock</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                    ${items.map(item => `
                        <tr class="hover:bg-gray-50">
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="text-sm font-medium text-gray-900">${item.name}</div>
                                <div class="text-sm text-gray-500">${item.supplier || 'No supplier'}</div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                                    ${capitalizeWord(item.category)}
                                </span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${item.current_stock} ${item.unit}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${item.minimum_stock} ${item.unit}</td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                                    Low Stock
                                </span>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function getStatusColorClass(status) {
    const statusColors = {
        pending: 'bg-yellow-100 text-yellow-800',
        preparing: 'bg-blue-100 text-blue-800',
        ready: 'bg-green-100 text-green-800',
        served: 'bg-gray-100 text-gray-800',
        completed: 'bg-green-100 text-green-800',
        cancelled: 'bg-red-100 text-red-800'
    };
    return statusColors[status] || 'bg-gray-100 text-gray-800';
}

// Order modal generators
function generateCreateOrderModal() {
    return `
        <div class="p-6">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-xl font-bold text-gray-900">Create New Order</h2>
                <button onclick="closeModal()" class="text-gray-400 hover:text-gray-600">
                    <i class="fas fa-times text-xl"></i>
                </button>
            </div>
            
            <form id="createOrderForm" class="space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Table Number</label>
                        <input type="number" name="table_number" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Customer Name</label>
                        <input type="text" name="customer_name" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
                    <select name="status" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <option value="pending">Pending</option>
                        <option value="preparing">Preparing</option>
                        <option value="ready">Ready</option>
                        <option value="served">Served</option>
                        <option value="completed">Completed</option>
                    </select>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Notes</label>
                    <textarea name="notes" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"></textarea>
                </div>
                
                <div class="flex justify-end space-x-3 pt-4">
                    <button type="button" onclick="closeModal()" class="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300">
                        Cancel
                    </button>
                    <button type="submit" class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
                        Create Order
                    </button>
                </div>
            </form>
        </div>
    `;
}

function generateEditOrderModal(order) {
    return `
        <div class="p-6">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-xl font-bold text-gray-900">Edit Order #${order.id}</h2>
                <button onclick="closeModal()" class="text-gray-400 hover:text-gray-600">
                    <i class="fas fa-times text-xl"></i>
                </button>
            </div>
            
            <form id="editOrderForm" class="space-y-4">
                <input type="hidden" name="id" value="${order.id}">
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Table Number</label>
                        <input type="number" name="table_number" value="${order.table_number || ''}" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Customer Name</label>
                        <input type="text" name="customer_name" value="${order.customer_name || ''}" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Status</label>
                    <select name="status" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <option value="pending" ${order.status === 'pending' ? 'selected' : ''}>Pending</option>
                        <option value="preparing" ${order.status === 'preparing' ? 'selected' : ''}>Preparing</option>
                        <option value="ready" ${order.status === 'ready' ? 'selected' : ''}>Ready</option>
                        <option value="served" ${order.status === 'served' ? 'selected' : ''}>Served</option>
                        <option value="completed" ${order.status === 'completed' ? 'selected' : ''}>Completed</option>
                    </select>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Notes</label>
                    <textarea name="notes" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">${order.notes || ''}</textarea>
                </div>
                
                <div class="flex justify-end space-x-3 pt-4">
                    <button type="button" onclick="closeModal()" class="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300">
                        Cancel
                    </button>
                    <button type="submit" class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
                        Update Order
                    </button>
                </div>
            </form>
        </div>
    `;
}

// Menu item modal generators
function generateCreateMenuItemModal() {
    return `
        <div class="p-6">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-xl font-bold text-gray-900">Create New Menu Item</h2>
                <button onclick="closeModal()" class="text-gray-400 hover:text-gray-600">
                    <i class="fas fa-times text-xl"></i>
                </button>
            </div>
            
            <form id="createMenuItemForm" class="space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Name</label>
                        <input type="text" name="name" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Price</label>
                        <input type="number" name="price" step="0.01" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Category</label>
                        <select name="category" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            <option value="">Select Category</option>
                            <option value="appetizers">Appetizers</option>
                            <option value="mains">Main Courses</option>
                            <option value="desserts">Desserts</option>
                            <option value="beverages">Beverages</option>
                            <option value="cocktails">Cocktails</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Preparation Time (minutes)</label>
                        <input type="number" name="preparation_time" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
                    <textarea name="description" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"></textarea>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Ingredients</label>
                    <textarea name="ingredients" rows="2" placeholder="Comma-separated list of ingredients" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"></textarea>
                </div>
                
                <div class="flex items-center">
                    <input type="checkbox" name="is_active" checked class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded">
                    <label class="ml-2 block text-sm text-gray-900">Active</label>
                </div>
                
                <div class="flex justify-end space-x-3 pt-4">
                    <button type="button" onclick="closeModal()" class="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300">
                        Cancel
                    </button>
                    <button type="submit" class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
                        Create Menu Item
                    </button>
                </div>
            </form>
        </div>
    `;
}

function generateEditMenuItemModal(item) {
    return `
        <div class="p-6">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-xl font-bold text-gray-900">Edit Menu Item</h2>
                <button onclick="closeModal()" class="text-gray-400 hover:text-gray-600">
                    <i class="fas fa-times text-xl"></i>
                </button>
            </div>
            
            <form id="editMenuItemForm" class="space-y-4">
                <input type="hidden" name="id" value="${item.id}">
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Name</label>
                        <input type="text" name="name" value="${item.name}" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Price</label>
                        <input type="number" name="price" value="${item.price}" step="0.01" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Category</label>
                        <select name="category" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            <option value="">Select Category</option>
                            <option value="appetizers" ${item.category === 'appetizers' ? 'selected' : ''}>Appetizers</option>
                            <option value="mains" ${item.category === 'mains' ? 'selected' : ''}>Main Courses</option>
                            <option value="desserts" ${item.category === 'desserts' ? 'selected' : ''}>Desserts</option>
                            <option value="beverages" ${item.category === 'beverages' ? 'selected' : ''}>Beverages</option>
                            <option value="cocktails" ${item.category === 'cocktails' ? 'selected' : ''}>Cocktails</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Preparation Time (minutes)</label>
                        <input type="number" name="preparation_time" value="${item.preparation_time || ''}" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
                    <textarea name="description" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">${item.description || ''}</textarea>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Ingredients</label>
                    <textarea name="ingredients" rows="2" placeholder="Comma-separated list of ingredients" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">${item.ingredients || ''}</textarea>
                </div>
                
                <div class="flex items-center">
                    <input type="checkbox" name="is_active" ${item.is_active ? 'checked' : ''} class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded">
                    <label class="ml-2 block text-sm text-gray-900">Active</label>
                </div>
                
                <div class="flex justify-end space-x-3 pt-4">
                    <button type="button" onclick="closeModal()" class="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300">
                        Cancel
                    </button>
                    <button type="submit" class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
                        Update Menu Item
                    </button>
                </div>
            </form>
        </div>
    `;
}

// Inventory item modal generators
function generateCreateInventoryItemModal() {
    return `
        <div class="p-6">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-xl font-bold text-gray-900">Create New Inventory Item</h2>
                <button onclick="closeModal()" class="text-gray-400 hover:text-gray-600">
                    <i class="fas fa-times text-xl"></i>
                </button>
            </div>
            
            <form id="createInventoryItemForm" class="space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Name</label>
                        <input type="text" name="name" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Category</label>
                        <select name="category" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            <option value="">Select Category</option>
                            <option value="ingredients">Ingredients</option>
                            <option value="beverages">Beverages</option>
                            <option value="alcohol">Alcohol</option>
                            <option value="supplies">Supplies</option>
                            <option value="cleaning">Cleaning</option>
                        </select>
                    </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Current Stock</label>
                        <input type="number" name="current_stock" step="0.01" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Minimum Stock</label>
                        <input type="number" name="minimum_stock" step="0.01" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Unit</label>
                        <select name="unit" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            <option value="">Select Unit</option>
                            <option value="kg">Kilograms</option>
                            <option value="g">Grams</option>
                            <option value="l">Liters</option>
                            <option value="ml">Milliliters</option>
                            <option value="pieces">Pieces</option>
                            <option value="bottles">Bottles</option>
                            <option value="cans">Cans</option>
                        </select>
                    </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Cost per Unit</label>
                        <input type="number" name="cost_per_unit" step="0.01" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Supplier</label>
                        <input type="text" name="supplier" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
                    <textarea name="description" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"></textarea>
                </div>
                
                <div class="flex justify-end space-x-3 pt-4">
                    <button type="button" onclick="closeModal()" class="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300">
                        Cancel
                    </button>
                    <button type="submit" class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
                        Create Inventory Item
                    </button>
                </div>
            </form>
        </div>
    `;
}

function generateEditInventoryItemModal(item) {
    return `
        <div class="p-6">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-xl font-bold text-gray-900">Edit Inventory Item</h2>
                <button onclick="closeModal()" class="text-gray-400 hover:text-gray-600">
                    <i class="fas fa-times text-xl"></i>
                </button>
            </div>
            
            <form id="editInventoryItemForm" class="space-y-4">
                <input type="hidden" name="id" value="${item.id}">
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Name</label>
                        <input type="text" name="name" value="${item.name}" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Category</label>
                        <select name="category" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            <option value="">Select Category</option>
                            <option value="ingredients" ${item.category === 'ingredients' ? 'selected' : ''}>Ingredients</option>
                            <option value="beverages" ${item.category === 'beverages' ? 'selected' : ''}>Beverages</option>
                            <option value="alcohol" ${item.category === 'alcohol' ? 'selected' : ''}>Alcohol</option>
                            <option value="supplies" ${item.category === 'supplies' ? 'selected' : ''}>Supplies</option>
                            <option value="cleaning" ${item.category === 'cleaning' ? 'selected' : ''}>Cleaning</option>
                        </select>
                    </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Current Stock</label>
                        <input type="number" name="current_stock" value="${item.current_stock}" step="0.01" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Minimum Stock</label>
                        <input type="number" name="minimum_stock" value="${item.minimum_stock}" step="0.01" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Unit</label>
                        <select name="unit" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            <option value="">Select Unit</option>
                            <option value="kg" ${item.unit === 'kg' ? 'selected' : ''}>Kilograms</option>
                            <option value="g" ${item.unit === 'g' ? 'selected' : ''}>Grams</option>
                            <option value="l" ${item.unit === 'l' ? 'selected' : ''}>Liters</option>
                            <option value="ml" ${item.unit === 'ml' ? 'selected' : ''}>Milliliters</option>
                            <option value="pieces" ${item.unit === 'pieces' ? 'selected' : ''}>Pieces</option>
                            <option value="bottles" ${item.unit === 'bottles' ? 'selected' : ''}>Bottles</option>
                            <option value="cans" ${item.unit === 'cans' ? 'selected' : ''}>Cans</option>
                        </select>
                    </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Cost per Unit</label>
                        <input type="number" name="cost_per_unit" value="${item.cost_per_unit || ''}" step="0.01" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Supplier</label>
                        <input type="text" name="supplier" value="${item.supplier || ''}" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Description</label>
                    <textarea name="description" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">${item.description || ''}</textarea>
                </div>
                
                <div class="flex justify-end space-x-3 pt-4">
                    <button type="button" onclick="closeModal()" class="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300">
                        Cancel
                    </button>
                    <button type="submit" class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
                        Update Inventory Item
                    </button>
                </div>
            </form>
        </div>
    `;
}

// Staff member modal generators
function generateCreateStaffMemberModal() {
    return `
        <div class="p-6">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-xl font-bold text-gray-900">Create New Staff Member</h2>
                <button onclick="closeModal()" class="text-gray-400 hover:text-gray-600">
                    <i class="fas fa-times text-xl"></i>
                </button>
            </div>
            
            <form id="createStaffMemberForm" class="space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">First Name</label>
                        <input type="text" name="first_name" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Last Name</label>
                        <input type="text" name="last_name" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
                        <input type="email" name="email" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Phone</label>
                        <input type="tel" name="phone" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Position</label>
                        <select name="position" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            <option value="">Select Position</option>
                            <option value="manager">Manager</option>
                            <option value="chef">Chef</option>
                            <option value="cook">Cook</option>
                            <option value="waiter">Waiter</option>
                            <option value="bartender">Bartender</option>
                            <option value="host">Host</option>
                            <option value="cleaner">Cleaner</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Hourly Rate</label>
                        <input type="number" name="hourly_rate" step="0.01" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Address</label>
                    <textarea name="address" rows="2" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"></textarea>
                </div>
                
                <div class="flex items-center">
                    <input type="checkbox" name="is_active" checked class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded">
                    <label class="ml-2 block text-sm text-gray-900">Active</label>
                </div>
                
                <div class="flex justify-end space-x-3 pt-4">
                    <button type="button" onclick="closeModal()" class="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300">
                        Cancel
                    </button>
                    <button type="submit" class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
                        Create Staff Member
                    </button>
                </div>
            </form>
        </div>
    `;
}

function generateEditStaffMemberModal(member) {
    return `
        <div class="p-6">
            <div class="flex justify-between items-center mb-6">
                <h2 class="text-xl font-bold text-gray-900">Edit Staff Member</h2>
                <button onclick="closeModal()" class="text-gray-400 hover:text-gray-600">
                    <i class="fas fa-times text-xl"></i>
                </button>
            </div>
            
            <form id="editStaffMemberForm" class="space-y-4">
                <input type="hidden" name="id" value="${member.id}">
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">First Name</label>
                        <input type="text" name="first_name" value="${member.first_name}" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Last Name</label>
                        <input type="text" name="last_name" value="${member.last_name}" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
                        <input type="email" name="email" value="${member.email}" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Phone</label>
                        <input type="tel" name="phone" value="${member.phone || ''}" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Position</label>
                        <select name="position" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                            <option value="">Select Position</option>
                            <option value="manager" ${member.position === 'manager' ? 'selected' : ''}>Manager</option>
                            <option value="chef" ${member.position === 'chef' ? 'selected' : ''}>Chef</option>
                            <option value="cook" ${member.position === 'cook' ? 'selected' : ''}>Cook</option>
                            <option value="waiter" ${member.position === 'waiter' ? 'selected' : ''}>Waiter</option>
                            <option value="bartender" ${member.position === 'bartender' ? 'selected' : ''}>Bartender</option>
                            <option value="host" ${member.position === 'host' ? 'selected' : ''}>Host</option>
                            <option value="cleaner" ${member.position === 'cleaner' ? 'selected' : ''}>Cleaner</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Hourly Rate</label>
                        <input type="number" name="hourly_rate" value="${member.hourly_rate || ''}" step="0.01" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                    </div>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Address</label>
                    <textarea name="address" rows="2" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">${member.address || ''}</textarea>
                </div>
                
                <div class="flex items-center">
                    <input type="checkbox" name="is_active" ${member.is_active ? 'checked' : ''} class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded">
                    <label class="ml-2 block text-sm text-gray-900">Active</label>
                </div>
                
                <div class="flex justify-end space-x-3 pt-4">
                    <button type="button" onclick="closeModal()" class="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300">
                        Cancel
                    </button>
                    <button type="submit" class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">
                        Update Staff Member
                    </button>
                </div>
            </form>
        </div>
    `;
}

// Complete Inventory and Staff HTML generators
function generateInventoryHTML(items, categories, summary) {
    return `
        <div class="space-y-6">
            <!-- Header -->
            <div class="flex justify-between items-center">
                <h2 class="text-2xl font-bold text-gray-900">Inventory Management</h2>
                <button onclick="openCreateInventoryItemModal()" class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center">
                    <i class="fas fa-plus mr-2"></i> Add Item
                </button>
            </div>

            <!-- Stats Cards -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div class="bg-white p-6 rounded-lg shadow">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-500 text-sm">Total Items</p>
                            <h3 class="text-2xl font-bold text-gray-900">${items.length}</h3>
                        </div>
                        <div class="bg-blue-100 p-3 rounded-full">
                            <i class="fas fa-boxes text-blue-600"></i>
                        </div>
                    </div>
                </div>
                
                <div class="bg-white p-6 rounded-lg shadow">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-500 text-sm">Low Stock Items</p>
                            <h3 class="text-2xl font-bold text-red-600">${summary.low_stock_items}</h3>
                        </div>
                        <div class="bg-red-100 p-3 rounded-full">
                            <i class="fas fa-exclamation-triangle text-red-600"></i>
                        </div>
                    </div>
                </div>
                
                <div class="bg-white p-6 rounded-lg shadow">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-500 text-sm">Total Value</p>
                            <h3 class="text-2xl font-bold text-gray-900">$${summary.total_value || '0.00'}</h3>
                        </div>
                        <div class="bg-green-100 p-3 rounded-full">
                            <i class="fas fa-dollar-sign text-green-600"></i>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Inventory Table -->
            <div class="bg-white rounded-lg shadow overflow-hidden">
                <div class="p-4 border-b border-gray-200">
                    <h3 class="font-semibold text-gray-900">Inventory Items</h3>
                </div>
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Item</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Current Stock</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Min Stock</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            ${items.map(item => `
                                <tr class="hover:bg-gray-50">
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <div class="text-sm font-medium text-gray-900">${item.name}</div>
                                        <div class="text-sm text-gray-500">${item.supplier || 'No supplier'}</div>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                                            ${item.category}
                                        </span>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                        ${item.current_stock} ${item.unit}
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                        ${item.minimum_stock} ${item.unit}
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        ${item.current_stock <= item.minimum_stock ? 
                                            '<span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">Low Stock</span>' :
                                            '<span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">In Stock</span>'
                                        }
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                        <button onclick="editInventoryItem(${item.id})" class="text-indigo-600 hover:text-indigo-900 mr-3">
                                            <i class="fas fa-edit"></i>
                                        </button>
                                        <button onclick="deleteInventoryItem(${item.id})" class="text-red-600 hover:text-red-900">
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
}

function generateStaffHTML(members, positions, summary) {
    return `
        <div class="space-y-6">
            <!-- Header -->
            <div class="flex justify-between items-center">
                <h2 class="text-2xl font-bold text-gray-900">Staff Management</h2>
                <button onclick="openCreateStaffMemberModal()" class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center">
                    <i class="fas fa-plus mr-2"></i> Add Staff Member
                </button>
            </div>

            <!-- Stats Cards -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div class="bg-white p-6 rounded-lg shadow">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-500 text-sm">Total Staff</p>
                            <h3 class="text-2xl font-bold text-gray-900">${summary.total_staff}</h3>
                        </div>
                        <div class="bg-blue-100 p-3 rounded-full">
                            <i class="fas fa-users text-blue-600"></i>
                        </div>
                    </div>
                </div>
                
                <div class="bg-white p-6 rounded-lg shadow">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-500 text-sm">Active Staff</p>
                            <h3 class="text-2xl font-bold text-green-600">${summary.active_staff}</h3>
                        </div>
                        <div class="bg-green-100 p-3 rounded-full">
                            <i class="fas fa-user-check text-green-600"></i>
                        </div>
                    </div>
                </div>
                
                <div class="bg-white p-6 rounded-lg shadow">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-500 text-sm">Positions</p>
                            <h3 class="text-2xl font-bold text-gray-900">${positions.length}</h3>
                        </div>
                        <div class="bg-purple-100 p-3 rounded-full">
                            <i class="fas fa-briefcase text-purple-600"></i>
                        </div>
                    </div>
                </div>
                
                <div class="bg-white p-6 rounded-lg shadow">
                    <div class="flex items-center justify-between">
                        <div>
                            <p class="text-gray-500 text-sm">Avg. Hourly Rate</p>
                            <h3 class="text-2xl font-bold text-gray-900">$${summary.average_hourly_rate || '0.00'}</h3>
                        </div>
                        <div class="bg-yellow-100 p-3 rounded-full">
                            <i class="fas fa-dollar-sign text-yellow-600"></i>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Staff Table -->
            <div class="bg-white rounded-lg shadow overflow-hidden">
                <div class="p-4 border-b border-gray-200">
                    <h3 class="font-semibold text-gray-900">Staff Members</h3>
                </div>
                <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Position</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Contact</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Hourly Rate</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            ${members.map(member => `
                                <tr class="hover:bg-gray-50">
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <div class="flex items-center">
                                            <div class="h-10 w-10 flex-shrink-0">
                                                <div class="h-10 w-10 rounded-full bg-indigo-600 flex items-center justify-center">
                                                    <span class="text-white font-medium">${member.first_name.charAt(0)}${member.last_name.charAt(0)}</span>
                                                </div>
                                            </div>
                                            <div class="ml-4">
                                                <div class="text-sm font-medium text-gray-900">${member.first_name} ${member.last_name}</div>
                                                <div class="text-sm text-gray-500">${member.email}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                                            ${member.position}
                                        </span>
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                        ${member.phone || 'No phone'}
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                        $${member.hourly_rate || '0.00'}/hr
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap">
                                        ${member.is_active ? 
                                            '<span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">Active</span>' :
                                            '<span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">Inactive</span>'
                                        }
                                    </td>
                                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                        <button onclick="editStaffMember(${member.id})" class="text-indigo-600 hover:text-indigo-900 mr-3">
                                            <i class="fas fa-edit"></i>
                                        </button>
                                        <button onclick="deleteStaffMember(${member.id})" class="text-red-600 hover:text-red-900">
                                            <i class="fas fa-trash"></i>
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
}

// Toggle functions for menu items
window.toggleMenuItemActive = async function(itemId) {
    try {
        await menuAPI.toggleActive(itemId);
        showNotification('Menu item status updated', 'success');
        loadSection(currentSection);
    } catch (error) {
        showNotification(error.message, 'error');
    }
};

window.deleteMenuItem = async function(itemId) {
    if (confirm('Are you sure you want to delete this menu item?')) {
        try {
            await menuAPI.delete(itemId);
            showNotification('Menu item deleted', 'success');
            loadSection(currentSection);
        } catch (error) {
            showNotification(error.message, 'error');
        }
    }
};

// Modal management functions
function openModal(content) {
    const modalContainer = document.getElementById('modalContainer');
    const modalContent = document.getElementById('modalContent');
    
    modalContent.innerHTML = content;
    modalContainer.classList.remove('hidden');
    
    // Setup modal event listeners
    setupModalEventListeners();
}

function closeModal() {
    const modalContainer = document.getElementById('modalContainer');
    modalContainer.classList.add('hidden');
}

function setupModalEventListeners() {
    const modalContainer = document.getElementById('modalContainer');
    
    // Close modal when clicking outside
    modalContainer.addEventListener('click', (e) => {
        if (e.target === modalContainer) {
            closeModal();
        }
    });
    
    // Close modal on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
}

// Placeholder functions for modals and complex operations
window.openCreateOrderModal = function() {
    openModal(generateCreateOrderModal());
};

window.openCreateMenuItemModal = function() {
    openModal(generateCreateMenuItemModal());
};

window.openCreateInventoryItemModal = function() {
    openModal(generateCreateInventoryItemModal());
};

window.openCreateStaffMemberModal = function() {
    openModal(generateCreateStaffMemberModal());
};

window.editOrder = function(orderId) {
    const order = currentData.orders?.find(o => o.id === orderId);
    if (order) {
        openModal(generateEditOrderModal(order));
    }
};

window.editMenuItem = function(itemId) {
    const item = currentData.menuItems?.find(i => i.id === itemId);
    if (item) {
        openModal(generateEditMenuItemModal(item));
    }
};

window.editInventoryItem = function(itemId) {
    const item = currentData.inventoryItems?.find(i => i.id === itemId);
    if (item) {
        openModal(generateEditInventoryItemModal(item));
    }
};

window.editStaffMember = function(staffId) {
    const member = currentData.staffMembers?.find(s => s.id === staffId);
    if (member) {
        openModal(generateEditStaffMemberModal(member));
    }
};

window.deleteOrder = async function(orderId) {
    if (confirm('Are you sure you want to delete this order?')) {
        try {
            await ordersAPI.delete(orderId);
            showNotification('Order deleted successfully', 'success');
            loadSection(currentSection);
        } catch (error) {
            showNotification(error.message, 'error');
        }
    }
};

window.deleteInventoryItem = async function(itemId) {
    if (confirm('Are you sure you want to delete this inventory item?')) {
        try {
            await inventoryAPI.delete(itemId);
            showNotification('Inventory item deleted successfully', 'success');
            loadSection(currentSection);
        } catch (error) {
            showNotification(error.message, 'error');
        }
    }
};

window.deleteStaffMember = async function(staffId) {
    if (confirm('Are you sure you want to delete this staff member?')) {
        try {
            await staffAPI.delete(staffId);
            showNotification('Staff member deleted successfully', 'success');
            loadSection(currentSection);
        } catch (error) {
            showNotification(error.message, 'error');
        }
    }
};

// Event listener functions
function setupOrderEventListeners() {
    // Add event listeners for order-specific functionality
    console.log('Order event listeners setup');
}

function setupMenuEventListeners() {
    // Add event listeners for menu-specific functionality
    console.log('Menu event listeners setup');
}

function setupInventoryEventListeners() {
    // Add event listeners for inventory-specific functionality
    console.log('Inventory event listeners setup');
}

function setupStaffEventListeners() {
    // Add event listeners for staff-specific functionality
    console.log('Staff event listeners setup');
}

// Global functions for button handlers
window.updateOrderStatus = async function(orderId, status) {
    try {
        await ordersAPI.updateStatus(orderId, status);
        await loadSection(currentSection); // Reload current section
        showNotification(`Order #${orderId} status updated to ${status}`, 'success');
    } catch (error) {
        showNotification(error.message, 'error');
    }
};
