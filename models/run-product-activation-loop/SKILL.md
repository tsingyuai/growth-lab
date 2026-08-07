---
name: run-product-activation-loop
description: Run a product activation observation-action-review loop with persistent Memory by defining a value-based activation event, diagnosing funnel evidence, implementing one measurable improvement, and reviewing the outcome. Use when improving onboarding, signup-to-value conversion, time to first value, workspace or project creation, first successful task completion, or continuing a previous activation experiment.
---

# Run the product activation loop

Coordinate the loop inside the current Product workspace. Use `<current-product-workspace>/memory/run-product-activation-loop/` as this Model's persistent Memory. Determine the Product workspace before reading or writing Memory; never combine different Products in one Memory namespace.

```text
Read Memory -> Define value -> Observe -> Decide -> Act -> Review -> Write Memory
```

Read [memory.md](references/memory.md) before starting. When the user requests recurring execution, also read root `AUTOMATION.md` and [automation.md](references/automation.md).

## Boundaries

- Optimize for a user's first meaningful product outcome, not signup completion, clicks, or screen views alone.
- Keep loop coordination and decision rules here. Delegate export interpretation to `$read-product-events`, implementation to `$implement-activation-improvement`, and outcome analysis to `$review-activation-performance`.
- Use Runtime-native repository inspection, browser testing, screenshots, and analytics connectors when available.
- Treat instrumentation, product-code implementation, deployment, experiment exposure, and automation as separate scopes. Approval for one does not authorize the next.
- Prefer one reversible change tied to one diagnosed constraint. Do not bundle unrelated onboarding redesigns into one test.
- Do not use forced consent, disguised controls, artificial urgency, obstructive cancellation, or other dark patterns to improve a metric.
- Keep raw identifiers and private event rows in the team's approved private data location. Store only necessary aggregates, provenance, limitations, and decisions in Memory.

## 1. Read Memory

Read recent Memory and older entries relevant to the current activation path, event definition, cohort, implementation, or pending review. Recover what was measured, what changed, what happened, and which recommendation remains untested.

## 2. Define first value

Before diagnosing a funnel, write a compact measurement contract:

- the qualifying population and journey start;
- the ordered steps that are useful for diagnosis;
- the activation event that demonstrates user value;
- the entity being counted, normally a user or account;
- the allowed time window from journey start to activation;
- identity rules across anonymous and authenticated states;
- exclusion rules for staff, tests, bots, duplicates, and invalid events;
- one primary metric and one or more harm guardrails.

Use the Product's actual value and capabilities. A convenient event is not automatically an activation event. If the value event is uncertain, inspect the product and label the definition as a hypothesis requiring product-owner or user evidence.

Do not change a historical activation definition silently. Version it, state why it changed, and avoid comparing incompatible windows or populations.

## 3. Observe

Inspect the real product journey, relevant code, analytics definitions, current UX, support or feedback evidence, and existing Memory.

When an event export is available, invoke `$read-product-events`. Require explicit field mapping when the source is ambiguous. Record collection time, source, data window, population, step definitions, exclusions, and data-quality limitations.

When event data is missing or unreliable, inspect the implementation and current instrumentation. The first action may be measurement repair. Do not invent conversion values or treat a successful analytics request as proof that events are correct.

Identify the largest decision-relevant constraint, such as:

- users cannot understand the next action;
- setup cost delays first value;
- required input, permission, or trust is missing;
- the product fails or is too slow on the critical path;
- users reach a step but do not receive a meaningful result;
- identity stitching, event semantics, or data quality makes the funnel unreadable.

Distinguish an observed drop from its cause. Event data locates friction; code, product behavior, feedback, or a focused test is needed to explain it.

## 4. Decide

Choose one action supported by current evidence. State:

- the observed constraint and confidence;
- the change hypothesis;
- the exact population and exposure rule;
- the primary metric, guardrails, and expected direction;
- the smallest implementation and rollback boundary;
- the observation window and decision rule;
- important alternative explanations.

Possible actions include repairing instrumentation, reducing setup work, improving guidance, supplying a useful default, moving trust information to the decision point, shortening processing time, or improving the first result.

Use an A/B experiment only when traffic, randomization, exposure logging, and a stable review window make it informative. With low traffic, prefer a staged rollout, pre/post evidence with explicit confounders, usability evidence, or a measurement-only change. Never manufacture statistical certainty.

If the action modifies product code, ask for implementation approval after presenting the evidence-backed scope. If measurement is not trustworthy enough to evaluate a product change, recommend measurement repair first.

## 5. Act

Invoke `$implement-activation-improvement` with the measurement contract, persisted evidence, approved scope, target product repository, and rollback boundary.

Build and locally verify the release candidate. Verify event names and properties against the existing analytics layer, test the critical path and failure path, and preserve accessibility, privacy, and existing product behavior outside the approved scope.

Return the locally verified release candidate. Deploy or start live exposure only after separate explicit approval through the Product's existing release process. Record implementation paths, checks, release state, exposure start, and baseline in Memory.

## 6. Review

Wait for the defined window or minimum evidence. Invoke `$review-activation-performance` with the measurement contract, baseline, implementation or exposure record, current evidence, and guardrails.

Separate instrumentation validity, reach, step conversion, activation, time to value, retention proxy, support burden, errors, and revenue. For randomized tests, analyze users by assigned exposure unless the experiment design explicitly requires another method. For pre/post comparisons, state seasonality, traffic mix, concurrent releases, and other confounders.

Choose one conclusion: continue collecting, ship, iterate, roll back, stop, or investigate measurement. Tie it to the predeclared decision rule; do not choose a favorable slice after seeing the data.

## 7. Write Memory and continue

Write dated evidence, measurement contracts, decisions, implementation records, outcomes, limitations, and one recommended next action to the current Product workspace's `memory/run-product-activation-loop/`. Link reviews to the observation and action they evaluate.

Apply method improvements directly to the owning Model, Collector, or Executor. Keep operational history in Memory and methodology out of it.

Before replying, read `.agents/skills/growth-lab/references/result-presentation.md`. Present one conclusion, the plain-language reason, the next available action, and one decision.
