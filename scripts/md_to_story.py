import sys
import os
import re
import argparse
import datetime

# Try to import required libraries
try:
    import markdown
    import yaml
    from bs4 import BeautifulSoup
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
    <script src="../js/theme-init.js"></script>
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

        <sp-story-nav menu-items='{toc_items}'></sp-story-nav>

        <div class="story-content">
            {content}
            <div class="license-note">
                <p>{title} is released under the CC0 License (<a href="https://creativecommons.org/publicdomain/zero/1.0/" target="_blank" class="peach-text">CC0 1.0</a>) meaning it is in the public domain. If you write stories or create art using my concepts or characters, I'd appreciate it if you have an author's note clarifying you're not the original creator and linking to my stuff. But since I've released it to the public domain, that's just me asking for a favor, it's not a requirement. Have fun!</p>
            </div>
        </div>

        <sp-story-footer></sp-story-footer>
    </article>

    <script src="../js/sp-header.js"></script>
    <script src="../js/main.js"></script>
    <script src="../js/sp-story-nav.js"></script>
    <script src="../js/sp-story-footer.js"></script>
    <script>
        // Progress Bar & ScrollSpy Logic
        window.addEventListener('scroll', () => {{
            const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
            const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (scrollTop / scrollHeight) * 100;
            document.getElementById('progress-bar').style.width = scrolled + '%';
        }});
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

def generate_toc(html_content, title_from_h1=False):
    """
    Scans HTML content.
    If title_from_h1 is True, extracts the first H1 text as the title and removes it from content.
    Generates a JSON string for TOC using ONLY H2 headers.
    Updates the html_content to include IDs for the headers.
    Returns (toc_items, final_content, extracted_title).
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    extracted_title = None
    if title_from_h1:
        h1 = soup.find('h1')
        if h1:
            extracted_title = h1.get_text()
            h1.decompose() # Remove from content
    
    # Generate Table of Contents (JSON) - ONLY H2
    toc_list = []
    
    # Find all h2 elements
    headers = soup.find_all('h2')
    
    for header in headers:
        header_text = header.get_text()
        # Create a slug from the header text
        slug = re.sub(r'[^a-z0-9]+', '-', header_text.lower()).strip('-')
        # Add id to the header in the content
        header['id'] = slug
        
        toc_list.append({
            "text": header_text,
            "href": f"#{slug}"
        })

    # Update the content with the new ids
    final_content = str(soup)
    
    # Convert TOC list to JSON string for the attribute
    import json
    toc_json = json.dumps(toc_list)
    # Escape single quotes for the attribute value if necessary, though mostly json.dumps uses double quotes
    toc_items = toc_json.replace("'", "&apos;")
         
    return toc_items, final_content, extracted_title

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
    
    prev_story = meta.get('previous_story', 'index.html')
    next_story = meta.get('next_story', 'index.html')
    
    # Convert Body to HTML
    # We enable 'extra' for better markdown support (tables, attr_list etc if needed)
    html_body = markdown.markdown(body_md, extensions=['extra', 'smarty'])

    # Calculate Read Time
    # Strip HTML to get text content for word count
    soup_for_text = BeautifulSoup(html_body, 'html.parser')
    text_content = soup_for_text.get_text()
    word_count = len(text_content.split())
    minutes = round(word_count / 200)
    
    if minutes < 1:
        minutes = 1
        
    if minutes >= 60:
        hours = minutes // 60
        mins = minutes % 60
        if mins > 0:
            read_time = f"{hours} hours and {mins} minutes read"
        else:
             read_time = f"{hours} hours read"
    else:
        read_time = f"{minutes} min read"

    # Allow override from metadata if specifically provided (optional, but good practice)
    if 'read_time' in meta:
        read_time = meta['read_time']
    
    # Generate TOC and inject IDs, and extract title if from H1
    # Check if we should ignore YAML title if it's "Untitled Story" or just always prefer H1?
    # User asked: "It should be getting the title from Markdown Heading Level 1"
    toc_items, final_content, extracted_title = generate_toc(html_body, title_from_h1=True)
    
    if extracted_title:
        title = extracted_title
    
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
