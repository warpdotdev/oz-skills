#!/bin/bash
# Run ESLint with jsx-a11y rules for accessibility checking

set -e

OUTPUT_DIR=".claude/skills/a11y-auditor"
mkdir -p "$OUTPUT_DIR"

echo "Running ESLint accessibility checks..."

# Check if eslint is available
if ! command -v npx &> /dev/null; then
    echo "Error: npx not found. Please install Node.js and npm."
    exit 1
fi

# Run ESLint and capture output
npx eslint \
  --ext .jsx,.tsx \
  --no-ignore \
  --format json \
  . > "$OUTPUT_DIR/eslint-results.json" 2>&1 || true

# Also generate a readable format
npx eslint \
  --ext .jsx,.tsx \
  --no-ignore \
  . > "$OUTPUT_DIR/eslint-results.txt" 2>&1 || true

echo "Results saved to:"
echo "  - $OUTPUT_DIR/eslint-results.json (machine-readable)"
echo "  - $OUTPUT_DIR/eslint-results.txt (human-readable)"

# Count violations
if [ -f "$OUTPUT_DIR/eslint-results.json" ]; then
    VIOLATIONS=$(grep -o '"ruleId":"jsx-a11y' "$OUTPUT_DIR/eslint-results.json" | wc -l || echo "0")
    echo ""
    echo "Found $VIOLATIONS jsx-a11y violations"
fi
