---
name: anchor-drift-monitor
description: Monitor Oz agent runs for intent drift using Anchor Engine. Use when running multi-step tasks where the agent might deviate from the original goal, modify files outside scope, add unintended dependencies, or gradually lose faithfulness to the task constraints.
license: MIT
---

# Anchor Intent Drift Monitor

Detect and prevent cumulative intent drift during multi-step agent runs. Uses HHEM-2.1-Open (hallucination evaluation model) to score each agent action against the original task contract.

## When to Use

- **Multi-step tasks** (5+ steps) where context erosion is likely
- Tasks with **explicit scope constraints** ("only modify files in /src/auth")
- **Refactoring or migration** tasks where the agent must stay within boundaries
- Any task where you've seen agents gradually drift off-topic

## Prerequisites

Set `ANCHOR_KEY` as an environment variable. Get a free key at [anchor-app-one.vercel.app](https://anchor-app-one.vercel.app).

Verify the key is set:

```bash
echo $ANCHOR_KEY
```

If empty, instruct the user to set it:

```bash
export ANCHOR_KEY="anchor_sk_..."
```

## How It Works

1. **Before the run starts**, define an intent contract: the original task description plus any constraints the user specified
2. **After each step**, score the step's summary against the contract
3. **If drift is detected** (score drops below threshold), stop and report what went wrong before executing further

## Workflow

### 1. Create Intent Contract

At the start of any multi-step task, extract the user's intent and constraints, then create a contract:

```bash
curl -s -X POST https://anchor-app-one.vercel.app/api/contracts \
  -H "Authorization: Bearer $ANCHOR_KEY" \
    -H "Content-Type: application/json" \
      -d '{
          "task": "<original task description including constraints>",
              "on_drift": "warn",
                  "drift_threshold": 0.7
                    }'
                    ```

                    Save the returned `id` 
                    Save the returned `id` - this is your contract ID for the run.

                    ### 2. Score Each Step

                    After completing each step, score what was done against the contract:

                    ```bash
                    curl -s -X POST https://anchor-app-one.vercel.app/api/monitor \
                      -H "Authorization: Bearer $ANCHOR_KEY" \
                        -H "Content-Type: application/json" \
                          -d '{
                              "contract_id": "<contract-id>",
                                  "action": {
                                        "type": "message",
                                              "content": "<summary of what this step did>"
                                                  }
                                                    }'
                                                    ```

                                                    The response includes:

                                                    | Field | Type | Meaning |
                                                    |-------|------|---------|
                                                    | `allow` | boolean | Whether the action is within scope |
                                                    | `score` | float | Faithfulness score (0.0-1.0) |
                                                    | `anchor_triggered` | boolean | Whether drift correction was activated |
                                                    | `intervention.message` | string | Explanation of what drifted and why |

                                                    ### 3. Interpret Results

                                                    - **`allow: true`** -> Step is on-track. Continue normally.
                                                    - **`allow: false`** -> Drift detected. **Stop before executing the next step.**

                                                    When drift is detected, report to the user:

                                                    ```
                                                    Intent drift detected at step N
                                                       Score: 0.45 (threshold: 0.70)
                                                          Reason: Agent modified files outside /src/auth and installed new dependencies

                                                                The remaining steps have been paused. Would you like to:
                                                                   1. Correct course and continue
                                                                      2. Cancel the remaining steps
                                                                         3. Override and continue anyway
                                                                         ```
                                                                            3. Override and continue anyway
                                                                            ```

                                                                            ### 4. Scoring Guidelines

                                                                            | Score Range | Status | Action |
                                                                            |-------------|--------|--------|
                                                                            | 0.85-1.00 | [OK] On track | Continue |
                                                                            | 0.70-0.84 | [WARN] Drifting | Warn user, tighten next steps |
                                                                            | 0.50-0.69 | [OFF] Off track | Pause and ask user |
                                                                            | Below 0.50 | [STOP] Lost intent | Stop immediately |

                                                                            ## Common Drift Patterns

                                                                            Watch for these patterns that indicate the agent is drifting:

                                                                            1. **Scope creep**: Modifying files outside the specified directories
                                                                            2. **Dependency bloat**: Adding packages not mentioned in the task
                                                                            3. **Goal substitution**: Solving a related but different problem
                                                                            4. **Over-engineering**: Adding abstractions or features beyond what was asked
                                                                            5. **Context confusion**: Mixing up requirements from different parts of the conversation

                                                                            ## Safety Notes

                                                                            - The contract is **read-only** - it captures intent at the start and doesn't change
                                                                            - Scoring is **non-blocking by default** - the skill warns but doesn't prevent execution unless configured to cancel
                                                                            - All scoring happens via the Anchor API - no local model required
                                                                            - If the API is unreachable, continue the task normally and note that drift monitoring was unavailable

                                                                            ## Deliverable

                                                                            After a monitored run completes, provide a drift summary:

                                                                            - **Contract**: Original task and constraints
                                                                            - **Steps scored**: Total steps / steps with drift
                                                                            - **Lowest score**: Which step drifted most and why
                                                                            - **Final status**: Completed within scope / Completed with drift / Cancelled due to drift

                                                                            ## Links

                                                                            - SDK: `npm install @anchor-engine/sdk`
                                                                            - GitHub: [github.com/anchor-engine/anchor-sdk](https://github.com/anchor-engine/anchor-sdk)
                                                                            - Agent Skills Spec: [agentskills.io](https://agentskills.io)
                                                                            
