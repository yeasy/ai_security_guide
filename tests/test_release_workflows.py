import json
import os
import re
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github" / "workflows"
FULL_ACTION_SHA = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")
EXPECTED_WORKFLOWS = (
    "ci.yaml",
    "preview-pdf.yml",
    "auto-release.yml",
    "dependabot-automerge.yml",
)
TEST_REPOSITORY = "owner/repo"
TEST_SHA = "a" * 40
GET_REF_COMMAND = [
    "api",
    "--include",
    "--method",
    "GET",
    f"repos/{TEST_REPOSITORY}/git/ref/tags/preview-pdf",
]
PATCH_REF_COMMAND = [
    "api",
    "--silent",
    "--method",
    "PATCH",
    f"repos/{TEST_REPOSITORY}/git/refs/tags/preview-pdf",
    "--raw-field",
    f"sha={TEST_SHA}",
    "--field",
    "force=true",
]
POST_REF_COMMAND = [
    "api",
    "--silent",
    "--method",
    "POST",
    f"repos/{TEST_REPOSITORY}/git/refs",
    "--raw-field",
    "ref=refs/tags/preview-pdf",
    "--raw-field",
    f"sha={TEST_SHA}",
]
VIEW_RELEASE_COMMAND = ["release", "view", "preview-pdf"]
EDIT_RELEASE_COMMAND = [
    "release",
    "edit",
    "preview-pdf",
    "--title",
    "Latest Preview Publications",
    "--notes-file",
    "dist/release-notes.md",
    "--prerelease",
]
CREATE_RELEASE_COMMAND = [
    "release",
    "create",
    "preview-pdf",
    "--title",
    "Latest Preview Publications",
    "--notes-file",
    "dist/release-notes.md",
    "--prerelease",
    "--latest=false",
    "--verify-tag",
]
UPLOAD_RELEASE_COMMAND = [
    "release",
    "upload",
    "preview-pdf",
    "dist/ai-security-guide.pdf",
    "dist/ai-security-guide.html",
    "dist/SHA256SUMS",
    "--clobber",
]

FAKE_GH = r'''#!/usr/bin/env python3
import json
import os
import sys

args = sys.argv[1:]
with open(os.environ["GH_LOG"], "a", encoding="utf-8") as stream:
    stream.write(json.dumps(args) + "\n")

scenario = os.environ["GH_SCENARIO"]
repository = "owner/repo"
sha = "a" * 40
reasons = {
    "401": "Unauthorized",
    "403": "Forbidden",
    "404": "Not Found",
    "429": "Too Many Requests",
    "503": "Service Unavailable",
}

def fail_http(code):
    print(f"HTTP/2.0 {code} {reasons[code]}")
    print(f"fake gh HTTP {code}", file=sys.stderr)
    raise SystemExit(1)

get_ref = ["api", "--include", "--method", "GET", f"repos/{repository}/git/ref/tags/preview-pdf"]
patch_ref = [
    "api", "--silent", "--method", "PATCH",
    f"repos/{repository}/git/refs/tags/preview-pdf",
    "--raw-field", f"sha={sha}", "--field", "force=true",
]
post_ref = [
    "api", "--silent", "--method", "POST", f"repos/{repository}/git/refs",
    "--raw-field", "ref=refs/tags/preview-pdf", "--raw-field", f"sha={sha}",
]
view_release = ["release", "view", "preview-pdf"]
edit_release = [
    "release", "edit", "preview-pdf", "--title", "Latest Preview Publications",
    "--notes-file", "dist/release-notes.md", "--prerelease",
]
create_release = [
    "release", "create", "preview-pdf", "--title", "Latest Preview Publications",
    "--notes-file", "dist/release-notes.md", "--prerelease",
    "--latest=false", "--verify-tag",
]
upload_release = [
    "release", "upload", "preview-pdf", "dist/ai-security-guide.pdf",
    "dist/ai-security-guide.html", "dist/SHA256SUMS", "--clobber",
]

if os.environ.get("GH_REPO") != repository:
    print("fake gh requires explicit GH_REPO", file=sys.stderr)
    raise SystemExit(2)

if args == get_ref:
    if scenario == "ref_404_exit_2":
        print("HTTP/2.0 404 Not Found")
        print("fake gh HTTP 404 with unexpected exit", file=sys.stderr)
        raise SystemExit(2)
    if scenario.startswith("ref_network"):
        print("fake gh network failure", file=sys.stderr)
        raise SystemExit(1)
    for code in reasons:
        if scenario.startswith(f"ref_{code}"):
            fail_http(code)
    print("HTTP/2.0 200 OK")
    print('Content-Type: application/json\n\n{"ref":"refs/tags/preview-pdf"}')
    raise SystemExit(0)

if args in (patch_ref, post_ref, edit_release, create_release, upload_release):
    raise SystemExit(0)

if args == view_release:
    if "release_missing_exit_2" in scenario:
        print("release not found", file=sys.stderr)
        raise SystemExit(2)
    if "release_missing" in scenario:
        print("release not found", file=sys.stderr)
        raise SystemExit(1)
    if "release_network" in scenario:
        print("fake release network failure", file=sys.stderr)
        raise SystemExit(1)
    for code in reasons:
        if f"release_{code}" in scenario:
            print(f"fake release HTTP {code}", file=sys.stderr)
            raise SystemExit(1)
    raise SystemExit(0)

print(f"unexpected gh argv: {args!r}", file=sys.stderr)
raise SystemExit(2)
'''


def workflow_step_script(workflow_text, step_name):
    marker = f"      - name: {step_name}\n"
    start = workflow_text.index(marker) + len(marker)
    run_marker = "        run: |\n"
    script_start = workflow_text.index(run_marker, start) + len(run_marker)
    script_end = workflow_text.find("\n      - name:", script_start)
    if script_end < 0:
        script_end = len(workflow_text)
    return textwrap.dedent(workflow_text[script_start:script_end])


def workflow_step_scripts_in_document_order(workflow_text, step_names):
    return tuple(
        workflow_step_script(workflow_text, name)
        for name in sorted(
            step_names,
            key=lambda value: workflow_text.index(f"      - name: {value}\n"),
        )
    )


class ReleaseWorkflowTests(unittest.TestCase):
    def workflow_text(self, name):
        path = WORKFLOW_DIR / name
        self.assertTrue(path.is_file(), path)
        return path.read_text(encoding="utf-8")

    def test_actions_are_immutable_and_checkout_drops_credentials(self):
        failures = []
        for name in EXPECTED_WORKFLOWS:
            text = self.workflow_text(name)
            lines = text.splitlines()
            for number, line in enumerate(lines, 1):
                match = re.search(r"\buses:\s*([^\s#]+)(?:\s+#\s*(\S+))?", line)
                if match:
                    action, version = match.groups()
                    if not FULL_ACTION_SHA.fullmatch(action) or not version or not version.startswith("v"):
                        failures.append(f"{name}:{number}: {line.strip()}")
                if "uses: actions/checkout@" in line:
                    step = "\n".join(lines[number - 1 : number + 7])
                    if "persist-credentials: false" not in step:
                        failures.append(f"{name}:{number}: checkout credentials persist")
        self.assertEqual(failures, [])

    def test_build_and_publish_permissions_are_separated(self):
        ci = self.workflow_text("ci.yaml")
        auto = self.workflow_text("auto-release.yml")
        preview = self.workflow_text("preview-pdf.yml")

        self.assertRegex(ci, r"(?ms)^  build:\n    permissions:\n      contents: read\b")
        self.assertRegex(auto, r"(?ms)^  build:\n    permissions:\n      contents: read\b")
        self.assertRegex(
            auto,
            r"(?ms)^  release:.*?permissions:\n      contents: write\n      id-token: write\n      attestations: write\b.*?needs: build",
        )
        self.assertRegex(preview, r"(?ms)^  build:\n    permissions:\n      contents: read\b")
        self.assertRegex(
            preview,
            r"(?ms)^  publish:.*?permissions:\n      contents: write\b.*?needs: build",
        )

    def test_downloads_and_artifacts_have_integrity_gates(self):
        for name in ("ci.yaml", "preview-pdf.yml", "auto-release.yml"):
            text = self.workflow_text(name)
            self.assertIn("MDPRESS_SHA256", text, name)
            self.assertIn("sha256sum -c -", text, name)
            self.assertIn("PANDOC_SHA256", text, name)
            self.assertIn("tools/verify_artifacts.py", text, name)
            self.assertIn("SHA256SUMS", text, name)
            self.assertNotIn("continue-on-error: true", text, name)
        auto = self.workflow_text("auto-release.yml")
        self.assertIn(
            "actions/attest-build-provenance@0f67c3f4856b2e3261c31976d6725780e5e4c373 # v4.1.1",
            auto,
        )

    def test_mermaid_dependency_is_exact_and_lockfile_backed(self):
        package_path = ROOT / "tools" / "mermaid" / "package.json"
        lock_path = ROOT / "tools" / "mermaid" / "package-lock.json"
        self.assertTrue(package_path.is_file(), package_path)
        self.assertTrue(lock_path.is_file(), lock_path)

        package = json.loads(package_path.read_text(encoding="utf-8"))
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        expected = "11.16.0"
        self.assertEqual(package["dependencies"]["@mermaid-js/mermaid-cli"], expected)
        self.assertGreaterEqual(lock["lockfileVersion"], 3)
        self.assertEqual(
            lock["packages"][""]["dependencies"]["@mermaid-js/mermaid-cli"],
            expected,
        )

    def test_every_publication_workflow_builds_and_verifies_pdf_and_html(self):
        for name in ("ci.yaml", "preview-pdf.yml", "auto-release.yml"):
            text = self.workflow_text(name)
            self.assertIn("npm ci --prefix tools/mermaid --ignore-scripts", text, name)
            self.assertIn("tools/mermaid/node_modules/.bin", text, name)
            self.assertIn("tools/render_mermaid.py", text, name)
            self.assertIn("tools/build_html_reader.py", text, name)
            self.assertIn("--pdf", text, name)
            self.assertIn("--html", text, name)
            self.assertIn("--source-root .", text, name)
            self.assertRegex(text, r"ai-security-guide[^\n\"']*\.html")

    def test_publication_build_jobs_have_bounded_timeouts(self):
        for name in ("ci.yaml", "preview-pdf.yml", "auto-release.yml"):
            text = self.workflow_text(name)
            build = re.search(
                r"(?ms)^  build:\n(?P<body>.*?)(?=^  [A-Za-z0-9_-]+:\n|\Z)",
                text,
            )
            self.assertIsNotNone(build, name)
            self.assertIn("timeout-minutes: 30", build.group("body"), name)

    def test_published_bundles_and_formal_attestation_cover_all_artifacts(self):
        ci = self.workflow_text("ci.yaml")
        preview = self.workflow_text("preview-pdf.yml")
        auto = self.workflow_text("auto-release.yml")

        self.assertIn("dist/ai-security-guide.html", ci)
        self.assertIn("dist/ai-security-guide.html", preview)
        self.assertRegex(auto, r"dist/ai-security-guide-\*\.html")
        self.assertRegex(auto, r"(?s)subject-path:.*?\.pdf.*?\.html.*?SHA256SUMS")
        self.assertRegex(auto, r"(?s)files:.*?\.pdf.*?\.html.*?SHA256SUMS")

    def run_preview_scripts(
        self,
        scenario,
        *,
        repository=TEST_REPOSITORY,
        sha=TEST_SHA,
    ):
        preview = self.workflow_text("preview-pdf.yml")
        scripts = workflow_step_scripts_in_document_order(
            preview,
            (
                "Synchronize mutable preview tag",
                "Create or update preview release",
                "Replace preview assets",
            ),
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fake_gh = root / "gh"
            fake_gh.write_text(FAKE_GH, encoding="utf-8")
            fake_gh.chmod(0o755)
            log = root / "commands.jsonl"
            env = os.environ.copy()
            env.update(
                {
                    "PATH": f"{root}{os.pathsep}{env.get('PATH', '')}",
                    "GH_LOG": str(log),
                    "GH_SCENARIO": scenario,
                    "GH_TOKEN": "test-token",
                    "GH_REPO": repository,
                    "GITHUB_REPOSITORY": repository,
                    "GITHUB_SHA": sha,
                }
            )
            result = None
            for script in scripts:
                result = subprocess.run(
                    ["/bin/bash", "-c", script],
                    cwd=ROOT,
                    env=env,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode != 0:
                    break
            self.assertIsNotNone(result)
            commands = (
                [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
                if log.exists()
                else []
            )
            return result, commands

    def test_preview_updates_existing_tag_and_release_before_upload(self):
        result, commands = self.run_preview_scripts("ref_200_release_exists")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            commands,
            [
                GET_REF_COMMAND,
                PATCH_REF_COMMAND,
                VIEW_RELEASE_COMMAND,
                EDIT_RELEASE_COMMAND,
                UPLOAD_RELEASE_COMMAND,
            ],
        )

    def test_preview_creates_only_on_explicit_tag_and_release_not_found(self):
        result, commands = self.run_preview_scripts("ref_404_release_missing")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            commands,
            [
                GET_REF_COMMAND,
                POST_REF_COMMAND,
                VIEW_RELEASE_COMMAND,
                CREATE_RELEASE_COMMAND,
                UPLOAD_RELEASE_COMMAND,
            ],
        )
        self.assertNotIn("--target", [arg for command in commands for arg in command])

    def test_preview_rejects_invalid_repository_and_sha_before_gh(self):
        cases = (
            ("owner/repo/extra", TEST_SHA, "Invalid GH_REPO"),
            (TEST_REPOSITORY, "a" * 39, "Invalid GITHUB_SHA"),
        )
        for repository, sha, message in cases:
            with self.subTest(repository=repository, sha=sha):
                result, commands = self.run_preview_scripts(
                    "ref_200_release_exists",
                    repository=repository,
                    sha=sha,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(commands, [])
                self.assertIn(message, result.stderr)

    def test_preview_tag_lookup_fails_closed_on_non_404_errors(self):
        for scenario in (
            "ref_401",
            "ref_403",
            "ref_429",
            "ref_503",
            "ref_network",
            "ref_404_exit_2",
        ):
            with self.subTest(scenario=scenario):
                result, commands = self.run_preview_scripts(scenario)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(commands, [GET_REF_COMMAND])
                if scenario.endswith("network"):
                    expected = "network failure"
                elif scenario == "ref_404_exit_2":
                    expected = "404"
                else:
                    expected = scenario[4:]
                self.assertIn(expected, result.stderr)

    def test_preview_release_lookup_fails_closed_except_exact_not_found(self):
        scenarios = (
            "ref_200_release_401",
            "ref_200_release_403",
            "ref_200_release_404",
            "ref_200_release_429",
            "ref_200_release_503",
            "ref_200_release_network",
            "ref_200_release_missing_exit_2",
        )
        for scenario in scenarios:
            with self.subTest(scenario=scenario):
                result, commands = self.run_preview_scripts(scenario)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(
                    commands,
                    [GET_REF_COMMAND, PATCH_REF_COMMAND, VIEW_RELEASE_COMMAND],
                )
                if scenario.endswith("network"):
                    expected = "network failure"
                elif scenario.endswith("missing_exit_2"):
                    expected = "release not found"
                else:
                    expected = scenario.rsplit("release_", 1)[1]
                self.assertIn(expected, result.stderr)

    def test_preview_publish_has_explicit_repo_context_and_isolated_token(self):
        preview = self.workflow_text("preview-pdf.yml")
        build, publish = preview.split("\n  publish:\n", 1)

        self.assertNotIn("GH_TOKEN", build)
        self.assertNotIn("GH_REPO", build)
        self.assertIn("GH_TOKEN: ${{ github.token }}", publish)
        self.assertIn("GH_REPO: ${{ github.repository }}", publish)
        self.assertNotIn("actions/checkout@", publish)

    def test_dependabot_configuration_and_guarded_automerge_exist(self):
        config = ROOT / ".github" / "dependabot.yml"
        self.assertTrue(config.is_file())
        text = config.read_text(encoding="utf-8")
        self.assertIn("github-actions", text)
        workflow = self.workflow_text("dependabot-automerge.yml")
        self.assertIn("dependabot/fetch-metadata@25dd0e34f4fe68f24cc83900b1fe3fe149efef98 # v3.1.0", workflow)


if __name__ == "__main__":
    unittest.main()
