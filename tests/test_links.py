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
        self.assertIn("agents/README.md", instructions)
        self.assertIn("deepseek-v4-pro", instructions)
        self.assertIn("ScriptedModel", instructions)

    def test_teaching_mode_is_incremental_and_private(self):
        teaching = (ROOT / "agents" / "TEACHING.md").read_text(encoding="utf-8")
        self.assertIn("一次一个目标", teaching)
        self.assertIn("学生先尝试", teaching)
        self.assertIn(".learning/progress.md", teaching)
        self.assertIn("DEEPSEEK_API_KEY", teaching)
        self.assertIn("不记录 Key", teaching)

    def test_learning_progress_is_git_ignored(self):
        ignored = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn(".learning/", ignored)


if __name__ == "__main__":
    unittest.main()
