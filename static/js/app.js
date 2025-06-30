// Main JavaScript file for AI Surveillance Dashboard

// Dark Mode Functionality
class DarkModeManager {
    constructor() {
        this.init();
    }

    init() {
        // Load saved theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            this.setTheme(savedTheme);
        }

        // Set up toggle button
        const toggleBtn = document.getElementById('darkModeToggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggleTheme());
        }
    }

    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
    }

    setTheme(theme) {
        document.documentElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Update toggle button
        const toggleBtn = document.getElementById('darkModeToggle');
        const icon = document.getElementById('darkModeIcon');
        const text = document.getElementById('darkModeText');
        
        if (toggleBtn && icon && text) {
            if (theme === 'dark') {
                icon.className = 'fas fa-sun';
                text.textContent = 'Light Mode';
                toggleBtn.className = 'btn btn-outline-warning btn-sm';
            } else {
                icon.className = 'fas fa-moon';
                text.textContent = 'Dark Mode';
                toggleBtn.className = 'btn btn-outline-light btn-sm';
            }
        }
    }
}

// Status Management
class StatusManager {
    constructor() {
        this.statusColors = {
            safe: '#198754',
            warning: '#ffc107',
            alert: '#dc3545',
            offline: '#6c757d'
        };
    }

    getStatusIcon(status) {
        const icons = {
            safe: 'fa-check-circle',
            warning: 'fa-exclamation-triangle',
            alert: 'fa-exclamation-circle',
            offline: 'fa-times-circle'
        };
        return icons[status] || 'fa-question-circle';
    }

    getStatusText(status) {
        const texts = {
            safe: 'No Threat',
            warning: 'Warning',
            alert: 'Alert',
            offline: 'Offline'
        };
        return texts[status] || 'Unknown';
    }

    getStatusColor(status) {
        return this.statusColors[status] || this.statusColors.offline;
    }
}

// Notification System
class NotificationManager {
    constructor() {
        this.container = this.createContainer();
    }

    createContainer() {
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1050;
                max-width: 350px;
            `;
            document.body.appendChild(container);
        }
        return container;
    }

    show(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show mb-2`;
        notification.style.cssText = `
            animation: slideInRight 0.3s ease-out;
            box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
        `;
        
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas ${this.getIcon(type)} me-2"></i>
                <span>${message}</span>
                <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert"></button>
            </div>
        `;

        this.container.appendChild(notification);

        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.style.animation = 'slideOutRight 0.3s ease-in';
                    setTimeout(() => {
                        if (notification.parentNode) {
                            notification.remove();
                        }
                    }, 300);
                }
            }, duration);
        }

        return notification;
    }

    getIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            warning: 'fa-exclamation-triangle',
            danger: 'fa-exclamation-circle',
            info: 'fa-info-circle'
        };
        return icons[type] || 'fa-info-circle';
    }
}

// Initialize managers
let darkModeManager;
let statusManager;
let notificationManager;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    darkModeManager = new DarkModeManager();
    statusManager = new StatusManager();
    notificationManager = new NotificationManager();
    
    // Add custom animations
    addCustomAnimations();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Add keyboard shortcuts
    addKeyboardShortcuts();
});

// Add custom CSS animations
function addCustomAnimations() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
        
        .card-hover-effect {
            transition: all 0.3s ease;
        }
        
        .card-hover-effect:hover {
            transform: translateY(-5px);
            box-shadow: 0 1rem 2rem rgba(0, 0, 0, 0.1);
        }
    `;
    document.head.appendChild(style);
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Add keyboard shortcuts
function addKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + D for dark mode toggle
        if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
            e.preventDefault();
            darkModeManager.toggleTheme();
        }
        
        // Ctrl/Cmd + R for refresh
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            if (typeof refreshAllModules === 'function') {
                refreshAllModules();
            }
        }
    });
}

// Utility functions
function getCurrentTimestamp() {
    return new Date().toLocaleString();
}

function formatTimestamp(timestamp) {
    return new Date(timestamp).toLocaleString();
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// Export for global access
window.showNotification = function(message, type = 'info', duration = 3000) {
    if (notificationManager) {
        notificationManager.show(message, type, duration);
    }
};

window.toggleDarkMode = function() {
    if (darkModeManager) {
        darkModeManager.toggleTheme();
    }
};