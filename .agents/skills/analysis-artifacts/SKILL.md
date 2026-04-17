---
name: analysis-artifacts
description: Generate reproducible analysis artifacts — SQL queries, Python visualizations, and summary tables — as you work through a BigQuery data analysis. Use when asked to conduct a deep dive, exploratory analysis, or investigation that goes beyond a simple data lookup.
---

# Analysis Artifacts

## When to Use

- When asked to do a "deep dive" or "analysis" on a question with a non-obvious answer
- When the analysis requires exploratory querying in BigQuery
- When the output should be reproducible and shareable (not just a one-off answer)

## Workflow

### 1. Scaffold the analysis directory

At the start of every analysis:

- Create a new directory in the `analyses` folder, named according to the existing pattern there
- Create subdirectories: `/assets/queries` and `/assets/visualizations`
- Create a `README.md` at the root of the new directory — this is the main readable document for the analysis

### 2. Plan the analysis

Always create a plan before starting, whether or not the user asked for one. Steps in the plan should map to the logical sub-questions or sub-areas you've deemed important to explore. Present the plan and wait for a go-ahead before proceeding.

### 3. Set up the README

Once the plan is approved:

- Add a title, author, and date to the top of the README
- Add a **Problem Statement** section summarizing the analysis question and the sub-pieces you'll explore
- Add a **Cohorts Definition** section. This must be extremely explicit about the groups being compared. If comparing two groups (e.g., free vs. paid, new vs. old, before vs. after a milestone), define cohorts in a way that controls for confounding factors. Consider:
  - Signup/activation time (as defined by your product — e.g., first login, first meaningful action); this relates to user tenure
  - Plan type or subscription tier (e.g., free vs. paid)
  - Controlling for observation time window length across cohorts
  - Product-specific usage propensity metrics relevant to the analysis question

  Once defined, respect these cohort definitions in all queries throughout the analysis.

### 4. Create artifacts as you go

For every material step in the analysis:

- **SQL query artifact**: For any BigQuery query that powers a visualization, summary, or key insight, save a `.sql` file in `/assets/queries/` with a descriptive name and a comment block explaining the query's purpose. Only create the file after you're satisfied with the results. Skip trivial or one-off lookup queries.
- **Visualization or table artifact**: For each key insight, assess whether it's best conveyed through a chart or a table. Lean toward visualizations. If a visualization, write a Python script to generate it and save both the script and the output image to `/assets/visualizations/` with descriptive names. If a table, save it as a `.csv` in `/assets/visualizations/`.

### 5. Overwriting artifacts

If you need to redo part of the analysis (due to a methodology correction or user feedback), overwrite all associated artifacts:

- Replace the `.sql` query file
- Replace the visualization script and regenerate the image
- Replace the `.csv` table file

Note the change to the user when you do this.

### 6. Summarize the analysis

When the analysis is complete (either at the end of the plan or when the user asks), write the full README:

- Summarize each step and sub-question in logical document sections
- Be crisp and concise — avoid unnecessary verbosity
- Embed saved viz images from `/assets/visualizations/` where appropriate
- Generate markdown tables from `.csv` files in `/assets/visualizations/`
- Include a small reference hyperlink to the associated query file in each section
- Add a **TL;DR** section near the top (after Problem Statement, before Cohorts Definition)
- Add a **Key Takeaways** section at the end

## Examples

```bash
analyses/
└── 2024-01-user-retention/
    ├── README.md
    └── assets/
        ├── queries/
        │   ├── cohort_retention_by_week.sql
        │   └── retention_by_plan_type.sql
        └── visualizations/
            ├── retention_curve.py
            ├── retention_curve.png
            └── plan_type_summary.csv
```
