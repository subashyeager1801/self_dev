/**
 * SelfDev — Core JavaScript
 * Theme toggle, toast auto-dismiss, CSRF helper, utility functions.
 */

// ================================================================
// 1. THEME MANAGEMENT
// ================================================================
const ThemeManager = {
    init() {
        const saved = localStorage.getItem('selfdev-theme') || 'dark';
        this.set(saved, false);

        const toggle = document.getElementById('themeToggle');
        if (toggle) {
            toggle.addEventListener('click', () => {
                const current = document.documentElement.getAttribute('data-theme');
                this.set(current === 'dark' ? 'light' : 'dark', true);
            });
        }
    },

    set(theme, animate) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('selfdev-theme', theme);

        const icon = document.getElementById('themeIcon');
        if (icon) {
            icon.textContent = theme === 'dark' ? '🌙' : '☀️';
            if (animate) {
                icon.style.transform = 'rotate(360deg)';
                setTimeout(() => { icon.style.transform = ''; }, 300);
            }
        }
    }
};

// ================================================================
// 2. TOAST / MESSAGE AUTO-DISMISS
// ================================================================
const ToastManager = {
    init() {
        document.querySelectorAll('.message[data-auto-dismiss]').forEach(msg => {
            const delay = parseInt(msg.dataset.autoDismiss) || 5000;
            setTimeout(() => {
                msg.style.opacity = '0';
                msg.style.transform = 'translateX(100%)';
                setTimeout(() => msg.remove(), 300);
            }, delay);
        });
    }
};

// ================================================================
// 3. CSRF TOKEN HELPER
// ================================================================
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

/**
 * Fetch wrapper with CSRF token.
 */
async function apiFetch(url, options = {}) {
    const defaults = {
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
    };

    const config = { ...defaults, ...options };
    if (options.headers) {
        config.headers = { ...defaults.headers, ...options.headers };
    }

    try {
        const response = await fetch(url, config);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        }
        return await response.text();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * POST form data via fetch.
 */
async function postForm(url, formData) {
    return fetch(url, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrftoken },
        credentials: 'same-origin',
        body: formData,
    });
}

// ================================================================
// 4. UI UTILITIES
// ================================================================

/**
 * Show a toast notification.
 */
function showToast(message, type = 'info') {
    let container = document.getElementById('messages');
    if (!container) {
        container = document.createElement('div');
        container.className = 'messages';
        container.id = 'messages';
        document.body.appendChild(container);
    }

    const icons = { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' };
    const toast = document.createElement('div');
    toast.className = `message message-${type}`;
    toast.innerHTML = `${icons[type] || 'ℹ'} ${message}`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

/**
 * Animate a number counting up.
 */
function animateNumber(element, target, duration = 800) {
    const start = parseInt(element.textContent) || 0;
    const increment = (target - start) / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= target) || (increment < 0 && current <= target)) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = Math.round(current);
    }, 16);
}

/**
 * Debounce function.
 */
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

/**
 * Format date to readable string.
 */
function formatDate(date) {
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(date).toLocaleDateString('en-IN', options);
}

/**
 * Get time-based greeting.
 */
function getGreeting() {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 17) return 'Good Afternoon';
    if (hour < 21) return 'Good Evening';
    return 'Good Night';
}

// ================================================================
// 5. CIRCULAR PROGRESS COMPONENT
// ================================================================
function createCircularProgress(containerId, percentage, size = 120) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const radius = (size - 16) / 2;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (percentage / 100) * circumference;

    container.innerHTML = `
        <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
            <defs>
                <linearGradient id="progressGradient-${containerId}" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#6C5CE7" />
                    <stop offset="100%" style="stop-color:#A29BFE" />
                </linearGradient>
            </defs>
            <circle class="bg" cx="${size/2}" cy="${size/2}" r="${radius}" />
            <circle class="fill"
                cx="${size/2}" cy="${size/2}" r="${radius}"
                stroke="url(#progressGradient-${containerId})"
                stroke-dasharray="${circumference}"
                stroke-dashoffset="${offset}" />
        </svg>
        <div class="value">
            <div class="number">${percentage}</div>
            <div class="label">score</div>
        </div>
    `;
}

// ================================================================
// 6. INITIALIZE ON DOM READY
// ================================================================
document.addEventListener('DOMContentLoaded', () => {
    ThemeManager.init();
    ToastManager.init();
});
