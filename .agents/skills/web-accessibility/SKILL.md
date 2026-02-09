---
name: web-accessibility
description: Audit web applications for WCAG accessibility compliance. Use when asked to run accessibility checks, identify common violations, and provide remediation guidance.
tags: [accessibility, a11y, wcag, testing, auditing]
---

# Accessibility Auditor

Audit web applications for WCAG 2.0/2.1/2.2 compliance by identifying common violations and providing actionable remediation steps.

## When to Use

- User requests accessibility audit, a11y check, or WCAG compliance review
- User mentions accessibility issues, screen readers, or keyboard navigation problems
- User asks to check or improve accessibility for people with disabilities

## WCAG Principles: POUR

| Principle | Description |
|-----------|-------------|
| **P**erceivable | Content can be perceived through different senses |
| **O**perable | Interface can be operated by all users |
| **U**nderstandable | Content and interface are understandable |
| **R**obust | Content works with assistive technologies |

## Conformance Levels

| Level | Requirement | Target |
|-------|-------------|--------|
| **A** | Minimum accessibility | Must pass |
| **AA** | Standard compliance | Should pass (legal requirement in many jurisdictions) |
| **AAA** | Enhanced accessibility | Nice to have |

---

## 12 Most Common WCAG Violations

Based on WebAIM Million (2021) research analyzing top 1M websites:

1. **Low Color Contrast (WCAG 1.4.3)** - 86.4% of sites
   - Text < 4.5:1 contrast ratio
   - Large text < 3:1 contrast ratio
   - UI components < 3:1

2. **Missing/Inadequate Alt Text (WCAG 1.1.1)** - 60.6% of sites
   - Images without alt attribute
   - Alt text with "image", "picture", "photo"
   - Empty alt on meaningful images

3. **Missing Name, Role, or Value (WCAG 4.1.2)**
   - Interactive elements without accessible names
   - Custom components without proper ARIA
   - Buttons, form fields, custom widgets

4. **Keyboard Navigation Failures (WCAG 2.1.1)**
   - Elements with onClick but not keyboard accessible
   - Missing focus indicators
   - Trapped keyboard focus

5. **Unlabeled Form Controls (WCAG 1.3.1, 3.3.2)** - 39.6% of sites
   - Inputs without `<label>` or aria-label
   - Labels not programmatically associated

6. **Missing Language Attributes (WCAG 3.1.1)** - 28.9% of sites
   - No lang attribute on `<html>`
   - Missing lang for foreign language passages

7. **Improper Heading Structure (WCAG 1.3.1, 2.4.6)**
   - Skipped heading levels (h1 → h3)
   - Multiple h1s or no h1
   - Empty headings

8. **Empty Links or Poor Link Text (WCAG 2.4.4)**
   - Links with "click here", "here", "read more"
   - Empty links or links with only icons

9. **Missing/Improper Focus Indicators (WCAG 2.4.7)**
   - CSS removing outline without replacement
   - Insufficient focus indicator contrast

10. **Overuse/Misuse of ARIA (WCAG 4.1.2)**
    - Unnecessary ARIA when native HTML works
    - Invalid ARIA attributes for roles
    - Required ARIA attributes missing

11. **Inadequate Data Table Markup (WCAG 1.3.1)**
    - Tables without `<th>` elements
    - Missing scope or headers attributes

12. **Missing Media Captions (WCAG 1.2.1, 1.2.2)**
    - Videos without captions/subtitles
    - Audio without transcripts

---

## Audit Process

### Phase 1: Automated Testing

**Run ESLint (React/JSX projects):**
```bash
npx eslint --ext .jsx,.tsx --no-ignore --format json . > .claude/skills/a11y-auditor/eslint-results.json 2>&1 || true
```
Or use helper script: `.claude/skills/a11y-auditor/scripts/run-eslint.sh`

**Run Lighthouse (production/staging):**
```bash
npx lighthouse https://example.com --only-categories=accessibility --output=json --output-path=./lighthouse-results.json
```

**Check for axe-core integration:**
```bash
grep -r "@axe-core\|axe-core" package.json
```

### Phase 2: Manual Code Inspection

Use grep patterns from `references/grep-patterns.md` to search for:
- Missing alt text
- Keyboard navigation issues
- Color values for contrast checking
- ARIA issues
- Form labels
- Heading structure
- Language attributes
- Poor link text
- Media elements

See `references/grep-patterns.md` for complete pattern list.

### Phase 3: Analyze & Prioritize

Group findings by severity using WCAG impact levels:

**Critical (fix immediately):**
- Keyboard traps
- No focus indicators
- Missing form labels
- Missing alt text on functional images
- Insufficient color contrast on interactive elements

**Serious (fix before launch):**
- Missing page language
- Improper heading structure
- Non-descriptive link text
- Missing skip links
- Auto-playing media

**Moderate (fix soon):**
- Missing ARIA labels on icons
- Inconsistent navigation
- Missing error identification
- Missing landmark regions

### Phase 4: Manual Testing

Follow `references/screen-reader-guide.md` for:
- Keyboard navigation testing
- Screen reader testing (VoiceOver, NVDA, JAWS)
- Zoom and reflow testing
- High contrast mode testing
- Reduced motion testing

---

## WCAG Pattern Examples

### Perceivable

#### Alt Text (1.1.1)
```html
<!-- ❌ Missing alt -->
<img src="chart.png">

<!-- ✅ Descriptive alt -->
<img src="chart.png" alt="Bar chart showing 40% increase in Q3 sales">

<!-- ✅ Decorative (empty alt) -->
<img src="decorative-border.png" alt="" role="presentation">
```

#### Color Contrast (1.4.3)
```css
/* ❌ Low contrast (2.5:1) */
.low-contrast {
  color: #999;
  background: #fff;
}

/* ✅ Sufficient contrast (7:1) */
.high-contrast {
  color: #333;
  background: #fff;
}
```

**Contrast requirements:**
- Normal text: 4.5:1 (AA), 7:1 (AAA)
- Large text (18px+ or 14px+ bold): 3:1 (AA), 4.5:1 (AAA)
- UI components: 3:1

#### Media Alternatives (1.2)
```html
<video controls>
  <source src="video.mp4" type="video/mp4">
  <track kind="captions" src="captions.vtt" srclang="en" label="English" default>
</video>
```

### Operable

#### Keyboard Navigation (2.1.1)
```javascript
// ❌ Only click
element.addEventListener('click', handleAction);

// ✅ Click + keyboard
element.addEventListener('click', handleAction);
element.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    handleAction();
  }
});
```

#### Focus Visible (2.4.7)
```css
/* ❌ Never remove focus */
*:focus { outline: none; }

/* ✅ Keyboard-only focus */
:focus-visible {
  outline: 2px solid #005fcc;
  outline-offset: 2px;
}
```

#### Skip Links (2.4.1)
```html
<body>
  <a href="#main-content" class="skip-link">Skip to main content</a>
  <header><!-- navigation --></header>
  <main id="main-content" tabindex="-1">
    <!-- content -->
  </main>
</body>
```

```css
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: #000;
  color: #fff;
  padding: 8px 16px;
  z-index: 100;
}

.skip-link:focus {
  top: 0;
}
```

#### Reduced Motion (2.3.3)
```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

### Understandable

#### Page Language (3.1.1)
```html
<!-- ❌ No language -->
<html>

<!-- ✅ Language specified -->
<html lang="en">

<!-- ✅ Language changes -->
<p>The French word for hello is <span lang="fr">bonjour</span>.</p>
```

#### Form Labels (3.3.2)
```html
<!-- ❌ No label -->
<input type="email" placeholder="Email">

<!-- ✅ Explicit label -->
<label for="email">Email address</label>
<input type="email" id="email" autocomplete="email">

<!-- ✅ With hint -->
<label for="password">Password</label>
<input type="password" id="password" aria-describedby="password-requirements">
<p id="password-requirements">
  Must be at least 8 characters with one number.
</p>
```

#### Error Handling (3.3.1)
```html
<label for="email">Email</label>
<input type="email" id="email" 
       aria-invalid="true" 
       aria-describedby="email-error">
<p id="email-error" role="alert">
  Please enter a valid email address.
</p>
```

### Robust

#### ARIA Usage (4.1.2)
```html
<!-- ❌ Unnecessary ARIA -->
<button role="button">Submit</button>

<!-- ✅ Native HTML -->
<button>Submit</button>

<!-- ✅ ARIA when needed (custom tabs) -->
<div role="tablist" aria-label="Product information">
  <button role="tab" aria-selected="true" aria-controls="panel-1">
    Description
  </button>
  <button role="tab" aria-selected="false" aria-controls="panel-2" tabindex="-1">
    Reviews
  </button>
</div>
<div role="tabpanel" id="panel-1" aria-labelledby="tab-1">
  <!-- content -->
</div>
```

#### Live Regions (4.1.3)
```html
<!-- Polite (waits for pause) -->
<div aria-live="polite" aria-atomic="true">
  Status update
</div>

<!-- Assertive (interrupts) -->
<div role="alert" aria-live="assertive">
  Error: Form submission failed
</div>
```

#### Visually Hidden Text
```css
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

```html
<button>
  <svg aria-hidden="true"><!-- icon --></svg>
  <span class="visually-hidden">Delete item</span>
</button>
```

---

## Output Format

Generate reports structured as:

```markdown
# Accessibility Audit Report

## Summary
- Total Issues: X
- Critical: X | Serious: X | Moderate: X | Minor: X
- WCAG Level: A, AA, or AAA
- Automated Coverage: ~57% (manual testing required)

## Critical Issues (Fix Immediately)

### 1. [Issue Name] - WCAG X.X.X
**Severity:** Critical  
**Impact:** [Who is affected and how]  
**Affected:** X elements

**Locations:**
- `path/to/file.tsx:123`
- `path/to/file.tsx:456`

**Problem:**
[Brief description]

**Fix:**
```tsx
// Before
<div onClick={handleClick}>Click me</div>

// After
<button onClick={handleClick}>Click me</button>
```

**Why:** [Accessibility principle]

---

## Serious Issues
[Same format]

## Moderate Issues  
[Same format]

## Testing Recommendations
1. Manual keyboard testing (Tab, Enter, Escape)
2. Screen reader testing (see references/screen-reader-guide.md)
3. Automated testing setup (@axe-core/react or Lighthouse CI)
4. Color contrast validation (WebAIM Contrast Checker)

## Next Steps
[Prioritized action items]
```

---

## Tools & Resources

### Development Tools
- **eslint-plugin-jsx-a11y** - React/JSX static analysis (~37 rules)
- **axe-core DevTools** - Browser extension for runtime testing
- **Lighthouse** - Built into Chrome DevTools

### Testing Tools  
- **@axe-core/react** - Runtime accessibility testing
- **@axe-core/playwright** - E2E test integration
- **pa11y** - Automated command-line testing

### Manual Testing
- **WebAIM Contrast Checker** - https://webaim.org/resources/contrastchecker/
- **WAVE** - Browser extension for visual feedback
- **Screen readers** - NVDA (Windows), VoiceOver (macOS), JAWS

### Reference Docs
- `references/WCAG-criteria.md` - All WCAG 2.1 success criteria
- `references/ARIA-patterns.md` - Common ARIA patterns and examples
- `references/screen-reader-guide.md` - Testing commands and scenarios
- `references/grep-patterns.md` - Search patterns for code audits

### References
- [WebAIM Million](https://webaim.org/projects/million/) - Annual analysis of top 1M websites (violation statistics)
- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/) - Interactive WCAG guide
- [WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/) - Official ARIA patterns
- [Deque axe Rules](https://dequeuniversity.com/rules/axe/) - All axe-core rules explained
- [jsx-a11y Rules](https://github.com/jsx-eslint/eslint-plugin-jsx-a11y#supported-rules) - ESLint accessibility rules

---

## Important Notes

- Automated tools catch 30-57% of issues; manual testing required
- Pages with ARIA average 41% more errors than without
- Always test with actual assistive technology when possible
- Focus on critical issues first (keyboard, screen readers, contrast)
- Document deliberate accessibility decisions
- Test on multiple browsers and devices
- Include users with disabilities in testing when possible

## Common Pitfalls to Avoid

1. Relying solely on automated testing
2. Using ARIA when native HTML suffices
3. Removing focus indicators
4. Using positive tabindex values
5. Color as only means of conveying information
6. Keyboard traps in modals/dialogs
7. Non-descriptive link text
8. Missing or incorrect heading hierarchy
9. Unlabeled form controls
10. Missing language attributes
