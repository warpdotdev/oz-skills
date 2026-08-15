---
name: factory-setup
description: Connect a third-party coding agent (Claude Code, Codex, Cursor, or any other MCP-capable client) to Warp Factory by installing and authenticating the oz CLI and registering the Factory MCP server. Use when someone outside Warp wants to set up Factory MCP access — for example to create or operate a software factory from Claude Code, Codex, Cursor, or another external agent.
---

# Factory Setup

Bootstrap **Warp Factory** access for a coding agent that is not Warp itself: install/authenticate the `oz` CLI, register the hosted **Factory MCP** server, verify the connection, and hand off to the canonical operating skill. This is a one-time setup skill, not the operating playbook.

## Scope

This skill:
1. Detects the target harness (Claude Code, Codex, Cursor, or generic MCP client).
2. Installs/authenticates the CLI and mints an API key.
3. Registers the Factory MCP server for that harness.
4. Verifies the connection (tools visible, `list_factories` works, canonical skill readable).
5. Optionally helps pick or create a factory and save it as the default.
6. Stops and hands off to the server-served operating skill for everything after setup.

This skill does **not**:
- Duplicate the day-2 operating playbook — that lives at `skill://warp/factory-mcp/SKILL.md` on the MCP connection itself and is the authoritative source once connected.
- Automate Slack, Linear, or GitHub integration OAuth for a factory. Point the user at the Factory web app for those; do not attempt to script them here.

## Step 1 — Pick a server root

The Factory MCP is always mounted at `{server_root}/api/v1/mcp/factory`. Third-party harnesses do not know Warp's server root on their own, so make it explicit up front:

| Target | Server root | CLI binary |
| --- | --- | --- |
| Warp Factory (public, once enabled) | `https://app.warp.dev` | `oz` |
| Internal staging / dogfood rehearsal | `https://staging.warp.dev` | `oz-dev` |

- If the machine already sets `FACTORY_MCP_URL`, use it verbatim instead of building one.
- If it sets `WARP_SERVER_ROOT` instead, build the URL as `{WARP_SERVER_ROOT}/api/v1/mcp/factory`.
- Otherwise ask which target the user means, or default to the public root (`https://app.warp.dev`) for an external user with no other context.
- As of this writing, the hosted Factory MCP is confirmed enabled on **staging**; enablement on the public/prod server root is a separate, server-side rollout this skill does not control. If registering against the public root fails with a not-found/disabled-feature style error, tell the user Factory MCP isn't turned on for that server yet — don't guess around it or silently fall back to staging.

## Step 2 — Get the CLI and an API key

Warp's CLI ships as `oz` through soft launch; it is renamed to `warp` at GA. Mention this once so the user isn't confused if they see the CLI called `warp` elsewhere later.

- **Installing `oz` (public):** the install command for external, non-Warp users is not finalized yet.
  > **PLACEHOLDER — do not invent a command here.** Ask the user how they installed/would install `oz`, or point them at `https://docs.warp.dev` for the current instructions. Do not guess a package name, curl-pipe URL, or script.
- **Installing `oz-dev` (staging/internal rehearsal only):** already present in Warp dogfood/dev environments; not for external users.

Once the CLI is available and logged in (`oz login`, or `oz-dev login` on staging), mint an API key for the harness to use:

```bash
oz api-key create --expires-in 30d "factory-setup"        # public / prod
oz-dev api-key create --expires-in 30d "factory-setup"    # staging rehearsal
```

Treat the printed key as a secret: export it to an environment variable (e.g. `WARP_API_KEY`) and use that variable everywhere below. Never paste it into a config file that gets committed, and never print it back to a shared terminal or log.

API key + `Authorization: Bearer` is the default, prod-safe auth path and works on every harness. OAuth is a secondary, best-effort option — see each harness's "OAuth alternative" note below — and is not guaranteed to be registered on every server root.

## Step 3 — Detect the harness and register the MCP server

Substitute `{mcp_url}` = `{server_root}/api/v1/mcp/factory` from Step 1, and `$WARP_API_KEY` from Step 2.

### Claude Code

```bash
claude mcp add --transport http warp-factory {mcp_url} \
  --header "Authorization: Bearer $WARP_API_KEY"
```

Flag names can shift between Claude Code versions — run `claude mcp add --help` first if this fails. Verified against `@anthropic-ai/claude-code` (`mcp add --transport http ... --header "..."`) as of this writing.

**OAuth alternative** (only where the target server root has registered the client, currently staging): `claude mcp add --transport http warp-factory {mcp_url} --client-id warp-factory-claude-code` and follow the browser prompt.

### Codex

```bash
codex mcp add warp-factory --url {mcp_url} --bearer-token-env-var WARP_API_KEY
```

This writes a `[mcp_servers.warp-factory]` block to `~/.codex/config.toml` with `url` and `bearer_token_env_var`; Codex reads the bearer token from that environment variable at connect time, so make sure `WARP_API_KEY` is exported in the same shell/session Codex runs in. Verified against `@openai/codex` (`mcp add <name> --url ... --bearer-token-env-var ...`).

**OAuth alternative** (staging only today): `codex mcp add warp-factory --url {mcp_url} --oauth-client-id warp-factory-codex`, then `codex mcp login warp-factory`.

### Cursor

Cursor has no MCP CLI; edit `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (project-scoped):

```json
{
  "mcpServers": {
    "warp-factory": {
      "url": "{mcp_url}",
      "headers": {
        "Authorization": "Bearer {WARP_API_KEY}"
      }
    }
  }
}
```

Cursor's `${env:VAR}` interpolation for header values has had version-dependent bugs, so inline the key directly rather than relying on it — and treat this file as a secret (do not commit a project-scoped `.cursor/mcp.json` with a real key in it). Restart Cursor after editing, then check Settings → Tools & MCP for a green connection.

**OAuth alternative** (staging only today): omit `headers` and let Cursor's OAuth 2.1 discovery flow use client id `warp-factory-cursor` on first connect.

### Generic / any other MCP-capable client

Any client that supports streamable HTTP with custom headers can connect directly: point it at `{mcp_url}` with header `Authorization: Bearer $WARP_API_KEY`. There is no special Warp-specific transport.

## Step 4 — Verify

From the harness with the MCP server attached:

1. List tools (`tools/list` or the client's equivalent) and confirm the Factory tools are present: `list_factories`, `create_factory`, `list_tasks`, `search_task`, `get_task`, `message_foreman`, `get_conversation`, `send_task`, `complete_task`, `list_notification_routes`.
2. Call `list_factories`. Success is any response without an auth error — an empty list just means the principal has no factories yet, which is fine.
3. Read the resource `skill://warp/factory-mcp/SKILL.md`. A successful read proves the handoff to the operating skill works. If the harness doesn't support reading MCP resources (some tool-only clients don't), tell the user to fetch it manually before their first real task.

If any step fails, stop and report the exact error instead of guessing a fix — see Troubleshooting below.

## Step 5 — Optional: pick or create a factory

Setup is complete once Step 4 passes; this step is optional follow-up, not the success bar.

- If the user already has a factory, use `list_factories` to find its `factory_uid` and, if they want, save it as their default per the operating skill's `~/.warp/factory/config.json` contract (`skill://warp/factory-mcp/references/factory-config.md`).
- If they want a new factory, `create_factory` needs `team_uid`, `name`, `code_forge`, and at least one `repositories` entry (`owner/repo`); `integrations` is optional. Avatars are REST-only, not settable over MCP.
- Connecting Slack, Linear, GitHub, or Jira integrations for a factory is out of scope here — send the user to the Factory web app for that; do not try to script integration OAuth from this skill.

## Step 6 — Hand off and stop

Once verified, tell the user setup is done. Day-2 operation — finding tasks, delegating work, pulling a task down locally, coordinating with the foreman, handing work back — is governed entirely by the canonical skill the server exposes at `skill://warp/factory-mcp/SKILL.md`. Read and follow that skill for anything after this point; do not reimplement its operating rules here.

## Troubleshooting

- **404 / feature-disabled-looking error at the MCP URL**: Factory MCP is not enabled for that server root. This is expected on the public root until it is rolled out there; it is not a skill bug.
- **401 Unauthorized**: the API key is missing, wrong, or expired. Recreate it (Step 2) and re-register.
- **OAuth client not found / OAuth flow rejected**: that harness's OAuth client (`warp-factory-claude-code` / `warp-factory-codex` / `warp-factory-cursor`) is not registered on the target server root yet. Fall back to the API key path — it always works.
- **`resources/read` for the skill URI fails or is unsupported**: some clients don't implement MCP resources. The tool surface still works; just tell the user to open the operating skill manually.
