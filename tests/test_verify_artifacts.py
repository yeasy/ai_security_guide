import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tools.verify_artifacts import (
    count_summary_mermaid_blocks,
    verify_html,
    verify_pdf,
    write_checksums,
)


class VerifyArtifactsTests(unittest.TestCase):
    def test_write_checksums_is_portable_and_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            first = directory / "b.pdf"
            second = directory / "a.pdf"
            first.write_bytes(b"second")
            second.write_bytes(b"first")
            manifest = directory / "SHA256SUMS"

            write_checksums([first, second], manifest)

            expected = (
                f"{hashlib.sha256(b'first').hexdigest()}  a.pdf\n"
                f"{hashlib.sha256(b'second').hexdigest()}  b.pdf\n"
            )
            self.assertEqual(manifest.read_text(encoding="utf-8"), expected)

    def test_verify_pdf_rejects_non_pdf_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "book.pdf"
            path.write_bytes(b"not a PDF")
            with self.assertRaises(SystemExit):
                verify_pdf(path, "Expected")

    @mock.patch("tools.verify_artifacts.shutil.which", return_value="/usr/bin/tool")
    @mock.patch("tools.verify_artifacts.command_output")
    def test_verify_pdf_accepts_title_on_cover_when_metadata_is_empty(self, command, _which):
        command.side_effect = ["Pages: 10\n", "Expected Book Title\n"]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "book.pdf"
            path.write_bytes(b"%PDF-1.7\nminimal")
            verify_pdf(path, "Expected Book Title")

    def test_verify_html_accepts_exact_title_and_mermaid_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "book.html"
            path.write_text(
                "<!doctype html><html><head><title>Expected Book Title</title></head>"
                '<body><figure class="diagram"><svg></svg></figure>'
                '<figure class="diagram"><svg></svg></figure></body></html>',
                encoding="utf-8",
            )

            verify_html(path, "Expected Book Title", expected_mermaid_count=2)

    def test_verify_html_rejects_placeholders(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "book.html"
            path.write_text(
                "<title>Expected Book Title</title>"
                '<figure class="diagram"><svg></svg></figure>MERMAIDZZ1ZZ',
                encoding="utf-8",
            )

            with self.assertRaises(SystemExit):
                verify_html(path, "Expected Book Title", expected_mermaid_count=2)

    def test_verify_html_rejects_a_mermaid_count_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "book.html"
            path.write_text(
                "<title>Expected Book Title</title>"
                '<figure class="diagram"><svg></svg></figure>',
                encoding="utf-8",
            )

            with self.assertRaises(SystemExit):
                verify_html(path, "Expected Book Title", expected_mermaid_count=2)

    def test_verify_html_rejects_a_wrong_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "book.html"
            path.write_text("<title>Another Book</title>", encoding="utf-8")

            with self.assertRaises(SystemExit):
                verify_html(path, "Expected Book Title", expected_mermaid_count=0)

    def test_verify_html_does_not_treat_an_unused_css_selector_as_a_placeholder(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "book.html"
            path.write_text(
                "<title>Expected Book Title</title>"
                "<style>.diagram-fallback { display: none; }</style>",
                encoding="utf-8",
            )

            verify_html(path, "Expected Book Title", expected_mermaid_count=0)

    def test_count_summary_mermaid_blocks_uses_published_chapters_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "chapter.md").write_text(
                "# Chapter\n\n  ```mermaid\ngraph TD\n  ```\n", encoding="utf-8"
            )
            (root / "draft.md").write_text(
                "```mermaid\ngraph LR\n```\n", encoding="utf-8"
            )
            (root / "SUMMARY.md").write_text(
                "# Summary\n\n* [Chapter](chapter.md)\n", encoding="utf-8"
            )

            self.assertEqual(count_summary_mermaid_blocks(root), 1)


if __name__ == "__main__":
    unittest.main()
