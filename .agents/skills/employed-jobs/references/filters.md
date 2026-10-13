# Filter vocabulary

Pass these as arguments to `search_jobs`, `count_jobs`, `list_companies` and `export_jobs`. Exact ids matter: a wrong spelling gives a silent zero-row answer. When unsure, call `api_meta` and copy values from it.

| Filter | Meaning and values |
|---|---|
| `q` | Free text against title or company. |
| `company` | Employer name, case-insensitive, comma-separated for several. |
| `domain` | `ai_ml`, `business`, `consulting`, `data`, `design_media`, `devops_cloud`, `embedded`, `finance`, `hardware_engineering`, `hr_people`, `law_policy`, `life_sciences`, `marketing`, `operations`, `product`, `research`, `security`, `tech`, `unspecified`. |
| `category` | Taxonomy path prefix such as `engineering/software` or `engineering/software/backend`. Matches that node and everything under it. |
| `role_type` | `internship`, `new_grad`, `junior`, `mid`, `senior`, `lead_exec`, `founding_engineer`. |
| `employment_type` | `internship`, `apprenticeship`, `trainee`, `new_grad_program`, `campus_hire`, `full_time`, `part_time`, `contract`, `permanent`, `fellowship`, `postdoc`, `freelance`, `volunteer`. Underscores, not hyphens. |
| `location_scope` | Lowercase country bucket: `india`, `us`, `uk`, `sg`, or an ISO country code (`de`, `ca`, `jp`); also `remote`, `multiple`, `unspecified`. India is `india` not `in`; the UK is `uk` not `gb`. There is no `eu` bucket. |
| `city` | Substring match with synonyms (`bangalore` finds Bengaluru). |
| `work_mode` | `remote`, `hybrid`, `on_site`, `unspecified`. |
| `tech` | A technology in the stack, for example `kubernetes`. Comma-separated for several. |
| `visa` | `stated` (posting says it sponsors), `likely` (stated or inferred), `refused`. |
| `yoe_min`, `yoe_max` | Years-of-experience band. |
| `grad_year` | Graduating cohort a new-grad role targets. |
| `seen_after` | ISO date; only roles confirmed live on or after it. |
| `limit`, `cursor` | `search_jobs` only: 1 to 50 rows (default 25) and the `next_cursor` from the previous page. |

## Worked examples

- New-grad backend roles in India that likely sponsor: `role_type=new_grad`, `location_scope=india`, `category=engineering/software/backend`, `visa=likely`.
- How many ML internships are open: `count_jobs` with `employment_type=internship`, `category=engineering/ml`.
- Is Stripe hiring in London: `company=Stripe`, `city=London`, then `company_profile` for the wider picture.
