---
name: github-issue-triage
description: Triage GitHub bug reports only. Check if the issue has sufficient detail to be actionable. If not, identify missing info and suggest what's needed from the issue filer.
---

# GitHub Issue Triage

Evaluate GitHub issues for bug reports only. Determine if they contain sufficient info to be actionable. If not, identify missing details and provide constructive feedback.

## Workflow

### 1. Locate Issue Template

**Check for existing templates:**
- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/ISSUE_TEMPLATE/bug_report.yml`
- `.github/ISSUE_TEMPLATE/*.md`
- `.github/ISSUE_TEMPLATE.md`
- `ISSUE_TEMPLATE.md`

**If no template exists**, use `references/ISSUE_TEMPLATE.md` from this skill as the fallback template, then evaluate the issue against it.


### 2. Evaluate Issue Quality

**Critical questions:**

1. **Is this a bug report?**
   - If the issue is a feature request or a question, do not evaluate this issue

2. **Is the description clear?**
   - What's broken or wrong
   - Expected behavior vs. what actually happens
   - Impact or severity

3. **Can we reproduce it?**
   - Step-by-step reproduction
   - OR sandbox/StackBlitz/CodeSandbox link
   - OR minimal code example

**Be reasonable:**
- Don't require every template field to be filled
- Focus on minimum info needed to investigate
- Consider context (obvious bugs vs. edge cases)

### 3. Make Determination

**Ready to be actionable:**
- Has clear problem description
- Includes reproduction path OR enough context to debug
- Actually a bug (not feature/question)

**Needs more info:**
- Vague description ("it doesn't work")
- Missing reproduction steps AND no code example
- Unclear what the expected behavior should be
- Missing critical context (e.g., "crashes" but no error message)

### 4. Provide Feedback

**If ready:** Confirm issue is actionable.

**If needs info:** Specify what's missing. Be constructive and specific.

## Examples

### Example 1: Ready to Investigate

```markdown
**Issue**: Dropdown menu doesn't close on mobile Safari

**Description**: 
When clicking a dropdown menu item on iOS Safari, the menu stays 
open instead of closing. Works fine on desktop Chrome/Firefox.

**Steps**:
1. Visit https://stackblitz.com/edit/my-repro
2. Open on iOS Safari
3. Click dropdown, select any item
4. Menu stays open (should close)

**Environment**: iOS 16.3, Safari
```

**Evaluation**: ✅ Ready
- Clear description
- Has reproduction link
- Specific environment details

### Example 2: Needs More Info

```markdown
**Issue**: Button is broken

**Description**: 
The submit button doesn't work properly.
```

**Evaluation**: ❌ Needs info
**Missing**:
- What does "doesn't work" mean? (no click? error? wrong behavior?)
- Expected vs. actual behavior
- Steps to reproduce
- Any error messages

### Example 3: Edge Case - Reasonable

```markdown
**Issue**: Console error on form submit

**Description**:
Getting "Cannot read property 'value' of null" when submitting 
the contact form. Happens 100% of the time.

**Error**:
```
TypeError: Cannot read property 'value' of null
  at handleSubmit (ContactForm.tsx:45)
```

**Environment**: Chrome 120, Windows 11
```

**Evaluation**: ✅ Ready
- Clear error message with stack trace
- Specific file/line reference
- Reproducible (100% of time)
- **Note**: No explicit repro steps, but error is clear enough to investigate

### Example 4: Bug Report with Insufficient Reproducibility

```markdown
**Issue**: [glob-loader] Duplicate id warning on file update

**Description**:
I'm encountering an issue with the glob loader. Whenever I update 
the watched file, I get a warning message in the logs.


The warning message:
```
13:23:31 [WARN] [glob-loader] Duplicate id "russian-test" found in 
/Users/user/Code/project/content/posts/russian-test.md. Later items 
with the same id will overwrite earlier ones.
```

**Expected**: No warning message

**Link to Minimal Reproducible Example**: - N/A
```

**Evaluation**: ❌ Needs info
- Describes a real bug (warning message)
- Has error output and code reference
- BUT: No minimal reproduction provided
- Code link points to private repo (can't access to debug)

**Missing**:
- Minimal reproduction (example code or link to a working reproduction)


