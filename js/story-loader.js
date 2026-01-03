/**
 * Loads and renders stories from data/stories.json
 * @param {Object} options Configuration options
 * @param {string} options.containerId ID of the container to render stories into
 * @param {number} [options.limit] Maximum number of stories to show (optional)
 * @param {string} options.basePath Path to the root of the site (e.g. '.' or '..')
 */
async function loadStories({ containerId, limit = null, basePath = '.', featuredOnly = false }) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container with ID '${containerId}' not found.`);
        return;
    }

    try {
        const response = await fetch(`${basePath}/data/stories.json`);
        if (!response.ok) {
            throw new Error(`Failed to load stories: ${response.statusText}`);
        }

        let allStories = await response.json();

        // Filter by featured if requested
        if (featuredOnly) {
            allStories = allStories.filter(story => story.featured);
        }

        // Helper to parse date string YYYY-MM-DD to local Date object
        const parseDate = (str) => {
            const [y, m, d] = str.split('-').map(Number);
            return new Date(y, m - 1, d);
        };

        // Sort by create_date (descending)
        let stories = allStories.sort((a, b) => parseDate(b.create_date) - parseDate(a.create_date));

        // Apply limit if specified
        if (limit) {
            stories = stories.slice(0, limit);
        }

        // Render
        container.innerHTML = stories.map(story => {
            // Format dates
            const options = { year: 'numeric', month: 'short', day: '2-digit' };
            const createDate = parseDate(story.create_date).toLocaleDateString('en-US', options);

            let dateHtml = createDate;

            // Add status/update info
            if (story.complete) {
                dateHtml += '<br>Complete';
            } else if (story.update_date && story.update_date !== story.create_date) {
                const updateDate = parseDate(story.update_date).toLocaleDateString('en-US', options);
                dateHtml += `<br>Last Update ${updateDate}`;
            }

            // Construct link (remove stories/ prefix if it exists in the data, then re-apply correctly based on base path)
            // The data has "stories/filename.html". 
            // If we are at root (basePath='.'), we want "stories/filename.html".
            // If we are in stories/ (basePath='..'), we want "filename.html". 

            // Actually, simpler logic:
            // Data = "stories/filename.html"
            // Root needs: "stories/filename.html" -> basePath + "/" + link -> "./stories/filename.html" (works)
            // Stories subdir needs: "../stories/filename.html" (works)
            // BUT, stories/index.html usually wants just "filename.html" or must traverse up then down?
            // ".." + "/stories/filename.html" -> traverses up to root, then down to stories. Valid.

            const link = `${basePath}/${story.link}`;

            return `
            <article class="story-card">
                <span class="date">${dateHtml}</span>
                <h3>${story.title}</h3>
                <p>${story.summary}</p>
                <a href="${link}" class="peach-text">Read Story &rarr;</a>
            </article>
            `;
        }).join('');

    } catch (error) {
        console.error('Error loading stories:', error);
        container.innerHTML = '<p class="text-center">Unable to load stories at this time.</p>';
    }
}
