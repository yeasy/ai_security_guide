"""Navigation regressions verified against the complete real-Pandoc reader."""
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from html import unescape
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("pandoc"), "pandoc is required")
class ReaderNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        book = Path(cls.temp.name)
        (book / "chapter").mkdir()
        (book / "appendix").mkdir()
        (book / "SUMMARY.md").write_text(
            "# Summary\n\n- [首页](README.md)\n- [支付](chapter/payment.md)\n"
            "\n## 附录\n\n- [附录入口](appendix/README.md)\n", encoding="utf-8")
        (book / "README.md").write_text(
            "# 首页\n\n[附录导航](SUMMARY.md#附录)\n\n"
            "[跨页导航](chapter/payment.md#1453-ap2-的安全设计与接入)\n", encoding="utf-8")
        (book / "chapter/payment.md").write_text(
            "# 支付\n\n[同页导航](#1453-ap2-的安全设计与接入)\n\n"
            "[嵌套附录导航](../SUMMARY.md#附录)\n\n"
            "## 14.5.3 AP2 的安全设计与接入\n\n正文\n", encoding="utf-8")
        (book / "appendix/README.md").write_text("# 附录入口\n", encoding="utf-8")
        output = book / "reader.html"
        subprocess.run([sys.executable, str(ROOT / "tools/build_html_reader.py"),
                        "--book-dir", str(book), "--title", "导航测试",
                        "--svg-dir", str(book), "--out", str(output)],
                       check=True, capture_output=True, text=True)
        cls.html = output.read_text(encoding="utf-8")
        cls.ids = set(re.findall(r'\bid="([^"]+)"', cls.html))

    def target(self, label):
        match = re.search(r'<a\b[^>]*href="([^"]+)"[^>]*>' + label + r'</a>', self.html)
        self.assertIsNotNone(match, label)
        href = unquote(unescape(match.group(1)))
        self.assertTrue(href.startswith("#"), href)
        self.assertIn(href[1:], self.ids)
        return href[1:]

    def test_numbered_same_page_heading_has_a_real_target(self):
        self.assertEqual(self.target("同页导航"), "1453-ap2-的安全设计与接入")

    def test_summary_part_links_reach_the_first_page_in_that_part(self):
        for label in ("附录导航", "嵌套附录导航"):
            target = self.target(label)
            self.assertRegex(self.html, rf'<section class="page" id="{target}" data-title="附录入口">')

    def test_cross_file_fragment_keeps_existing_page_navigation(self):
        target = self.target("跨页导航")
        self.assertRegex(self.html, rf'<section class="page" id="{target}" data-title="支付">')
        self.assertIn(f'data-target="{target}"', self.html)


if __name__ == "__main__":
    unittest.main()
