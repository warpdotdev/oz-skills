# GitHub Duplicate Issue Detection

Automatically detect and flag duplicate GitHub issues using agent-based semantic search.

## GitHub Actions Integration

Create `.github/workflows/duplicate-check.yml`:

```yaml
name: Check for duplicate issues
on:
  issues:
    types:
      - opened

jobs:
  dedupe_check:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write
    steps:
      - uses: actions/checkout@v4
      
      - name: Run duplicate detection agent
        uses: warpdotdev/warp-agent-action@v1
        with:
          warp_api_key: ${{ secrets.WARP_API_KEY }}
          profile: ${{ vars.WARP_AGENT_PROFILE || '' }}
          environment_id: ${{ vars.WARP_AGENT_ENVIRONMENT }}
          skill_spec: "warpdotdev/oz-skills:github-issue-dedupe"
          prompt: |
            Find duplicates of issue #${{ github.event.issue.number }} in ${{ github.repository }}.
            
            Export GH_TOKEN first:
            ```bash
            export GH_TOKEN=${{ secrets.GITHUB_TOKEN }}
            ```
            
            Current Issue:
            - Number: #${{ github.event.issue.number }}
            - Title: ${{ github.event.issue.title }}
            - Body: ${{ github.event.issue.body }}
```

## Setup

1. Add `WARP_API_KEY` to repository secrets
2. (Optional) Set `WARP_AGENT_PROFILE` variable for custom agent config
3. Workflow triggers automatically on new issues
4. Agent comments on duplicates found

The `skill_spec` parameter loads this skill's workflow and best practices automatically.
