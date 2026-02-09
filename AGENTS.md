# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Repository Overview

This is the `oz-skills` repository - a public catalog of reusable Agent Skills for Warp AI agents and Oz. These are pre-built skills that external users can copy into their projects to teach agents about common workflows and best practices.

## Agent Skills Standard

This repository follows the [Agent Skills](https://agentskills.io) open standard. Agent Skills are folders containing a `SKILL.md` file with YAML frontmatter and markdown instructions that agents can discover and use.

For comprehensive details about the skills format and usage patterns, see `wip/warp-skills-overview.md`.

## Repository Structure

All skills are stored in the `.agents/skills/` directory. Each skill has its own subdirectory:

```
.agents/skills/
├── docs-update/
│   └── SKILL.md
├── another-skill/
│   └── SKILL.md
└── ...
```

## Skill File Format

Each skill must have a `SKILL.md` file with this structure:

```markdown
---
name: skill-name
description: Imperative summary sentence. Use when sentence.
---

# Skill Title

Your instructions, examples, and guidance here in markdown format.
```

### Required Fields

- **name**: Kebab-case identifier (e.g., `docs-update`, `rust-testing`, `api-conventions`)
- **description**: Two sentences in a strict pattern:
  - Sentence 1: Imperative verb + what the skill does (e.g., `Audit...`, `Build...`, `Test...`)
  - Sentence 2: Starts with `Use when...` and describes trigger scenarios

## Skill Metadata Style Guide (Canonical)

Use these rules whenever creating or editing a skill:

- `name` must be kebab-case and exactly match the skill directory name
- `description` must be exactly two sentences
- `description` sentence 1 must start with an imperative verb (`Build`, `Audit`, `Test`, `Optimize`, `Triage`, `Generate`, `Investigate`, etc.)
- `description` sentence 2 must start with `Use when...`
- Keep `description` concise and concrete; avoid filler and unnecessary quotes
- `SKILL.md` must include a single H1 in Title Case
- H1 should reflect the skill's human-readable purpose (for example, `# Web Performance Audit`)

### Authoring Template (Copy/Paste)

Use this exact template when authoring a new skill:

````markdown
---
name: your-skill-name
description: Verb-first summary of what this skill does. Use when the user asks for the workflow this skill is designed to handle.
---

# Your Skill Title

## When to Use

- Trigger condition 1
- Trigger condition 2
- Trigger condition 3

## Workflow

1. Step one
2. Step two
3. Step three

## Examples

```bash
# Example command(s)
```
````

## Repository Conventions

When working in this repository:

- **One skill per directory** in `.agents/skills/`
- **Use kebab-case** for skill directory names (e.g., `docs-update`, `deployment-workflow`)
- **Each skill must have** a `SKILL.md` file with proper frontmatter
- **Keep descriptions concise** - they help agents decide when to load the skill
- **Include examples** - real code snippets and commands make skills more useful
- **Focus on workflows** - skills should capture procedural knowledge, not general documentation

## Testing Skills

To test a skill from this repository:

1. Copy the skill folder to a test project's `.agents/skills/` directory
2. Interact with a Warp agent on a relevant task
3. Verify the agent follows the skill's guidance
4. Refine the skill based on results

## Common Skill Types

Good candidates for skills in this repository:

- **Workflow automation** (e.g., docs-update for automatic documentation updates)
- **Testing patterns** (e.g., how to write tests for specific frameworks)
- **Deployment procedures** (e.g., CI/CD workflows)
- **Code conventions** (e.g., style guides, naming patterns)
- **Tool usage** (e.g., how to use specific CLIs or APIs)
