import markdown
from bs4 import BeautifulSoup
import sys

with open('stories/umpc.md', 'r', encoding='utf-8') as f:
    raw = f.read()

# simplistic frontmatter strip
parts = raw.split('---', 2)
body = parts[2] if len(parts) >= 3 else raw

html = markdown.markdown(body, extensions=['extra', 'smarty'])
soup = BeautifulSoup(html, 'html.parser')

h2s = soup.find_all('h2')
for i, h2 in enumerate(h2s):
    text = h2.get_text(strip=True)
    print(f"H2 #{i}: '{text}' (len={len(text)}) repr={repr(text)}")
    if not text:
        print(" -> IS EMPTY")
    else:
        print(" -> NOT EMPTY")
