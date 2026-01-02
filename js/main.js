console.log("Savage Peach loaded.");

// Theme Management
const ThemeManager = {
    init() {
        this.applySavedTheme();

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
        } else {
            document.documentElement.removeAttribute('data-theme');
        }
        localStorage.setItem('theme', theme);

        // Update toggle button if present (it might be inside shadow DOM or component)
        const toggleBtn = document.getElementById('theme-toggle');
        if (toggleBtn) {
            toggleBtn.textContent = theme === 'light' ? '☀️' : '🌙';
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    ThemeManager.init();
});
