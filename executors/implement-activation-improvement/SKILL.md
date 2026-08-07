---
name: implement-activation-improvement
description: Design and implement one approved, measurable, reversible product activation improvement in an existing product repository. Use when Growth Lab has diagnosed an onboarding or time-to-value constraint and needs to repair instrumentation, reduce setup friction, improve first-run guidance, provide a useful default, strengthen trust, or build a controlled activation experiment without deploying it automatically.
---

# Implement an activation improvement

Turn one approved activation hypothesis into a locally verified release candidate. Read [experiment-design.md](references/experiment-design.md) when the change will be exposed to real users or compared across cohorts.

## Required input

Require:

- the Product repository and current Product workspace;
- the persisted observation or evidence supporting the constraint;
- the measurement contract: population, journey start, activation event, entity, window, exclusions, primary metric, and guardrails;
- the approved change scope and rollback boundary;
- the current analytics or feature-flag conventions when they exist.

If the evidence, activation definition, target repository, or approval scope is ambiguous, stop before editing the Product.

## Inspect the actual path

Read repository instructions, relevant routes, components, services, analytics utilities, tests, and current working-tree changes. Walk the critical path in the running Product when feasible. Identify where the diagnosed friction occurs and where events are emitted.

Work with existing frameworks, design systems, analytics helpers, feature flags, and deployment conventions. Do not introduce a new vendor or abstraction for one experiment unless the Product requires it and the user approves it.

## Write a small implementation brief

Before editing, make the following explicit in the owning Model Memory or implementation context:

- hypothesis and diagnosed constraint;
- qualifying and exposed population;
- control and treatment behavior, or staged-rollout behavior;
- exact UI or system change;
- event names, firing conditions, versions, and required properties;
- failure behavior, guardrails, and rollback;
- local checks and post-release observation window.

Instrumentation-only work must also state which future decision it enables. Do not add events without an owner or question.

## Implement

- Make the smallest coherent change that can test the hypothesis.
- Preserve behavior outside the approved population and scope.
- Reuse the Product's identity, analytics, consent, accessibility, localization, and error-handling patterns.
- Emit exposure only when the user actually becomes eligible and sees the assigned experience. Keep assignment stable for the experiment unit.
- Emit outcome events from the true success boundary, preferring server-confirmed completion when appropriate.
- Avoid raw content, prompts, documents, credentials, emails, or other sensitive values in event properties.
- Version changed event semantics and retain compatibility when downstream consumers require it.
- Add or update focused tests for assignment, event firing, critical success, failure, and rollback paths in proportion to risk.

Do not use coercive defaults, hidden choices, false scarcity, forced consent, or obstructive exits to improve activation.

## Verify

Run the Product's smallest relevant formatter, type check, unit or integration tests, and local browser path. Confirm:

- the release candidate renders and the critical action works;
- events fire once at the documented boundary with the documented properties;
- refresh, retry, duplicate requests, and failed actions do not create false activation;
- assignment or rollout is stable;
- control or unaffected users retain existing behavior;
- rollback removes the change without corrupting user state;
- accessibility and responsive layout remain usable for UI work.

Use a local analytics stub, debug sink, or test double when available. Do not send test events into production analytics unless explicitly authorized and safely labeled.

## Hand off

Return changed Product paths, verified behavior, commands and results, unresolved risks, release requirements, and the exact post-release evidence needed. Record the implementation state in the owning Model Memory.

Implementation approval does not authorize merge, deployment, experiment allocation, user messaging, or spending. Ask separately before each action that changes live state.
