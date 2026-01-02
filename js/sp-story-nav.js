class StoryNav extends HTMLElement {
    constructor() {
        super();
    }

    connectedCallback() {
        this.render();
        this.initializeEvents();
        this.highlightActiveLink();

        // Listen for hash changes to update active link
        window.addEventListener('hashchange', () => this.highlightActiveLink());

        // Listen for scroll to update active link (scroll spy)
        window.addEventListener('scroll', () => {
            // Debounce for performance could be added here if needed
            this.handleScrollSpy();
        });
    }

    get menuItems() {
        try {
            return JSON.parse(this.getAttribute('menu-items') || '[]');
        } catch (e) {
            console.error('Error parsing menu-items attribute:', e);
            return [];
        }
    }

    render() {
        const items = this.menuItems;
        const listItems = items.map(item =>
            `<li><a href="${item.href}">${item.text}</a></li>`
        ).join('');

        this.innerHTML = `
            <button id="story-nav-toggle" class="mobile-only" aria-label="Toggle Navigation">
                <span class="icon">&#128366;</span>
            </button>
            <aside id="story-nav-menu">
                <h3>Jump to Chapter</h3>
                <ul>
                    ${listItems}
                </ul>
            </aside>
        `;
    }

    initializeEvents() {
        const toggleBtn = this.querySelector('#story-nav-toggle');
        const menu = this.querySelector('#story-nav-menu');

        if (toggleBtn && menu) {
            toggleBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                menu.classList.toggle('open');
            });

            document.addEventListener('click', (e) => {
                if (!menu.contains(e.target) && !toggleBtn.contains(e.target)) {
                    menu.classList.remove('open');
                }
            });

            // Close menu when a link is clicked (mobile UX)
            menu.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', () => {
                    menu.classList.remove('open');
                });
            });
        }
    }

    highlightActiveLink() {
        const currentHash = window.location.hash;
        const links = this.querySelectorAll('#story-nav-menu a');

        if (!links) return;

        links.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === currentHash) {
                link.classList.add('active');
            }
        });
    }

    handleScrollSpy() {
        // Simple scroll spy logic
        const sections = document.querySelectorAll('.story-content h2, .story-content h3'); // Assuming these are the targets
        const links = this.querySelectorAll('#story-nav-menu a');

        if (sections.length === 0) return;

        let current = '';
        const scrollPosition = (document.documentElement.scrollTop || document.body.scrollTop) + 100; // Offset

        sections.forEach(section => {
            if (section.offsetTop <= scrollPosition) {
                current = '#' + section.getAttribute('id');
            }
        });

        if (current) {
            links.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === current) {
                    link.classList.add('active');
                }
            });
        }
    }
}

customElements.define('sp-story-nav', StoryNav);
