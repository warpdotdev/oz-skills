---
name: docs-bot
description: Automatically update user-facing documentation when code changes. Use when asked to "update docs", "review docs", "documentation changes", running as a scheduled documentation task, or analyzing recent commits for documentation needs.
---

# Documentation Bot

Automatically review code changes and update user-facing documentation to keep it synchronized with the codebase. Works across documentation platforms (Mintlify, Docusaurus, GitBook, Fumadocs, etc.) and supports both monorepo and multi-repo setups.

## Workflow

### 1. Identify Significant Code Changes

Determine which commits need documentation updates:

- Find the default branch
- Get recent commits (default: last 24 hours, or accept user-specified timeframe)
- Examine each commit's changes to understand what was modified

**Filter for significant changes:**
- New features or capabilities
- API changes (new endpoints, parameters, return values)
- Breaking changes
- New configuration options
- New CLI commands or flags
- Changes to user-facing behavior

**Skip documentation for:**
- Internal refactoring
- Test-only changes
- Minor bug fixes
- Typo corrections in code
- Performance optimizations without user impact

Be conservative: quality over quantity. When in doubt about significance, skip the update.

### 2. Analyze Documentation Context

**Locate documentation:**
- Check for documentation directory in current repo (monorepo pattern)
- Look for separate documentation repository in environment

**Identify documentation platform:**
Determine the platform by examining configuration files and directory structure (e.g., Mintlify, Docusaurus, GitBook, Fumadocs, or generic markdown).

**Understand documentation style:**
Read several existing documentation files to identify tone, voice, structure, code example patterns, terminology, and formatting conventions. Check for style guides or contribution documentation.

### 3. Determine Documentation Updates

Map code changes to documentation needs (new content, modifications, or additions to existing content).

**Guidelines:**
- Prioritize user-facing changes over implementation details
- Match existing documentation verbosity (some docs are comprehensive, others minimal)
- Preserve existing accurate content—be strictly additive when possible
- Keep content focused and avoid generic advice

### 4. Generate Documentation Changes

**Match existing style:**
- Use the same tone, voice, and formality level identified in step 2
- Follow the same heading structure and hierarchy
- Use consistent terminology
- Match code block formatting (language tags, highlighting)
- Follow platform conventions (frontmatter, special syntax, custom components)

### 5. Execute or Report

**Testing mode** (when user asks to "see what would change"):

Output a text summary describing:
- What changes were detected in commits
- Which documentation files would be modified
- What content would be added or changed
- Rationale for why these updates are needed

**Execution mode** (when running as automation):

1. Create a descriptive branch name (e.g., `docs/auto-update-YYYYMMDD`)

2. Make documentation changes to appropriate files

3. Commit with descriptive message listing the changes
   - Include co-author line: `Co-Authored-By: Warp <agent@warp.dev>`

4. Push branch and create PR with description linking to relevant commits:
   - List which code changes triggered which documentation updates
   - Include commit references or URLs from source repository
   - Request review for accuracy and completeness

## Multi-Repository Setup

When source code and documentation are in separate repositories, identify changes in the source repo, then switch to the docs repo and follow the workflow above. Reference source commits in the PR description.

## Edge Cases

- If no significant changes found, report that no documentation updates are needed
- If documentation platform is unclear, default to standard markdown syntax
- If conflicting with existing content, preserve existing information and note conflicts for human review

## Key Principles

- **Conservative**: Better to skip than clutter documentation
- **Consistent**: Match existing style, tone, and structure exactly
- **Contextual**: Consider the full documentation landscape, not just individual files
- **Clear**: Explain significance of changes and rationale for updates
- **Practical**: Focus on helping users accomplish tasks, not describing implementation
