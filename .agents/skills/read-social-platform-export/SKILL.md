---
name: read-social-platform-export
description: Use Growth Lab's social export Collector to normalize authorized Xiaohongshu, WeChat official account, or other platform CSV/JSON exports into aggregate campaign metrics without exposing private rows.
---

# Read social platform export

1. Read repository `AGENTS.md` and `DATA.md`, determine the current Product workspace, then read its `SOUL.md`.
2. Read `../../../collectors/read-social-platform-export/SKILL.md` completely.
3. For a supported export, invoke `python -B ../../../collectors/read-social-platform-export/scripts/normalize_social_platform_export.py <export> --platform <platform>` from this Skill directory, adding explicit field options when required.
4. Use only aggregate script output for counts and rates. If the command fails, report measurement as blocked.
5. Never expose private comments, direct messages, raw user identifiers, credentials, or full row-level exports.
