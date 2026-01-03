/**
 * Loads and renders news from data/news.json
 * @param {Object} options Configuration options
 * @param {string} options.containerId ID of the container to render news into
 * @param {number} [options.limit] Maximum number of news items to show (optional)
 * @param {string} options.basePath Path to the root of the site (e.g. '.' or '..')
 */
async function loadNews({ containerId, limit = null, basePath = '.' }) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container with ID '${containerId}' not found.`);
        return;
    }

    try {
        const response = await fetch(`${basePath}/data/news.json`);
        if (!response.ok) {
            throw new Error(`Failed to load news: ${response.statusText}`);
        }

        let newsItems = await response.json();

        // Helper to parse date string YYYY-MM-DD to local Date object
        const parseDate = (str) => {
            const [y, m, d] = str.split('-').map(Number);
            return new Date(y, m - 1, d);
        };

        // Sort by date (descending)
        newsItems.sort((a, b) => parseDate(b.date) - parseDate(a.date));

        // Apply limit if specified
        if (limit) {
            newsItems = newsItems.slice(0, limit);
        }

        // Render items sequentially to maintain order (since we might need async fetch for md)
        container.innerHTML = ''; // Clear loading state

        for (const item of newsItems) {
            const options = { year: 'numeric', month: 'short', day: 'numeric' };
            const dateStr = parseDate(item.date).toLocaleDateString('en-US', options);

            let contentHtml = '';

            if (item.src) {
                try {
                    const mdResponse = await fetch(`${basePath}/${item.src}`);
                    if (mdResponse.ok) {
                        const mdText = await mdResponse.text();
                        // Use marked.parse if available, otherwise fallback to plain text
                        contentHtml = (window.marked && window.marked.parse)
                            ? window.marked.parse(mdText)
                            : `<p>${mdText}</p>`;
                    } else {
                        contentHtml = '<p><em>Error loading content.</em></p>';
                    }
                } catch (e) {
                    console.error('Failed to load news content:', e);
                    contentHtml = '<p><em>Error loading content.</em></p>';
                }
            } else {
                contentHtml = item.content;
                // Simple link handling for legacy items
                if (item.link) {
                    const linkPath = item.link.startsWith('http') ? item.link : `${basePath}/${item.link}`;
                    contentHtml += ` <a href="${linkPath}" class="peach-text">Read more &rarr;</a>`;
                }
            }

            const itemHtml = `
            <div class="news-item">
                <div class="news-date">${dateStr}</div>
                ${item.title ? `<h3 class="news-title">${item.title}</h3>` : ''}
                <div class="news-content">${contentHtml}</div>
            </div>
            `;

            container.insertAdjacentHTML('beforeend', itemHtml);
        }

    } catch (error) {
        console.error('Error loading news:', error);
        container.innerHTML = '<p class="text-center" style="color: var(--text-secondary)">No news at this time.</p>';
    }
}
