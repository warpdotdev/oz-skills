# Contributing to Oz Skills

Thanks for your interest in contributing! We welcome new skills that help agents work more effectively.

## How to Contribute

1. **Fork** this repository
2. **Create** your skill in `.agents/skills/your-skill-name/`
3. **Test** it locally (see below)
4. **Submit** a pull request

## Creating a Skill

Each skill is a folder containing a `SKILL.md` file:

```
.agents/skills/
└── your-skill-name/
    └── SKILL.md
```

Skills follow the [Agent Skills](https://agentskills.io) standard format.

## Testing Locally

Before submitting:

1. Copy your skill folder to `~/.agents/skills/` or a test project's `.agents/skills/`
2. Interact with a Warp agent on a relevant task
3. Verify the agent follows your skill's guidance

## Getting Help

Questions? Join the [Warp Preview Slack](https://warp.dev/preview-slack) and ask in the #general channel.
