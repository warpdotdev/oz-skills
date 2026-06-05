---
name: agent-test-generation
description: Generate monocle_test_tools pytest tests for Python AI agent applications instrumented with monocle. Use when asked to scaffold routing, input/output, performance, multi-agent orchestration, or quality tests for a LangGraph, Google ADK, CrewAI, LlamaIndex, or Strands agent app.
license: Complete terms in LICENSE.txt
---

# Agent Test Generation

Scaffold pytest tests for AI agent applications using [`monocle_test_tools`](https://github.com/monocle2ai/monocle/tree/main/test_tools) — a framework-agnostic testing library that asserts on traces produced by [monocle](https://github.com/monocle2ai/monocle) instrumentation. Works across LangGraph, Google ADK, CrewAI, LlamaIndex, and Strands.

## When to Use

- The user asks to generate, scaffold, or write tests for an AI agent app
- The user mentions `monocle`, `monocle_test_tools`, or trace-based agent testing
- The user wants to verify agent routing, tool invocations, input/output content, or performance
- The user wants to add quality assessments (sentiment, hallucination, bias, toxicity, frustration)

## Prerequisites

The target project must have:

- A Python AI agent app using a supported framework (LangGraph, Google ADK, CrewAI, LlamaIndex, Strands)
- `pip install monocle_test_tools` in the project's environment
- At least one agent with tools

The Quality Assessment directive is dual-mode:

- **No `OKAHU_API_KEY` set** → falls back to local assertions (deterministic `contains_output`/`does_not_contain_output` and BERTScore similarity via `pip install bert_score`). No network call, no LLM required.
- **`OKAHU_API_KEY` set** → uses Okahu cloud LLM-as-judge classification for label-based assertions (sentiment, toxicity, bias, etc.).

Both paths use the same `monocle_test_tools` fluent API. The skill never reads `.env` files — credentials must already be in the environment.

## Workflow

### 1. Discover the agent

If the user did not name an app folder, ask which folder to target. Then scan the project to extract:

1. **Framework** — detect from imports and map to the `agent_type` string used by `run_agent_async()`:
   - `from langgraph` → `"langgraph"`
   - `from google.adk` or `google.genai` → `"google_adk"`
   - `from crewai` → `"crewai"`
   - `from llama_index` → `"llamaindex"`
   - `from strands` → `"strands"`
2. **Agents** — every `name=` argument in agent-creation calls
3. **Tools** — every `@tool()`-decorated function or tool definition, plus the agent that owns each
4. **Hierarchy** — supervisor/coordinator → sub-agents (for multi-agent apps)
5. **Entry point** — the main agent or supervisor object, and any individually accessible sub-agents
6. **Setup function** — how agents are constructed (async? returns what?)
7. **Python interpreter** — the project venv (e.g. `.venv/bin/python`) or system Python
8. **Existing tests** — scan `tests/` for `agent_test_*.py` to avoid overwrites

### 2. Confirm scope with the user

Show what was found:

```
Discovered:
  Framework:    LangGraph
  Supervisor:   travel_supervisor
  Agents:       flight_assistant, hotel_assistant
  Tools:        book_flight (→ flight_assistant), book_hotel (→ hotel_assistant)
  Entry point:  setup_agents() → supervisor
  Python:       .venv/bin/python
```

Then ask which test categories to generate. Offer these (multi-select):

1. **Agent & Tool Routing** *(recommended)* — positive + negative tests that the right agent/tool is invoked for each request type
2. **Input Validation** — verify user inputs are forwarded correctly to agents/tools
3. **Output Validation** — verify outputs contain expected content
4. **Performance** — token-limit and duration checks
5. **Quality Assessment** — sentiment / toxicity / bias / hallucination / frustration (dual-mode: cloud or local)
6. **Multi-task Orchestration** — complex requests touching multiple agents
7. **Individual Agent Testing** — each sub-agent in isolation (bypassing the supervisor)

### 3. Generate test files

For each selected category, generate one file under the target project's `tests/` directory using the `agent_test_` prefix.

**Critical rules:**

- **Never overwrite** an existing file. If `agent_test_routing.py` already exists, warn the user and skip — or ask before replacing.
- Each file uses the `monocle_trace_asserter` pytest fixture (provided by `monocle_test_tools`).
- All test functions are `async` and marked `@pytest.mark.asyncio`.
- Use the actual framework string, agent names, and tool names discovered in Step 1 — not placeholders.
- Each test function asserts ONE clear behavior. Diversify prompts: don't reuse the same city/entity across tests.
- The Quality Assessment file uses runtime branching on `os.getenv("OKAHU_API_KEY")` to pick cloud vs. local assertions (see Test Categories §5 below).

If `tests/conftest.py` is missing, create a minimal one:

```python
import os, sys
import pytest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
```

Do not auto-load `.env` files. If the user wants `OKAHU_API_KEY` from `.env`, they can `export $(grep -v '^#' .env | xargs)` before running pytest, or add their own dotenv loader.

### 4. Run and report

Run the generated suite:

```bash
cd <app_folder> && <python> -m pytest tests/agent_test_*.py -v
```

If any tests fail, classify the failure:

- **Test bug** (wrong tool name, wrong span_type chain, etc.) → fix the test
- **App bug** (agent actually misroutes, tool returns wrong output) → report to the user, do not auto-fix

Then print a summary:

```
Generated:
  tests/agent_test_routing.py            — 6 tests (3 positive, 3 negative)
  tests/agent_test_input_validation.py   — 5 tests
  tests/agent_test_output_validation.py  — 7 tests
  tests/agent_test_performance.py        — 7 tests (token + duration)
  tests/agent_test_quality.py            — 8 tests (cloud) + 4 (local always-on)
  tests/agent_test_multi_task.py         — 4 tests
  tests/agent_test_individual_agents.py  — 3 tests

Total: 44 tests — 40 passed, 0 failed, 4 skipped (OKAHU_API_KEY not set)
```

---

## Test Categories

Each generated file follows this skeleton:

```python
import os
import pytest
import pytest_asyncio
from monocle_test_tools import TraceAssertion
from <app_module> import <setup_function>

supervisor = None  # plus other agents you want to test individually

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_agents_fixture():
    global supervisor
    supervisor = await <setup_function>()

# ... test functions ...

if __name__ == "__main__":
    pytest.main([__file__])
```

### 1. Agent & Tool Routing — `agent_test_routing.py`

Tests that the correct agents and tools are invoked (positive) and that unrelated ones are not (negative).

Assertions: `called_tool(tool, agent)`, `does_not_call_tool(tool)`, `called_agent(agent)`, `does_not_call_agent(agent)`.

```python
# POSITIVE
async def test_flight_request_calls_flight_assistant(monocle_trace_asserter):
    await monocle_trace_asserter.run_agent_async(supervisor, "langgraph",
        "Book a flight from SFO to JFK on Dec 1.")
    monocle_trace_asserter.called_tool("book_flight", "flight_assistant")
    monocle_trace_asserter.called_agent("flight_assistant")

# NEGATIVE
async def test_hotel_request_does_not_call_flight_assistant(monocle_trace_asserter):
    await monocle_trace_asserter.run_agent_async(supervisor, "langgraph",
        "Book a hotel in Mumbai for 3 nights.")
    monocle_trace_asserter.does_not_call_tool("book_flight")
    monocle_trace_asserter.does_not_call_agent("flight_assistant")
```

Generate at minimum: one positive + one negative per agent/tool pair, plus one test where all agents are called together (multi-agent apps).

### 2. Input Validation — `agent_test_input_validation.py`

Verify user inputs are forwarded into agent/tool calls.

Assertions: `has_input`, `has_any_input`, `does_not_have_input`, `does_not_have_any_input`, `contains_input`, `contains_any_input`, `does_not_contain_input`, `does_not_contain_any_input`.

```python
async def test_book_flight_receives_route(monocle_trace_asserter):
    await monocle_trace_asserter.run_agent_async(supervisor, "langgraph",
        "Book a flight from Paris to Tokyo on 2025-12-15.")
    monocle_trace_asserter.called_tool("book_flight", "flight_assistant") \
        .contains_input("Paris") \
        .contains_input("Tokyo")
```

### 3. Output Validation — `agent_test_output_validation.py`

Verify outputs contain expected content (or do not contain unexpected content).

Assertions: `has_output`, `has_any_output`, `does_not_have_output`, `does_not_have_any_output`, `contains_output`, `contains_any_output`, `does_not_contain_output`, `does_not_contain_any_output`.

```python
async def test_book_hotel_output_confirms_booking(monocle_trace_asserter):
    await monocle_trace_asserter.run_agent_async(supervisor, "langgraph",
        "Book a hotel in Berlin for 2 nights.")
    monocle_trace_asserter.called_tool("book_hotel", "hotel_assistant") \
        .contains_output("Berlin") \
        .contains_any_output("booked", "confirmed", "reserved")

async def test_output_has_no_error_indicators(monocle_trace_asserter):
    await monocle_trace_asserter.run_agent_async(supervisor, "langgraph",
        "Book a hotel in Lisbon.")
    monocle_trace_asserter.does_not_have_any_output("ERROR", "FAILED", "REJECTED")
```

### 4. Performance — `agent_test_performance.py`

Verify token usage and execution duration.

Assertions: `under_token_limit(limit)`, `under_duration(limit, units, span_type)`.

```python
async def test_single_agent_token_budget(monocle_trace_asserter):
    await monocle_trace_asserter.run_agent_async(supervisor, "langgraph",
        "Book a flight from SFO to LAX.")
    monocle_trace_asserter.under_token_limit(3000)

async def test_multi_agent_token_budget(monocle_trace_asserter):
    await monocle_trace_asserter.run_agent_async(supervisor, "langgraph",
        "Book a flight from SFO to LAX and a hotel near LAX.")
    monocle_trace_asserter.under_token_limit(8000)

async def test_workflow_duration(monocle_trace_asserter):
    await monocle_trace_asserter.run_agent_async(supervisor, "langgraph",
        "Book a flight.")
    monocle_trace_asserter.under_duration(60)  # workflow-level seconds

async def test_inference_duration_ms(monocle_trace_asserter):
    await monocle_trace_asserter.run_agent_async(supervisor, "langgraph",
        "Book a flight.")
    monocle_trace_asserter.under_duration(5000, units="ms", span_type="inference")
```

> ⚠️ **`under_duration` gotcha.** It defaults to `span_type="workflow"`. After `called_tool(...)`, the filtered spans are tool spans — calling `under_duration` on that chain compares the limit to tool spans, not workflow time. Either start a fresh `monocle_trace_asserter` chain or pass the matching `span_type` (`"tool_invocation"`, `"agent_invocation"`, `"inference"`, `"agent_turn"`).

### 5. Quality Assessment — `agent_test_quality.py` *(dual-mode)*

Generate this file with both local and cloud test groups. Local tests always run; cloud tests are skipped when `OKAHU_API_KEY` is unset.

```python
import os
import pytest
import pytest_asyncio
from monocle_test_tools import TraceAssertion
from <app_module> import <setup_function>

OKAHU_AVAILABLE = bool(os.getenv("OKAHU_API_KEY"))

supervisor = None

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_agents_fixture():
    global supervisor
    supervisor = await <setup_function>()

# ───────────────────────────────────────────────────────────
# LOCAL MODE — always runs, no API or LLM required
# Deterministic assertions + optional BERTScore semantic similarity
# ───────────────────────────────────────────────────────────

async def test_response_excludes_failure_terms(monocle_trace_asserter):
    """Negative quality check — no failure terms in output."""
    await monocle_trace_asserter.run_agent_async(supervisor, "langgraph",
        "Book a flight from SFO to JFK.")
    monocle_trace_asserter.does_not_have_any_output(
        "error", "failed", "unable", "cannot", "sorry"
    )

async def test_response_contains_confirmation(monocle_trace_asserter):
    """Positive quality check — response confirms the action."""
    await monocle_trace_asserter.run_agent_async(supervisor, "langgraph",
        "Book a flight from SFO to JFK.")
    monocle_trace_asserter.contains_any_output("booked", "confirmed", "reserved")

# Optional: semantic similarity via BERTScore. Requires `pip install bert_score`.
# Skipped automatically if bert_score is not installed.
try:
    import bert_score  # noqa: F401
    _BERT_AVAILABLE = True
except ImportError:
    _BERT_AVAILABLE = False

@pytest.mark.skipif(not _BERT_AVAILABLE, reason="bert_score not installed")
async def test_response_similar_to_expected(monocle_trace_asserter):
    """Local semantic similarity — agent output close to expected text."""
    expected = "A flight from San Francisco to New York has been booked."
    await monocle_trace_asserter.run_agent_async(supervisor, "langgraph",
        "Book a flight from SFO to JFK.")
    # The bert_score evaluator returns Precision/Recall/F1 dicts; use the
    # configured comparer in monocle_test_tools to threshold on F1.
    monocle_trace_asserter.with_evaluation("bert_score") \
        .check_eval(eval_args={"input": expected, "output": None})

# ───────────────────────────────────────────────────────────
# CLOUD MODE — only runs when OKAHU_API_KEY is set
# LLM-as-judge classification on traces
# ───────────────────────────────────────────────────────────

pytestmark_cloud = pytest.mark.skipif(
    not OKAHU_AVAILABLE,
    reason="OKAHU_API_KEY not set; cloud quality assessment skipped"
)

@pytestmark_cloud
async def test_response_sentiment_positive(monocle_trace_asserter):
    await monocle_trace_asserter.run_agent_async(supervisor, "langgraph",
        "Book a flight from SFO to JFK.")
    monocle_trace_asserter.with_evaluation("okahu") \
        .check_eval("sentiment", "positive")

@pytestmark_cloud
async def test_response_not_toxic(monocle_trace_asserter):
    await monocle_trace_asserter.run_agent_async(supervisor, "langgraph",
        "Book a flight from SFO to JFK.")
    monocle_trace_asserter.with_evaluation("okahu") \
        .check_eval("toxicity", not_expected=["highly_toxic", "moderately_toxic", "mildly_toxic"])

@pytestmark_cloud
async def test_response_no_hallucination(monocle_trace_asserter):
    await monocle_trace_asserter.run_agent_async(supervisor, "langgraph",
        "Book a flight from SFO to JFK.")
    monocle_trace_asserter.with_evaluation("okahu") \
        .check_eval("hallucination", "no_hallucination")
```

**Available cloud evaluation templates** (when `OKAHU_API_KEY` is set):

| Template | Fact names | Positive labels | Negative labels |
|---|---|---|---|
| `sentiment` | traces, inferences, conversations | `positive`, `neutral` | `negative` |
| `toxicity` | traces, agent_sessions | `non_toxic` | `highly_toxic`, `moderately_toxic`, `mildly_toxic` |
| `bias` | traces, agent_sessions | `unbiased` | `biased` |
| `hallucination` | traces, agent_sessions | `no_hallucination` | `hallucination` |
| `frustration` | traces, conversations | `ok` | `frustrated` |
| `contextual_precision` | traces | `high_precision` | `low_precision` |
| `contextual_relevancy` | traces, agent_sessions | `highly_relevant` | `not_relevant` |
| `conversation_completeness` | traces, agent_sessions | `complete` | `incomplete` |
| `offtopic` | conversations | `on_topic` | `off_topic` |
| `role_adherence` | agent_sessions | `excellent_adherence`, `good_adherence` | `poor_adherence`, `no_adherence` |
| `misuse` | agent_sessions | — | `clear_misuse`, `potential_misuse` |
| `pii_leakage` | agent_sessions | — | `pii_leakage` |
| `summarization` | traces | `excellent` | `poor` |

Pass `fact_name="agent_sessions"` to `check_eval()` when evaluating at the session level instead of the default trace level.

### 6. Multi-task Orchestration — `agent_test_multi_task.py`

Complex requests that exercise multiple agents. Combines routing, output, and performance assertions.

```python
async def test_combined_request_routes_all_agents(monocle_trace_asserter):
    await monocle_trace_asserter.run_agent_async(supervisor, "langgraph",
        "Book a flight from Seattle to Tokyo and a hotel in Shibuya for 4 nights.")
    monocle_trace_asserter.called_tool("book_flight", "flight_assistant") \
        .contains_input("Seattle") \
        .contains_output("booked")
    monocle_trace_asserter.called_tool("book_hotel", "hotel_assistant") \
        .contains_input("Shibuya") \
        .contains_output("booked")

async def test_combined_request_within_budget(monocle_trace_asserter):
    await monocle_trace_asserter.run_agent_async(supervisor, "langgraph",
        "Book a flight from Seattle to Tokyo and a hotel in Shibuya.")
    monocle_trace_asserter.under_token_limit(8000) \
        .under_duration(120)
```

### 7. Individual Agent Testing — `agent_test_individual_agents.py`

Test each sub-agent directly (bypassing the supervisor). Only generate this file if the setup function exposes the individual agents.

```python
async def test_flight_assistant_direct(monocle_trace_asserter):
    await monocle_trace_asserter.run_agent_async(flight_assistant, "langgraph",
        "Book a flight from Boston to Miami.")
    monocle_trace_asserter.called_tool("book_flight", "flight_assistant") \
        .contains_output("booked")
    monocle_trace_asserter.under_token_limit(2000)
```

---

## Assertion API Quick Reference

All methods return a `TraceAssertion` scoped to the matching spans, enabling fluent chains.

| Category | Methods |
|---|---|
| **Span filters** | `called_tool(tool, agent)`, `does_not_call_tool(tool)`, `called_agent(agent)`, `does_not_call_agent(agent)` |
| **Input checks** | `has_input`, `has_any_input`, `does_not_have_input`, `does_not_have_any_input`, `contains_input`, `contains_any_input`, `does_not_contain_input`, `does_not_contain_any_input` |
| **Output checks** | `has_output`, `has_any_output`, `does_not_have_output`, `does_not_have_any_output`, `contains_output`, `contains_any_output`, `does_not_contain_output`, `does_not_contain_any_output` |
| **Performance** | `under_token_limit(n)`, `under_duration(n, units="seconds", span_type="workflow")` |
| **Evaluation** | `with_evaluation("okahu" \| "bert_score")`, `check_eval(eval_name, expected, not_expected, fact_name)` |

**Chaining rule:** assertions chained from a filter (`called_tool(...)`, `called_agent(...)`) apply only to those filtered spans. Start a new chain from `monocle_trace_asserter` for assertions on different spans.

## Important Notes

- **File safety.** Never overwrite an existing `agent_test_*.py`. Detect first, warn if present.
- **Prompt variety.** Use diverse, realistic prompts. Don't reuse the same city/entity across tests in the same file.
- **No `.env` reads.** The skill does not read `.env`. If the user wants `OKAHU_API_KEY` in `.env`, they load it before running pytest (`export $(grep -v '^#' .env | xargs)` or a `python-dotenv` snippet in their `conftest.py`).
- **No credential echoing.** Never print, log, or embed `OKAHU_API_KEY` or any secret in generated code, output, or commit messages.
- **`under_duration` after a filter.** Defaults to `span_type="workflow"`. Set the matching `span_type` when chaining after `called_tool`/`called_agent`, or start a new chain.
- **Assessor lifecycle.** `with_evaluation("okahu")` configures the assessor once on a `TraceAssertion` instance; subsequent `check_eval` calls on the same instance reuse it.
- **`bert_score` lazy install.** If the generated quality file imports `bert_score` and it isn't installed, the semantic similarity test is `pytest.skip`-marked rather than failing.

## Examples

```bash
# Generate all categories for an ADK travel app, run against a venv python
$ <agent> "generate tests for ./travel-agent"
# → Discovers framework=google_adk, agents=flight_assistant,hotel_assistant
# → Asks which categories to include
# → Writes tests/agent_test_*.py
# → Runs pytest, reports pass/fail/skip

# Run only the local quality tests (no Okahu key needed)
$ pytest tests/agent_test_quality.py -v -k "not sentiment and not toxic and not hallucination"

# Run the full quality suite (cloud + local) when OKAHU_API_KEY is set
$ OKAHU_API_KEY=$(your-key-loader) pytest tests/agent_test_quality.py -v
```
