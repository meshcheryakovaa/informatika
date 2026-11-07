"""Build a single HTML using only the Python standard library."""
from pathlib import Path
import base64
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'

def build():
    html = (SRC / 'index.html').read_text(encoding='utf-8')
    pages = sorted((SRC / 'pages').glob('*.html'))
    if not pages:
        raise ValueError('No content pages found')
    html = html.replace('<!-- PAGES -->', ''.join(p.read_text(encoding='utf-8') for p in pages))
    html = re.sub(r'<link rel="stylesheet" href="([^"]+)">',
                  lambda m: '<style>' + (SRC / m[1]).read_text(encoding='utf-8') + '</style>', html)
    html = re.sub(r'<script src="([^"]+)"></script>',
                  lambda m: '<script>' + (SRC / m[1]).read_text(encoding='utf-8') + '</script>', html)
    assets = json.loads((SRC / 'assets.json').read_text(encoding='utf-8'))
    # One pass avoids repeatedly scanning the large document for every image.
    def inline(match):
        path = match[0]
        return 'data:' + assets[path] + ';base64,' + base64.b64encode((SRC / path).read_bytes()).decode('ascii')
    html = re.sub(r'assets/[a-f0-9]{24}\.[a-z0-9]+', inline, html)
    out = ROOT / 'dist' / 'informatika_all_in_one.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding='utf-8')
    print(f'{out.name}: {len(pages)} pages, {len(assets)} assets, {out.stat().st_size:,} bytes')
    return out

if __name__ == '__main__':
    build()
