#!/usr/bin/env python3
"""Rebuild the 52 blind stimuli from immutable Git revisions and a pinned source.

No third-party glyph PNGs are committed to this repository. This tool
reconstructs them as external, license-noticed artifacts. Fails closed if any
PNG's SHA-256 differs from the recorded pilot stimulus.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

# Git commits that produced the original November 2026 preview images.
HISTORICAL_MAIN = "a9ddfabbdfe32d781c816ffbd6c93fc194d12e30"
THICKNESS = "89c843699fe65f9c9b6df6534e6042dca60d536d"
R_ODD = "f764a66493bbd0d8a5d91d64f89e56b60657f2f9"
HARMONIC = "a1f0c83a2665632688c75f3d4db9232da1cc5c47"
AB_FUSION = "c222133c59d07103d162dda5a1a3357764cfd0c7"

SOURCE_SHA = "a28c478b5178e98f67f510b2d52fde08a69dc664654ef43498253b9b764d46ee"
SOURCE_COMMIT = "bddc96d41bef78427ed0e034e9f7e31d71fd1b92"
CHARACTERS = ("田", "中", "口", "日", "目")
PAIRS = (("甲", "由"), ("韦", "芈"))

# First value is geometry implementation; second is the experiment renderer.
REVISIONS = {
    "main-original": (HISTORICAL_MAIN, THICKNESS, None),
    "thickness-fixed": (THICKNESS, THICKNESS, None),
    "r-odd": (R_ODD, R_ODD, "prc_r_odd.py"),
    "harmonic": (HARMONIC, HARMONIC, "prc_harmonic.py"),
    "ab-fusion": (AB_FUSION, AB_FUSION, "prc_ab_fusion.py"),
}
TASK_ARMS = {
    "self": ("main-original", "thickness-fixed", "r-odd", "harmonic"),
    "pair": ("main-original", "thickness-fixed", "ab-fusion"),
}

PROMPT = ("Identify the single Chinese character shown in this image. Return exactly "
          "one Unicode CJK character if you can recognize it, or UNKNOWN if you "
          "cannot. Do not explain, do not guess from filenames or metadata, "
          "and do not alter or rotate the image.")


def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def git_blob(repo: Path, commit: str, path: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(repo), "show", f"{commit}:{path}"])


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(geometry_source: Path, key: Path, repo: Path, out_zip: Path) -> dict:
    if sha256(geometry_source) != SOURCE_SHA:
        raise ValueError("MMah geometry source does not match the immutable SHA-256 pin")
    with key.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 52 or len({r["trial_id"] for r in rows}) != 52:
        raise ValueError("Expected exactly 52 unique stimulus IDs")
    if {r["arm"] for r in rows} != set(REVISIONS):
        raise ValueError("Unexpected experimental method set")
    for row in rows:
        if row["task"] not in TASK_ARMS or row["arm"] not in TASK_ARMS[row["task"]]:
            raise ValueError("Unexpected task/arm")

    with tempfile.TemporaryDirectory(prefix="prc-rebuild-") as workspace:
        tmp = Path(workspace)
        by_arm = {}
        for arm, (geometry_ref, renderer_ref, module) in REVISIONS.items():
            project = tmp / "sources" / arm
            project.mkdir(parents=True, exist_ok=True)
            (project / "prc_construct.py").write_bytes(
                git_blob(repo, geometry_ref, "code/prc_construct.py"))
            (project / "exp_render_prc.py").write_bytes(
                git_blob(repo, renderer_ref, "code/exp_render_prc.py"))
            if module:
                (project / module).write_bytes(git_blob(repo, geometry_ref, "code/" + module))
            by_arm[arm] = {}
            for task, allowed in TASK_ARMS.items():
                if arm not in allowed:
                    continue
                output = tmp / "rendered" / arm / task
                cmd = [sys.executable, str(project / "exp_render_prc.py"),
                       "--graphics", str(geometry_source.resolve()),
                       "--mode", (
                           "baseline" if arm in ("main-original", "thickness-fixed")
                           else arm),
                       "--out", str(output)]
                if task == "self":
                    cmd.extend(["--characters", ",".join(CHARACTERS)])
                else:
                    cmd.extend(["--pairs", ",".join(a + ":" + b for a, b in PAIRS)])
                run(*cmd, stdout=subprocess.DEVNULL)
                by_arm[arm][task] = output

        blind = tmp / "blind"
        images = blind / "stimuli"
        images.mkdir(parents=True)
        manifest = []
        for seq, row in enumerate(rows, 1):
            task, arm, a, b = (row[k] for k in (
                "task", "arm", "character_a", "character_b"))
            if task == "self":
                if a != b or a not in CHARACTERS:
                    raise ValueError("Unrecognized self-rotation target")
                index = CHARACTERS.index(a) + 1
            else:
                if (a, b) not in PAIRS:
                    raise ValueError("Unrecognized pair target")
                index = PAIRS.index((a, b)) + 1
            suffix = "upright" if row["orientation"] == "upright" else "rotated"
            png = by_arm[arm][task] / f"case-{index:05d}-{suffix}.png"
            digest = sha256(png)
            if digest != row["sha256"]:
                raise RuntimeError(
                    f"Rebuild mismatch at trial {row['trial_id']}: "
                    f"expected {row['sha256']} got {digest}")
            dest = images / (row["trial_id"] + ".png")
            shutil.copyfile(png, dest)
            manifest.append({
                "trial_order": seq, "trial_id": row["trial_id"],
                "image_path": "stimuli/" + dest.name, "sha256": digest})
        with (blind / "trial_order.csv").open(
                "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=("trial_order", "trial_id", "image_path", "sha256"))
            writer.writeheader()
            writer.writerows(manifest)

        (blind / "README.md").write_text(
            "# Blind VLM recognition — image-only pilot\n\n"
            "52 grayscale PNG images, shuffled trial IDs, no target labels. "
            "Use one independent model call per image. Do not inspect the "
            "public answer key or previous results before freezing responses.\n\n"
            "## Exact prompt P1\n\n> " + PROMPT + "\n\n"
            "Use the same prompt and model settings for all images. Keep every "
            "raw response and error. Decode exactly one CJK ideograph or literal "
            "UNKNOWN. Report outputs without estimating correctness until the "
            "full blinded run is complete. See the project's bilingual research "
            "protocol and its upstream licence notice.\n",
            encoding="utf-8")
        (blind / "README.zh-CN.md").write_text(
            "# 旋转汉字视觉模型盲测\n\n"
            "本包包含 52 张匿名 PNG 图像。请对每张图像发起独立、无历史记录的模型请求。"
            "在冻结所有回答之前，不得读取公开的标准答案、实验分支名称或已有结果。"
            "请使用英文 README.md 中完全相同的 P1 提示词，保存所有原始回答、"
            "UNKNOWN、无效输出和错误，再进行评分。\n",
            encoding="utf-8")
        license_file = repo / "licenses/ARPHICPL.TXT"
        if not license_file.is_file():
            raise FileNotFoundError("Unmodified upstream licence not found")
        shutil.copyfile(license_file, blind / "ARPHICPL.TXT")
        (blind / "PROVENANCE.json").write_text(
            json.dumps({
                "kind": "Arphic-licensed MMah-derived experimental glyph images",
                "source_revision": SOURCE_COMMIT,
                "source_sha256": SOURCE_SHA,
                "images": len(manifest),
                "historical_main_commit": HISTORICAL_MAIN,
                "method_geometry_commits": {
                    k: v[0] for k, v in REVISIONS.items()},
                "note": "Derived modified raster graphics, not MIT-relicensed. "
                        "Answers deliberately withheld from this blind package."
            }, indent=2) + "\n", encoding="utf-8")
        out_zip.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
            for file in sorted(blind.rglob("*")):
                if file.is_file():
                    z.write(file, file.relative_to(blind).as_posix())
    return {"images": len(manifest), "zip": str(out_zip), "zip_sha256": sha256(out_zip)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parents[1]
    repo = Path(__file__).resolve().parents[3]
    p.add_argument("--graphics", type=Path, required=True)
    p.add_argument("--key", type=Path, default=here / "data/ground_truth.csv")
    p.add_argument("--repo", type=Path, default=repo)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(build(a.graphics, a.key, a.repo, a.out), indent=2))


if __name__ == "__main__":
    main()
