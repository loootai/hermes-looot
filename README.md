# looot for Hermes Agent

looot gives an agent one sign-in and one prepaid balance for 2,500+ data API endpoints from 90+ providers: work emails, phone numbers, company and people search, Google results, web pages as markdown, news, LinkedIn profiles, local businesses. The agent searches the catalog by the job it wants done, sees each price before it runs, and pays per call. A failed call costs nothing. There is no subscription, and you top up from $5.

This repository is a portable [Agent Plugins v1](https://agent-plugins.org) package for [Hermes Agent](https://hermes-agent.nousresearch.com). It ships no code and installs no dependencies. It contains:

- `mcp.json`: the hosted looot MCP server, `https://api.looot.ai/mcp` (streamable HTTP, OAuth 2.1 with dynamic client registration).
- `skills/`: 21 skills. `looot` is the base skill (search, inspect, run, money rules, errors). The other 20 are one data job each, such as `looot-find-professional-emails`, `looot-google-serp` and `looot-keyword-volume`.
- `plugin.json`: the manifest. It marks the `looot` server as `untrusted`, so Hermes asks you before any call that is not read-only (`run`, `top_up`).

## Set up looot in Hermes

### Option 1: the plugin (MCP server and skills)

```bash
hermes plugins install loootai/hermes-looot --no-enable
hermes plugins enable looot
hermes gateway restart   # only if you run the messaging gateway
```

Once the plugin is in the Hermes plugin catalog you can use `hermes plugins install looot` instead.

On the first looot tool call Hermes prints an authorization link. Open it, sign in at looot.ai, pick the organization to bill, and click Connect. Hermes stores the token under `~/.hermes/mcp-tokens/` and refreshes it. To sign in again later, run `hermes mcp login looot`.

### Option 2: only the MCP server, in `config.yaml`

Add this to `~/.hermes/config.yaml`. A server in `config.yaml` replaces a plugin server of the same name.

```yaml
mcp_servers:
  looot:
    url: "https://api.looot.ai/mcp"
    auth: oauth
```

Start Hermes with `hermes chat`.

### Option 3: API key instead of browser sign-in (servers, cron, CI)

Create a key at https://looot.ai/settings?tab=agent-tokens (the page is labelled "API keys"). Give it `catalog.read`, `runs.read` and `runs.execute`, plus `usage.read` to read the balance. Put it in `~/.hermes/.env`:

```bash
LOOOT_API_KEY=your-key-here
```

Then reference it from `config.yaml`. Hermes substitutes `${VAR}` in `headers` when it connects:

```yaml
mcp_servers:
  looot:
    url: "https://api.looot.ai/mcp"
    headers:
      Authorization: "Bearer ${LOOOT_API_KEY}"
```

Never put the key itself in `config.yaml` or in this plugin's `mcp.json`.

### Try it (free)

Ask Hermes:

```text
Use looot to show me what it covers, then search for a way to verify an email address.
```

`catalog_overview`, `search_catalog`, `inspect`, `balance` and run history cost nothing. A new workspace starts at $0 with no trial credit, so top up before the first paid run (minimum $5). Then try:

```text
Use looot to find the work email of Patrick Collison at stripe.com.
```

The agent quotes the price, asks you to approve the `run`, and returns the result with a receipt.

## What it costs

You pay per successful call from a prepaid USD balance. Each endpoint shows its price before it runs. Failed calls, refused calls and most "not found" results charge $0. There is no subscription and no seat fee. Balance and top-up links are in the MCP tools `balance` and `top_up`.

## Disclosure

- The plugin makes network calls only to `https://api.looot.ai` (through Hermes's MCP client) and to a looot sign-in page you open yourself.
- The `run` tool spends your prepaid balance. The plugin declares the server `untrusted`, so Hermes asks before each paid call, and fails closed in unattended runs. You can relax this by defining a `looot` server in `config.yaml`.
- The plugin reads no files outside its own, runs no shell commands and starts no background processes. It stores no credentials. Hermes stores the OAuth token.
- No telemetry.

## Layout

```text
plugin.json    manifest
mcp.json       hosted MCP server
skills/        21 skills, one directory each
tests/         tests/validate.py, an offline check of the manifest and skills
```

## Develop

```bash
python3 tests/validate.py
hermes plugins validate . --install-deps   # the check the Hermes catalog CI runs
git config core.hooksPath .githooks        # leak scan before every commit
```

## Links

looot https://looot.ai, docs https://docs.looot.ai, MCP server details https://github.com/loootai/looot-mcp, skills for other agents https://github.com/loootai/looot-skills, privacy https://looot.ai/privacy, terms https://looot.ai/terms, support https://looot.ai/contact.

MIT licensed.
