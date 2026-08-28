---
name: i-have-an-idea
description: Capture and co-develop new product, feature, experience, architecture, or creative-workflow ideas in one traceable Markdown record without starting implementation. Use when a user explicitly shares an idea, proposes a high-confidence new direction, or wants to explore an ambiguous feature instead of implementing it immediately.
---

# I Have an Idea

Preserve an unfinished but potentially important idea, develop it with its author, and maintain one traceable Markdown record. Contribute structure, alternatives, tradeoffs, and counterexamples while preserving author ownership and refusing to implement without separate explicit authorization.

Write the record and user-facing responses in the user's primary language unless the project requires another language. Recognize equivalent triggers across languages, including `/idea`, `I have an idea`, `What if...`, `我有一个想法`, `我想做一个...`, and `要是...就好了`.

## Core Contract

- Maintain exactly one living Markdown record for each distinct idea.
- Create new records at `docs/ideas/IDEA-YYYYMMDD-<slug>.md` by default.
- Only create or update that record and converse briefly with the author.
- Do not modify source code, create issues, tasks, PRDs, implementation plans, or prototypes, run builds, tests, or deployments, or invoke an implementation agent.
- Keep idea maturity separate from permission to act: `status: shaped` never implies `implementation_authorization: granted`.
- After explicit implementation authorization, update the record, provide a handoff, and stop. Another workflow must perform implementation.

## Choose the Interaction Mode

Apply these cases in order:

1. **Explicit idea:** The user says `/idea`, `I have an idea`, `我有一个想法`, or an equivalent phrase. Capture it immediately without asking whether to create a document.
2. **High-confidence implicit idea:** The user proposes a new, durable product, experience, architecture, or creative direction such as `What if...` or `要是……就好了`. Tell the user you are preserving the idea, then capture it.
3. **Ambiguous feature statement:** The message could mean either idea exploration or immediate implementation, such as “Should this have an export button?” Ask only whether the user wants to explore the idea or implement it now. Do not create a record before the answer.
4. **Explicit execution:** Do not use this skill for bugs, factual questions, mechanical edits, an already-understood requirement, or progress on an existing task.
5. **Idea plus implementation request:** Capture and shape the idea first. Record the explicit implementation authorization, provide the handoff, stop this skill, and let a separate workflow continue.

Do not ask whether to create an Idea document. Installing and enabling this skill grants standing permission for its record-keeping workflow unless the host project says otherwise. Clarify the collaboration mode only when the user's intent is ambiguous.

## Search Before Creating

Before creating a record:

1. Extract the topic, synonyms, named entities, and likely tags from the user's words.
2. Search existing Markdown in this order:
   - `docs/ideas/`
   - `docs/product/`
   - `docs/architecture/`
   - `docs/adr/`
3. Read the most relevant candidates and compare meaning, not only filenames.
4. Resolve the result:
   - Update the existing record when it is the same idea.
   - Link to an established product, architecture, or ADR source of truth instead of duplicating a competing conclusion.
   - Explain the overlap and ask the author whether to continue the existing record or create a separate one when the boundaries differ.
   - Create a new record when no relevant record exists.
   - Let the author decide when identity remains uncertain; never merge records silently.

Prefer `rg --files` and `rg -n -i --glob '*.md'` when available. Skip missing directories without treating them as errors.

## Capture the Minimum

Use `assets/idea-record-template.md` for a new record and replace every placeholder.

- Use the local date and an ISO 8601 timestamp.
- Use `IDEA-YYYYMMDD-<short-stable-ascii-slug>.md`; keep the initial ID and path stable.
- If a path already exists, confirm that the ideas differ before adding the shortest numeric suffix. Never overwrite.
- Start with `status: captured`, `version: "0.1"`, and `implementation_authorization: not-granted`.
- Quote direction-setting user language verbatim. Keep interpretation outside the quote.
- Put only the strongest preliminary understanding in Current Shape and identify what remains unresolved.
- Label agent inferences as judgments or assumptions rather than user decisions or facts.
- Tell the user which record changed, then continue the discussion naturally.

Do not create a second index, summary, task, or management artifact.

## Co-develop the Idea

For each substantive turn:

1. Restate why the idea makes sense from the author's perspective.
2. Add real value through structure, alternatives, tradeoffs, counterexamples, or a recommendation.
3. Focus on the single question most likely to change the direction; do not give the author a questionnaire.
4. Read available project context instead of asking the author to repeat it.
5. Distinguish author intent, facts, judgments, assumptions, decisions, and open questions.
6. When the author adds or corrects intent, makes a decision, sets a boundary, or exposes a critical unknown:
   - rewrite Current Shape as a concise current snapshot;
   - append the reasoning trail under Evolution, Decisions & Boundaries;
   - update Open Questions & Assumptions;
   - update `updated_at` and append a changelog entry.

Do not update the record for greetings, stylistic edits, or repetition that does not change its meaning.

## Preserve the Five-section Record

Keep these five top-level sections and their meanings:

1. **Current Shape:** One-sentence definition, core value, and current recommendation.
2. **Origin & Raw Intent:** The original expression and real cause. Append important quotations; never silently rewrite them.
3. **Evolution, Decisions & Boundaries:** Reasoning history, decisions and rationale, discarded options, boundaries, and non-goals.
4. **Open Questions & Assumptions:** Matters still requiring author judgment or evidence.
5. **Changelog:** Append-only changes to understanding, state, and decisions.

Current Shape may be rewritten. Raw intent, historical decisions, and changelog entries may not be deleted. Mark overturned decisions as `superseded` and link the replacement instead of manufacturing a single seamless consensus.

## Manage State Explicitly

- `captured`: The origin is preserved; substantive exploration has not begun.
- `exploring`: At least one substantive discussion changed or expanded the understanding.
- `shaped`: The agent produced a coherent synthesis and the author explicitly confirmed it with language such as “I agree,” “That's it,” “Good enough to converge,” `我同意`, `就是这样`, or `可以收敛`.
- `parked`: The author paused it or a required condition is missing. Record the reason and restart condition.
- `superseded`: Another idea or decision replaced it. Preserve links in both directions.

The agent may recommend convergence but must not set `shaped` without author confirmation. Praise, a request for next steps, or “sounds good” does not grant implementation authorization.

## Require Separate Implementation Authorization

Only treat unambiguous author language such as “Start implementing this idea,” “Proceed with implementation,” `开工`, `开始实现这个想法`, or a contextually equivalent command as authorization.

After authorization:

1. Set `implementation_authorization: granted`.
2. Preserve the author's exact authorization, timestamp, and scope under Evolution and in the changelog.
3. Return a short handoff containing the idea ID, absolute record path, Current Shape, and remaining unknowns.
4. State that this skill has ended and the implementer must read the Idea record first.
5. Stop immediately. Do not invoke another skill, modify source, or run implementation commands.

Authorization applies only to the explicitly named idea and scope.

## Handle Corrections Safely

- Preserve the old expression when the author corrects it, record the correction, and update Current Shape.
- Treat a complete direction change as evolution of the same idea unless the author confirms it is separate.
- If the author says an automatic capture was not an idea, set the record to `parked`, record the misclassification, and stop exploring it.
- Do not silently delete or merge duplicate records. Present the evidence and let the author select the source of truth.
- If the conversation stops, leave the current state and open questions sufficient for another agent to continue.

## User-facing Response

Keep responses concise: name the changed record, its current `status`, the implementation authorization state, and the single most valuable question to explore next. Do not paste the full record back into the chat.
