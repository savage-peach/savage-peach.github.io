class StoryFooter extends HTMLElement {
    constructor() {
        super();
    }

    connectedCallback() {
        this.render();
    }

    render() {
        // Hardcoded link to ../index.html based on requirement to link to "My Stories" page at stories/index.html
        // Since story files are in stories/, linking to ../index.html would go to root index.html
        // Wait, the user said: "I'd like this link to go to the main 'My Stories' page at stories/index.html"
        // If the story is at /stories/story.html, then stories/index.html is just ./index.html
        // Let's check where stories/index.html is relative to stories/ai-girlfriend.html
        // Both are in the same directory: stories/
        // So the link should be "index.html"

        this.innerHTML = `
            <div class="story-nav">
                <a href="index.html" class="btn">Back to Archive</a>
            </div>
            <footer>
                <p>&copy; 2026 Savage Peach. All rights reserved.</p>
            </footer>
        `;
    }
}

customElements.define('sp-story-footer', StoryFooter);
