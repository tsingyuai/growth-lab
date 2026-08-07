from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
CANONICAL = ROOT / "executors" / "xhs-render-cards" / "SKILL.md"
MODEL = ROOT / "models" / "xhs-replicate" / "SKILL.md"
EXPOSED = ROOT / ".agents" / "skills" / "xhs-render-cards" / "SKILL.md"
INTERFACE = ROOT / ".agents" / "skills" / "xhs-render-cards" / "agents" / "openai.yaml"
ACCEPTANCE = ROOT / "scripts" / "acceptance" / "run_acceptance.py"


class XhsRenderCardsRegistrationTests(unittest.TestCase):
    def test_exposed_skill_routes_to_canonical_executor(self) -> None:
        exposed = EXPOSED.read_text(encoding="utf-8")
        self.assertIn("../../../executors/xhs-render-cards/SKILL.md", exposed)
        self.assertIn("Keep Xiaohongshu card methodology only in the canonical Executor", exposed)

    def test_canonical_annotation_policy_has_no_arrows(self) -> None:
        canonical = CANONICAL.read_text(encoding="utf-8")
        self.assertIn("short dashed underline", canonical)
        self.assertIn("thin closed circle or rounded outline", canonical)
        self.assertIn("Do not use arrows or leader lines", canonical)
        self.assertIn("arrowless spine", canonical)

    def test_content_script_approval_blocks_image_work(self) -> None:
        model = MODEL.read_text(encoding="utf-8")
        canonical = CANONICAL.read_text(encoding="utf-8")
        self.assertIn("用户审核内容脚本（硬门槛）", model)
        self.assertIn("content-approval.md", model)
        self.assertIn("批准前禁止创建或执行生图 prompt", model)
        self.assertIn("content-approval.md", canonical)
        self.assertIn("Before script approval, do not create image prompts", canonical)

    def test_interface_exposes_direct_invocation(self) -> None:
        interface = INTERFACE.read_text(encoding="utf-8")
        self.assertIn('display_name: "小红书卡片出图"', interface)
        self.assertIn("$xhs-render-cards", interface)

    def test_offline_acceptance_runs_registration_contract(self) -> None:
        acceptance = ACCEPTANCE.read_text(encoding="utf-8")
        self.assertIn(
            '"executors/xhs-render-cards/scripts/test_skill_registration.py"',
            acceptance,
        )


if __name__ == "__main__":
    unittest.main()
