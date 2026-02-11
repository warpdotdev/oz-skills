---
name: github-issue-dedupe
description: Detect duplicate GitHub issues using semantic search and keyword matching. Use when asked to find duplicates, check for similar issues, or set up automated duplicate detection.
license: MIT
---

# GitHub Duplicate Issue Detection

Find duplicate GitHub issues using multi-strategy search. Can be run manually or automated via GitHub Actions.

## Workflow

### 1. Gather Issue Context

**Extract key information from the target issue:**
- Issue number and title
- Full body content
- Error messages or stack traces
- Keywords and technical terms
- Symptoms or behavior descriptions

### 2. Search Strategy

**Use `gh` to search for related issues using multiple strategies:**
- Keyword search from title and body
- Search for similar error messages
- Look for similar symptoms

### 3. Candidate Inspection

**For each potential duplicate:**
- View full issue with `gh issue view <number>`
- Compare:
  - Root cause (same underlying problem?)
  - Symptoms (identical behavior?)
  - Error messages (exact match or very similar?)
  - Affected components (same area of code?)

**High confidence indicators:**
- Identical error messages
- Same reproduction steps
- Same root cause with different descriptions
- One issue references the other

**Low confidence (not duplicates):**
- Similar symptoms but different causes
- Related but independent bugs
- Same component but different behaviors

### 4. Report Findings

**If duplicates found:**

Post comment on target issue:
```bash
gh issue comment <number> --body "This is potentially a duplicate of #123 and #456."
```

**Format rules:**
- Single duplicate: "This is potentially a duplicate of #123."
- Two duplicates: "This is potentially a duplicate of #123 and #456."
- Three+ duplicates: "This is potentially a duplicate of #123, #456, and #789."

**Only comment if high confidence** (90%+ certain). When uncertain, do nothing.

## Examples

### Example 1: Clear Duplicate

**Target Issue #150:**
```
Title: "Dropdown menu stays open on mobile Safari"
Body: Clicking menu items doesn't close dropdown on iOS
```

**Search process:**
```bash
gh issue list --search "dropdown mobile safari"
gh issue list --search "menu doesn't close"
gh issue view 87  # Found similar issue
```

**Issue #87:**
```
Title: "Mobile menu not closing after selection"
Body: On iOS Safari, menu stays open after clicking items
```

**Determination:** Duplicate
- Same symptom (menu stays open)
- Same platform (iOS Safari)
- Same root cause

### Example 2: Similar But Not Duplicate

**Target Issue #200:**
```
Title: "Form validation error on submit"
Error: "Cannot read property 'value' of null"
```

**Search process:**
```bash
gh issue list --search "form validation"
gh issue list --search "Cannot read property value null"
gh issue view 175
```

**Issue #175:**
```
Title: "Form submission fails"
Error: "Cannot read property 'email' of undefined"
```

**Determination:** Not duplicate
- Different error messages
- Different null references (value vs email)
- Related area but different bugs

### Example 3: Multiple Duplicates

**Target Issue #300:**
```
Title: "Build fails with 'module not found' error"
Error: Error: Cannot find module './config'
```

**Search results:**
- Issue #250: Same error, same module
- Issue #280: Same error, same module
- Issue #290: Different module error (not duplicate)

**Action:**
```bash
gh issue comment 300 --body "This is potentially a duplicate of #250 and #280."
```

