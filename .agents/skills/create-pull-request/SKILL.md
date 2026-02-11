---
name: create-pull-request
description: Create a GitHub pull request following project conventions. Use when the user asks to create a PR, submit changes for review, or open a pull request. Handles commit analysis, branch management, and PR creation using the gh CLI tool.
license: MIT
---

# Create Pull Request

This skill guides you through creating a well-structured GitHub pull request that follows project conventions and best practices.

## Prerequisites Check

Before proceeding, verify the following:

### 1. Check if `gh` CLI is installed

```bash
gh --version
```

If not installed, inform the user:
> The GitHub CLI (`gh`) is required but not installed. Please install it:
> - macOS: `brew install gh`
> - Other: https://cli.github.com/

### 2. Check if authenticated with GitHub

```bash
gh auth status
```

If not authenticated, guide the user to run `gh auth login`.

### 3. Check for related skills

Before creating a PR, check if any skills are available that relate to code review, CI, or testing. These should be invoked first as prerequisites.

Look for skills with descriptions containing:
- "review" (e.g., code review, PR review, web-design-guidelines)
- "CI" or "ci-fix" (e.g., fixing CI failures)
- "testing" or "test" (e.g., running tests, webapp-testing)

If such skills exist, invoke them before proceeding with PR creation. For example:
- If a `ci-fix` skill exists and CI is failing, use it to diagnose and fix issues
- If a `web-design-guidelines` skill exists for UI changes, use it to review the changes
- If a testing skill exists, use it to ensure tests pass

**Only proceed with PR creation after these prerequisite skills have been satisfied.**

### 4. Verify clean working directory

```bash
git status
```

If there are uncommitted changes, ask the user whether to:
- Commit them as part of this PR
- Stash them temporarily
- Discard them (with caution)

## Check for Existing PR

Before gathering context, check if a PR already exists for the current branch:

```bash
gh pr list --head $(git branch --show-current) --json number,title,url
```

If a PR already exists:
- Display the existing PR details (number, title, URL)
- Ask the user if they want to:
  - View the existing PR: `gh pr view`
  - Update the existing PR (push more commits and the PR will update automatically)
  - Close the existing PR and create a new one

**Only proceed with creating a new PR if no PR exists for this branch.**

## Gather Context

### 1. Identify the current branch

```bash
git branch --show-current
```

Ensure you're not on `main` or `master`. If so, ask the user to create or switch to a feature branch.

### 2. Find the base branch

```bash
git remote show origin | grep "HEAD branch"
```

This is typically `main` or `master`.

### 3. Analyze recent commits relevant to this PR

```bash
git log origin/main..HEAD --oneline --no-decorate
```

Review these commits to understand:
- What changes are being introduced
- The scope of the PR (single feature/fix or multiple changes)
- Whether commits should be squashed or reorganized

### 4. Review the diff

```bash
git diff origin/main..HEAD --stat
```

This shows which files changed and helps identify the type of change.

## Information Gathering

Gather the following information from available context (commit messages, branch names, changed files):

### Information to Extract

1. **Related Issue Number**: Look for patterns like `#123`, `fixes #123`, or `closes #123` in:
   - Commit messages
   - Branch name (e.g., `fix/issue-123`, `feature/123-new-login`)
   - If found, include it in the PR title and/or description
   - If not found, proceed without it

2. **Description**: What problem does this solve? Why were these changes made?
   - Infer from commit messages and diff
   - Describe the changes made

3. **Type of Change**: Bug fix, new feature, breaking change, refactor, cosmetic, documentation, or workflow
   - Determine from commit messages and changed files

4. **Test Procedure**: How was this tested? What could break?
   - Mention test files if they were modified
   - Describe testing approach if evident from changes

### Intelligent PR Title Generation

The PR title should be descriptive and meaningful. **Avoid generic titles** like:
- "initial commit"
- "fix"
- "update"
- "changes"

Instead, create a title that clearly summarizes the changes. Consider these approaches:

#### 1. Conventional Commits Format

Check if the project uses conventional commits by analyzing:
- Commit messages for patterns like `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Branch name prefixes like `feat/`, `fix/`, `docs/`

If conventional commits are detected, use the appropriate prefix for the PR title:
- `feat: Add user authentication with OAuth`
- `fix: Resolve memory leak in data processing`
- `docs: Update API documentation for v2 endpoints`
- `refactor: Simplify error handling logic`
- `test: Add integration tests for payment flow`
- `chore: Update dependencies to latest versions`

**Include issue number if found:**
- `feat: Add user authentication with OAuth (#123)`
- `fix(auth): Resolve memory leak in data processing (fixes #456)`

#### 2. Descriptive Summary

If not using conventional commits, create a clear, action-oriented title:
- Good: "Add pagination to search results"
- Bad: "initial commit"
- Good: "Fix race condition in authentication flow"
- Bad: "fix bug"

**Include issue number if found:**
- "Add pagination to search results (#123)"
- "Fix race condition in authentication flow (fixes #456)"

#### 3. Title Generation Strategy

1. Look at the most significant commit message (often the first or last)
2. Identify the main change from the diff (new feature, bug fix, etc.)
3. Extract the issue title if linked
4. If none of these provide a good title, synthesize one from the changed files and their purpose
5. Append issue number to title if found in commits or branch name

## Git Best Practices

Before creating the PR, consider these best practices:

### Commit Hygiene

1. **Atomic commits**: Each commit should represent a single logical change
2. **Clear commit messages**: Follow conventional commit format when possible
3. **No merge commits**: Prefer rebasing over merging to keep history clean

### Branch Management

1. **Rebase on latest main** (if needed):
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Squash if appropriate**: If there are many small "WIP" commits, consider interactive rebase:
   ```bash
   git rebase -i origin/main
   ```
   Only suggest this if commits appear messy and the user is comfortable with rebasing.

### Push Changes

Ensure all commits are pushed:
```bash
git push origin HEAD
```

If the branch was rebased, you may need:
```bash
git push origin HEAD --force-with-lease
```

## Create the Pull Request

**IMPORTANT**: Read and use the PR template at `.github/pull_request_template.md` if it exists. The PR body format should match the template structure.

When filling out the template:
- Include issue number (e.g., `Fixes #123`, `Closes #456`) if found in context
- If no template exists, create a clear description with:
  - Summary of changes
  - Related issue (if found)
  - Testing performed
  - Any breaking changes or notable impacts
- Fill in all sections with relevant information gathered from commits and context
- Mark the appropriate "Type of Change" checkbox(es) if template has them
- Complete any checklist items that apply

### Draft PR Decision

Decide whether to create a draft PR or a regular PR based on the following:

**Use `--draft` flag when:**
- Changes are incomplete or work-in-progress, but you want early feedback
- Tests are currently failing and you need help debugging
- You're blocked on an architectural decision and need guidance
- Creating the PR as a bookmark for work you'll continue later
- You want to trigger CI checks but aren't ready for full review

**Use regular PR (no `--draft`) when:**
- All tests pass and code is ready for review
- Changes are complete and you're confident in the approach
- You want the PR to be reviewed and merged soon

### Create PR with gh CLI

For a regular PR:
```bash
gh pr create --title "PR_TITLE" --body "PR_BODY" --base main
```

For a draft PR:
```bash
gh pr create --title "PR_TITLE" --body "PR_BODY" --base main --draft
```

## Post-Creation

After creating the PR:

### 1. Open PR in browser for verification

Immediately open the PR in the browser to verify it was created correctly:

```bash
gh pr view --web
```

This allows you to:
- Verify the PR title and description render correctly
- Check that all links work (issue references, etc.)
- Ensure the diff looks as expected
- See any immediate CI status

### 2. Remind about CI checks

Tests and linting will run automatically. Monitor the checks to ensure they pass.

### 3. Suggest next steps (if needed)

- Add reviewers if needed: `gh pr edit --add-reviewer USERNAME`
- Add labels if needed: `gh pr edit --add-label "bug"`

## Error Handling

### Common Issues

1. **No commits ahead of main**: The branch has no changes to submit
   - Ask if the user meant to work on a different branch

2. **Branch not pushed**: Remote doesn't have the branch
   - Push the branch first: `git push -u origin HEAD`

3. **PR already exists**: A PR for this branch already exists
   - Show the existing PR: `gh pr view`
   - Ask if they want to update it instead

4. **Merge conflicts**: Branch conflicts with base
   - Guide user through resolving conflicts or rebasing

## Summary Checklist

Before finalizing, ensure:
- [ ] `gh` CLI is installed and authenticated
- [ ] Related review/CI/testing skills have been invoked
- [ ] No existing PR exists for this branch
- [ ] Working directory is clean
- [ ] All commits are pushed
- [ ] Branch is up-to-date with base branch
- [ ] PR title is descriptive and meaningful (not generic)
- [ ] PR title uses conventional commit format if project uses it
- [ ] Issue number included in title/description if found in context
- [ ] PR description follows template (if template exists)
- [ ] Appropriate type of change is selected
- [ ] Correct draft/regular status chosen
- [ ] PR opened in browser for verification
