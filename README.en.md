
<div align="center">

# 🧪 Growth Lab

<p>Run product operations and user growth loops through natural language: understand your product, find real demand, take action, and learn what to do next.</p>

[![GitHub stars](https://img.shields.io/github/stars/tsingyuai/growth-lab?style=for-the-badge&logo=github&color=071a2b)](https://github.com/tsingyuai/growth-lab/stargazers)
[![Open Source](https://img.shields.io/badge/OPEN_SOURCE-YES-2667FF?style=for-the-badge)](https://github.com/tsingyuai/growth-lab)

[Website](https://growthlab.tsingyuai.com)

[简体中文](./README.md) · [English](./README.en.md) · [繁體中文](./docs/readmes/README.zh-Hant.md) · [Français](./docs/readmes/README.fr.md) · [Español](./docs/readmes/README.es.md) · [Русский](./docs/readmes/README.ru.md) · [Português](./docs/readmes/README.pt.md) · [Deutsch](./docs/readmes/README.de.md) · [日本語](./docs/readmes/README.ja.md) · [한국어](./docs/readmes/README.ko.md) · [Türkçe](./docs/readmes/README.tr.md) · [Tiếng Việt](./docs/readmes/README.vi.md) · [Polski](./docs/readmes/README.pl.md)

</div>

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

## What makes Growth Lab different

### Every channel, through its full lifecycle

Growth Lab is designed to cover every growth channel from understanding the opportunity and choosing an action to execution, measurement, and the next decision. It currently supports SEO page growth plus Xiaohongshu content collection, high-performing-content research, writing, image generation, card rendering, compliance checks, and post-result feedback.

### Continuous collaboration through natural language

Automation does not have to mean an unattended process running forever. People give the Agent goals in natural language, receive completed work and results, provide feedback, and ask it to continue. The conversation is the interface.

### Information, methods, and execution connected

Growth information usually lives in reports, methods live in specialists' experience, and execution lives across disconnected tools. Growth Lab brings them into one workspace so the Agent can collect evidence, apply a method, complete the action, and carry the result into the next round.

### Open source, user-owned data, accessible knowledge

Growth Lab is open source and stores product context, operational data, Memory, and outputs in the user's own workspace. It does not hold user data or create lock-in through private formats and closed workflows. Its purpose is to make effective growth knowledge inspectable, adaptable, and available to everyone.

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

Collect high-performing Xiaohongshu content related to this product, choose a transferable structure, and create a complete post with images.

Review the latest results and execute the next growth action.
```

The Runtime reads the available Models, builds the missing product and market context, invokes the relevant Collectors and Executors, and writes its evidence, results, deliverables, and next actions back into the workspace.

### Connect your product

Tell the AI, in natural language, where your product repository or existing materials are located. The AI first reads the product facts it can verify. Users, problems, and value propositions that lack evidence remain open questions and are developed progressively through later growth loops.

### Configure through natural language

One unified [onboarding Skill](models/onboard-growth-lab/SKILL.md) audits dependencies across every Growth Lab capability. Users do not need to learn a separate command or open a setup page. Ask the Agent directly:

```text
Check which Growth Lab configuration is still missing.
Set up Xiaohongshu collection and image generation; skip SEO for now.
```

The Agent checks API keys, third-party clients, external repositories, browsers, and authentication, explains where missing configuration comes from, and lets the user configure or bypass each capability for the current session. Xiaohongshu uses the local browser-first `xiaohongshu-mcp` with a recommended first batch of 25; AI image generation needs either local OpenAI or Gemini credentials. See [CONFIGURATION.md](CONFIGURATION.md) for exact fields, storage, and removal. Third-party clients and authentication remain outside the repository; secrets, cookies, and browser profiles do not enter Memory.

Methods and executable scripts stay with their owning Collector, Executor, or Model Skill. Private product materials, collected samples, generated outputs, and historical operating Memory are not distributed with the repository. A Model creates its own Memory namespace when the user runs it.

## System components

- Collectors for demand, competitors, content, and product growth data;
- Model Skills coordinating observation-action-review loops and persistent Memory;
- Executor Skills for creation, publishing, human collaboration, and review;
- Example workspaces showing complete growth journeys.

## Available capabilities

One capability is one complete observation-action-review loop, represented by one Model. The Model coordinates Collectors and Executors and preserves operational evidence, outcomes, and next actions in its own Memory.

| Name | Introduction | Observed result |
|---|---|---|
| [SEO Page Growth Loop](models/run-seo-page-loop/SKILL.md) | Identify the situations in which users may need your product, research what they actually search for in those situations, and create informative SEO pages that solve their problems and lead them to the product. | In our own run, new pages were indexed within 1–2 days. On a 7-day average basis, overall CTR decreased by 50%, while impressions and clicks each increased by 1000%. |
| [Xiaohongshu Replication and Review Loop](models/xhs-replicate/SKILL.md) | Coordinates collection, drafting, editing, screenshots, image generation, card rendering, compliance checks, and post-result review. | Commercial content created with this workflow has reached [4,000+ likes/saves and 700+ comments on a single post](http://xhslink.cn/o/37uik9K9WHr). Publishing remains manual. |

These figures describe one observed run and provide evidence for continued iteration. Results depend on the product, domain, search demand, page quality, site authority, and observation window.

## Status

Growth Lab includes a working SEO Page Growth Loop and a Xiaohongshu replication and review workflow. Reusable Skills, scripts, CLIs, and automated checks remain in their owning capability directories. Private product data, samples, screenshots, generated posts, and historical Memory are intentionally excluded. Xiaohongshu publishing remains manual.

If this direction resonates with you, open an issue and tell us what product you are growing, where the current workflow breaks, and which tools the Runtime should be able to use.

## License

Growth Lab is open source under the [Apache License 2.0](./LICENSE).
