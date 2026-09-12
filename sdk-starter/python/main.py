#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pipeshub-sdk", "httpx"]
# ///
"""Search your company's knowledge, then ask a question and stream a cited answer.

Usage:
    export PIPESHUB_URL=http://localhost:3000
    export PIPESHUB_BEARER_AUTH=<personal access token>
    uv run main.py "what's our on-call policy?"
"""

import json
import os
import sys

import httpx
from pipeshub_sdk import Pipeshub, models


def main() -> None:
    query = " ".join(sys.argv[1:]) or "what's our on-call policy?"
    base_url = os.environ.get("PIPESHUB_URL", "http://localhost:3000").rstrip("/")
    token = os.environ.get("PIPESHUB_BEARER_AUTH")
    if not token:
        sys.exit("Set PIPESHUB_BEARER_AUTH to a Personal Access Token (Workspace -> Developer settings).")

    with Pipeshub(
        server_url=f"{base_url}/api/v1",
        security=models.Security(bearer_auth=token),
    ) as pipeshub:
        search(pipeshub, query)
    ask(base_url, token, query)


def search(pipeshub: Pipeshub, query: str) -> None:
    """Semantic search: ranked, permission-filtered records with their source."""
    print(f"\n== Search: {query}\n")
    res = pipeshub.semantic_search.search(query=query, limit=5)
    hits = res.search_response.search_results or []
    if not hits:
        print("  No results. Connect a source or upload documents to a knowledge base first.")
        return
    # Hits are per chunk, so the same record can appear several times; show each record once, best score first.
    seen: set[str] = set()
    shown = 0
    for hit in hits:
        meta = hit.metadata
        record_id = (meta.record_id if meta else None) or ""
        if record_id in seen:
            continue
        seen.add(record_id)
        shown += 1
        name = (meta.record_name if meta else None) or "(untitled)"
        source = (meta.connector_name if meta else None) or "knowledge base"
        score = f"{hit.score:.2f}" if hit.score is not None else "-"
        url = (meta.web_url if meta else None) or ""
        print(f"  {shown}. {name}  [{source}, score {score}]")
        if url:
            print(f"     {url}")


def iter_sse(resp: httpx.Response):
    """Yield (event, data) pairs from a text/event-stream response."""
    event, data = None, []
    for line in resp.iter_lines():
        if line == "":
            if event or data:
                yield event, "\n".join(data)
            event, data = None, []
        elif line.startswith("event:"):
            event = line[6:].strip()
        elif line.startswith("data:"):
            data.append(line[5:].lstrip())


def ask(base_url: str, token: str, query: str) -> None:
    """Start a conversation and stream the answer token by token, then list its citations.

    This reads the Server-Sent Events stream directly rather than through the
    SDK: the SDK's generated stream parser expects each event's `data` to be a
    string, but the server sends JSON objects, so it fails on the first event.
    The same two lines of SSE parsing above are all the SDK would save you.
    """
    print("\n== Answer\n")
    with httpx.Client(base_url=base_url, timeout=180) as client, client.stream(
        "POST",
        "/api/v1/conversations/stream",
        json={"query": query, "chatMode": "internal_search"},
        headers={"Authorization": f"Bearer {token}", "Accept": "text/event-stream"},
    ) as resp:
        resp.raise_for_status()
        for event, raw in iter_sse(resp):
            payload = json.loads(raw) if raw else {}
            if event == "TEXT_MESSAGE_CONTENT":
                print(payload.get("delta", ""), end="", flush=True)
            elif event == "RUN_FINISHED":
                print("\n")
                print_citations(payload.get("result") or {})
            elif event == "RUN_ERROR":
                print(f"\n\nError: {payload.get('message', 'stream failed')}")


def print_citations(result: dict) -> None:
    """RUN_FINISHED carries the persisted conversation; its last message holds the citations."""
    conversation = result.get("conversation") or {}
    messages = conversation.get("messages") or []
    citations = (messages[-1].get("citations") if messages else None) or []
    if not citations:
        return
    print("== Sources\n")
    seen: set[str] = set()
    for c in citations:
        meta = (c.get("citationData") or {}).get("metadata") or c.get("metadata") or {}
        name = meta.get("recordName") or c.get("citationId", "source")
        if name in seen:
            continue
        seen.add(name)
        source = meta.get("connectorName") or meta.get("connector") or "knowledge base"
        url = meta.get("webUrl") or ""
        print(f"  - {name}  [{source}]" + (f"  {url}" if url else ""))


if __name__ == "__main__":
    main()
