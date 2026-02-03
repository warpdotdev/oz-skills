#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: scripts/seo/pagespeed.sh <url|urls.txt> [output_dir]" >&2
  exit 1
fi

if [ -z "${PAGESPEED_API_KEY:-}" ]; then
  echo "Missing PAGESPEED_API_KEY env var." >&2
  echo "Get an API key from Google Cloud Console, then run:" >&2
  echo "  PAGESPEED_API_KEY=... scripts/seo/pagespeed.sh https://example.com" >&2
  exit 1
fi

INPUT="$1"
OUTPUT_DIR="${2:-reports/pagespeed}"

mkdir -p "$OUTPUT_DIR"

urlencode() {
  python3 - <<'PY' "$1"
import sys, urllib.parse
print(urllib.parse.quote(sys.argv[1], safe=""))
PY
}

run_pagespeed() {
  local url="$1"
  local safe_name
  safe_name=$(echo "$url" | sed -E 's#https?://##; s#[^a-zA-Z0-9._-]#_#g')
  local out_path="$OUTPUT_DIR/${safe_name}.json"
  local encoded_url
  encoded_url=$(urlencode "$url")

  echo "Running PageSpeed Insights (SEO) for $url"
  curl -sS \
    "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=${encoded_url}&category=SEO&category=PERFORMANCE&strategy=mobile&key=${PAGESPEED_API_KEY}" \
    -o "$out_path"
}

if [ -f "$INPUT" ]; then
  while IFS= read -r url; do
    [ -z "$url" ] && continue
    run_pagespeed "$url"
  done < "$INPUT"
else
  run_pagespeed "$INPUT"
fi

echo "Reports saved to $OUTPUT_DIR"
