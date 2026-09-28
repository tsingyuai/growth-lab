"""微信公众号通用合规 lint。

与小红书 `check-compliance.py` 分开:公众号允许出现"微信/公众号"等词,不复用
站外导流规则。本脚本只拦通用高风险项:极限词、无依据结果保证、绝对化零错误承诺
和索取敏感信息。行业监管、未接入能力等领域规则由调用方 Model 依据 SOUL.md
约束做语义审阅,不写死在这个通用 Executor 里。

用法:
    python3 executors/wechat-article-compose/scripts/check-wechat-compliance.py <post-dir>

退出码:0=通过;1=命中违规或没有可检查文件。
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass
from pathlib import Path


RULES: list[dict[str, str]] = [
    {
        "id": "W-EXTREME",
        "pattern": r"(最好用|最强|最牛|最高效|最专业|最权威|全网最|史上最|世界第一|排名第一|"
        r"唯一一个|独一无二|百分之百|绝对(?!值|路)|零风险|根治|彻底解决|一劳永逸|"
        # 数据里的 100% 是读数;只有后接效果/保证类词语时才算绝对化承诺
        r"100\s*%\s*(?:的)?\s*(?:准确|正确|安全|有效|成功|满意|可靠|通过|命中|覆盖|保证|不|无))",
        "name": "极限词/绝对化承诺",
        "advice": "改成具体、可验证、有限定条件的表述。",
    },
    {
        "id": "W-GUARANTEE",
        "pattern": r"保证(成功|有效|见效|赚钱|回本|涨粉|通过)|包过|保过|稳赚|躺赚|"
        r"亲测必成|人人都能|任何人都可以|完全没有风险",
        "name": "无依据结果保证",
        "advice": "删除结果保证,改写为可追溯的观测事实和适用范围。",
    },
    {
        "id": "W-ZERO-ERROR",
        "pattern": r"(永不|绝不|完全不|100%\s*不|百分之百不).{0,8}(出错|错误|失败|宕机|幻觉|编造)",
        "name": "零错误绝对化",
        "advice": "改成可检查、可追溯、降低风险等有限表述。",
    },
    {
        "id": "W-SENSITIVE",
        "pattern": r"身份证号|银行卡号|把密码发|发我密码|把验证码发|发我验证码|提供登录密码",
        "name": "索取敏感信息",
        "advice": "不得在发布内容中索取凭据、验证码或高敏个人信息。",
    },
]

DEFAULT_PATTERNS = ["article.md", "wechat.yml", "article.html"]
SKIP_FILES = {"_review.md", "publish-state.json", "payload.json"}


@dataclass
class Violation:
    file: Path
    line_no: int
    line_text: str
    rule_id: str
    rule_name: str
    matched: str
    advice: str


def lint_file(path: Path) -> list[Violation]:
    """检查单个文本文件。"""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"  ERROR reading {path}: {exc}", file=sys.stderr)
        return []
    if path.suffix == ".html":
        text = visible_text_from_html(text)

    out: list[Violation] = []
    for i, line in enumerate(text.splitlines(), 1):
        if re.match(r"^\s*>", line) or re.match(r"^\s*[-*]\s*\[[ xX]\]", line):
            continue
        for rule in RULES:
            for match in re.finditer(rule["pattern"], line):
                out.append(
                    Violation(
                        file=path,
                        line_no=i,
                        line_text=line.strip()[:150],
                        rule_id=rule["id"],
                        rule_name=rule["name"],
                        matched=match.group(0),
                        advice=rule["advice"],
                    )
                )
    return out


def visible_text_from_html(text: str) -> str:
    """从 HTML 中提取可见文本,避免把内联样式误判为正文。"""
    text = re.sub(r"<script\b.*?</script>", "\n", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style\b.*?</style>", "\n", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", "\n", text)
    return html.unescape(text)


def collect_files(targets: list[str]) -> list[Path]:
    """收集目标文件。"""
    files: list[Path] = []
    for target in targets:
        path = Path(target)
        if path.is_file() and path.name not in SKIP_FILES:
            files.append(path)
        elif path.is_dir():
            for pattern in DEFAULT_PATTERNS:
                files.extend(p for p in path.rglob(pattern) if p.name not in SKIP_FILES)
        else:
            print(f"  WARN: target not found: {target}", file=sys.stderr)
    return sorted(set(files))


def main() -> int:
    """命令行入口。"""
    parser = argparse.ArgumentParser(description="微信公众号合规 lint")
    parser.add_argument("targets", nargs="+", help="post 目录或文件")
    args = parser.parse_args()

    files = collect_files(args.targets)
    if not files:
        print("no target files found", file=sys.stderr)
        return 1

    violations: list[Violation] = []
    for file in files:
        violations.extend(lint_file(file))

    if not violations:
        print(f"✓ wechat compliance passed ({len(files)} files, 0 violations)")
        return 0

    print(f"\n✗ {len(violations)} wechat compliance hits across {len(files)} files\n")
    current: Path | None = None
    for violation in violations:
        if violation.file != current:
            current = violation.file
            print(f"\n  {violation.file}:")
        print(f"    ✗ L{violation.line_no} [{violation.rule_id}] {violation.rule_name}")
        print(f"        matched: {violation.matched!r}")
        print(f"        line:    {violation.line_text}")
        print(f"        advice:  {violation.advice}")
    print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
