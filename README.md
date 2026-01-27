# Oz Skills

A curated collection of reusable [Agent Skills](https://agentskills.io) for Warp AI agents and Oz.

## What Are Agent Skills?

Agent Skills are markdown files that teach AI agents about your conventions, best practices, and workflows. When you work with agents in Warp, they automatically discover and use these skills to provide context-aware help.

Think of skills as onboarding guides that help agents understand how you work.

## How Skills Work

- **Skills live in `.warp/skills/` directories** - either in your project (`.warp/skills/`) or globally (`~/.warp/skills/`)
- **Each skill is a folder** containing a `SKILL.md` file with YAML frontmatter and markdown content
- **Warp agents automatically discover** and load skills when relevant to your current task

## Using These Skills

To use a skill from this repository:

1. Copy the skill folder (e.g., `docs-bot`) from `.warp/skills/` 
2. Paste it into your project's `.warp/skills/` directory, or
3. Paste it into `~/.warp/skills/` to use it across all projects

Warp will automatically detect the new skill on your next interaction.

## Skills in This Repository

_Skills will be listed here as they are added._

## Contributing

Contributions are welcome! More guidelines coming soon.

## Learn More

- [Agent Skills Specification](https://agentskills.io)
- [Warp Documentation](#) _(coming soon)_
