# Product activation loop Memory

Use `<current-product-workspace>/memory/run-product-activation-loop/` as this Model's persistent Memory. Never read or write another Product's Memory unless the user explicitly requests a comparison and the output owner is clear.

## Before observation

Read entries relevant to the current journey, population, activation definition, event version, implementation, or review. Recover:

- the latest measurement contract and its evidence status;
- comparable baselines and data windows;
- known instrumentation limitations;
- actions, releases, exposures, and rollback boundaries;
- outcomes and the pending next decision.

Treat prior definitions and conclusions as time-scoped judgments. Do not compare incompatible populations, event versions, or activation windows.

## After observation, action, or review

Use date- or timestamp-prefixed readable files. Make these facts recoverable:

- collection time, source, population, and analysis window;
- journey start, ordered steps, activation event, entity, and time window;
- exclusions, identity rules, event versions, and data-quality checks;
- observed constraint, hypothesis, alternatives, and confidence;
- approved scope, implementation paths, release or exposure state, and rollback;
- primary metric, guardrails, results, uncertainty, and confounders;
- decision and one recommended next action.

Keep private row-level exports under the team's approved retention path. Memory intended for sharing should contain redacted aggregates and provenance, not user identifiers or credentials.

## Keep methodology with its owner

Apply better loop sequencing or decision rules to this Model, event-source techniques to the Collector, and implementation or review techniques to the responsible Executor. Memory records what happened; it is not a backlog for method changes.
