#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pipeshub-sdk", "fastapi", "uvicorn", "httpx"]
# ///
"""A private, permission-aware search page for your company, on your own infrastructure.

Usage:
    export PIPESHUB_URL=http://localhost:3000
    export PIPESHUB_BEARER_AUTH=<personal access token>
    uv run app.py                 # PORT=8090 uv run app.py to change the port
    # open http://localhost:8080
"""

import json
import os
import sys

import httpx
import uvicorn
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from pipeshub_sdk import Pipeshub, models

BASE_URL = os.environ.get("PIPESHUB_URL", "http://localhost:3000").rstrip("/")
TOKEN = os.environ.get("PIPESHUB_BEARER_AUTH")
if not TOKEN:
    sys.exit("Set PIPESHUB_BEARER_AUTH to a Personal Access Token (Workspace -> Developer settings).")

app = FastAPI(title="Private enterprise search")


def client() -> Pipeshub:
    return Pipeshub(server_url=f"{BASE_URL}/api/v1", security=models.Security(bearer_auth=TOKEN))


@app.get("/api/search")
def api_search(q: str = Query(..., min_length=1), limit: int = 10) -> dict:
    """Ranked, permission-filtered results. Each carries the record it came from."""
    with client() as pipeshub:
        res = pipeshub.semantic_search.search(query=q, limit=limit)
    hits = res.search_response.search_results or []
    results = []
    seen: set[str] = set()
    for hit in hits:
        meta = hit.metadata
        record_id = (meta.record_id if meta else None) or ""
        if record_id in seen:
            continue
        seen.add(record_id)
        results.append(
            {
                "title": (meta.record_name if meta else None) or "(untitled)",
                "source": (meta.connector_name if meta else None) or "knowledge base",
                "url": (meta.web_url if meta else None) or "",
                "score": hit.score,
                "snippet": (hit.content or "")[:300],
            }
        )
    return {"query": q, "results": results}


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


@app.get("/api/ask")
def api_ask(q: str = Query(..., min_length=1)) -> dict:
    """A synthesised answer with its citations, collected from the streaming endpoint.

    Reads the Server-Sent Events stream directly: the SDK's generated stream
    parser expects each event's `data` to be a string, but the server sends
    JSON objects, so it fails on the first event.
    """
    answer: list[str] = []
    citations: list[dict] = []
    with httpx.Client(base_url=BASE_URL, timeout=180) as c, c.stream(
        "POST", "/api/v1/conversations/stream",
        json={"query": q, "chatMode": "internal_search"},
        headers={"Authorization": f"Bearer {TOKEN}", "Accept": "text/event-stream"},
    ) as resp:
        resp.raise_for_status()
        for event, raw in iter_sse(resp):
            payload = json.loads(raw) if raw else {}
            if event == "TEXT_MESSAGE_CONTENT":
                answer.append(payload.get("delta", ""))
            elif event == "RUN_FINISHED":
                messages = ((payload.get("result") or {}).get("conversation") or {}).get("messages") or []
                for cit in (messages[-1].get("citations") if messages else None) or []:
                    meta = (cit.get("citationData") or {}).get("metadata") or {}
                    citations.append(
                        {
                            "title": meta.get("recordName") or "source",
                            "source": meta.get("connectorName") or meta.get("connector") or "knowledge base",
                            "url": meta.get("webUrl") or "",
                        }
                    )
            elif event == "RUN_ERROR":
                return {"query": q, "error": payload.get("message", "stream failed")}
    # De-duplicate citations by title, keeping first occurrence.
    seen: set[str] = set()
    unique = [c for c in citations if not (c["title"] in seen or seen.add(c["title"]))]
    return {"query": q, "answer": "".join(answer), "citations": unique}


PAGE = """<!doctype html>
<meta charset="utf-8">
<title>Company search</title>
<style>
  body { font: 16px/1.5 system-ui, sans-serif; max-width: 760px; margin: 48px auto; padding: 0 20px; color: #1b2433; }
  form { display: flex; gap: 8px; }
  input { flex: 1; font: inherit; padding: 10px 12px; border: 1px solid #c9d1dc; border-radius: 6px; }
  button { font: inherit; padding: 10px 16px; border: 0; border-radius: 6px; background: #0e7c86; color: #fff; cursor: pointer; }
  h2 { font-size: 14px; letter-spacing: .06em; text-transform: uppercase; color: #66708a; margin: 32px 0 8px; }
  .r { padding: 10px 0; border-bottom: 1px solid #e6eaf0; }
  .r a { font-weight: 600; color: #0a5c64; }
  .src { font-size: 13px; color: #66708a; }
  .snip { font-size: 14px; color: #3d4757; margin-top: 2px; }
  #answer { white-space: pre-wrap; }
  .muted { color: #66708a; }
</style>
<h1>Company search</h1>
<p class="muted">Results are filtered by your permissions before ranking. Answers cite their sources.</p>
<form onsubmit="go(event)"><input id="q" placeholder="why did we change the retry logic in the billing worker?" autofocus><button>Search</button></form>
<h2>Answer</h2><div id="answer" class="muted">Ask something to get a cited answer.</div>
<div id="cites"></div>
<h2>Matching records</h2><div id="results" class="muted">—</div>
<script>
async function go(e) {
  e.preventDefault();
  const q = document.getElementById('q').value.trim(); if (!q) return;
  document.getElementById('answer').textContent = 'Thinking…';
  document.getElementById('results').textContent = 'Searching…';
  document.getElementById('cites').innerHTML = '';
  const [s, a] = await Promise.all([
    fetch('/api/search?q=' + encodeURIComponent(q)).then(r => r.json()),
    fetch('/api/ask?q=' + encodeURIComponent(q)).then(r => r.json()),
  ]);
  document.getElementById('results').innerHTML = s.results.length
    ? s.results.map(r => `<div class="r"><a href="${r.url || '#'}" target="_blank">${esc(r.title)}</a> <span class="src">· ${esc(r.source)}</span><div class="snip">${esc(r.snippet)}</div></div>`).join('')
    : '<span class="muted">No results. Connect a source or upload documents to a knowledge base.</span>';
  document.getElementById('answer').textContent = a.error ? 'Error: ' + a.error : (a.answer || '(no answer)');
  document.getElementById('cites').innerHTML = (a.citations || []).map(c => `<div class="r"><a href="${c.url || '#'}" target="_blank">${esc(c.title)}</a> <span class="src">· ${esc(c.source)}</span></div>`).join('');
}
function esc(s) { return String(s ?? '').replace(/[&<>"]/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch])); }
</script>
"""


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return PAGE


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", "8080")))
