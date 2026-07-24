# Growth Lab

[中文](README.zh-CN.md)

> AI-native growth workspace powered by Codex and Claude Code skills.

Growth Lab is an open-source, end-to-end growth tool that takes a product from code to market. Powered by coding agents, it understands the product, connects the tools and channels it needs, researches the market, creates growth assets, executes campaigns, and reviews real-world data to improve the next round of growth.

> This repository is currently at the idea stage. This README describes the direction we intend to build in public.

## Why Growth Lab

Most AI growth tools solve one fragment of the problem. Some generate copy, some research competitors, some schedule posts, and some display analytics. Product context is repeatedly lost between these tools, while the most important decisions still depend on disconnected dashboards, documents, prompts, and manual handoffs.

Growth is a continuous learning loop:

```text
Understand the product
→ Identify users and markets
→ Research channels and content
→ Form a strategy
→ Create and distribute
→ Observe real outcomes
→ Learn and improve the next action
```

Modern coding agents can read repositories, search the web, operate tools, edit files, reason across many kinds of context, and collaborate with people in a session. Growth Lab uses Codex and Claude Code as its application runtime and turns these capabilities into an end-to-end growth workflow.

## The model

```text
Session = Control Plane
Codex or Claude Code = Runtime
Skill = Growth Method
Client = External Action
Filesystem = Memory
```

Skills teach the Runtime how to understand a product, conduct research, choose tools, develop a strategy, create assets, examine feedback, and decide what to do next. Client tools provide access to browsers, official APIs, analytics exports, content platforms, and media generation. Files preserve product context, research, decisions, and outputs across conversations.

The AI session controls the entire workflow.

Every Model is an observation-action-review loop. Every Model owns persistent Memory containing time-based operational data, analysis, outcomes, and recommended next actions. The next run reads that Memory before making a new observation.

Loop methodology lives in the Model and evolves through direct edits to its Skill and references. Memory records what happened when the Model was used.

## What it enables

### Product-native understanding

Growth Lab runs alongside the product, so it can study source code, documentation, landing pages, configuration, analytics definitions, and previous growth work together. Its decisions are grounded in actual product context and accumulated evidence.

### One continuous context

Research, strategy, content, experiments, and results live alongside the product. The Runtime reuses previous findings and connects new evidence to earlier decisions.

### From advice to action

The same session that produces a recommendation can inspect a website, analyze metrics, prepare a campaign, generate assets, edit the product, or call an authorized publishing API.

### Transparent and adaptable

Skills, Clients, Memory, and outputs are ordinary local files. Teams can inspect the method, replace an integration, and improve the workflow while using it.

### Local-first and open

The workspace remains under the user's control and can be versioned with Git. Growth Lab works with tools and services the team already trusts while keeping product and growth data in the team's chosen environment.

## How to use it

```bash
git clone https://github.com/tsingyuai/growth-lab.git
cd growth-lab
```

Open the directory in Codex or Claude Code, then ask what Growth Lab can do or describe the growth outcome you want.

Example prompts:

```text
What can you do?

Understand this product and run its first growth loop.

Review the latest results and execute the next growth action.
```

The Runtime reads the available Models, builds the missing product and market context, invokes the relevant Collectors and Executors, and writes its evidence, results, deliverables, and next actions back into the workspace.

## Connect your product

Let your AI open this workspace, then ask the AI.

## Planned building blocks

- Collectors for demand, competitors, content, and product growth data;
- Model Skills coordinating observation-action-review loops and persistent Memory;
- Executor Skills for creation, publishing, human collaboration, and review;
- Example workspaces showing complete growth journeys.

## Available capabilities

One capability is one complete observation-action-review loop, represented by one Model. The Model coordinates Collectors and Executors and preserves operational evidence, outcomes, and next actions in its own Memory.

| Name | Introduction | Observed result |
|---|---|---|
| [SEO Page Growth Loop](models/run-seo-page-loop/SKILL.md) | Identify the situations in which users may need your product, research what they actually search for in those situations, and create informative SEO pages that solve their problems and lead them to the product. | In our own run, new pages were indexed within 1–2 days. On a 7-day average basis, overall CTR decreased by 50%, while impressions and clicks each increased by 1000%. |

These figures describe one observed run and provide evidence for continued iteration. Results depend on the product, domain, search demand, page quality, site authority, and observation window.

## Status

Growth Lab is at the beginning. We are publishing the idea first, then turning it into a practical set of Models, Collectors, and Executors through real product-growth work.

If this direction resonates with you, open an issue and tell us what product you are growing, where the current workflow breaks, and which tools the Runtime should be able to use.

## License

To be decided before the first implementation release.
