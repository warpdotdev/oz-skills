#!/usr/bin/env bash
set -euo pipefail

if ! command -v lighthouse >/dev/null 2>&1; then
  echo "lighthouse CLI not found. Install with: npm i -g lighthouse" >&2
  exit 1
fi

if [ "$#" -lt 1 ]; then
  echo "Usage: scripts/seo/lighthouse.sh <url|urls.txt> [output_dir]" >&2
  exit 1
fi

INPUT="$1"
OUTPUT_DIR="${2:-reports/lighthouse}"

mkdir -p "$OUTPUT_DIR"

run_lighthouse() {
  local url="$1"
  local safe_name
  safe_name=$(echo "$url" | sed -E 's#https?://##; s#[^a-zA-Z0-9._-]#_#g')
  local out_path="$OUTPUT_DIR/${safe_name}.json"

  echo "Running Lighthouse (SEO) for $url"
  lighthouse "$url" \
    --only-categories=seo \
    --output=json \
    --output-path="$out_path" \
    --quiet
}

if [ -f "$INPUT" ]; then
  while IFS= read -r url; do
    [ -z "$url" ] && continue
    run_lighthouse "$url"
  done < "$INPUT"
else
  run_lighthouse "$INPUT"
fi

echo "Reports saved to $OUTPUT_DIR"
