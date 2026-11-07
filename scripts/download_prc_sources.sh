#!/usr/bin/env bash
# Fetch the pinned Make Me a Hanzi geometry source for the PRC track.
# Usage: bash scripts/download_prc_sources.sh
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${ROTG_DATA:-$ROOT/data}/prc"
mkdir -p "$DEST"
URL="https://raw.githubusercontent.com/skishore/makemeahanzi/bddc96d41bef78427ed0e034e9f7e31d71fd1b92/graphics.txt"
SHA256="a28c478b5178e98f67f510b2d52fde08a69dc664654ef43498253b9b764d46ee"
TARGET="$DEST/graphics.txt"
if [[ -f "$TARGET" ]] && printf '%s  %s\n' "$SHA256" "$TARGET" | sha256sum -c --status; then
  echo "Verified existing snapshot: $TARGET"
  exit 0
fi
TMP="$(mktemp "$DEST/.graphics.XXXXXXXX")"
trap 'rm -f "$TMP"' EXIT
curl --fail --location --silent --show-error --retry 3 "$URL" -o "$TMP"
printf '%s  %s\n' "$SHA256" "$TMP" | sha256sum -c --status || {
  echo "PRC snapshot checksum mismatch; refusing to install data" >&2
  exit 1
}
mv "$TMP" "$TARGET"
echo "Verified and installed: $TARGET"
# Only graphics.txt is used; dictionary.txt is deliberately excluded.
