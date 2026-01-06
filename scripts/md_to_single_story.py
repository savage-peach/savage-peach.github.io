import sys
import os
import re
import argparse
import datetime
import json
import shutil

# Try to import required libraries
try:
    import markdown
    import yaml
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"Error: Missing required libraries. Please install them using:\npip install markdown pyyaml beautifulsoup4")
    sys.exit(1)

SINGLE_STORY_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta content="width=device-width, initial-scale=1.0" name="viewport" />
    <title>{title} | Savage Peach</title>
    <meta content="{description}" name="description" />
    <link href="../../css/style.css" rel="stylesheet" />
    <link href="../../css/story.css" rel="stylesheet" />
    <script src="../../js/theme-init.js"></script>
</head>
<body>
    <div id="progress-container">
        <div id="progress-bar"></div>
    </div>

    <sp-header base-path="../.." active-page="stories"></sp-header>
    <article class="story-container section">
        <header>
            <h1>{title}</h1>
            <div class="story-meta">
                Published on {date} &bull; {word_count} &bull; {read_time}
            </div>
        </header>

        <div class="story-content">
            {author_note}
            {content}
            
            <div class="source-download">
                <a href="{source_link}" download class="peach-text"><i class="fas fa-file-download"></i> Download Story</a>
            </div>

             <div class="license-note">
                <p>{title} is released under the CC0 License (<a href="https://creativecommons.org/publicdomain/zero/1.0/" target="_blank" class="peach-text">CC0 1.0</a>) meaning it is in the public domain. If you write stories or create art using my concepts or characters, I'd appreciate it if you have an author's note clarifying you're not the original creator and linking to my stuff. But since I've released it to the public domain, that's just me asking for a favor, it's not a requirement. Have fun!</p>
            </div>
        </div>

        <sp-story-footer></sp-story-footer>
    </article>

    <script src="../../js/sp-header.js"></script>
    <script src="../../js/main.js"></script>
    <script src="../../js/sp-story-footer.js"></script>
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

def get_word_count_and_time(text):
    word_count = len(text.split())
    minutes = round(word_count / 200)
    if minutes < 1: minutes = 1
    
    if minutes >= 60:
        hours = minutes // 60
        mins = minutes % 60
        read_time = f"{hours} hours and {mins} minutes read" if mins > 0 else f"{hours} hours read"
    else:
        read_time = f"{minutes} min read"
        
    return word_count, read_time

def clean_title(soup):
    title = None
    h1s = soup.find_all('h1')
    if h1s:
        title = h1s[0].get_text().strip()
        for h1 in h1s:
            h1.decompose()
    return title

def extract_author_note(soup):
    author_note_html = ""
    # Find h2 with text "Author's Note" (case insensitive)
    for h2 in soup.find_all('h2'):
        text = h2.get_text(strip=True).lower()
        # Normalize smart quotes
        text = text.replace('\u2019', "'").replace('\u2018', "'")
        
        if text == "author's note":
            # Found it. Extract content until next header or end.
            note_content = []
            curr = h2.next_sibling
            while curr:
                next_node = curr.next_sibling
                if curr.name and re.match(r'h[1-6]', curr.name):
                    # Stop at next header
                    break
                
                if curr.name == 'hr':
                    # Stop at horizontal rule, and consume it (don't include in note)
                    if hasattr(curr, 'decompose'):
                        curr.decompose()
                    elif hasattr(curr, 'extract'):
                         curr.extract()
                    break

                note_content.append(str(curr))
                # Remove from soup
                if hasattr(curr, 'decompose'):
                     curr.decompose()
                elif hasattr(curr, 'extract'):
                     curr.extract()
                curr = next_node
            
            # Remove the header itself
            h2.decompose()
            
            author_note_html = f'<div class="author-note">\n{"".join(note_content)}\n</div>'
            break
            
    return author_note_html

def main():
    parser = argparse.ArgumentParser(description="Convert Single-Chapter Markdown story to HTML")
    parser.add_argument("input_file", help="Path to input Markdown file")
    parser.add_argument("-o", "--output_slug", help="Slug for the output directory (e.g. 'invasive-species')", required=True)
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        sys.exit(1)
        
    # Read input file
    with open(args.input_file, 'r', encoding='utf-8') as f:
        raw_content = f.read()

    # Pre-process: Fix escaped blockquotes
    # Replace lines starting with '\>' with '>'
    raw_content = re.sub(r'(?m)^\\>', '>', raw_content)
    raw_content = re.sub(r'(?m)^\*\\>\s*', '>*', raw_content)

    # Parse Metadata
    meta, body_md = parse_frontmatter(raw_content)
    
    # Defaults
    slug = args.output_slug
    title = meta.get('title', 'Untitled Story')
    description = meta.get('description', '')
    date = meta.get('date', datetime.date.today().strftime("%b %d, %Y"))
    
    # Convert Body to HTML
    html_body = markdown.markdown(body_md, extensions=['extra', 'smarty'])
    soup = BeautifulSoup(html_body, 'html.parser')
    
    # 1. Extract and Clean Title (First H1)
    extracted_title = clean_title(soup)
    if extracted_title:
        title = extracted_title
        
    # 2. Calculate Read Time & Word Count
    raw_word_count, read_time = get_word_count_and_time(soup.get_text())
    
    if 'read_time' in meta:
        read_time = meta['read_time']

    # 2b. Extract Author's Note
    author_note = extract_author_note(soup)
        
    word_count_str = f"{raw_word_count:,} words"
    
    # 3. Prepare Output Directory
    output_dir = os.path.join('stories', slug)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    # Copy source markdown to output directory
    source_filename = "source.md"
    shutil.copy2(args.input_file, os.path.join(output_dir, source_filename))
    print(f"Copied source file to: {os.path.join(output_dir, source_filename)}")
    
    # 4. Generate Index Page (The Story)
    index_html = SINGLE_STORY_TEMPLATE.format(
        title=title,
        description=description,
        date=date,
        word_count=word_count_str,
        read_time=read_time,
        content=str(soup),
        author_note=author_note,
        source_link=source_filename
    )
    
    out_path = os.path.join(output_dir, "index.html")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(index_html)
    print(f"Generated Story: {out_path}")

if __name__ == "__main__":
    main()
