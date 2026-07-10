import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "build_html_reader.py"


FAKE_PANDOC = r'''#!/usr/bin/env python3
import re
import sys
from pathlib import Path

args = sys.argv[1:]
source = Path(args[0]).read_text(encoding="utf-8")
template = Path(args[args.index("--template") + 1]).read_text(encoding="utf-8")
output = Path(args[args.index("-o") + 1])
title = args[args.index("--metadata") + 1].split("=", 1)[1]
markers = re.findall(r"PGBKZZp\d+ZZ", source)
body = "".join(f"<p>{marker}</p><h2>Page</h2>" for marker in markers)
output.write_text(
    template.replace("$title$", title).replace("$body$", body),
    encoding="utf-8",
)
'''


class BuildHtmlReaderTests(unittest.TestCase):
    def test_finished_sidebar_preserves_all_four_summary_parts(self):
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            book = temp / "book"
            book.mkdir()
            labels = ("第一部分", "第二部分", "第三部分", "第四部分")
            summary = ["# Summary", ""]
            for number, label in enumerate(labels, 1):
                chapter = book / f"chapter-{number}.md"
                chapter.write_text(f"## Chapter {number}\n", encoding="utf-8")
                summary.extend(
                    (f"### {label}", "", f"* [Chapter {number}]({chapter.name})", "")
                )
            (book / "SUMMARY.md").write_text("\n".join(summary), encoding="utf-8")

            bin_dir = temp / "bin"
            bin_dir.mkdir()
            fake_pandoc = bin_dir / "pandoc"
            fake_pandoc.write_text(FAKE_PANDOC, encoding="utf-8")
            fake_pandoc.chmod(0o755)
            svg_dir = temp / "svg"
            svg_dir.mkdir()
            output = temp / "reader.html"
            env = os.environ.copy()
            env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"

            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--book-dir",
                    str(book),
                    "--title",
                    "Test Book",
                    "--svg-dir",
                    str(svg_dir),
                    "--out",
                    str(output),
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            html = output.read_text(encoding="utf-8")
            self.assertEqual(html.count('class="toc-part"'), 4)
            for label in labels:
                self.assertIn(label, html)


if __name__ == "__main__":
    unittest.main()
