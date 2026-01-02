import sys
import os
import re
import argparse
import datetime

# Try to import required libraries
try:
    import markdown
    import yaml
except ImportError as e:
    print(f"Error: Missing required libraries. Please install them using:\npip install markdown pyyaml")
    sys.exit(1)

TEMPLATE = """<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="utf-8" />
    <meta content="width=device-width, initial-scale=1.0" name="viewport" />
    <title>{title} | Savage Peach</title>
    <meta content="{description}" name="description" />
    <link href="../css/style.css" rel="stylesheet" />
    <link href="../css/story.css" rel="stylesheet" />
</head>

<body>
    <div id="progress-container">
        <div id="progress-bar"></div>
    </div>

    <sp-header base-path=".." active-page="stories"></sp-header>
    <article class="story-container section">
        <header>
            <h1>{title}</h1>
            <div class="story-meta">
                Published on {date} &bull; {read_time}
            </div>
        </header>

        <button id="story-nav-toggle" class="mobile-only" aria-label="Toggle Navigation">
            <span class="icon">&#128366;</span>
        </button>
        <aside id="story-nav-menu">
            <h3>Jump to Chapter</h3>
            <ul>
                {toc_items}
            </ul>
        </aside>

        <div class="story-content">
            {content}
        </div>

        <div class="story-nav">
            <a href="index.html" class="btn">Back to Archive</a>
        </div>
    </article>

    <footer>
        <p>&copy; 2026 Savage Peach. All rights reserved.</p>
    </footer>

    <script src="../js/sp-header.js"></script>
    <script src="../js/main.js"></script>
    <script>
        // Progress Bar & ScrollSpy Logic
        window.addEventListener('scroll', () => {{
            const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
            const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (scrollTop / scrollHeight) * 100;
            document.getElementById('progress-bar').style.width = scrolled + '%';
        }});
        
        // Mobile Nav Toggle
        const storyNavToggle = document.getElementById('story-nav-toggle');
        const storyNavMenu = document.getElementById('story-nav-menu');
        
        if (storyNavToggle && storyNavMenu) {{
            storyNavToggle.addEventListener('click', (e) => {{
                e.stopPropagation();
                storyNavMenu.classList.toggle('active');
            }});
            
            document.addEventListener('click', (e) => {{
                if (!storyNavMenu.contains(e.target) && !storyNavToggle.contains(e.target)) {{
                    storyNavMenu.classList.remove('active');
                }}
            }});
        }}
    </script>
</body>
</html>"""

def parse_frontmatter(content):
    """
    Parses YAML frontmatter from the content.
    Returns (metadata_dict, remaining_content).
    """
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                metadata = yaml.safe_load(parts[1])
                return metadata, parts[2].strip()
            except yaml.YAMLError as e:
                print(f"Warning: Error parsing YAML frontmatter: {e}")
                return {}, content
    return {}, content

def generate_toc(html_content):
    """
    Scans HTML content for <h2> headers and generates TOC list items.
    Updates the html_content to include IDs for the headers if missing.
    """
    # Simple regex to find h2 tags
    # We will use a more robust approach: replace standard headers with headers containing IDs
    
    toc_html = ""
    
    def replacer(match):
        nonlocal toc_html
        header_text = match.group(1)
        # Create a slug from text
        slug = re.sub(r'[^a-z0-9]+', '-', header_text.lower()).strip('-')
        
        toc_html += f'<li><a href="#{slug}">{header_text}</a></li>\n'
        return f'<h2 id="{slug}">{header_text}</h2>'

    # Regex to match <h2>Your Title</h2>
    new_content = re.sub(r'<h2>(.*?)</h2>', replacer, html_content)
    
    if not toc_html:
         # Fallback if no h2s found, maybe empty or different structure
         toc_html = "<!-- No headers found -->"
         
    return toc_html, new_content

def main():
    parser = argparse.ArgumentParser(description="Convert Markdown story to HTML")
    parser.add_argument("input_file", help="Path to input Markdown file")
    parser.add_argument("-o", "--output", help="Path to output HTML file (default: same name as input in same dir)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        sys.exit(1)
        
    # Read input file
    with open(args.input_file, 'r', encoding='utf-8') as f:
        raw_content = f.read()
        
    # Python 3.9+ encoding issues sometimes occur with default open, utf-8 specified above
    
    # Parse Metadata
    meta, body_md = parse_frontmatter(raw_content)
    
    # Defaults
    title = meta.get('title', 'Untitled Story')
    description = meta.get('description', '')
    date = meta.get('date', datetime.date.today().strftime("%b %d, %Y"))
    read_time = meta.get('read_time', '5 min read')
    prev_story = meta.get('previous_story', 'index.html')
    next_story = meta.get('next_story', 'index.html')
    
    # Convert Body to HTML
    # We enable 'extra' for better markdown support (tables, attr_list etc if needed)
    html_body = markdown.markdown(body_md, extensions=['extra', 'smarty'])
    
    # Generate TOC and inject IDs
    toc_items, final_content = generate_toc(html_body)
    
    # Fill Template
    output_html = TEMPLATE.format(
        title=title,
        description=description,
        date=date,
        read_time=read_time,
        content=final_content,
        toc_items=toc_items
    )
    
    # Determine output filename
    if args.output:
        out_path = args.output
    else:
        out_path = os.path.splitext(args.input_file)[0] + '.html'
        
    # Write output
    try:
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output_html)
        print(f"Successfully created: {out_path}")
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    main()
