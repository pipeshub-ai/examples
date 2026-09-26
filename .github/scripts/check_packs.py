#!/usr/bin/env python3
"""Checks that keep the examples working: links, YAML, and each Build Pack.

- Every relative link in a Markdown file points at a file that exists.
- Every YAML file parses.
- Each pack under packs/ has its files, and its instructions agree: the
  Omnigent agent's AGENTS.md is the pack's AGENTS.md, and the Claude Code
  snippet is the same text under one heading.
- Every record a pack's demo questions cite (INC-2031, PR #482, SUP-114,
  `#eng-payments`, ...) exists in PipesHub's Acme Corp demo data. A pack whose
  README links an open pipeshub-ai pull request is checked against that pull
  request's data; otherwise against main. PIPESHUB_DEMO_FIXTURE=<path> checks
  every pack against that acme-corp.yaml instead, which is how pipeshub-ai's
  own integration run tests its checkout.

Run from the repository root: python .github/scripts/check_packs.py
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = "backend/python/app/connectors/sources/demo/fixture/acme-corp.yaml"
PIPESHUB = "pipeshub-ai/pipeshub-ai"
PACK_FILES = ("README.md", "AGENTS.md", "claude-code/CLAUDE.md.snippet", "demo/questions.md")
# Record identifiers as the demo data writes them.
RECORD_ID = re.compile(r"\b[A-Z]{2,4}-\d+\b|\b(?:CS|HR)\d{7}\b|(?:PR|issue) #\d+|`#[a-z0-9-]+`")
LINK = re.compile(r"\]\(([^)\s]+)\)")


def markdown_files() -> list[Path]:
    return [p for p in ROOT.rglob("*.md") if ".git" not in p.parts and "node_modules" not in p.parts]


def broken_links() -> list[str]:
    errors = []
    for md in markdown_files():
        for target in LINK.findall(md.read_text(encoding="utf-8")):
            if re.match(r"[a-z][a-z0-9+.-]*:|#", target):
                continue  # a URL or an in-page anchor
            path = target.split("#")[0]
            if path and not (md.parent / path).exists():
                errors.append(f"{md.relative_to(ROOT)}: broken link {target}")
    return errors


def bad_yaml() -> list[str]:
    errors = []
    for y in [*ROOT.rglob("*.yaml"), *ROOT.rglob("*.yml")]:
        if ".git" in y.parts or "node_modules" in y.parts:
            continue
        try:
            yaml.safe_load(y.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            errors.append(f"{y.relative_to(ROOT)}: YAML does not parse: {e}")
    return errors


def pack_dirs() -> list[Path]:
    packs = ROOT / "packs"
    return sorted(p for p in packs.iterdir() if p.is_dir()) if packs.is_dir() else []


def pack_errors(pack: Path) -> list[str]:
    name = f"packs/{pack.name}"
    errors = [f"{name}: missing {f}" for f in PACK_FILES if not (pack / f).is_file()]
    agents = [p for p in (pack / "omnigent").glob("*/AGENTS.md")]
    if len(agents) != 1:
        errors.append(f"{name}: expected one omnigent/<agent>/AGENTS.md, found {len(agents)}")
    if errors:
        return errors
    text = (pack / "AGENTS.md").read_text(encoding="utf-8")
    if agents[0].read_text(encoding="utf-8") != text:
        errors.append(f"{name}: {agents[0].relative_to(ROOT)} differs from AGENTS.md")
    if not (agents[0].parent / "config.yaml").is_file():
        errors.append(f"{name}: {agents[0].parent.relative_to(ROOT)} has no config.yaml")
    snippet = (pack / "claude-code/CLAUDE.md.snippet").read_text(encoding="utf-8")
    body = re.sub(r"\A## [^\n]+\n\n", "", snippet)
    if body == snippet or body != text:
        errors.append(f"{name}: claude-code/CLAUDE.md.snippet is not '## <title>' followed by AGENTS.md")
    return errors


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "examples-check-packs"})
    token = os.environ.get("GITHUB_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 - fixed GitHub hosts
        return resp.read()


def fixture_ref(readme: str) -> tuple[str, str]:
    """The pipeshub-ai ref whose demo data this pack needs, and why."""
    for number in re.findall(rf"github\.com/{PIPESHUB}/pull/(\d+)", readme):
        pr = json.loads(fetch(f"https://api.github.com/repos/{PIPESHUB}/pulls/{number}"))
        if pr["state"] == "open":
            return pr["head"]["sha"], f"open pull request #{number}"
    return "main", "main"


_fixtures: dict[str, str] = {}


def fixture_text(ref: str) -> str:
    if ref not in _fixtures:
        _fixtures[ref] = fetch(f"https://raw.githubusercontent.com/{PIPESHUB}/{ref}/{FIXTURE}").decode("utf-8")
    return _fixtures[ref]


def cited_ids(questions_md: str) -> set[str]:
    """Record identifiers named in the questions table's "Should cite" column."""
    ids: set[str] = set()
    header: list[str] | None = None
    for line in questions_md.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not line.lstrip().startswith("|"):
            header = None
            continue
        if header is None:
            header = cells
            continue
        if "Should cite" in header and len(cells) == len(header) and not set(cells[0]) <= set("-: "):
            ids |= set(RECORD_ID.findall(cells[header.index("Should cite")]))
    return ids


def in_fixture(record_id: str, text: str) -> bool:
    if record_id.startswith("`#"):
        return record_id.strip("`#") in text
    if record_id.startswith(("PR #", "issue #")):
        return re.search(rf"#{record_id.split('#')[1]}\b", text) is not None
    return re.search(rf"\b{re.escape(record_id)}\b", text) is not None


def demo_record_errors(pack: Path) -> list[str]:
    ids = cited_ids((pack / "demo/questions.md").read_text(encoding="utf-8"))
    if not ids:
        return [f"packs/{pack.name}: demo/questions.md names no records in its Should cite column"]
    local = os.environ.get("PIPESHUB_DEMO_FIXTURE", "").strip()
    if local:
        text, why = Path(local).read_text(encoding="utf-8"), local
    else:
        try:
            ref, why = fixture_ref((pack / "README.md").read_text(encoding="utf-8"))
            text = fixture_text(ref)
        except urllib.error.URLError as e:
            return [f"packs/{pack.name}: could not fetch PipesHub's demo data from GitHub: {e}"]
    missing = sorted(i for i in ids if not in_fixture(i, text))
    print(f"packs/{pack.name}: {len(ids)} cited records checked against {why}")
    return [f"packs/{pack.name}: cites {i}, which is not in the demo data ({why})" for i in missing]


def main() -> int:
    errors = broken_links() + bad_yaml()
    for pack in pack_dirs():
        found = pack_errors(pack)
        errors += found or demo_record_errors(pack)
    for e in errors:
        print(f"::error::{e}")
    print(f"{len(errors)} problem(s)" if errors else "all checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
