class SavagePeachHeader extends HTMLElement {
    constructor() {
        super();
    }

    connectedCallback() {
        const basePath = this.getAttribute('base-path') || '.';
        const activePage = this.getAttribute('active-page') || '';

        this.innerHTML = `
            <nav>
                <a href="${basePath}/index.html" class="logo">
                    <span class="savage-text">Savage</span> <span class="peach-text">Peach</span>
                </a>
                <button class="hamburger" aria-label="Toggle navigation">
                    <span></span>
                    <span></span>
                    <span></span>
                </button>
                <div class="nav-links">
                    <a href="${basePath}/index.html" class="${activePage === 'home' ? 'active-link' : ''}">Home</a>
                    <a href="${basePath}/stories/index.html" class="${activePage === 'stories' ? 'peach-text' : ''}">Stories</a>
                    <a href="${basePath}/about.html" class="${activePage === 'about' ? 'active-link' : ''}">About</a>
                    <!-- Theme toggle will be appended here or logic handled below -->
                    <button id="theme-toggle" class="theme-toggle-btn" aria-label="Toggle theme"></button>
                </div>
            </nav>
        `;

        this.initializeMenu();
        this.initializeTheme();
    }

    initializeMenu() {
        const hamburger = this.querySelector('.hamburger');
        const navLinks = this.querySelector('.nav-links');

        if (hamburger && navLinks) {
            hamburger.addEventListener('click', () => {
                hamburger.classList.toggle('active');
                navLinks.classList.toggle('active');
            });

            // Close menu when a link is clicked
            navLinks.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', () => {
                    hamburger.classList.remove('active');
                    navLinks.classList.remove('active');
                });
            });
        }
    }

    initializeTheme() {
        const toggleBtn = this.querySelector('#theme-toggle');

        // Helper to update button icon
        const updateIcon = (theme) => {
            if (toggleBtn) {
                toggleBtn.textContent = theme === 'light' ? '☀️' : '🌙';
            }
        };

        // Check current theme
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
        updateIcon(currentTheme);

        toggleBtn.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme');
            const newTheme = current === 'light' ? 'dark' : 'light';

            if (newTheme === 'light') {
                document.documentElement.setAttribute('data-theme', 'light');
            } else {
                document.documentElement.removeAttribute('data-theme');
            }

            localStorage.setItem('theme', newTheme);
            updateIcon(newTheme);
        });

        // Listen for changes from other sources (if ThemeManager updates it)
        // Ideally we shouldn't have two sources of truth, but this component handles its own UI.
    }
}

customElements.define('sp-header', SavagePeachHeader);
