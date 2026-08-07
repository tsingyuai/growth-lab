# Capability onboarding

Configure only the capability required by the selected Model and current action. Apply this flow to credentials, connectors, private-data imports, local dependencies, filesystem or network permissions, publishing access, analytics or instrumentation, and automation settings.

## Contents

- Configuration experience
- Proactive discovery
- Explain strict boundaries
- User-facing levels and progressive setup
- Runtime-aware handoff
- Minimize user effort
- Missing capability

## Configuration experience

Use three progressive levels:

1. **Disclose**: when configuration could materially improve a confirmed task, proactively state that it exists, what result it improves, whether it is optional, and the no-configuration alternative. Do not wait for the user to know its name.
2. **Explain**: when the user asks about it, explain the exact access boundary, data touched, read/write behavior, persistence, cost or side effects, storage location, verification, revocation, and safer alternatives. Do not start setup merely because they asked a question.
3. **Configure**: when the user expresses intent, inspect the current Runtime and provide the most automated supported route. Ask only for the irreducible authorization or hidden secret entry, then perform readiness checks, setup, and verification on the user's behalf within granted permissions.

Do not list every possible configuration during onboarding. Mention only configuration relevant to the current Product stage, selected Model, or immediately foreseeable next decision. Preserve a compact “可稍后配置” option so cautious users know the capability exists without being pushed into it.

## Proactive discovery

Do not require the user to ask how to configure a capability. When the selected Model first reaches an action that would materially benefit from or require unavailable private access:

1. run the non-secret readiness check;
2. explain in one sentence what the capability would improve;
3. automatically present the safe paths that are actually available now;
4. continue with the least connected valid path when the capability is optional, or wait for the user's choice when it is required.

Use a compact choice such as:

```text
这一步如果连接 <platform>，可以获得 <specific benefit>。当前尚未连接。

- 继续 Basic：使用公开资料，不配置；
- 使用导出：提供受支持的 CSV/JSON，不需要 Key；
- 安全连接：仅在当前环境已安装安全配置向导或官方连接器时显示。
```

Do not interrupt first Product understanding merely because optional private data could improve a later stage. Surface the choice when it becomes relevant to a confirmed Model or when the user asks about Connected mode.

## Explain strict boundaries

When the user asks what a configuration means or whether it is safe, answer before requesting consent. Cover only the applicable items, but do not omit a material risk:

- purpose and the concrete result it improves;
- exact account, site, repository, directory, dataset, or channel in scope;
- read-only versus write, publish, spend, contact, or account-changing access;
- requested permission or API scope and why each part is needed;
- where authorization or a secret is held, how long it persists, and which process can receive it;
- whether data leaves the local machine and which provider receives it;
- expected cost, rate limits, external side effects, and rollback or revocation path;
- lowest-impact verification and what success does not prove;
- Basic or export-based alternative and the resulting evidence limitation.

Configuration consent authorizes only setup and lowest-impact verification. It does not authorize research beyond the confirmed scope, importing unrelated private data, changing product code, publishing, deploying, spending, contacting people, scheduling tasks, or widening future permissions.

## User-facing levels

- Basic: local product material and public sources; no credentials.
- Assisted: user-authorized browser access or user-provided exports; no persistent repository credential.
- Connected: an implemented official API or authorized Client required by the Model.

These levels explain available evidence; they are not Models or complete growth capabilities.

## Progressive setup

1. State what result the missing capability improves.
2. Show only Clients actually implemented in the repository.
3. Explain whether access is read-only or side-effecting.
4. Run `python .agents/skills/growth-lab/scripts/check_capabilities.py` to check implemented local Client readiness without printing credential values.
5. When a Client needs a secret, require the user to set the documented environment variable through a trusted local prompt or their own environment setup.
6. Run the lowest-impact verification and distinguish authentication failure, permission failure, successful empty data, and valid data.
7. Continue only within the verified scope.

## Runtime-aware handoff

Determine what the current Codex, ChatGPT, CLI, IDE, or compatible Agent Runtime can actually invoke. A Skill can provide the workflow and run repository scripts within granted permissions; it cannot assume that every surface exposes an interactive terminal, local credential store, browser authorization, connector, or persistent environment.

Prefer, in order:

1. an installed official connector or MCP authorization flow for live private data and controlled actions;
2. an installed local guided adapter that opens a hidden input prompt and injects the secret only into the required child process;
3. a user-provided supported export that needs no credential;
4. an exact advanced manual environment-variable command for the current operating system and Runtime.

For a local guided adapter, ask before opening a terminal, browser, or operating-system prompt. After approval, run the adapter instead of telling the user to find or edit a file. Report only `configured`, `limited`, or `failed`; never read the entered value back into the conversation.

When no secure adapter or connector is installed, say that the guided setup is not available in the current installation. Do not call a plain environment-variable instruction “one-click”. Offer the export and Basic paths first; place manual terminal setup last and explain any restart or process-scope requirement.

On a web or cloud surface without local-machine access, do not offer a local keychain or terminal action. Use an available authorized connector, request an export, or continue with public evidence.

Never ask a novice user to locate, create, or edit `.env`, Markdown, JSON, repository configuration, or credential files. Do not expect the user to know the terms API Key, environment variable, MCP, or integrated terminal before presenting the available choice.

## Minimize user effort

Treat user attention as a limited budget:

- ask for one decision at a time and combine non-secret readiness checks before asking;
- prefer one official authorization flow, one hidden-input prompt, or one generated launcher over several manual commands;
- when several safe mechanical steps can be executed under one clearly scoped approval, explain the bundle once and execute them together;
- never ask the user to copy values between several files, terminals, or screens when an installed adapter can pass them directly;
- preserve completed non-secret setup and resume from the failed step instead of restarting the whole flow;
- do not repeat warnings unchanged; show the full boundary once, then summarize only new risk;
- stop after repeated failure and offer Basic or export fallback instead of creating an exhausting troubleshooting loop.

Aim for no more than two user operations for a supported guided setup: one authorization decision and, only when unavoidable, one private action such as signing in, approving scopes, or entering a secret in a trusted hidden prompt. If the current installation cannot meet that target, state the remaining steps before starting and offer a lower-effort alternative.

Never reduce user operations by weakening consent, hiding a consequential boundary, broadening permissions, persisting a secret insecurely, or combining setup with publication or another external action.

Repository Clients receive credentials only from environment variables. External secret managers may inject an environment variable before execution, but Growth Lab does not read keychains or credential files directly.

Never ask for a secret in chat. Never write one to SOUL, Memory, source, Markdown, JSON, command arguments, logs, or commits.

Configuration grants capability, not action approval. Publishing, deployment, spending, contacting people, and account changes still require explicit confirmation.

## Missing capability

Do not block unrelated work. Continue with public evidence or a user export when methodologically valid. State unavailable metrics and lower confidence.

When the missing capability prevents the Model's required evidence or review, record the waiting condition and smallest recovery input in the current Product workspace's `memory/<model-name>/`. Do not invent data or a substitute capability.

Distinguish these states in the user-facing result:

- `not needed yet`: continue without setup;
- `available but not connected`: proactively offer the supported paths;
- `guided setup unavailable`: offer export, Basic, and an accurately labeled advanced manual route;
- `connected but unverified`: run the lowest-impact verification before use;
- `verified`: continue only within the confirmed permission scope.
