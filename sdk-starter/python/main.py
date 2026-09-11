#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pipeshub-sdk"]
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
        ask(pipeshub, query)


def search(pipeshub: Pipeshub, query: str) -> None:
    """Semantic search: ranked, permission-filtered records with their source."""
    print(f"\n== Search: {query}\n")
    res = pipeshub.semantic_search.search(query=query, limit=5)
    hits = res.search_response.search_results or []
    if not hits:
        print("  No results. Connect a source or upload documents to a knowledge base first.")
        return
    for i, hit in enumerate(hits, 1):
        meta = hit.metadata
        name = (meta.record_name if meta else None) or "(untitled)"
        source = (meta.connector_name if meta else None) or "knowledge base"
        score = f"{hit.score:.2f}" if hit.score is not None else "-"
        url = (meta.web_url if meta else None) or ""
        print(f"  {i}. {name}  [{source}, score {score}]")
        if url:
            print(f"     {url}")


def ask(pipeshub: Pipeshub, query: str) -> None:
    """Start a conversation and stream the answer token by token, then list its citations."""
    print(f"\n== Answer\n")
    res = pipeshub.conversations.stream_chat(query=query, chat_mode="internal_search")
    with res as stream:
        for event in stream:
            kind = event.event
            payload = json.loads(event.data) if event.data else {}
            if kind == "TEXT_MESSAGE_CONTENT":
                print(payload.get("delta", ""), end="", flush=True)
            elif kind == "RUN_FINISHED":
                print("\n")
                print_citations(payload.get("result") or {})
            elif kind == "RUN_ERROR":
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
        meta = c.get("metadata") or {}
        name = meta.get("recordName") or meta.get("record_name") or c.get("citationId", "source")
        if name in seen:
            continue
        seen.add(name)
        source = meta.get("connectorName") or meta.get("connector_name") or "knowledge base"
        print(f"  - {name}  [{source}]")


if __name__ == "__main__":
    main()
