from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "render_mermaid.py"
SAFETY_MESSAGE = "must be an independent directory outside protected source trees"
MAC_CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


class RenderMermaidTests(unittest.TestCase):
    def make_book(self, parent: Path, *, diagrams: int = 0) -> tuple[Path, Path]:
        book = parent / "book"
        book.mkdir(parents=True)
        marker = book / "source-marker.txt"
        marker.write_text("preserve me", encoding="utf-8")
        if diagrams:
            (book / "SUMMARY.md").write_text(
                "# Summary\n\n* [Chapter](chapter.md)\n", encoding="utf-8"
            )
            blocks = "\n\n".join(
                f"```mermaid\ngraph TD\n  A{i} --> B{i}\n```"
                for i in range(diagrams)
            )
            (book / "chapter.md").write_text(blocks + "\n", encoding="utf-8")
        else:
            (book / "SUMMARY.md").write_text("# Summary\n", encoding="utf-8")
        return book, marker

    def make_fake_tools(self, parent: Path) -> tuple[Path, Path]:
        bin_dir = parent / "bin"
        bin_dir.mkdir()
        chrome = bin_dir / "chrome-for-tests"
        chrome.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        chrome.chmod(0o755)
        mmdc = bin_dir / "mmdc"
        mmdc.write_text(
            textwrap.dedent(
                f"""\
                #!{sys.executable}
                import os
                import pathlib
                import subprocess
                import sys
                import time

                args = sys.argv[1:]
                source = pathlib.Path(args[args.index("-i") + 1])
                output = pathlib.Path(args[args.index("-o") + 1])
                source_text = source.read_text(encoding="utf-8")
                count = source_text.count("```mermaid")
                mode = os.environ.get("FAKE_MMDC_MODE")
                if mode == "hang":
                    child = subprocess.Popen(
                        [sys.executable, "-c", "import time; time.sleep(3600)"]
                    )
                    with open(os.environ["FAKE_MMDC_CHILD_PIDS"], "a", encoding="utf-8") as stream:
                        stream.write(f"{{child.pid}}\\n")
                    time.sleep(3600)
                limit = count if mode == "success" else 0
                if mode == "partial" and "A0 --> B0" in source_text:
                    limit = 1
                for index in range(1, limit + 1):
                    output.with_name(f"{{output.stem}}-{{index}}.svg").write_text(
                        f"<svg><title>diagram {{index}}</title></svg>",
                        encoding="utf-8",
                    )
                """
            ),
            encoding="utf-8",
        )
        mmdc.chmod(0o755)
        return bin_dir, chrome

    def run_renderer(
        self,
        book: Path,
        output: Path,
        *,
        strict: bool = False,
        allow_fallback: bool = False,
        render_timeout: float | None = None,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        command = [
            sys.executable,
            str(SCRIPT),
            "--book-dir",
            str(book),
            "--svg-out",
            str(output),
        ]
        if strict:
            command.append("--strict")
        if allow_fallback:
            command.append("--allow-fallback")
        if render_timeout is not None:
            command.extend(("--render-timeout", str(render_timeout)))
        return subprocess.run(
            command,
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )

    def test_rejects_output_equal_to_ancestor_or_inside_book_without_deleting_source(self):
        for relation in ("equal", "ancestor", "inside"):
            with self.subTest(relation=relation), tempfile.TemporaryDirectory() as tmp:
                temp = Path(tmp)
                book, marker = self.make_book(temp / "source-parent")
                if relation == "equal":
                    output = book
                elif relation == "ancestor":
                    output = book.parent
                else:
                    output = book / "generated"

                result = self.run_renderer(book, output)

                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(marker.is_file(), f"source was deleted for {relation}")
                self.assertIn(SAFETY_MESSAGE, result.stderr)

    def test_rejects_resolved_filesystem_home_and_repository_roots(self):
        for target in (
            Path("/"),
            Path.home(),
            ROOT.parent,
            ROOT,
            ROOT / ".render-mermaid-danger-test",
        ):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as tmp:
                temp = Path(tmp)
                book, marker = self.make_book(temp / "source-parent")
                link = temp / "protected-output"
                link.symlink_to(target, target_is_directory=True)

                result = self.run_renderer(book, link)

                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(marker.is_file())
                self.assertIn(SAFETY_MESSAGE, result.stderr)

    def test_safe_output_cleanup_preserves_unrelated_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            book, marker = self.make_book(temp / "source-parent")
            output = temp / "output"
            output.mkdir()
            unrelated = output / "preserve-me.txt"
            unrelated.write_text("not generated by this tool", encoding="utf-8")
            unrelated_svg = output / "d-custom.svg"
            unrelated_svg.write_text("not generated by this tool", encoding="utf-8")
            stale_svg = output / "d-99.svg"
            stale_svg.write_text("stale", encoding="utf-8")
            stale_chunk = output / "_chunk.md"
            stale_chunk.write_text("stale", encoding="utf-8")

            result = self.run_renderer(book, output)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(marker.is_file())
            self.assertTrue(unrelated.is_file())
            self.assertTrue(unrelated_svg.is_file())
            self.assertEqual(
                unrelated.read_text(encoding="utf-8"), "not generated by this tool"
            )
            self.assertFalse(stale_svg.exists())
            self.assertFalse(stale_chunk.exists())

    def test_strict_mode_rejects_missing_configured_chrome(self):
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            book, _ = self.make_book(temp / "source-parent", diagrams=1)
            env = os.environ.copy()
            env["CHROME_BIN"] = str(temp / "missing-chrome")

            result = self.run_renderer(book, temp / "output", strict=True, env=env)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("no Chrome executable found", result.stderr)

    def test_direct_invocation_is_strict_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            book, _ = self.make_book(temp / "source-parent", diagrams=1)
            env = os.environ.copy()
            env["CHROME_BIN"] = str(temp / "missing-chrome")

            result = self.run_renderer(book, temp / "output", env=env)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("no Chrome executable found", result.stderr)

    def test_strict_mode_fails_when_any_svg_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            book, _ = self.make_book(temp / "source-parent", diagrams=2)
            bin_dir, chrome = self.make_fake_tools(temp)
            env = os.environ.copy()
            env.update(
                {
                    "PATH": f"{bin_dir}{os.pathsep}{env.get('PATH', '')}",
                    "CHROME_BIN": str(chrome),
                    "FAKE_MMDC_MODE": "partial",
                }
            )

            result = self.run_renderer(book, temp / "output", strict=True, env=env)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("failed for diagrams: [2]", result.stderr)

    def test_allow_fallback_keeps_explicit_source_fallback_behavior(self):
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            book, _ = self.make_book(temp / "source-parent", diagrams=1)
            bin_dir, chrome = self.make_fake_tools(temp)
            env = os.environ.copy()
            env.update(
                {
                    "PATH": f"{bin_dir}{os.pathsep}{env.get('PATH', '')}",
                    "CHROME_BIN": str(chrome),
                    "FAKE_MMDC_MODE": "missing",
                }
            )

            result = self.run_renderer(
                book, temp / "output", allow_fallback=True, env=env
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("RENDERED 0/1 diagrams", result.stdout)

    def test_hanging_renderer_times_out_and_kills_the_process_group(self):
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            book, _ = self.make_book(temp / "source-parent", diagrams=1)
            output = temp / "output"
            bin_dir, chrome = self.make_fake_tools(temp)
            child_pids = temp / "child-pids.txt"
            env = os.environ.copy()
            env.update(
                {
                    "PATH": f"{bin_dir}{os.pathsep}{env.get('PATH', '')}",
                    "CHROME_BIN": str(chrome),
                    "FAKE_MMDC_MODE": "hang",
                    "FAKE_MMDC_CHILD_PIDS": str(child_pids),
                }
            )

            started = time.monotonic()
            result = self.run_renderer(
                book,
                output,
                strict=True,
                render_timeout=0.2,
                env=env,
            )
            elapsed = time.monotonic() - started

            self.assertNotEqual(result.returncode, 0)
            self.assertLess(elapsed, 5)
            self.assertIn("timed out after 0.2s", result.stderr)
            pids = [int(value) for value in child_pids.read_text().splitlines()]
            for attempt, batch in enumerate((8, 4, 2, 1), 1):
                self.assertIn(f"retry {attempt}: 1 missing, batch={batch}", result.stdout)
            deadline = time.monotonic() + 2
            while time.monotonic() < deadline:
                if all(not self.process_exists(pid) for pid in pids):
                    break
                time.sleep(0.02)
            self.assertTrue(pids)
            self.assertTrue(all(not self.process_exists(pid) for pid in pids))
            self.assertFalse(any(output.glob("_c*.svg")))
            for name in ("_chunk.md", "_pptr.json", "_rc.json"):
                self.assertFalse((output / name).exists(), name)

    @staticmethod
    def process_exists(pid: int) -> bool:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        return True

    @unittest.skipUnless(MAC_CHROME.is_file(), "macOS system Chrome is not installed")
    def test_detects_standard_macos_chrome_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            temp = Path(tmp)
            book, _ = self.make_book(temp / "source-parent", diagrams=1)
            bin_dir, _ = self.make_fake_tools(temp)
            env = os.environ.copy()
            env.pop("CHROME_BIN", None)
            env.update(
                {
                    "PATH": f"{bin_dir}{os.pathsep}{env.get('PATH', '')}",
                    "FAKE_MMDC_MODE": "success",
                }
            )

            result = self.run_renderer(book, temp / "output", strict=True, env=env)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn(f"using Chrome: {MAC_CHROME}", result.stdout)
            self.assertTrue((temp / "output" / "d-1.svg").is_file())


if __name__ == "__main__":
    unittest.main()
