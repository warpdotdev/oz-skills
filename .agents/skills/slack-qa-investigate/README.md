# Slack Q&A Bot Skill

This is an agent skill for the **Oz Slack Q&A Bot** — a Slack bot that answers questions about your codebase using [the Oz platform API](https://docs.warp.dev/agents/ambient-agents).

The skill defines how the agent investigates and answers questions: read-only, deep investigation, following links, and citing sources.

## Getting Started

To deploy your own Slack Q&A Bot, set up the infrastructure repo:

**[github.com/warpdotdev/oz-slack-q-and-a-bot](https://github.com/warpdotdev/oz-slack-q-and-a-bot)**

The repo README walks through Slack app creation, Warp API credentials, and running the bot.

## Quick Setup via Warp

Instead of manually cloning and configuring, paste this prompt into Warp Agent Mode:

```
Clone https://github.com/warpdotdev/oz-slack-q-and-a-bot and walk me through the setup process for environment variables and deployment using Railway. Use the README as a guide.
```
