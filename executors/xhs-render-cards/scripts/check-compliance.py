#!/usr/bin/env python3
"""小红书发布物通用合规 lint。

检查绝对化营销、站外导流、伪造承诺和敏感个人信息引导。领域专用规则应由具体
Model 在自己的流程中检查，不得塞进这个通用 Executor。

退出码：0=通过；1=存在 ERROR 或没有可检查文件。
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


RULES = [
    {
        "id": "C-ABSOLUTE",
        "pattern": r"最好用|最强|最牛|最高效|最专业|最权威|全网最|史上最|世界第一|排名第一|"
                   r"唯一一个|独一无二|100%|百分之百|保证成功|保证有效|零风险|永不失败|一劳永逸",
        "name": "绝对化或无法证明的营销宣称",
        "severity": "ERROR",
        "advice": "改成具体、可验证并保留适用条件的表达。",
    },
    {
        "id": "C-DIVERT",
        "pattern": r"微信|[vV]\s*[xXｘ]|[wW][xX]号|加我(微信|v|好友)?|私我|滴滴我|"
                   r"二维码|扫码加|加群|公众号|gzh|薇信",
        "name": "站外导流或联系方式",
        "severity": "ERROR",
        "advice": "删除站外联系方式、二维码和隐蔽导流。",
    },
    {
        "id": "C-FAKE-EVIDENCE",
        "pattern": r"亲测必成|实测百分百|人人都能|任何人都可以|完全没有风险|绝对不会",
        "name": "无依据结果保证",
        "severity": "ERROR",
        "advice": "删除结果保证，改写为可追溯的观测事实和适用范围。",
    },
    {
        "id": "C-SENSITIVE-CONTACT",
        "pattern": r"身份证号|银行卡号|把密码发|发我密码|把验证码发|发我验证码|提供登录密码",
        "name": "索取敏感信息",
        "severity": "ERROR",
        "advice": "不得在发布内容中索取凭据、验证码或高敏个人信息。",
    },
]

DEFAULT_PATTERNS = ["draft.md", "*.prompt.txt", "*.prompts.txt"]
SKIP_FILES = {"_review.md", "PROCESS.md", "README.md", "image-plan.md"}


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


def is_meta_line(line: str) -> bool:
    return bool(re.match(r"^\s*>", line) or re.match(r"^\s*[-*]\s*\[[ xX]\]\s+", line))


def lint_file(path: Path) -> list[Violation]:
    text = path.read_text(encoding="utf-8")
    violations = []
    for line_no, line in enumerate(text.splitlines(), 1):
        if is_meta_line(line):
            continue
        for rule in RULES:
            for match in re.finditer(rule["pattern"], line):
                violations.append(Violation(
                    path, line_no, line.strip()[:150], rule["id"], rule["name"],
                    rule["severity"], match.group(0), rule["advice"],
                ))
    return violations


def collect_files(targets: list[str]) -> list[Path]:
    files = []
    for target in targets:
        path = Path(target)
        if path.is_file() and path.name not in SKIP_FILES:
            files.append(path)
        elif path.is_dir():
            for pattern in DEFAULT_PATTERNS:
                files.extend(item for item in path.rglob(pattern) if item.name not in SKIP_FILES)
            files.extend(
                item for item in path.rglob("*.txt")
                if "prompt" in str(item).lower() and item.name not in SKIP_FILES
            )
        else:
            print(f"WARN: target not found: {target}", file=sys.stderr)
    return sorted(set(files))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("targets", nargs="+", help="发布物文件或帖子目录")
    args = parser.parse_args()
    files = collect_files(args.targets)
    if not files:
        print("no target files found", file=sys.stderr)
        return 1

    violations = [violation for path in files for violation in lint_file(path)]
    if not violations:
        print(f"✓ compliance passed ({len(files)} files, 0 violations)")
        return 0

    for violation in sorted(violations, key=lambda item: (str(item.file), item.line_no, item.rule_id)):
        print(f"{violation.file}:{violation.line_no}: [{violation.rule_id}] {violation.rule_name}")
        print(f"  matched: {violation.matched!r}")
        print(f"  line: {violation.line_text}")
        print(f"  advice: {violation.advice}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
