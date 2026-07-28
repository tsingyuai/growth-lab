#!/usr/bin/env python3
"""Content lint - prevent model-shaped phrases from entering publishable copy.

Usage:
    python3 executors/xhs-render-cards/scripts/check-banned-phrases.py memory/<loop>/outputs/<post>
    python3 executors/xhs-render-cards/scripts/check-banned-phrases.py file1.md prompt.txt ...

Exit code:
    0 = 全部通过
    1 = 命中违规(列文件/行号/原文/规则链接,阻塞后续步骤)

设计原则:
- 字面规则机械拦截(LLM 自律已被证伪,多轮对话 context drift 会忘)
- 只查实际喂给生图模型的 prompt 文本；方法论与策划文件允许引用违规词作为分析对象
- 不查方法论 / skill / template 这些"描述规则的文档"自身(它们会引用违规词作为反面例子)
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


# 违规规则清单
# Rule source: executors/xhs-render-cards/references/deai.md
RULES: list[dict] = [
    # ── 「不是」否定起手式(2026-06 新规则,广义)──────────────────────
    {
        "id": "BANNED-001",
        "pattern": r"不是\s*[A-Za-z一-鿿]+\s*[—,，]+\s*[A-Za-z一-鿿]+",
        "name": "「不是 A —— B」否定+对仗",
        "severity": "ERROR",
        "advice": "直接说肯定句 B,不要先否定 A。例:「不是凑字 — 全替你排好」→「全替你排好」",
        "ref": "xhs-render-cards/references/deai.md",
    },
    {
        "id": "BANNED-002",
        "pattern": r"不是.{1,15}[,，].{0,3}(是|而是)",
        "name": "「不是 A,是/而是 B」对仗金句",
        "severity": "ERROR",
        "advice": "用「问题是」「真正难的是」「卡的是」「关键在」替代否定起手",
        "ref": "xhs-render-cards/references/deai.md",
    },
    {
        "id": "BANNED-003",
        "pattern": r"而不是",
        "name": "「而不是」",
        "severity": "ERROR",
        "advice": "去掉「而不是 X」,直接说前半句肯定句即可",
        "ref": "xhs-render-cards/references/deai.md",
    },
    {
        "id": "BANNED-004",
        # 独立的"不是"(非「不替你」「不像」「不再」等单字否定),
        # 排除 "是不是" "再不是" "也不是" 等疑问/转折语境
        "pattern": r"(?<![是再也并都还])\s*不是(?!是)",
        "name": "单独「不是」",
        "severity": "WARN",
        "advice": "1 条文案/1 张图 ≤ 1 处;尽量改肯定句。这条是 WARN,只在「错位上下文」时升级 ERROR",
        "ref": "xhs-render-cards/references/deai.md",
    },
    # ── anti-ai-checklist 警惕词 ───────────────────────────────────
    {
        "id": "AI-001",
        "pattern": r"总之|综上所述|不难看出|由此可见",
        "name": "AI 总结套话",
        "severity": "ERROR",
        "advice": "直接给结论,删掉过渡套话",
        "ref": "anti-ai-checklist 警惕词",
    },
    {
        "id": "AI-002",
        "pattern": r"首先[,,].{1,30}其次[,,]|其次[,,].{1,30}再者[,,]|首先[\s\S]{1,200}其次[\s\S]{1,200}最后",
        "name": "首先/其次/再者刻板列举",
        "severity": "ERROR",
        "advice": "用数字标号或场景化叙述替代",
        "ref": "anti-ai-checklist 警惕词",
    },
    {
        "id": "AI-003",
        "pattern": r"值得一提的是|不可否认",
        "name": "AI 强调套话",
        "severity": "ERROR",
        "advice": "删掉,直接说事实",
        "ref": "anti-ai-checklist 警惕词",
    },
    {
        "id": "AI-004",
        "pattern": r"希望对你?有(所)?帮助|希望对大家有(所)?帮助",
        "name": "AI 套话尾句",
        "severity": "ERROR",
        "advice": "删尾句或改成具体提问 / 互动钩子",
        "ref": "anti-ai-checklist 警惕词",
    },
    {
        "id": "AI-005",
        "pattern": r"与此同时|在.{1,20}的同时",
        "name": "AI 工整连接词",
        "severity": "WARN",
        "advice": "改成短句拆分,避免长复合句",
        "ref": "anti-ai-checklist 警惕词",
    },
]

# 待检查文件类型 = 真正进发布物的文件
# prompts/*.txt 喂给生图模型直接写图上。
# image-plan.md / draft.md / _review.md / PROCESS.md 是元信息/策划/复盘,允许引用违规词作为分析对象。
DEFAULT_TARGET_PATTERNS = [
    "*.prompt.txt",
    "*.prompts.txt",
]

# Prompt 目录或文件路径里出现 "prompt" 就检查
PROMPT_HINT = "prompt"

SKIP_FILES = {
    "_review.md",  # 合规自检
    "PROCESS.md",  # 决策溯源
    "README.md",
    "image-plan.md",  # 视觉策划,含「铁律 0:0 处不是 X」这种元规则
    "draft.md",  # 文案草稿,含「内容策略」段落讨论违规词作为分析对象
}


@dataclass
class Violation:
    file: Path
    line_no: int
    line_text: str
    rule_id: str
    rule_name: str
    severity: str
    matched: str
    advice: str
    ref: str


def lint_file(path: Path) -> list[Violation]:
    """Lint 单文件,返回所有违规。"""
    violations: list[Violation] = []

    if not path.exists():
        print(f"  WARN: file not found: {path}", file=sys.stderr)
        return violations

    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  ERROR reading {path}: {e}", file=sys.stderr)
        return violations

    lines = text.split("\n")
    for i, line in enumerate(lines, 1):
        # 跳过 markdown task list 行(- [ ] / - [x]):这种格式 ≈ "checklist 引用规则",
        # 不是违规使用。例:`- [x] 0 处「希望对你有帮助」尾句套话` 是元规则引用。
        if re.match(r"^\s*[-*]\s*\[[ xX]\]\s+", line):
            continue
        # 跳过 markdown blockquote 行(>):同上,引用规则文本
        if re.match(r"^\s*>", line):
            continue
        for rule in RULES:
            for m in re.finditer(rule["pattern"], line):
                violations.append(
                    Violation(
                        file=path,
                        line_no=i,
                        line_text=line.strip()[:150],
                        rule_id=rule["id"],
                        rule_name=rule["name"],
                        severity=rule["severity"],
                        matched=m.group(0),
                        advice=rule["advice"],
                        ref=rule["ref"],
                    )
                )
    return violations


def collect_target_files(targets: list[str]) -> list[Path]:
    """收集所有待检查文件。targets 可以是文件或目录。"""
    files: list[Path] = []
    for t in targets:
        p = Path(t)
        if p.is_file():
            if p.name not in SKIP_FILES:
                files.append(p)
        elif p.is_dir():
            for pattern in DEFAULT_TARGET_PATTERNS:
                files.extend(
                    f for f in p.rglob(pattern) if f.name not in SKIP_FILES
                )
            # prompt 文件
            for f in p.rglob("*.txt"):
                if PROMPT_HINT in str(f).lower() and f.name not in SKIP_FILES:
                    files.append(f)
        else:
            print(f"  WARN: target not found: {t}", file=sys.stderr)
    # dedup
    return sorted(set(files))


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Content lint for Xiaohongshu publication units",
    )
    ap.add_argument("targets", nargs="+", help="files or post directories to lint")
    ap.add_argument("--strict", action="store_true", help="treat WARN as ERROR")
    args = ap.parse_args()

    files = collect_target_files(args.targets)
    if not files:
        print("no target files found", file=sys.stderr)
        return 1

    all_violations: list[Violation] = []
    for f in files:
        all_violations.extend(lint_file(f))

    if not all_violations:
        print(f"✓ lint passed ({len(files)} files, 0 violations)")
        return 0

    # 按文件 + 行号 排序
    all_violations.sort(key=lambda v: (str(v.file), v.line_no, v.rule_id))

    error_count = sum(1 for v in all_violations if v.severity == "ERROR")
    warn_count = sum(1 for v in all_violations if v.severity == "WARN")

    print(f"\n✗ {len(all_violations)} violations across {len(files)} files "
          f"(ERROR={error_count}, WARN={warn_count})\n")

    current_file = None
    for v in all_violations:
        if v.file != current_file:
            current_file = v.file
            print(f"\n  {v.file}:")
        sev_mark = "✗" if v.severity == "ERROR" else "⚠"
        print(f"    {sev_mark} L{v.line_no}  [{v.rule_id}] {v.rule_name}")
        print(f"        matched: {v.matched!r}")
        print(f"        line:    {v.line_text}")
        print(f"        advice:  {v.advice}")
        print(f"        ref:     {v.ref}")

    print()
    if args.strict:
        # strict 模式 WARN 也算 fail
        return 1 if all_violations else 0
    # 默认: 只 ERROR 算 fail
    return 1 if error_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
