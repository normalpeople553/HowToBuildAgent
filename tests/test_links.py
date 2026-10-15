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


if __name__ == "__main__":
    unittest.main()
