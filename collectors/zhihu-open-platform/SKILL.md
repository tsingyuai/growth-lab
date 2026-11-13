---
name: zhihu-open-platform
description: Collect Zhihu search results, hot-list topics, and question answer summaries through Zhihu's official CLI and Open Platform API. Use for current discussions, expert language, objections, problem framing, topic discovery, and evidence that must retain original Zhihu URLs. Do not use MediaCrawler or browser-cookie automation for Zhihu.
---

# Zhihu Open Platform

Use Zhihu's official CLI described at <https://developer.zhihu.com/docs?key=zhihu_cli>. The CLI is published by Zhihu, downloads from the official CDN, verifies the release against its manifest, and authenticates with an Open Platform Access Secret.

## Collection boundary

- `search zhihu` returns titles, authors, excerpts, engagement counts, and original URLs. An excerpt is not the full article or answer.
- `hot` discovers current topics. It does not establish that the framing or claims are true.
- `question answers` returns service-provided answer summaries and original URLs. Do not call them AI summaries or answer bodies.
- `me content` can return the current account's own full content. It cannot read another user's private content.
- Do not use cookie automation, page scraping, or MediaCrawler as a fallback.

## Readiness

Follow [onboard-growth-lab](../../models/onboard-growth-lab/SKILL.md) for global dependency handling. From the repository root, inspect the official client without changing the machine:

```bash
python3 models/onboard-growth-lab/scripts/onboard_zhihu.py status
```

If the CLI is missing, explain that it is Zhihu's official binary, that it installs under the user's application data directory, and that no administrator access or PATH change is needed. Install only after explicit approval:

```bash
python3 models/onboard-growth-lab/scripts/onboard_zhihu.py install --yes
```

If authentication is missing:

1. Ask the user to open <https://developer.zhihu.com/profile>, sign in, and generate an Access Secret.
2. Prefer asking the user to run `python3 models/onboard-growth-lab/scripts/onboard_zhihu.py auth` in their own terminal so the no-echo prompt handles the secret.
3. Never put the secret in a command line argument, source file, Memory, or normal configuration file.
4. After approval for the online call and possible quota use, run `onboard_zhihu.py verify --query "<real query>" --yes` or use `--hot` when a real query is unavailable.
5. Treat `auth status` without `--verify` as local configuration evidence, not proof that the credential works or that content collection is ready.

For headless environments, `ZHIHU_ACCESS_SECRET` may be injected by the host's secret manager. Never read it into a transcript or persist it in the repository.

## Content collection

Before running, define:

- the research question;
- query variants;
- content types needed;
- result and date bounds;
- whether question answer summaries or hot-list discovery are required;
- the invoking Model's Memory destination.

Use multiple short, problem-shaped queries. A useful first pass combines audience language, category language, and use-case language:

```bash
python3 collectors/zhihu-open-platform/scripts/zhihu_cli.py collect \
  --query "用户问题的原始说法" \
  --query "品类或概念词" \
  --query "使用场景 困难 解决" \
  --count 10 \
  --output memory/<model-name>/<timestamp>-zhihu-topic
```

Add hot-list discovery or answer summaries when they answer a specific research question:

```bash
python3 collectors/zhihu-open-platform/scripts/zhihu_cli.py collect \
  --query "问题变体" \
  --hot \
  --question-url "https://www.zhihu.com/question/123" \
  --answer-limit 20 \
  --output memory/<model-name>/<timestamp>-zhihu-topic
```

The script invokes only documented read commands, preserves each raw JSON response, writes normalized JSONL records with discovery provenance, removes tracking parameters from canonical URLs, and deduplicates repeated content. It stops on authentication, quota, or service errors instead of retrying.

For full text of the current account's own answer or article, use the official binary directly only after reading the collection scope and authorization the task requires:

```bash
"<binary_path>" me content --content-url "https://www.zhihu.com/answer/123"
```

## Evidence handling

- Preserve `Title`, `AuthorName`, `ContentText` or `Summary`, and `Url`.
- Keep content type and question context. An answer without its question loses meaning.
- Deduplicate by `ContentID` or canonical URL while retaining every discovery query that found it.
- Separate platform excerpts from Agent analysis.
- Do not write complete follow/favorite/history collections to Memory without an explicit task need.
- Link the raw and normalized files from the invoking Model's Memory.

## Completion report

Return:

- exact queries, question URLs, and collection time;
- official CLI version and binary path;
- count by content type and source;
- raw and normalized output paths;
- deduplicated record count, empty-result explanation, and any excluded inputs;
- auth, quota, rate-limit, or partial-failure status;
- whether the evidence is excerpt-only or includes service-provided summaries.

Never report excerpt-level evidence as full-text collection.
