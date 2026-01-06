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

INDEX_TEMPLATE = """<!DOCTYPE html>
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
    <sp-header base-path="../.." active-page="stories"></sp-header>
    <article class="story-container section">
        <header>
            <h1>{title}</h1>
            <div class="story-meta">
                Published on {date} &bull; {word_count} &bull; {read_time}
            </div>
        </header>

        <div class="story-content">
            {intro_content}

            {author_note}
            
            <div class="chapter-list">
                <h2>Chapters</h2>
                <ul>
                    {chapter_links}
                </ul>
            </div>

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
</body>
</html>"""

CHAPTER_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta content="width=device-width, initial-scale=1.0" name="viewport" />
    <title>{chapter_title} - {story_title} | Savage Peach</title>
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
            <h1>{story_title}</h1>
            <h2>{chapter_title}</h2>
        </header>

        <sp-story-nav menu-items='{toc_items}'></sp-story-nav>

        <div class="story-content">
            {content}
            
            <div class="chapter-nav">
                {prev_link}
                {next_link}
            </div>
        </div>

        <sp-story-footer></sp-story-footer>
    </article>

    <script src="../../js/sp-header.js"></script>
    <script src="../../js/main.js"></script>
    <script src="../../js/sp-story-nav.js"></script>
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

def split_content_by_headers(soup, tag='h2'):
    """
    Splits the soup content into sections based on the specified header tag.
    Returns:
    - intro_soup: BeautifulSoup object containing content before the first header
    - chapters: list of dicts {'title': str, 'id': str, 'content': BeautifulSoup}
    """
    intro_soup = BeautifulSoup("", 'html.parser')
    chapters = []
    
    current_soup = intro_soup
    current_chapter = None
    
    # We iterate through top-level elements
    # Using list(soup.children) safely creates a copy so we can append to new soups without breaking iteration
    for element in list(soup.contents):
        if element.name == tag:
            # Start of a new chapter
            header_text = element.get_text(strip=True)
            
            # Skip empty headers (and those that are just punctuation or invisible chars if needed, though strip handles whitespace)
            # Also skip headers that are just "##" if that somehow happened
            if not header_text or header_text.replace('\u200b', '').strip() == '':
                print(f"DEBUG: Skipping empty header. Original: {repr(header_text)}")
                current_soup.append(element)
                continue

            print(f"DEBUG: Creating chapter for header: '{header_text}'")
            slug = re.sub(r'[^a-z0-9]+', '-', header_text.lower()).strip('-')
            
            # Additional safety: ensure slug is not empty
            if not slug:
                 current_soup.append(element)
                 continue
            
            current_chapter = {
                'title': header_text,
                'id': slug,
                'content': BeautifulSoup("", 'html.parser')
            }
            # Add the header to the new chapter content (optional, but good for context)
            # Actually, the template handles the H2 title separately, but valid HTML usually keeps it.
            # Let's KEEP it in the content for semantic structure within the "story-content" div.
            # But wait, the template has <h2>{chapter_title}</h2> in the header block.
            # So we might want to remove it from the body content.
            # Let's NOT add the header element to the content.
            
            chapters.append(current_chapter)
            current_soup = current_chapter['content']
        else:
            # Append element to current section
            # appending moves the element from original soup to new soup
            current_soup.append(element)
            
    return intro_soup, chapters

def main():
    parser = argparse.ArgumentParser(description="Convert Markdown story to HTML with Chapter Splitting")
    parser.add_argument("input_file", help="Path to input Markdown file")
    parser.add_argument("-o", "--output_slug", help="Slug for the output directory and filenames (e.g. 'using-master-pc')", required=True)
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        sys.exit(1)
        
    # Read input file
    with open(args.input_file, 'r', encoding='utf-8') as f:
        raw_content = f.read()

    # Pre-process: Convert Chat Messages to HTML
    def format_chat_message(match, sender_class):
        content = match.group(1).strip()
        content = content.replace('\\!', '!')
        content_html = markdown.markdown(content)
        # Removed chat-container wrapper here; will group later
        return f'<div class="chat-message {sender_class}">{content_html}</div>'

    # Received Messages: |\> Message
    # Matches line starting with |\>
    raw_content = re.sub(r'(?m)^\|\\\>\s*(.*?)$', 
                         lambda m: format_chat_message(m, "msg-received"), 
                         raw_content)
    
    # Sent Messages: ||\> Message
    # Matches line starting with ||\>
    raw_content = re.sub(r'(?m)^\|\|\\\>\s*(.*?)$', 
                         lambda m: format_chat_message(m, "msg-sent"), 
                         raw_content)

    # Pre-process: Fix escaped blockquotes
    # Replace lines starting with '\>' with '>'
    raw_content = re.sub(r'(?m)^\\>\s?', '>', raw_content)
    raw_content = re.sub(r'(?m)^\*\\>\s?', '>*', raw_content)

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
        
    # 2. Calculate Read Time & Word Count (Total)
    raw_word_count, read_time = get_word_count_and_time(soup.get_text())
    
    if 'read_time' in meta:
        read_time = meta['read_time']
        
    word_count_str = f"{raw_word_count:,} words"
    
    # 3. Split into Chapters (H2)
    intro_soup, chapters = split_content_by_headers(soup, 'h2')
    
    # Cleanup Intro: If it only contains HR and whitespace, clear it
    intro_has_content = False
    for child in intro_soup.contents:
        if isinstance(child, str):
            if child.strip():
                intro_has_content = True
                break
        elif child.name != 'hr':
            intro_has_content = True
            break
    
    if not intro_has_content:
        intro_soup.clear()

    # Check for Author's Note
    author_note_html = ""
    if chapters:
        first_title = chapters[0]['title'].strip().lower()
        # Normalize smart quotes
        first_title = first_title.replace('\u2019', "'").replace('\u2018', "'")
        
        if first_title == "author's note":
            print("DEBUG: Found Author's Note, extracting...")
            note_chap = chapters.pop(0)
            note_soup = note_chap['content']
            
            # Cleanup trailing HR and whitespace from Author's Note
            while note_soup.contents:
                last_node = note_soup.contents[-1]
                if isinstance(last_node, str):
                    if not last_node.strip():
                        last_node.extract()
                        continue
                    else:
                        break
                elif last_node.name == 'hr':
                    last_node.extract()
                    continue
                else:
                    break
            
            author_note_html = f'<div class="author-note">\n<strong>Author\'s Note</strong>\n{note_soup}\n</div>'
    
    # 3b. Pre-calculate filenames
    for i, chap in enumerate(chapters):
        idx = i + 1
        # Format: 1-the-blonde.html
        chap['filename'] = f"{idx}-{chap['id']}.html"

    # 4. Prepare Output Directory
    output_dir = os.path.join('stories', slug)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")
        
    # Copy source markdown to output directory
    source_filename = f"{slug}.md"
    shutil.copy2(args.input_file, os.path.join(output_dir, source_filename))
    print(f"Copied source file to: {os.path.join(output_dir, source_filename)}")
    
    # 5. Build Global TOC for Navigation
    nav_items = []
    nav_items.append({"text": "Index", "href": "index.html"})
    for i, chap in enumerate(chapters):
        # Use robust relative linking for the TOC JSON to handle base path issues
        # "../../stories/{slug}/{filename}"
        href = f"../../stories/{slug}/{chap['filename']}"
        
        nav_items.append({
            "text": chap['title'],
            "href": href 
        })
    
    toc_json = json.dumps(nav_items).replace("'", "&apos;")
    
    # 6. Generate Index Page
    chapter_links_html = ""
    for item in nav_items:
        if item['href'] == 'index.html': continue
        chapter_links_html += f'<li><a href="{item["href"]}">{item["text"]}</a></li>\n'
        
    index_html = INDEX_TEMPLATE.format(
        title=title,
        description=description,
        date=date,
        word_count=word_count_str,
        read_time=read_time,
        intro_content=str(intro_soup),
        author_note=author_note_html,
        chapter_links=chapter_links_html,
        source_link=f"../../stories/{slug}/{source_filename}"
    )
    
    with open(os.path.join(output_dir, "index.html"), 'w', encoding='utf-8') as f:
        f.write(index_html)
    print(f"Generated Index: {os.path.join(output_dir, 'index.html')}")
    
    # 7. Generate Chapter Pages
    for i, chap in enumerate(chapters):
        filename = chap['filename']
        
        # Navigation Links
        prev_link = ""
        next_link = ""
        
        if i > 0:
            prev_filename = chapters[i-1]['filename']
            prev_link = f'<a href="{prev_filename}" class="nav-prev">&larr; Previous Chapter</a>'
        else:
            prev_link = f'<a href="index.html" class="nav-prev">&larr; Index</a>'

        if i < len(chapters) - 1:
            next_filename = chapters[i+1]['filename']
            next_link = f'<a href="{next_filename}" class="nav-next">Next Chapter &rarr;</a>'
            
        chapter_html = CHAPTER_TEMPLATE.format(
            story_title=title,
            chapter_title=chap['title'],
            description=description,
            content=str(chap['content']),
            toc_items=toc_json,
            prev_link=prev_link,
            next_link=next_link
        )
        
        out_path = os.path.join(output_dir, filename)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(chapter_html)
        print(f"Generated Chapter: {out_path}")

if __name__ == "__main__":
    main()
