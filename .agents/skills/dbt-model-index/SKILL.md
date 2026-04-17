---
name: dbt-model-index
description: Provide a lookup index of dbt models (BigQuery tables) to guide query writing against a data warehouse. Use when you need to query, analyze, or look up data in a dbt-powered data warehouse, or when resolving a vague data question into the right BigQuery tables to query.
---

# dbt Model Index

## When to Use

- Before writing any BigQuery SQL against production data
- When the task has not already explicitly stated which models/tables to query
- When resolving a vague or ambiguous data question into the right BigQuery tables

## How to Set Up This Skill

This skill is a curated index of your dbt models. Each entry describes a model (a BigQuery table), what it contains, and what types of questions it is best suited to answer.

To customize this index for your project:
- Organize models into logical domain sections (e.g., Users, Activity, Revenue, Events)
- For each model, include: the table name, a 1–2 sentence description of its grain and content, and "Useful for:" bullets covering common query patterns
- Note key join keys, standard filters, and partition fields where relevant

---

## [Domain: e.g., Users & Identity]

### `your_model_name`

Brief description of what this model contains. One row per [entity]. Include what makes this model's grain unique and the most important fields.

**Useful for:**

- [Type of question this model answers, e.g., user counts, cohort sizes]
- [Another use case, e.g., filtering to a specific user segment]
- [Common join pattern, e.g., joining to other tables as the canonical user dimension]

---

### `another_model_name`

Description of this model and its grain.

**Useful for:** [Brief use case description]

---

## [Domain: e.g., Activity & Engagement]

### `your_activity_model`

Description of the activity signal (e.g., what counts as "active"), the grain, and the time dimension.

**Useful for:**

- [Use case 1, e.g., daily/weekly active user metrics]
- [Use case 2, e.g., retention analysis]

---

### `your_engagement_model`

Description.

**Useful for:**

- [Use case 1]
- [Use case 2]

---

## [Domain: e.g., Revenue & Subscriptions]

### `your_revenue_model`

Description of the revenue grain (e.g., one row per customer per day, or one row per subscription event).

**Useful for:**

- [Use case 1, e.g., MRR/ARR reporting]
- [Use case 2, e.g., churn analysis]

---

### `your_subscription_model`

Description.

**Useful for:**

- [Use case 1]
- [Use case 2]

---

## [Domain: e.g., Events & Telemetry]

### `your_events_model`

Description of the event source, enrichment applied, and key fields available.

**Useful for:**

- [Use case 1, e.g., raw event-level analysis]
- [Use case 2, e.g., building domain-specific funnels]

---

## Important Notes

- **Standard filters:** Document any filters that should always be applied in user-facing queries (e.g., excluding test accounts, soft-deleted records, internal users, or flagged/fraudulent users). Example: `where not is_internal_user`
- **Production data:** Specify your default project/dataset path. Example: `your-gcp-project.prod.<model_name>`
- **Cost control:** For large partitioned tables, always filter on the partition field and constrain the date range to avoid full-table scans
- **Model grain:** Always note the grain (one row per _what_?) for each model to avoid accidental fan-outs in joins
- **Plan/tier types:** If your product has subscription tiers or plan types, document the valid values here so queries filter correctly
- **Sensitive datasets:** If any models live in a separate dataset, call that out explicitly so queries use the right fully-qualified table reference
