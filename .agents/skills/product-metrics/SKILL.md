---
name: product-metrics
description: >-
  Manage ecommerce advertising through Product Metrics with server-side tracking, profit bidding, product segmentation and campaign planning.
  Use when connecting a store or ad channel, checking tracking, analysing product profit, or setting up POAS, new customer and LTV bidding.
license: MIT
metadata:
  source: https://github.com/product-metrics/skills/blob/985fcc473a6485772059ba4001a2b8041dac2381/plugins/product-metrics/skills/product-metrics/SKILL.md
  author: Product Metrics
  version: "1.2.0"
  docs: https://www.productmetrics.io/docs/agent-skills/overview
---

# Product Metrics

Product Metrics is a profit optimisation platform for ecommerce advertising: one app for server-side tracking, profit bidding, product segmentation and campaign planning across Google Ads, Meta and ChatGPT Ads. It sends each order’s profit, new or returning status and lifetime value to the ad platforms, so merchants can bid on POAS, new customers and LTV. Machine learning segments every product into custom labels for Shopping and Performance Max, and the campaign plan sets out the ideal campaign structure for those segments. A dashboard shows profit, customers, stock and returns. Docs: https://www.productmetrics.io/docs (index for agents: https://www.productmetrics.io/docs/llms.txt).

This skill picks the right one for the job. Follow the rules below from your first command.

## Rules

- **All conversion actions by agents are secondary**, the status Product Metrics creates its actions with. Choosing what a campaign bids or optimises on (making an action primary, or picking the Meta or ChatGPT Ads conversion) is the person's step, by every route and also when they ask: give them the exact clicks, wait until they say it is done, then read it back.
- **Pick the interface in this order:** the `productmetrics` CLI (check with `productmetrics status --json`, pass `--json` to every command, and run `productmetrics <group> <command> --help --json` before one you have not used); then the Product Metrics MCP server (`https://www.productmetrics.io/mcp`: `search` the API spec, then `execute`; never guess a path or body); otherwise the app steps in https://app.productmetrics.io.
- **Read where setup stands first:** `productmetrics setup get-status --json` (MCP: `setup.get_status`). Read `journey_stage` and the `next_action` fields, read it again with `--company-id` and `--property-id` once you know them, skip every step that is done and tell the person which ones are.
- **Discover ids, never invent them.** `company_id`, `property_id`, installation and scope ids come from earlier results.
- **Writes:** pass `--auto-idempotency-key` (MCP: `idempotencyKey: crypto.randomUUID()`) where the command's `--help` lists it, and retry a failed write with the key the error hint names. Other writes take no key: read the state before you retry.
- **Browser steps:** exit code 4 or `next_action: { "type": "browser", "url": … }` means the person opens the URL. Say what they will see, wait until they say they are done, then read the state again. A WooCommerce or Shopware 6 store returns `"type": "store_plugin"` instead: the person pastes the setup token into the Product Metrics plugin in their store admin before it expires.
- **Steps in the store admin or ad platform are the person's:** give them the exact labels from the reference or docs page.
- **Secrets:** never ask for, print or store passwords, tokens or API keys, except a credential the API needs from the person (the Lightspeed API key and secret, the Meta Conversions API access token, the OpenAI Conversions API key). Pass it straight to the command and never repeat it, log it or put it in a summary.
- **Deletes** only when the person explicitly asks.
- **"Ask your assistant" steps are yours.** Answer them with `productmetrics orders list --company-id <company_id> --storefront-scope-id <scope_id> --json` (MCP: `orders.list`, newest first) and `productmetrics orders get --company-id <company_id> --order-id <order_id> --storefront-scope-id <scope_id> --json` (MCP: `orders.get`), which shows an order's margin and whether its customer was new or returning.
- **Talk to a store owner, not a developer:** short sentences, what you did, what they need to do, what comes next. ROAS is a plain number (4.2); a target ROAS is a percentage (420%). Recommend increasing or lowering priority, never "raise or cut bids".
- The long form of these rules: https://www.productmetrics.io/docs/cli/for-agents.

## 1. Find the store platform and channel

Ask, or read it with `productmetrics setup get-status --json` (MCP: `setup.get_status`). Store platforms: Shopify, WooCommerce, Lightspeed eCom (C-Series), Magento 2 (installed by a developer), Shopware 6, and any other website through Cloudflare Tracking (sign in to Cloudflare; no plugin). A custom-built store sends orders by webhook: https://www.productmetrics.io/docs/platforms/custom-store.

## 2. Pick the skill

One skill per task, store platform and channel. Replace `<platform>` with `shopify`, `woocommerce`, `lightspeed`, `magento`, `shopware` or `cloudflare` (any website):

| Task | Google Ads | Meta | ChatGPT Ads |
| --- | --- | --- | --- |
| Server-side tracking | `set-up-<platform>-google-ads-conversion-tracking` | `set-up-<platform>-meta-conversions-api` | `set-up-<platform>-chatgpt-ads-conversions-api` |
| Enhanced Conversions | `set-up-<platform>-google-ads-enhanced-conversions` | `set-up-<platform>-meta-advanced-matching` | `set-up-<platform>-chatgpt-ads-customer-matching` |
| Customer lists | `set-up-<platform>-google-ads-customer-match` | – | – |
| New customer bidding | `set-up-<platform>-google-ads-new-customer-bidding` | `set-up-<platform>-meta-new-customer-bidding` | – |
| Returning customer bidding | `set-up-<platform>-google-ads-returning-customer-bidding` | `set-up-<platform>-meta-returning-customer-bidding` | – |
| POAS and ROAS bidding | `set-up-<platform>-google-ads-poas-bidding` | `set-up-<platform>-meta-poas-bidding` | `set-up-<platform>-chatgpt-ads-poas-bidding` |
| LTV bidding | `set-up-<platform>-google-ads-ltv-bidding` | `set-up-<platform>-meta-ltv-bidding` | `set-up-<platform>-chatgpt-ads-ltv-bidding` |

Order of work: server-side tracking first, then customer data for matching, then a bidding goal.

By task, on any store:

| Skill | Use it to |
| --- | --- |
| `set-up-tracking` | Go from nothing to tracking active: workspace, store, Google Ads, Meta, consent, costs, first purchase |
| `connect-google-ads` | Connect Google Ads and Merchant Center, or fix a broken connection |
| `check-tracking` | Check every part of tracking and find a test order (read only) |
| `bid-on-profit` | Set up and check POAS or ROAS bidding in Google Ads and Meta |
| `analyse-google-ads` | Answer "how are my campaigns doing" and "why did ROAS drop" with real figures (read only) |
| `check-product-segments` | Explain the six segments, what each holds, the budget on Drainers and why a product changed segment (read only) |
| `find-unprofitable-products` | Find the products that lose money after ads, with their decision, margin and competitor prices |
| `set-up-product-segmentation` | Choose the custom labels, tune segmentation settings and product rules, and generate the feed, after you confirm each change |
| `check-campaign-structure` | Check that Shopping and Performance Max campaigns use the segments, and read the campaign plan results (read only) |
| `check-stock-and-returns` | Find products advertised while out of stock, reorder dates, slow movers and return rates per category |
| `bid-on-new-customers` | Set up new customer bidding (new customer acquisition) in Google Ads, Meta and ChatGPT Ads |
| `bid-on-returning-customers` | Set up returning customer bidding in Google Ads, Meta and ChatGPT Ads |
| `bid-on-ltv` | Set up LTV (customer lifetime value) bidding in Google Ads, Meta and ChatGPT Ads |

If the skill you need isn't installed, install it (`npx skills add product-metrics/skills --skill <name>`) or follow its docs page: every docs URL serves Markdown with `.md` appended, and https://www.productmetrics.io/docs/llms.txt lists them all.

## 3. Key facts

- **POAS** = profit ÷ ad spend; **ROAS** = revenue ÷ ad spend, written as a plain number (4.2). A **target ROAS** is a percentage (420%); on the profit value, 100% is break-even.
- All conversion actions by agents are secondary, as Product Metrics creates them. The person makes one primary in Google Ads (**Goals → Conversions**) and keeps one purchase action primary.
- Profit is sent once the additional costs are active and every cost of the order is known; a loss is sent as 0. Costs: https://www.productmetrics.io/docs/using/costs.
- Consent: Product Metrics reads the store's consent banner and sends only what the visitor allowed: https://www.productmetrics.io/docs/using/consent.
- All three channels get revenue, profit, new and returning customer and lifetime value. On ChatGPT Ads, new and returning customer bidding has no per-store skill yet: use `bid-on-new-customers` or `bid-on-returning-customers`. Customer Match lists are Google Ads only.

## MCP server

For analysis (campaign and product profit, segments, changes), connect the Product Metrics MCP server: `https://www.productmetrics.io/mcp` (https://www.productmetrics.io/docs/mcp/connect).

If there is no `references/` folder next to this file (the skill was installed from the docs site), use the docs pages linked above instead, with `.md` appended for Markdown: it has the same steps.
