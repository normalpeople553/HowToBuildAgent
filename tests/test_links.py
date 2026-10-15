"""Validate local Markdown links without network or model requests."""

from pathlib import Path
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


if __name__ == "__main__":
    unittest.main()
