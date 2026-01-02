console.log("Savage Peach loaded.");

// Theme Management
const ThemeManager = {
    init() {
        this.toggleBtn = null;
        this.applySavedTheme();
        this.injectToggle();

        // Listen for system changes
        window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', e => {
            if (!localStorage.getItem('theme')) {
                this.setTheme(e.matches ? 'light' : 'dark');
            }
        });
    },

    applySavedTheme() {
        const saved = localStorage.getItem('theme');
        const systemLikesLight = window.matchMedia('(prefers-color-scheme: light)').matches;

        if (saved === 'light' || (!saved && systemLikesLight)) {
            this.setTheme('light');
        } else {
            this.setTheme('dark');
        }
    },

    setTheme(theme) {
        if (theme === 'light') {
            document.documentElement.setAttribute('data-theme', 'light');
            if (this.toggleBtn) this.toggleBtn.textContent = '☀\uFE0E'; // Sun
        } else {
            document.documentElement.removeAttribute('data-theme');
            if (this.toggleBtn) this.toggleBtn.textContent = '🌙'; // Moon
        }
        localStorage.setItem('theme', theme);
    },

    injectToggle() {
        // Find nav-links to append to
        const navLinks = document.querySelector('.nav-links');
        if (!navLinks) return;

        // Check if button already exists (if manual HTML added later)
        if (document.getElementById('theme-toggle')) return;

        const btn = document.createElement('button');
        btn.id = 'theme-toggle';
        btn.className = 'theme-toggle-btn';
        btn.ariaLabel = 'Toggle theme';
        // Set initial icon based on current state
        const isLight = document.documentElement.getAttribute('data-theme') === 'light';
        btn.textContent = isLight ? '☀\uFE0E' : '🌙';

        btn.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme');
            this.setTheme(current === 'light' ? 'dark' : 'light');
        });

        navLinks.appendChild(btn);
        this.toggleBtn = btn;
    }
};

document.addEventListener('DOMContentLoaded', () => {
    ThemeManager.init();
});
