# PRC source and median-cache reproducibility (2026-11-07)

**Status:** Independently regenerated from the pinned upstream geometry on GitHub Actions, with two complete runs compared byte for byte. This verifies deterministic *preprocessing*, not ambigram legibility or the archived filled-ink experimental improvements.

## Fixed source

- Repository: [Make Me a Hanzi](https://github.com/skishore/makemeahanzi)
- Source file: `graphics.txt` (original content not redistributed here)
- Immutable upstream revision: `bddc96d41bef78427ed0e034e9f7e31d71fd1b92` (pinned by later PR)
- Source SHA-256: `a28c478b5178e98f67f510b2d52fde08a69dc664654ef43498253b9b764d46ee`
- Source size: **30,778,076 bytes**
- Source license: **Arphic Public License** (see upstream `COPYING`).
- Verification run: [GitHub Actions #42379382585](https://github.com/ClaudioDrews/sinogram-ambigram/actions/runs/42379382585).

## Observations from pinned source

| Observable | Reproduced value |
|---|---:|
| Unique `graphics.txt` records | **9,574** |
| GB2312 unified ideograph inventory | **6,763** |
| GB2312 characters covered by the source | **6,763 / 6,763** |
| Stage 12 generated median points | **9,322,985** |
| Complete, independent Stage 12 rebuilds | **2** |
| Byte comparison of four generated files | **Identical** |

**Correction:** the internal roadmap v2.0.6 states 9,534 source glyphs.
The pinned file instead yields **9,574** valid unique records. Treat 9,534
as an older, non-reproduced figure for this exact source snapshot. It must not
be copied into public dataset summaries or used as a denominator without a
source revision identifier. The GB2312 coverage figure remains verified.

## Byte-level output SHA-256

| Output | SHA-256 |
|---|---|
| `meta.json` | `aa5ab97a6f35468b4c6e3dc97a0692b9d4f374956710201e4e3ee6ae1339db71` |
| `points.npy` | `7d00af9a7314145556e20fcebe5493d3d7d867038cb3781bb9901dc8e7ff4c15` |
| `offsets.npy` | `e7c14b07874b073ca24cb255083da84a246e7464dce705df80d7322198a2466e` |
| `dt.npy` | `549f6eae1c2dda2889c4cf50bb61a895928da25320deb1050cfb96b329080690` |

The recorded digests are **verification fixtures** for this environment and
current implementation, not a guarantee that every future NumPy version,
CPU backend, or source revision produces the same serialized bytes.

## Reproduce

```bash
bash scripts/download_prc_sources.sh
python code/prc_inventory.py --graphics data/prc/graphics.txt
python code/stage12_prc_ingest.py --graphics data/prc/graphics.txt --out /tmp/prc-a
python code/stage12_prc_ingest.py --graphics data/prc/graphics.txt --out /tmp/prc-b
for f in meta.json points.npy offsets.npy dt.npy; do
  cmp "/tmp/prc-a/$f" "/tmp/prc-b/$f"
  sha256sum "/tmp/prc-a/$f"
done
```

## Remaining scientific gates

The source stores both simplified and traditional glyphs and supplies
PRC stroke order; a codepoint repertoire is not independent proof that
every stored glyph agrees with an authoritative Mainland simplified
printed standard. Official 2013 TCC membership lists, per-form review,
and source-derived-asset redistribution checks remain separate gates.
This median-skeleton cache is also **different** from the earlier PRC
filled-ink experimental archive. No perceptual validation is claimed.
