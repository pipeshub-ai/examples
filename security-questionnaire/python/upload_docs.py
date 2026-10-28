#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pipeshub-sdk>=2.0.0"]
# ///
"""Upload a folder of Markdown (.md, .mdx) to a PipesHub knowledge base, so the workbench can cite it.

Usage:
    export PIPESHUB_URL=http://localhost:3000
    export PIPESHUB_BEARER_AUTH=<personal access token>
    git clone --depth 1 https://github.com/pipeshub-ai/documentation
    uv run upload_docs.py documentation          # KB_NAME="..." to pick the knowledge base name

Each file becomes one record named after its path (`auth/sso.mdx` -> `auth-sso.md`).
Indexing continues in PipesHub after the upload; records are searchable a minute or two later.
Run it once: a second run uploads every file again.
"""

import os
import sys
from pathlib import Path

from pipeshub_sdk import Pipeshub, models

BASE_URL = os.environ.get("PIPESHUB_URL", "http://localhost:3000").rstrip("/")
TOKEN = os.environ.get("PIPESHUB_BEARER_AUTH")
KB_NAME = os.environ.get("KB_NAME", "PipesHub documentation")
SKIP = {"node_modules", "changelog", "snippets"}


def find_or_create_kb(pipeshub: Pipeshub) -> str:
    listed = pipeshub.knowledge_base.list_knowledge_bases(search=KB_NAME)
    for kb in listed.knowledge_bases or []:
        if kb.name == KB_NAME:
            return kb.id
    return pipeshub.knowledge_base.create_knowledge_base(kb_name=KB_NAME).id


def main() -> None:
    if not TOKEN or len(sys.argv) < 2:
        sys.exit(__doc__)
    root = Path(sys.argv[1])
    paths = sorted(p for p in root.rglob("*") if p.suffix in (".md", ".mdx")
                   and not any(part in SKIP or part.startswith(".") for part in p.relative_to(root).parts))
    files = [models.UploadRecordsFile(file_name=str(p.relative_to(root).with_suffix(".md")).replace("/", "-"),
                                      content=p.read_bytes(), content_type="text/markdown") for p in paths]
    with Pipeshub(server_url=f"{BASE_URL}/api/v1", security=models.Security(bearer_auth=TOKEN)) as pipeshub:
        kb_id = find_or_create_kb(pipeshub)
        ok = failed = 0
        for start in range(0, len(files), 50):
            with pipeshub.knowledge_base.upload_records(kb_id=kb_id, files=files[start:start + 50]) as stream:
                for event in stream:
                    if event.event == "file:succeeded":
                        ok += 1
                    elif event.event in ("file:failed", "error"):
                        failed += 1
                        print(f"  {event.event}: {event.data}", file=sys.stderr)
            print(f"{ok + failed}/{len(files)} sent to '{KB_NAME}'")
    print(f"Uploaded {ok}, failed {failed}. Indexing continues in PipesHub.")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
