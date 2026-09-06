---
name: aeon
description: Set up and run an Aeon autonomous agent instance from your coding agent. Use when the user mentions Aeon, aeon.yml, an Aeon skill, instance, pack, or routine, or asks to schedule, enable, edit, or debug an agent that runs on a cron in GitHub Actions.
license: MIT
---

# Aeon Operator Console

Aeon is an autonomous agent framework that runs your own skills on a schedule in GitHub Actions, in a repo you own. A skill is a Markdown file (`skills/<name>/SKILL.md`); `aeon.yml` decides which skills run and when; results are delivered to a channel you wire up (Telegram, Discord, Slack, or email). This skill is the operator console: set an instance up, choose what runs, edit or debug skills, and turn repeated manual work into scheduled ones.

Canonical source and install: https://github.com/aeonfun/aeon

## When to Use

- The user mentions Aeon, `aeon.yml`, or an Aeon skill / instance / pack / routine.
- They want to set up an agent that runs on a cron in GitHub Actions.
- They want to enable, reschedule, edit, or debug a scheduled skill.
- They want to turn this chat, or their past repeated work, into a scheduled skill.

## Setup

The operator console ships as a plugin for Claude Code and Codex:

```bash
# Claude Code
/plugin marketplace add aeonfun/aeon
/plugin install aeon@aeon

# Codex
codex plugin marketplace add aeonfun/aeon
codex plugin add aeon@aeon
```

Aeon runs from an instance repo the operator owns. A public fork is recommended: Actions minutes are free and upstream skill updates arrive with one command.

```bash
gh repo fork aeonfun/aeon --clone && cd aeon
gh repo set-default <owner>/aeon      # REQUIRED - see Gotchas
```

From the instance repo, everything runs through the `./aeon` CLI. It edits `aeon.yml` safely (it preserves comments and validates) - do not hand-edit the YAML.

## Workflow

The console has eight modes; pick the one the user is asking for.

1. **Start** - no instance yet. Auth a model (`./aeon auth --oauth`, or `--key <key>` which detects the provider from the key prefix), wire one channel, run one skill now, then schedule it. Aim for one real notification fast; do not configure a schedule first.
2. **Reschedule** - change times or cadence. Show the day as a timeline in the user's timezone, take plain-language edits, apply with `./aeon skills schedule`.
3. **Unblock** - "it didn't run". Check in order and stop at the first hit: enabled? duplicate key in `aeon.yml`? actually cron (not `workflow_dispatch` or `reactive`)? Actions disabled? schedule quoted? ran and failed?
4. **Chat to skill** - turn what you just did into `skills/<name>/SKILL.md`, harden it for unattended runs, add its `aeon.yml` entry, and ship it as a PR.
5. **Edit a skill** - change what an existing skill does. Prefer a `--var` config change over a file edit; if you edit the body, keep the notify path, the silent-on-no-signal exit, and the log append.
6. **What to turn on** - ask what they want handled, propose three skills with a one-line reason each, browse packs (`./aeon packs ls`), install more (`bin/install-skill-pack`).
7. **Strategy and voice** - `STRATEGY.md` (the north star) and `soul/` (the tone), both read on every run: `./aeon strategy set`, `./aeon soul build`.
8. **Mine history** - surface repeated manual work from past coding-agent transcripts worth automating, then hand the winner to mode 4.

## Gotchas

- **Pin the default repo first.** With no default pinned, `gh` prefers an `upstream` remote over `origin`, so writes (secrets, dispatches) land on `aeonfun/aeon` instead of the instance - with no error, because the commands genuinely succeed on the wrong repo. Verify: `gh repo view --json nameWithOwner -q .nameWithOwner` must print the user's repo.
- **The `schedule:` value must be double-quoted in `aeon.yml`.** The scheduler matches `schedule: "..."` with a regex; an unquoted value never fires and reports no error anywhere. After any schedule edit, confirm the quotes with `grep '^  <skill>:' aeon.yml`.
- **All cron in `aeon.yml` is UTC.** Convert from the user's timezone and say so.
- **Silence on no signal is correct.** A clean run that finds nothing sends nothing rather than an empty report.
- **A missing key degrades, it does not always break.** Optional keys are marked `KEY?` in a skill's `requires:`.

## Examples

```bash
./aeon skills ls --enabled                   # what actually runs
./aeon skills run digest                      # run one skill now
./aeon runs logs <id>                         # read its output
./aeon skills schedule digest "0 6 * * *"     # 06:00 UTC daily (cron is UTC)
./aeon skills disable token-movers            # stop one
./aeon secrets set TELEGRAM_BOT_TOKEN --stdin # set a secret (never on the command line)
```

Full operator guide, every mode in depth, the provider and harness matrix, and the skill file format: https://github.com/aeonfun/aeon
