"""Check repository-local links in Markdown, excluding fenced code blocks."""
from __future__ import annotations
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r'(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)')
errors = []
checked = 0
for page in ROOT.rglob('*.md'):
    if any(part.startswith('.') for part in page.relative_to(ROOT).parts):
        continue
    text = page.read_text(encoding='utf-8')
    # Markdown code fences are documentation examples, not navigation.
    text = re.sub(r'^\s*(```|~~~)[^\n]*\n.*?^\s*\1[^\n]*$', '', text, flags=re.M | re.S)
    for match in LINK.finditer(text):
        target = match.group(1).split('#', 1)[0].strip()
        if not target or target.startswith(('http:', 'https:', 'mailto:', 'data:', '#')):
            continue
        checked += 1
        resolved = (page.parent / unquote(target)).resolve()
        if not resolved.is_relative_to(ROOT.resolve()) or not resolved.exists():
            errors.append(f'{page.relative_to(ROOT)} -> {target}')
print(f'Checked {checked} repository-local links in Markdown.')
if errors:
    for error in errors:
        print(f'BROKEN: {error}')
    sys.exit(1)
print('All repository-local Markdown links resolve.')
