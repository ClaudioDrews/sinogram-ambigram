"""Build the self-contained evaluation page from the item selection and the text.

The page template lives in ``evaluation/template.html`` and carries two empty
payload blocks. This script injects the selected items and the interface text
into a copy, producing ``evaluation/index.html``: a single file that works
offline, needs no server, and can be handed to a participant as-is.

The **selection** lives in ``evaluation/items.json`` and is never edited by
hand; it is produced by the item-selection stage. Keeping it separate from the
page means the page stays item-agnostic and can be rebuilt with a different
selection without touching the interface.

Usage:
    python evaluation/build_page.py
    python evaluation/build_page.py --items evaluation/items.json --out evaluation/index.html
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ITEMS_BLOCK = 'id="evaluation-items" type="application/json"'
TEXT_BLOCK = 'id="evaluation-text" type="application/json"'


def _replace_block(html: str, marker: str, payload: str) -> str:
    """Replace the contents of a <script id=... type="application/json"> block."""
    start_tag = f'<script {marker}>'
    start = html.find(start_tag)
    if start < 0:
        raise SystemExit(f"block {marker!r} not found in the template")
    open_end = html.find(">", start) + 1
    close = html.find("</script>", open_end)
    if close < 0:
        raise SystemExit(f"block {marker!r} is not closed")
    return html[:open_end] + payload + html[close:]


def build(template: Path, items: Path, text: Path, out: Path) -> int:
    html = template.read_text(encoding="utf-8")
    item_data = json.loads(items.read_text(encoding="utf-8"))
    items_payload = json.dumps(item_data, ensure_ascii=False, separators=(",", ":"))
    text_payload = json.dumps(json.loads(text.read_text(encoding="utf-8")),
                              ensure_ascii=False, separators=(",", ":"))
    missing = [item.get("id", "?") for item in item_data.get("items", [])
               if not item.get("construction_svg")]
    if missing:
        raise SystemExit(
            f"{len(missing)} of {len(item_data.get('items', []))} items have no "
            f"rendered construction ({', '.join(missing[:5])}...). Run "
            f"code/stage9_select_pilot_items.py, which renders the constructions "
            f"into the item file."
        )
    html = _replace_block(html, ITEMS_BLOCK, items_payload)
    html = _replace_block(html, TEXT_BLOCK, text_payload)
    # Canonical POSIX final newline keeps the generated artifact byte-for-byte reproducible.
    html = html.rstrip("\n") + "\n"
    out.write_text(html, encoding="utf-8")
    count = len(item_data.get("items", []))
    print(f"Wrote {out} with {count} items ({out.stat().st_size:,} bytes)")
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", type=Path, default=HERE / "template.html")
    parser.add_argument("--items", type=Path, default=HERE / "items.json")
    parser.add_argument("--text", type=Path, default=HERE / "text.json")
    parser.add_argument("--out", type=Path, default=HERE / "index.html")
    args = parser.parse_args()
    build(args.template, args.items, args.text, args.out)


if __name__ == "__main__":
    main()