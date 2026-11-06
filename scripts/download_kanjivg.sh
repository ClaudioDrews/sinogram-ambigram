#!/usr/bin/env bash
# Download the exact KanjiVG snapshot used for the published geometry.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMMIT="70a0b7ae0c18ceb5cb358274b029cce0234a43bc"
SHA256="8a9686f4cda0188d926ddcd4010eda521630f5f40de8b9c308bb8892923136c9"
DEST="${ROTG_DATA:-$ROOT/data}/kanjivg"
mkdir -p "$DEST"
TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT
curl --fail --location --retry 3 \
  "https://github.com/KanjiVG/kanjivg/archive/$COMMIT.tar.gz" -o "$TMP"
tar -xzf "$TMP" -C "$DEST" --strip-components=1
echo "$SHA256  $DEST/kvg-index.json" | sha256sum --check --status || {
  echo "KanjiVG index checksum mismatch" >&2
  exit 1
}
echo "KanjiVG pinned at $COMMIT in $DEST"
