#!/usr/bin/env python3
"""Render all Mermaid diagrams in a GitBook-style book to SVG (for the mobile reader).

Extracts ```mermaid blocks in SUMMARY.md order and renders them with mermaid-cli,
pointing Puppeteer at a system Chrome (CHROME_BIN env or auto-detected). Rendering
is chunked and retried because a large mmdc pass can crash headless Chrome. Writes
d-1.svg .. d-N.svg into --svg-out. Rendering is strict by default: missing
prerequisites or SVGs fail instead of allowing source fallbacks in the HTML reader.
Use --allow-fallback only when source-code fallbacks are explicitly acceptable.
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


SAFETY_MESSAGE = "must be an independent directory outside protected source trees"
STANDARD_CHROME_PATHS = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
)


def paths_overlap(left: Path, right: Path) -> bool:
    return left == right or left in right.parents or right in left.parents


def validate_output_directory(book_dir: str, svg_out: str) -> tuple[Path, Path]:
    book = Path(book_dir).expanduser().resolve()
    output = Path(svg_out).expanduser().resolve()
    repository = Path(__file__).resolve().parents[1]
    protected_exact = {
        Path(output.anchor).resolve(),
        Path.home().resolve(),
        Path.cwd().resolve(),
    }
    if (
        output in protected_exact
        or paths_overlap(output, book)
        or paths_overlap(output, repository)
    ):
        raise ValueError(f"--svg-out {output} {SAFETY_MESSAGE}")
    return book, output


def clean_generated_files(output: Path) -> None:
    generated_svg = re.compile(r"^(?:d-\d+|_c(?:-\d+)?)\.svg$")
    generated_names = {"_chunk.md", "_pptr.json", "_rc.json"}
    for entry in output.iterdir():
        if entry.name in generated_names or generated_svg.fullmatch(entry.name):
            if entry.is_file() or entry.is_symlink():
                entry.unlink()


def find_chrome() -> str | None:
    configured = os.environ.get("CHROME_BIN")
    candidates = (
        [configured]
        if configured
        else [
            *(
                shutil.which(name)
                for name in (
                    "google-chrome-stable",
                    "google-chrome",
                    "chromium-browser",
                    "chromium",
                    "chrome",
                )
            ),
            *STANDARD_CHROME_PATHS,
        ]
    )
    return next(
        (
            str(Path(path).resolve())
            for path in candidates
            if path and Path(path).is_file()
        ),
        None,
    )

ap = argparse.ArgumentParser()
ap.add_argument("--book-dir", default=".")
ap.add_argument("--svg-out", required=True)
ap.add_argument("--chunk", type=int, default=25)
mode = ap.add_mutually_exclusive_group()
mode.add_argument(
    "--strict",
    dest="strict",
    action="store_true",
    default=True,
    help="fail if Chrome, mmdc, or any rendered SVG is missing",
)
mode.add_argument(
    "--allow-fallback",
    dest="strict",
    action="store_false",
    help="allow missing SVGs to fall back to Mermaid source",
)
a = ap.parse_args()
try:
    book_path, svg_path = validate_output_directory(a.book_dir, a.svg_out)
except ValueError as error:
    print(f"Mermaid rendering failed: {error}", file=sys.stderr)
    sys.exit(2)
BOOK, SVG = str(book_path), str(svg_path)
svg_path.mkdir(parents=True, exist_ok=True)
clean_generated_files(svg_path)

# extract mermaid sources in SUMMARY order (same order build_mobile_book.py uses)
srcs, seen = [], set()
sm = os.path.join(BOOK, "SUMMARY.md")
order = []
for line in open(sm, encoding="utf-8"):
    m = re.match(r'^\s*[-*]\s+\[.*?\]\(([^)]+?)\)', line)
    if m and m.group(1).endswith(".md"):
        p = m.group(1).strip()
        if p not in seen and os.path.isfile(os.path.join(BOOK, p)):
            seen.add(p); order.append(p)
for p in order:
    txt = open(os.path.join(BOOK, p), encoding="utf-8").read()
    for mm in re.finditer(r'```mermaid[ \t]*\n(.*?)\n[ \t]*```', txt, re.DOTALL):
        srcs.append(mm.group(1))
N = len(srcs)
print(f"mermaid diagrams found: {N}")
if N == 0:
    sys.exit(0)

chrome = find_chrome()
if not chrome:
    message = "no Chrome executable found"
    if a.strict:
        print(f"Mermaid rendering failed: {message}", file=sys.stderr)
        sys.exit(1)
    print(f"WARNING: {message} -> all diagrams will fall back to source")
    sys.exit(0)
print(f"using Chrome: {chrome}")
pptr = os.path.join(SVG, "_pptr.json")
with open(pptr, "w", encoding="utf-8") as stream:
    json.dump(
        {
            "executablePath": chrome,
            "args": ["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
        },
        stream,
    )
rc = os.path.join(SVG, "_rc.json")
with open(rc, "w", encoding="utf-8") as stream:
    json.dump({"theme": "default"}, stream)
MMDC = shutil.which("mmdc")
if not MMDC:
    message = "mmdc is not on PATH"
    clean_generated_files(svg_path)
    if a.strict:
        print(f"Mermaid rendering failed: {message}", file=sys.stderr)
        sys.exit(1)
    print(f"WARNING: {message} -> all diagrams will fall back to source")
    sys.exit(0)

def render(indices):
    cm = os.path.join(SVG, "_chunk.md")
    open(cm, "w", encoding="utf-8").write("\n".join("```mermaid\n"+srcs[i]+"\n```\n" for i in indices))
    for stale in glob.glob(os.path.join(SVG, "_c*.svg")):
        os.remove(stale)
    result = subprocess.run(
        [
            MMDC,
            "-i",
            cm,
            "-o",
            os.path.join(SVG, "_c.svg"),
            "-p",
            pptr,
            "-c",
            rc,
            "-b",
            "transparent",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr.strip() or result.stdout.strip(), file=sys.stderr)
    for j, i in enumerate(indices, 1):
        sp = os.path.join(SVG, f"_c-{j}.svg")
        if len(indices) == 1 and not os.path.isfile(sp):
            sp = os.path.join(SVG, "_c.svg")
        if os.path.isfile(sp) and os.path.getsize(sp) > 0:
            os.replace(sp, os.path.join(SVG, f"d-{i+1}.svg"))
    for st in glob.glob(os.path.join(SVG, "_c*.svg")): os.remove(st)

def done(): return len([i for i in range(N) if os.path.isfile(os.path.join(SVG, f"d-{i+1}.svg"))])

for c in range((N + a.chunk - 1) // a.chunk):
    s, e = c*a.chunk, min(c*a.chunk + a.chunk, N)
    render(list(range(s, e)))
    print(f"  chunk {c+1}: {done()}/{N}", flush=True)
for att in range(4):
    miss = [i for i in range(N) if not os.path.isfile(os.path.join(SVG, f"d-{i+1}.svg"))]
    if not miss: break
    print(f"  retry {att+1}: {len(miss)} missing", flush=True)
    for b in range(0, len(miss), 8): render(miss[b:b+8])

for f in glob.glob(os.path.join(SVG, "*.json")) + glob.glob(os.path.join(SVG, "_chunk.md")):
    os.remove(f)
print(f"RENDERED {done()}/{N} diagrams")
missing = [
    i + 1
    for i in range(N)
    if not os.path.isfile(os.path.join(SVG, f"d-{i+1}.svg"))
]
if a.strict and missing:
    print(f"Mermaid rendering failed for diagrams: {missing}", file=sys.stderr)
    sys.exit(1)
