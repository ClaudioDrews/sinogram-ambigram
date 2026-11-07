# Source data and redistribution notice

The PRC glyph geometry is derived from **Make Me a Hanzi** (`graphics.txt`) at revision
`bddc96d41bef78427ed0e034e9f7e31d71fd1b92` with SHA-256
`a28c478b5178e98f67f510b2d52fde08a69dc664654ef43498253b9b764d46ee`.

Upstream stroke geometry and derived renderings carry **Arphic Public License** obligations; see the unmodified [Arphic license text](../../licenses/ARPHICPL.TXT), the project's [license audit](../../LICENSE-AUDIT.md) and [NOTICE](../../NOTICE.md). The repository's MIT license on original code and prose does **not** relicense upstream font-derived glyph material.

**Distribution decision for this benchmark:** do not commit PNG renderings, source outlines or stroke medians in this directory. Regenerate 436×436 black/white preview PNGs from the pinned upstream source via `scripts/rebuild_stimuli.py` and the `vlm-stimuli-rebuild.yml` GitHub workflow. Every original PNG hash is validated; images are distributed only in separately licensed workflow artifacts with the Arphic license and modification notice. Record source pin, code commit and file checksums. The exact classification and obligations for derived numeric measurements may require further legal review; do not describe all such measurements as unconditionally MIT.

This benchmark publishes trial-to-condition identifiers, expected character codepoints, and observed textual VLM responses as research data, while withholding raw private inference logs, API account information and host paths. This is not a statement that any upstream source is in the public domain.

**Modification notice:** images shown in the pilot were rasterized/modified experimental stroke constructions generated during November 2026; they are not official, certified glyph designs, and no upstream author endorsement is claimed.
