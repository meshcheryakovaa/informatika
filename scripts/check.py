"""Check assembled content, image integrity and local dependency inlining."""
from pathlib import Path
import base64
from html.parser import HTMLParser
import json
import re

ROOT = Path(__file__).resolve().parents[1]
class Document(HTMLParser):
    def __init__(self):
        super().__init__(); self.pages=[]; self.targets=[]; self.assets=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag=='section' and 'page-section' in a.get('class','').split(): self.pages.append(a['id'])
        if 'data-nav-page' in a: self.targets.append(a['data-nav-page'])
        for key in ('src','href'):
            if a.get(key,'').startswith('assets/'): self.assets.append(a[key])
html=(ROOT/'dist/informatika_all_in_one.html').read_text(encoding='utf-8')
doc=Document();doc.feed(html)
source_pages=list((ROOT/'src/pages').glob('*.html'))
assert len(doc.pages)==len(source_pages)>0, 'Missing pages'
assert len(set(doc.pages))==len(doc.pages), 'Duplicate page IDs'
assert set(doc.targets)==set(doc.pages), 'Navigation differs from pages'
assert not doc.assets, 'Local assets were not inlined'
assert '<!-- PAGES -->' not in html
assert not re.search(r'<(?:script|link)[^>]+(?:src|href)=[\"\'](?:app.js|.*\.css)',html)
assets=json.loads((ROOT/'src/assets.json').read_text())
for path,mime in assets.items():
    encoded=base64.b64encode((ROOT/'src'/path).read_bytes()).decode('ascii')
    assert 'data:'+mime+';base64,'+encoded in html, f'Missing asset {path}'
assert '@import' not in (ROOT/'src/katex.css').read_text(), 'Remote CSS dependency'
print(f'OK: {len(doc.pages)} pages, navigation and {len(assets)} embedded assets')
