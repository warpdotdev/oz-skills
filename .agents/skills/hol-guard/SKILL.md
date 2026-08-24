---
name: hol-guard
description: Protect local AI harnesses and agent workflows with HOL Guard runtime checks, approvals, receipts, and package scans. Use when a Warp or Oz agent needs to install HOL Guard, protect a supported harness, review a blocked action, or verify a plugin, skill, or MCP package before use.
license: Apache-2.0
---

# HOL Guard

Use HOL Guard when a task needs local AI runtime protection, approval review, evidence, or package verification. Prefer Guard-owned commands over editing harness security configuration directly.

## When to Use

- Set up HOL Guard for a supported local AI harness.
- Check whether Guard protection is installed and healthy.
- Review blocked or approval-required actions without bypassing the policy decision.
- Collect receipts, inventory, or other Guard evidence.
- Verify an agent plugin, skill, MCP package, or mixed agent workspace before use or release.

## Safety Rules

- Never read `.env` files to make Guard work.
- Never bypass a Guard approval or convert a review outcome into an automatic allow.
- Do not claim a harness is protected until a Guard command proves it.
- Preserve existing user configuration and prefer reversible Guard commands.
- Treat scanner findings as real until they are inspected.

## Install and Inspect

Install the runtime in an isolated environment when possible:

```bash
pipx install hol-guard
hol-guard status
hol-guard detect --json
```

For package scanning, install the scanner separately:

```bash
pipx install plugin-scanner
```

Do not assume the `hol-guard` distribution also provides `plugin-scanner`.

## Protect a Supported Harness

HOL Guard supports Codex, Claude Code, Copilot CLI, Cursor, Gemini CLI, Hermes, OpenClaw, OpenCode, and Antigravity. Use the Guard-owned setup flow instead of hand-editing the harness config:

```bash
hol-guard bootstrap
hol-guard install <harness>
hol-guard run <harness> --dry-run
hol-guard run <harness>
hol-guard doctor <harness> --json
```

Common harness names include:

- `codex`
- `claude-code`
- `copilot`
- `cursor`
- `gemini`
- `hermes`
- `openclaw`
- `opencode`
- `antigravity`

For Hermes, prefer its dedicated bootstrap when appropriate:

```bash
hol-guard hermes bootstrap
```

Warp and Oz can use this skill to operate HOL Guard, but do not describe Warp itself as a protected harness unless HOL Guard reports support for it.

## Review Approvals and Evidence

When Guard blocks or queues work, inspect the request rather than bypassing it:

```bash
hol-guard approvals
hol-guard approvals open
hol-guard receipts
hol-guard diff <harness>
```

Only after the user has reviewed the risk and requested a terminal decision:

```bash
hol-guard approvals approve <request-id>
hol-guard approvals deny <request-id>
```

For audit and handoff evidence:

```bash
hol-guard receipts
hol-guard inventory
hol-guard abom --format json
hol-guard events
hol-guard explain <artifact-id>
```

## Scan Agent Packages

Run scanner mode from the package or workspace root so related plugin, skill, MCP, and harness surfaces can be discovered together:

```bash
plugin-scanner lint .
plugin-scanner verify .
```

For a specific package:

```bash
plugin-scanner lint <path>
plugin-scanner verify <path>
```

Useful targets include Codex plugins and marketplaces, Claude Code projects, MCP servers, Agent Skills folders containing `SKILL.md`, and mixed agent workspaces.

## Debugging

Use Guard-owned diagnostics before changing configuration manually:

```bash
hol-guard doctor
hol-guard detect --json
hol-guard settings show
plugin-scanner verify . --json
```

When reporting the result, state what command ran, what Guard found, what remains blocked or risky, and what proof exists. Never claim protection, approval, or release readiness without command output proving it.
