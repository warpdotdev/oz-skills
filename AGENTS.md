# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Repository Overview

This is the `oz-skills` repository - a public catalog of reusable Agent Skills for Warp AI agents and Oz. These are pre-built skills that external users can copy into their projects to teach agents about common workflows and best practices.

## Agent Skills Standard

This repository follows the [Agent Skills](https://agentskills.io) open standard. Agent Skills are folders containing a `SKILL.md` file with YAML frontmatter and markdown instructions that agents can discover and use.

For comprehensive details about the skills format and usage patterns, see `wip/warp-skills-overview.md`.

## Repository Structure

All skills are stored in the `.warp/skills/` directory. Each skill has its own subdirectory:

```
.warp/skills/
├── docs-bot/
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
description: Brief one-sentence description of what this skill does
---

# Skill Content

Your instructions, examples, and guidance here in markdown format.
```

### Required Fields

- **name**: Kebab-case identifier (e.g., `docs-bot`, `rust-testing`, `api-conventions`)
- **description**: One sentence explaining what the skill teaches and when to use it

## Repository Conventions

When working in this repository:

- **One skill per directory** in `.warp/skills/`
- **Use kebab-case** for skill directory names (e.g., `docs-bot`, `deployment-workflow`)
- **Each skill must have** a `SKILL.md` file with proper frontmatter
- **Keep descriptions concise** - they help agents decide when to load the skill
- **Include examples** - real code snippets and commands make skills more useful
- **Focus on workflows** - skills should capture procedural knowledge, not general documentation

## Testing Skills

To test a skill from this repository:

1. Copy the skill folder to a test project's `.warp/skills/` directory
2. Interact with a Warp agent on a relevant task
3. Verify the agent follows the skill's guidance
4. Refine the skill based on results

## Common Skill Types

Good candidates for skills in this repository:

- **Workflow automation** (e.g., docs-bot for automatic documentation updates)
- **Testing patterns** (e.g., how to write tests for specific frameworks)
- **Deployment procedures** (e.g., CI/CD workflows)
- **Code conventions** (e.g., style guides, naming patterns)
- **Tool usage** (e.g., how to use specific CLIs or APIs)
