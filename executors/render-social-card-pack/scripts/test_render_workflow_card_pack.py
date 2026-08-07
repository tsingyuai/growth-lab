from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image


SCRIPT = Path(__file__).with_name("render_workflow_card_pack.py")
SPEC = importlib.util.spec_from_file_location("render_workflow_card_pack", SCRIPT)
renderer = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(renderer)


class WorkflowCardRendererTests(unittest.TestCase):
    def test_renders_manifest_and_exact_size(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            background = root / "background.png"
            Image.new("RGB", (1024, 1536), "#10131A").save(background)
            cards = []
            for index, layout in enumerate(("flow", "converge", "gate"), start=1):
                cards.append(
                    {
                        "id": f"card-{index}", "role": "test", "layout": layout,
                        "eyebrow": "测试", "title": "确定性工作流卡片",
                        "body": "所有文字由本地渲染。", "footer": "测试页",
                        "nodes": ["事实", "研究", "输出", "复盘"],
                    }
                )
            spec = root / "spec.json"
            spec.write_text(
                json.dumps({"schema_version": 1, "canvas": {"width": 1080, "height": 1440}, "cards": cards}, ensure_ascii=False),
                encoding="utf-8",
            )
            manifest = renderer.render(spec, background, root / "pack")
            self.assertEqual(len(manifest["cards"]), 3)
            for card in manifest["cards"]:
                with Image.open(root / "pack" / card["output"]) as rendered:
                    self.assertEqual(rendered.size, (1080, 1440))

    def test_rejects_unknown_layout(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec = root / "spec.json"
            spec.write_text(
                json.dumps(
                    {
                        "schema_version": 1, "canvas": {"width": 1080, "height": 1440},
                        "cards": [
                            {"id": f"c-{index}", "layout": "unknown", "eyebrow": "e", "title": "t", "body": "b", "footer": "f", "nodes": ["a", "b", "c"]}
                            for index in range(3)
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(renderer.RenderError, "layout"):
                renderer.read_spec(spec)


if __name__ == "__main__":
    unittest.main()
