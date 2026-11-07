"""Stage 12: deterministic, provenance-aware MMah median ingestion.

This builds a *median skeleton* cache, not the filled-ink cache used by the
archived PRC construction experiments. Do not compare their scores directly.

Download graphics.txt with scripts/download_prc_sources.sh before use.
No third-party source data is bundled into this repository.

    python code/stage12_prc_ingest.py --graphics data/prc/graphics.txt
    python code/stage12_prc_ingest.py --graphics data/prc/graphics.txt \
        --out data/prc/cache --jp-meta output/cache/meta.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from stage1_skeleton import GRID, SPACING, chamfer_dt, rasterize_segments, resample_polyline

ROOT = Path(__file__).resolve().parents[1]
PIN = ROOT / "data" / "MMAH_PIN.txt"
SOURCE = "skishore/makemeahanzi graphics.txt"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def pinned_sha(path: Path = PIN) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("SHA256="):
            digest = line.partition("=")[2].strip().lower()
            if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
                raise ValueError("Invalid SHA256 in MMah pin")
            return digest
    raise ValueError("MMAH_PIN.txt has no SHA256 field")


def _medians(entry: dict, line_number: int) -> list[np.ndarray]:
    strokes = entry.get("strokes")
    medians = entry.get("medians")
    if not isinstance(strokes, list) or not strokes:
        raise ValueError(f"Missing strokes at line {line_number}")
    if not isinstance(medians, list) or len(medians) != len(strokes):
        raise ValueError(f"Stroke/median count mismatch at line {line_number}")
    out: list[np.ndarray] = []
    for median in medians:
        try:
            pts = np.asarray(median, dtype=np.float64)
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Invalid median at line {line_number}") from exc
        if pts.ndim != 2 or pts.shape[1] != 2 or not len(pts) or not np.isfinite(pts).all():
            raise ValueError(f"Invalid median coordinates at line {line_number}")
        # Official MMah coordinates: (0,900) is top left; +y points up.
        # The canonical 109x109 raster has +y pointing down.
        scaled = np.column_stack((pts[:, 0], 900.0 - pts[:, 1])) * (GRID / 1024.0)
        out.append(scaled)
    return out


def load_entries(graphics: Path) -> list[tuple[str, list[np.ndarray]]]:
    seen: set[str] = set()
    entries = []
    with graphics.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            raw = json.loads(line)
            character = raw.get("character")
            if not isinstance(character, str) or len(character) != 1:
                raise ValueError(f"Invalid character at line {line_number}")
            if character in seen:
                raise ValueError(f"Duplicate character at line {line_number}: {character}")
            seen.add(character)
            entries.append((character, _medians(raw, line_number)))
    if not entries:
        raise ValueError("Empty graphics file")
    return sorted(entries, key=lambda item: ord(item[0]))


def read_jp_counts(path: Path | None) -> dict[str, int]:
    if path is None:
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("JP metadata must be a list of Stage 1 glyph records")
    return {row["char"]: int(row["n_strokes"]) for row in data}


def build(graphics: Path, out: Path, expected_sha: str, jp_meta: Path | None = None) -> dict:
    """Fail closed on a source checksum mismatch and emit deterministic arrays.

    The source is intentionally not mixed into any regional ranking. MMah
    contains both simplified and traditional characters; a subsequent
    verified regional preset must assign a region to each selected glyph.
    """
    actual_sha = sha256(graphics)
    if actual_sha != expected_sha.lower():
        raise ValueError(f"MMah source SHA-256 mismatch: got {actual_sha}, expected {expected_sha}")
    entries = load_entries(graphics)  # full validation before writing anything
    jp_counts = read_jp_counts(jp_meta)
    out.mkdir(parents=True, exist_ok=True)
    all_points: list[np.ndarray] = []
    offsets = [0]
    meta = []
    dt = np.lib.format.open_memmap(out / "dt.npy", mode="w+", dtype=np.float32,
                                   shape=(len(entries), GRID, GRID))
    for index, (character, medians) in enumerate(entries):
        occ = np.zeros((GRID, GRID), dtype=bool)
        pieces = []
        for median in medians:
            sampled = resample_polyline(median, SPACING).astype(np.float32)
            pieces.append(sampled)
            if len(sampled) == 1:
                x, y = np.clip(sampled[0].astype(int), 0, GRID - 1)
                occ[y, x] = True
            else:
                rasterize_segments(sampled, occ)
        if not occ.any():
            raise ValueError(f"Empty raster for {character}")
        points = np.concatenate(pieces, axis=0)
        all_points.append(points)
        offsets.append(offsets[-1] + len(points))
        dt[index] = chamfer_dt(occ)
        jp_n = jp_counts.get(character)
        meta.append({
            "char": character,
            "codepoint": f"{ord(character):04X}",
            "n_strokes": len(medians),
            "n_points": int(len(points)),
            "source": SOURCE,
            "source_sha256": actual_sha,
            "source_scope": "mixed-simplified-traditional",
            "region": "unassigned",
            "jp_n_strokes": jp_n,
            "jp_stroke_count_diff": None if jp_n is None else (jp_n != len(medians)),
        })
    dt.flush()
    del dt
    np.save(out / "points.npy", np.concatenate(all_points).astype(np.float32))
    np.save(out / "offsets.npy", np.asarray(offsets, dtype=np.int64))
    (out / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {"glyphs": len(meta), "points": int(offsets[-1]),
            "source_sha256": actual_sha, "regional_ranking_ready": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graphics", type=Path, default=ROOT / "data/prc/graphics.txt")
    parser.add_argument("--out", type=Path, default=ROOT / "data/prc/cache")
    parser.add_argument("--expected-sha", default=None,
                        help="explicit SHA-256 for isolated fixtures; defaults to MMAH_PIN.txt")
    parser.add_argument("--jp-meta", type=Path, default=None,
                        help="optional JP Stage 1 meta.json for stroke-count divergence only")
    args = parser.parse_args()
    result = build(args.graphics, args.out, args.expected_sha or pinned_sha(), args.jp_meta)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
