# Grep Patterns for Accessibility Auditing

Search patterns for finding common accessibility violations in codebases.

## Missing Alt Text

### Images without alt attribute
```bash
grep -rn "<img[^>]*src" \
    --include="*.jsx" \
    --include="*.tsx" \
    --include="*.html" \
    --include="*.vue" \
    --include="*.astro" \
    . | grep -v "alt="
```

### Images with redundant alt text
```bash
grep -rn 'alt="image\|alt="picture\|alt="photo\|alt="img' \
    --include="*.jsx" \
    --include="*.tsx" \
    --include="*.html" \
    --include="*.vue" \
    --include="*.astro" \
    .
```

## Keyboard Navigation

### onClick without keyboard handlers
```bash
grep -rn "onClick=" \
    --include="*.jsx" \
    --include="*.tsx" \
    . | grep -v "onKeyDown\|onKeyPress\|onKeyUp\|<button\|<a "
```

### Positive tabIndex values
```bash
grep -rn 'tabIndex="\?[1-9]' \
    --include="*.jsx" \
    --include="*.tsx" \
    --include="*.html" \
    .
```

### Focus indicators removed
```bash
grep -rn "outline:\s*none\|outline:\s*0" \
    --include="*.css" \
    --include="*.scss" \
    --include="*.sass" \
    --include="*.less" \
    . | grep "focus"
```

## Color Contrast

### Extract hex colors
```bash
grep -rh "#[0-9a-fA-F]\{3,8\}" \
    --include="*.css" \
    --include="*.scss" \
    --include="*.sass" \
    --include="*.less" \
    --include="*.tsx" \
    --include="*.jsx" \
    . | grep -o "#[0-9a-fA-F]\{3,8\}" | sort -u
```

### Extract RGB/RGBA colors
```bash
grep -rh "rgba\?\([^)]*)" \
    --include="*.css" \
    --include="*.scss" \
    --include="*.sass" \
    --include="*.less" \
    . | grep -o "rgba\?\([^)]*)" | sort -u
```

## ARIA Issues

### Find ARIA attributes
```bash
grep -rn "aria-" \
    --include="*.jsx" \
    --include="*.tsx" \
    --include="*.html" \
    .
```

### Find role attributes
```bash
grep -rn 'role=' \
    --include="*.jsx" \
    --include="*.tsx" \
    --include="*.html" \
    .
```

## Form Labels

### Inputs without labels
```bash
grep -rn "<input" \
    --include="*.jsx" \
    --include="*.tsx" \
    --include="*.html" \
    . | grep -v "aria-label\|aria-labelledby"
```

### Form elements without associated labels
```bash
grep -rn "<input\|<select\|<textarea" \
    --include="*.jsx" \
    --include="*.tsx" \
    --include="*.html" \
    . | grep -v "id=\|aria-label"
```

## Heading Structure

### Find all headings
```bash
grep -rn "<h[1-6]" \
    --include="*.jsx" \
    --include="*.tsx" \
    --include="*.html" \
    .
```

### Check for h1 presence
```bash
grep -r "<h1" \
    --include="*.jsx" \
    --include="*.tsx" \
    --include="*.html" \
    .
```

## Language Attributes

### Check for lang attribute on html
```bash
grep -rn "<html" \
    --include="*.html" \
    --include="*.astro" \
    . | grep -v 'lang='
```

## Link Text

### Find potentially ambiguous link text
```bash
grep -rn 'click here\|here\|read more\|learn more\|link' \
    --include="*.jsx" \
    --include="*.tsx" \
    --include="*.html" \
    . | grep -i "<a"
```

## Media Elements

### Videos without captions
```bash
grep -rn "<video" \
    --include="*.jsx" \
    --include="*.tsx" \
    --include="*.html" \
    . | grep -v "<track"
```

### Audio without transcripts
```bash
grep -rn "<audio" \
    --include="*.jsx" \
    --include="*.tsx" \
    --include="*.html" \
    .
```

## Usage Notes

- All patterns use `-rn` for recursive search with line numbers
- Customize `--include` patterns based on your project's file types
- Pipe results through `wc -l` to count occurrences
- Use `> output.txt` to save results to file
- Patterns may have false positives - manual review required
- Combine patterns with context flags: `-A 2` (after), `-B 2` (before), `-C 2` (context)
