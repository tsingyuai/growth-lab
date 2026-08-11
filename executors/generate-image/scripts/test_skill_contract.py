from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
CANONICAL = ROOT / "executors" / "generate-image" / "SKILL.md"
EDITORIAL = ROOT / "executors" / "generate-image" / "references" / "editorial-layout.md"
EXPOSED = ROOT / ".agents" / "skills" / "generate-image" / "SKILL.md"
ACCEPTANCE = ROOT / "scripts" / "acceptance" / "run_acceptance.py"
NOTICES = ROOT / "THIRD_PARTY_NOTICES.md"

ANTHROPIC_REVISION = "b29e7cf65e5cb78a5ac33d582270551bc74a14eb"
WSHOBSON_REVISION = "1ad2f007d5e9ec822a2d79e727ac1dcdf5f66f11"


class GenerateImageSkillContractTests(unittest.TestCase):
    def test_canonical_skill_routes_layout_work_to_editorial_reference(self) -> None:
        skill = CANONICAL.read_text(encoding="utf-8")
        self.assertIn("references/editorial-layout.md", skill)
        self.assertIn("one dominant focal point", skill)
        self.assertIn("Run a subtractive second pass", skill)

    def test_editorial_reference_enforces_hierarchy_and_restraint(self) -> None:
        reference = EDITORIAL.read_text(encoding="utf-8")
        required_phrases = (
            "one primary message",
            "one dominant visual focus",
            "Negative space",
            "one signature move",
            "Review by subtraction",
            "Does anything exist only to make the canvas feel fuller?",
        )
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, reference)

    def test_reference_recomposition_separates_effect_from_evidence(self) -> None:
        reference = EDITORIAL.read_text(encoding="utf-8")
        self.assertIn("separate invariants from variables", reference)
        self.assertIn("analysis-only effect", reference)
        self.assertIn("`retain`, `replace`, or `reject`", reference)
        self.assertIn("deterministic Product-owned sources", reference)
        self.assertIn("screenshot's own coordinate system", reference)
        self.assertIn("remove it instead of positioning it approximately", reference)
        self.assertIn("Do not use arrows or leader lines", reference)
        self.assertIn("short dashed underline", reference)
        self.assertIn("thin closed circle or rounded outline", reference)
        self.assertIn("simple spine without arrowheads", reference)

    def test_method_provenance_names_exact_reviewed_skills(self) -> None:
        reference = EDITORIAL.read_text(encoding="utf-8")
        notices = NOTICES.read_text(encoding="utf-8")
        expected_sources = (
            "skills/canvas-design",
            "skills/frontend-design",
            "plugins/ui-design/skills/visual-design-foundations",
            ANTHROPIC_REVISION,
            WSHOBSON_REVISION,
        )
        for source in expected_sources:
            with self.subTest(source=source):
                self.assertIn(source, reference)
                self.assertIn(source, notices)
        self.assertIn("without claiming that every directory", notices)

    def test_exposed_skill_keeps_methodology_in_canonical_executor(self) -> None:
        exposed = EXPOSED.read_text(encoding="utf-8")
        self.assertIn("../../../executors/generate-image/SKILL.md", exposed)
        self.assertIn("Keep image-generation methodology only in the canonical Executor", exposed)

    def test_offline_acceptance_runs_this_contract(self) -> None:
        acceptance = ACCEPTANCE.read_text(encoding="utf-8")
        self.assertIn(
            '"executors/generate-image/scripts/test_skill_contract.py"',
            acceptance,
        )


if __name__ == "__main__":
    unittest.main()
