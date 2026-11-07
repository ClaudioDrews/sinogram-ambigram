"""Export the complete grid-screened rotation graph as a reproducible gzip CSV.

This is a *new*, explicitly labelled schema: no claim is made that its bytes
match a historical archive. All distances are coarse grid approximations.
"""
from __future__ import annotations

import csv
import gzip
import io
import json
from pathlib import Path

import numpy as np

from paths import CACHE, OUT

EM = 109.0
FIELDS = (
    "a", "b", "hausdorff_grid", "chamfer_grid", "rms_grid",
    "iou2_grid", "iou3_grid", "iou4_grid", "self",
)


def export(cache: Path = CACHE, output: Path | None = None) -> tuple[Path, int]:
    cache = Path(cache)
    target = Path(output) if output is not None else OUT / "catalog" / "rotation_pairs_full_grid.csv.gz"
    meta = json.loads((cache / "meta.json").read_text(encoding="utf-8"))
    chars = [item["char"] for item in meta]
    pairs = np.load(cache / "pairs3.npy", mmap_mode="r")
    required = {"a", "b", "haus", "mean", "rms", "iou2", "iou3", "iou4"}
    if not required.issubset(pairs.dtype.names or ()):
        raise ValueError(f"pairs3.npy lacks fields: {sorted(required - set(pairs.dtype.names or ()))!r}")
    target.parent.mkdir(parents=True, exist_ok=True)
    # Canonical ordering independently of multiprocessing completion order.
    order = np.lexsort((pairs["b"], pairs["a"]))
    with target.open("wb") as raw:
        with gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as gz:
            with io.TextIOWrapper(gz, encoding="utf-8", newline="") as out:
                writer = csv.writer(out, lineterminator="\n")
                writer.writerow(FIELDS)
                for idx in order:
                    row = pairs[int(idx)]
                    a, b = int(row["a"]), int(row["b"])
                    writer.writerow((
                        chars[a], chars[b],
                        f'{float(row["haus"]) / EM:.8f}',
                        f'{float(row["mean"]) / EM:.8f}',
                        f'{float(row["rms"]) / EM:.8f}',
                        f'{float(row["iou2"]):.8f}',
                        f'{float(row["iou3"]):.8f}',
                        f'{float(row["iou4"]):.8f}',
                        a == b,
                    ))
    return target, len(order)


if __name__ == "__main__":
    path, count = export()
    print(f"Exported {count} grid-measured pairs to {path}")
