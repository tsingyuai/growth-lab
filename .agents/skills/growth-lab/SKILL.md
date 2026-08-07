---
name: growth-lab
description: Start or continue Growth Lab by understanding the current product or idea, confirming ambiguous user intent, selecting an actually implemented growth Model, coordinating its evidence and actions, and preserving stable product knowledge in SOUL.md and operational results in the Model's Memory. Use when onboarding a product, starting a growth project, asking what Growth Lab can do, resuming previous growth work, or deciding the next evidence-backed action.
---

# Run Growth Lab

Treat the current Coding Agent session as the control plane. Follow repository `AGENTS.md` and `DATA.md`, determine the current Product workspace, then read that workspace's `SOUL.md` before executing a growth task.

## Start clearly

When the user has not identified a product or only asks to start Growth Lab, use [first-run-experience.md](references/first-run-experience.md).

For the first response about every new Product, including when the user immediately supplies a URL, repository, prototype, or document, read the new-Product preface in [first-run-experience.md](references/first-run-experience.md). Introduce Growth Lab, the current stage, and the compact non-blocking mode choice before returning Product understanding. Do not repeat this preface when continuing an already understood Product.

Separate:

- an existing product: live site, testable prototype, application, repository, or implemented product documentation;
- an idea: a proposed problem, user, solution, or business without a current product artifact.

When ambiguous, ask: “目前已经有可访问的产品/原型，还是只有一个待验证的想法？”

For an idea, follow [idea-validation.md](references/idea-validation.md). Do not present product analytics, publishing, platform connection, or API Key setup before a product or an implemented Model needs it.

## Confirm compound intent

When the user supplies a known product together with files, data, history, or an implied objective, follow [intent-confirmation.md](references/intent-confirmation.md).

Use read-only inspection to infer the product, likely Model, relevant prior Memory, supplied evidence, expected output, and excluded actions. Ask whether that interpretation is correct only when two plausible intents remain or the ambiguity would change data ownership, external actions, cost, publication, or product modification.

When the user clearly identifies a new product and asks for a read-only first test, show the compact new-Product preface and begin product understanding directly. Do not repeat their request as a confirmation question. Keep internal paths, SOUL, Memory, Model names, and storage mechanics out of the user-facing response unless a conflict requires a decision or the user asks.

## Establish product context

Locate the product in the current repository, another local path, a public URL, a prototype, or the user's description. Read available evidence before asking questions.

Update the current Product workspace's `SOUL.md` only with stable product knowledge:

- product identity and form;
- users and situations;
- value and differentiation;
- implemented capabilities and channels;
- business objective and constraints;
- verified facts, hypotheses, and open questions.

Keep timed observations, data, task decisions, execution results, and deliverables out of SOUL.

For a new user, finish product understanding before recommending a growth loop. Return a short product summary, clearly marked uncertainties, and only the smallest questions needed to confirm stable context. Do not mix storage setup, loop assessment, automation, and product understanding into the same result.

## Show actual capabilities

After the user confirms the product understanding, or when asked what Growth Lab can do, read [loop-discovery.md](references/loop-discovery.md), scan `models/README.md` and actual `models/*/SKILL.md` files, and produce a concise applicability assessment. Explain “growth loop” once in ordinary language, then present each Model as one complete user-facing capability. Do not advertise a Collector, Executor, script, planned integration, or onboarding mode as a complete growth capability.

If no Model matches the objective, explain the boundary. Use the closest Model only for the scope it actually covers.

Do not initialize every Model, create empty history, or schedule work during discovery. Recommend one next loop. Initialize operational Memory only when that Model actually runs.

A recommendation is not execution. Explain why it fits, what the first stage will do, what it will not do, and when the user will decide again. Ask for confirmation before starting a Model unless the user directly invoked that specific Model with a clear scope.

## Select and run one Model

Choose the Model that matches the confirmed outcome. Read its `SKILL.md`, required references, and relevant files under the current Product workspace's `memory/<model-name>/` completely before acting.

Let the Model decide how to observe, choose an action, execute, review, and continue. Read Collectors and Executors only when the Model needs them.

Use [capability-onboarding.md](references/capability-onboarding.md) when the selected Model could use configuration such as private data, credentials, a connector, local tooling, permissions, publishing access, measurement, or automation. Missing optional configuration must not block unrelated product understanding or public research.

Do not wait for the user to know that configuration exists or to name a Key, environment variable, terminal command, connector, permission, export, or scheduler. When configuration becomes relevant, proactively disclose its benefit and optionality. Explain its strict boundary when the user asks, and begin the shortest safe setup only after the user expresses intent. Never imply that a guided setup exists until its adapter or connector is actually discoverable.

## Preserve the result

Write dated evidence, analysis, decisions, actions, outcomes, deliverables, and next recommendations to the current Product workspace's `memory/<model-name>/`. Use ordinary readable files and clear links; do not impose a universal Product/Study/version schema.

Apply a discovered method improvement directly to its owner:

- loop coordination and Memory method → `models/`;
- collection method → `collectors/`;
- creation, execution, publishing, or task review → `executors/`.

Never store credentials in SOUL, Memory, source, Markdown, JSON, command arguments, or output. Repository Clients receive credentials only from environment variables.

Before returning any Model result, read [result-presentation.md](references/result-presentation.md). Preserve full evidence and operational detail in the owning Memory, but default the user-facing response to the conclusion, plain-language reason, next available action, and one decision. Expand sources, detailed comparisons, methods, files, and validation only when the user asks, challenges the conclusion, or needs them to make a safe decision.
