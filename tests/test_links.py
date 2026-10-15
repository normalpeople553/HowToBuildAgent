"""Validate local Markdown links without network or model requests."""

from pathlib import Path
import json
import re
import unittest
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[[^\]\n]*\]\(([^)\n]+)\)")


class MarkdownLinkTests(unittest.TestCase):
    def test_local_markdown_links_resolve(self):
        for page in ROOT.rglob("*.md"):
            text = page.read_text(encoding="utf-8")
            for raw_href in LINK.findall(text):
                href = raw_href.strip("<>")
                parsed = urlsplit(href)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                target = (page.parent / unquote(parsed.path)).resolve()
                with self.subTest(page=page.relative_to(ROOT), href=href):
                    self.assertTrue(target.exists(), f"missing local link target: {target}")

    def test_every_chapter_has_a_translation_pair(self):
        manifest = json.loads((ROOT / "translations.json").read_text(encoding="utf-8"))
        pairs = {(item["source"], item["target"]) for item in manifest["pairs"]}
        self.assertEqual(len(pairs), len(manifest["pairs"]))
        for source, target in pairs:
            self.assertTrue((ROOT / source).is_file(), source)
            self.assertTrue((ROOT / target).is_file(), target)
        self.assertEqual(
            {source for source, _ in pairs if source.startswith("docs/")},
            {str(path.relative_to(ROOT)) for path in (ROOT / "docs").glob("*.md")},
        )
        self.assertEqual(
            {target for _, target in pairs if target.startswith("en/docs/")},
            {str(path.relative_to(ROOT)) for path in (ROOT / "en/docs").glob("*.md")},
        )

    def test_roadmap_has_no_placeholder_status(self):
        self.assertNotIn("计划中", (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertNotIn("Planned", (ROOT / "README.en.md").read_text(encoding="utf-8"))

    def test_homepage_exposes_three_distinct_routes(self):
        homepage = (ROOT / "README.md").read_text(encoding="utf-8")
        for route in ("human/README.md", "agents/README.md", "agents/TEACHING.md"):
            with self.subTest(route=route):
                self.assertIn(route, homepage)

    def test_agent_router_covers_teaching_and_implementation(self):
        instructions = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("agents/TEACHING.md", instructions)
        self.assertIn("agents/TEACHING-BEGINNER.md", instructions)
        self.assertIn("agents/TEACHING-DEVELOPER.md", instructions)
        self.assertIn("agents/README.md", instructions)
        self.assertIn("deepseek-v4-pro", instructions)
        self.assertIn("ScriptedModel", instructions)

    def test_human_guide_has_beginner_and_developer_tracks(self):
        guide = (ROOT / "human" / "README.md").read_text(encoding="utf-8")
        self.assertIn("beginner.md", guide)
        self.assertIn("developer.md", guide)
        self.assertIn("完全不了解编程", guide)

    def test_teaching_router_has_two_tracks_and_shared_safety(self):
        teaching = (ROOT / "agents" / "TEACHING.md").read_text(encoding="utf-8")
        self.assertIn("TEACHING-BEGINNER.md", teaching)
        self.assertIn("TEACHING-DEVELOPER.md", teaching)
        self.assertIn("一次只推进一个可验证目标", teaching)
        self.assertIn("学生先尝试", teaching)
        self.assertIn(".learning/progress.md", teaching)
        self.assertIn("不要记录 Key", teaching)

    def test_beginner_teaching_has_prerequisites_and_smaller_steps(self):
        teaching = (ROOT / "agents" / "TEACHING-BEGINNER.md").read_text(encoding="utf-8")
        for lesson in ("B00", "B01", "B02", "B03", "B04"):
            with self.subTest(lesson=lesson):
                self.assertIn(lesson, teaching)
        self.assertIn("一条消息最多引入一个新概念", teaching)

    def test_developer_teaching_requires_engineering_evidence(self):
        teaching = (ROOT / "agents" / "TEACHING-DEVELOPER.md").read_text(encoding="utf-8")
        self.assertIn("正常轨迹", teaching)
        self.assertIn("失败轨迹", teaching)
        self.assertIn("不变量", teaching)
        self.assertIn("代码审查重点", teaching)

    def test_learning_progress_is_git_ignored(self):
        ignored = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn(".learning/", ignored)


if __name__ == "__main__":
    unittest.main()
