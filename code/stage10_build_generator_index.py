"""Stage 10: rebuild the pair index embedded in the browser generator.

The generator page embeds a copy of the refined pair table so that it works
offline. When the underlying dataset changes, that copy has to change with it:
otherwise the published site keeps serving the previous ranking while the
repository publishes a new one.

This stage regenerates the embedded block in place, from a chosen dataset, and
verifies that the file still parses and that the page loads. It touches only
the contents of the ``pair-dataset`` script block; the rest of the page is
left byte-identical.

Usage:
    python code/stage10_build_generator_index.py --dataset v1
    python code/stage10_build_generator_index.py --dataset v2
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import re
import sys

CODE = Path(__file__).resolve().parent
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

import paths  # noqa: E402
from paths import add_common_args, resolve  # noqa: E402

BLOCK = re.compile(
    r'(<script id="pair-dataset" type="application/json">)(.*?)(</script>)',
    re.S)

V1_FILES = ("data/rotation_pairs.csv",)
V2_FILES = ("data/v2/rotation_pairs_refined_v2.csv",)


def _rows_v1(repo: Path) -> list[list]:
    with open(repo / "data" / "rotation_pairs.csv", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    out = []
    for row in rows:
        out.append([row["a"], row["b"],
                    round(float(row["hausdorff"]), 5),
                    round(float(row["chamfer"]), 5),
                    row["self"] == "True"])
    return out


def _rows_v2(repo: Path) -> list[list]:
    path = repo / "data" / "v2" / "rotation_pairs_refined_v2.csv"
    with open(path, encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    out = []
    for row in rows:
        out.append([row["a"], row["b"],
                    round(float(row["hausdorff_grid_optimal"]), 5)
                    if "hausdorff_grid_optimal" in row
                    else round(float(row["hausdorff_exact"]), 5),
                    round(float(row["chamfer_exact"]), 5),
                    row["self"] == "True"])
    return out


def build_index(repo: Path, dataset: str) -> list[list]:
    if dataset == "v1":
        return _rows_v1(repo)
    if dataset == "v2":
        return _rows_v2(repo)
    raise SystemExit(f"unknown dataset {dataset!r}")


def inject(html: str, rows: list[list]) -> str:
    payload = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    new, count = BLOCK.subn(lambda m: m.group(1) + payload + m.group(3), html, count=1)
    if count != 1:
        raise SystemExit("pair-dataset block not found in the page")
    return new


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_args(parser)
    parser.add_argument("--dataset", choices=("v1", "v2"), default="v1")
    parser.add_argument("--repo", type=Path, default=paths.REPOSITORY)
    parser.add_argument("--target", type=Path, default=None,
                        help="page to update (default: <repo>/generator/index.html)")
    parser.add_argument("--dry-run", action="store_true",
                        help="report what would change without writing")
    args = parser.parse_args(argv)
    resolve(args)

    repo = args.repo
    target = args.target if args.target is not None else repo / "generator" / "index.html"
    rows = build_index(repo, args.dataset)
    html = target.read_text(encoding="utf-8")
    updated = inject(html, rows)

    # The page must still parse and still carry the expected payload.
    match = BLOCK.search(updated)
    payload = json.loads(match.group(2))
    if len(payload) != len(rows):
        raise SystemExit("payload length mismatch after injection")

    if args.dry_run:
        print(f"would write {len(rows)} rows into {target}")
        return
    target.write_text(updated, encoding="utf-8")
    print(f"wrote {len(rows)} rows into {target} ({target.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()