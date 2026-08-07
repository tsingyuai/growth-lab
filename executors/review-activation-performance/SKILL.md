---
name: review-activation-performance
description: Review a released activation improvement or experiment against its predeclared measurement contract, data quality, primary metric, guardrails, uncertainty, and confounders. Use when deciding whether to continue collecting, ship, iterate, roll back, stop, or investigate measurement after an onboarding, signup-to-value, or first-value change.
---

# Review activation performance

Evaluate the decision, not just the most favorable metric. Read [decision-rules.md](references/decision-rules.md) before drawing a conclusion.

## Required evidence

Recover from the owning Model Memory:

- measurement contract and activation-definition version;
- diagnosed constraint and hypothesis;
- qualifying population, exposure or release record, and exact start time;
- baseline or control definition;
- primary metric, guardrails, observation window, and decision rule;
- implementation paths, concurrent releases, incidents, campaigns, or traffic changes.

When an export is supplied, invoke `$read-product-events`. Use a provider-specific authorized connector when available, but preserve the same provenance and privacy boundaries.

If the contract was written after results were viewed, say so and treat the review as exploratory.

## Validate measurement first

Check:

- event names, versions, firing boundaries, delivery delay, duplicates, and missing periods;
- population, exclusions, identity stitching, timezone, and activation window;
- experiment eligibility, stable assignment, exposure logging, and allocation balance;
- compatibility between baseline and current evidence;
- whether guardrail events and failure paths are observable.

Separate `no effect` from `no usable measurement`. Do not average across incompatible definitions to create a clean trend.

## Compare outcomes

Report absolute counts before rates. Then compare:

- reach and eligible population;
- each diagnostic step and the primary activation metric;
- time to first value;
- errors, latency, abandonment, support burden, privacy or trust signals;
- an early retention or revenue outcome only when the review window and data path support it.

For randomized experiments, analyze the predeclared assignment unit and report absolute difference, relative difference, uncertainty interval when defensible, sample size, and exposure duration. Check sample-ratio mismatch before interpreting effect.

For pre/post evidence, match comparable windows and state traffic mix, seasonality, weekday effects, campaigns, outages, and concurrent releases. Describe association, not causation.

Avoid declaring subgroup wins that were not predeclared. Use them as hypotheses for a later run.

## Decide

Choose exactly one primary disposition:

- `continue collecting`: the contract is valid but the decision window is incomplete;
- `ship`: the primary outcome improved enough and guardrails remain acceptable;
- `iterate`: evidence supports the direction but identifies a specific remaining constraint;
- `roll back`: harm, regression, or a predeclared rollback threshold is present;
- `stop`: the hypothesis is not supported enough to justify more exposure;
- `investigate measurement`: data validity prevents a product decision.

Tie the disposition to the predeclared rule and important uncertainty. Do not convert a neutral result into a win because one secondary metric moved.

## Preserve and return

Write a dated review linked to the measurement contract, implementation, release/exposure record, and aggregate evidence in `memory/run-product-activation-loop/`. Include limitations, disposition, rollback status when relevant, and one next action.

Return one plain-language conclusion, why the evidence supports it, the next available action, and one decision. Expand tables and statistical details only when the user needs them.
