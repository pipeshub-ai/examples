#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pipeshub-sdk>=2.0.0", "fastapi", "uvicorn", "httpx"]
# ///
"""Draft answers to an RFP or security questionnaire from your company's knowledge, with sources.

Every answer is a draft: one with no source stays "needs review", and only answers a person
approves go into the export.

Usage:
    export PIPESHUB_URL=http://localhost:3000
    export PIPESHUB_BEARER_AUTH=<personal access token>
    uv run app.py                 # PORT=8090 uv run app.py to change the port
    # open http://localhost:8080
    uv run app.py --self-test     # check the questionnaire parser and the review rule, offline
"""

import csv
import io
import os
import re
import sys
from pathlib import Path

import httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse
from pipeshub_sdk import Pipeshub, models
from pydantic import BaseModel, Field

BASE_URL = os.environ.get("PIPESHUB_URL", "http://localhost:3000").rstrip("/")
# Where a reviewer's browser reaches PipesHub, for the source links. Defaults to PIPESHUB_URL.
PUBLIC_URL = os.environ.get("PIPESHUB_PUBLIC_URL", BASE_URL).rstrip("/")
TOKEN = os.environ.get("PIPESHUB_BEARER_AUTH", "")
SAMPLE = Path(__file__).resolve().parent.parent / "sample-questionnaire.csv"

PROMPT = """You are drafting one answer for an RFP or security questionnaire that a customer sent us.

Question: {question}

Answer only from our connected company knowledge. Do not invent certifications, security controls,
product capabilities, SLAs, legal terms or customer claims. If the knowledge does not answer the
question, start the answer with NEEDS REVIEW and say what evidence is missing.
Keep it to a short paragraph a reviewer can paste into the questionnaire, and cite your sources."""

app = FastAPI(title="Security questionnaire workbench")


class Question(BaseModel):
    question_id: str = Field(min_length=1)
    question: str = Field(min_length=3)
    section: str = ""


class DraftRequest(BaseModel):
    questions: list[Question] = Field(min_length=1, max_length=50)


class ParseRequest(BaseModel):
    text: str


def parse_questionnaire(text: str) -> list[dict]:
    """A CSV with a `question` column (and optional `id`/`question_id`, `section`), or one question per line."""
    text = text.strip().lstrip("﻿")
    if not text:
        return []
    first = next(csv.reader([text.splitlines()[0]]))
    if "question" in [c.strip().lower() for c in first]:
        out = []
        for i, row in enumerate(csv.DictReader(io.StringIO(text)), 1):
            row = {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
            if row.get("question"):
                out.append({
                    "question_id": row.get("question_id") or row.get("id") or f"Q{i}",
                    "section": row.get("section", ""),
                    "question": row["question"],
                })
        return out
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return [{"question_id": f"Q{i}", "section": "", "question": q} for i, q in enumerate(lines, 1)]


def review_status(answer: str, citations: list) -> str:
    """A workflow gate, not a truth score: a person approves every answer either way."""
    if not citations or re.search(r"NEEDS[\s_]+REVIEW", answer, re.IGNORECASE):
        return "NEEDS_REVIEW"
    return "DRAFT_SINGLE_SOURCE" if len(citations) == 1 else "DRAFT_WITH_EVIDENCE"


def clean_answer(text: str) -> str:
    """Drop the inline citation links ([1](/record/...), [source](ref12)): they point into PipesHub,
    not at anything a customer can open, and the sources are listed next to the answer."""
    return re.sub(r"[ \t]*\[(?:\d+|source)\]\s*\([^)\s]*\)", "", text).strip()


def link(url: str) -> str:
    return f"{PUBLIC_URL}{url}" if url.startswith("/") else url


def client() -> Pipeshub:
    # Answers are written by an agent that searches several times, so allow a few minutes per question.
    return Pipeshub(server_url=f"{BASE_URL}/api/v1", security=models.Security(bearer_auth=TOKEN), timeout_ms=300_000)


def find_evidence(question: str) -> list[dict]:
    """The records PipesHub ranks highest for the question, filtered by the token owner's permissions.

    POST /retrieve is the search that stores no history, so a 200-question run doesn't fill the user's
    search list. It is read without the SDK: pipeshub-sdk 2.0.0 types `citation.pageNum` as a list of
    integers, but the server sends [null] for records without pages, and the SDK rejects the response.
    """
    resp = httpx.post(f"{BASE_URL}/api/v1/retrieve", json={"query": question, "limit": 8},
                      headers={"Authorization": f"Bearer {TOKEN}"}, timeout=120)
    resp.raise_for_status()
    seen: set[str] = set()
    out = []
    for chunk in resp.json().get("chunks") or []:
        record, cit = chunk.get("record") or {}, chunk.get("citation") or {}
        if record.get("recordId") in seen:
            continue
        seen.add(record.get("recordId"))
        out.append({
            "title": record.get("name") or "(untitled)",
            "source": record.get("connector") or "knowledge base",
            "url": link(cit.get("recordUrl") or cit.get("url") or ""),
            "snippet": (chunk.get("text") or "")[:400],
        })
    return out


def draft_answer(pipeshub: Pipeshub, question: str) -> tuple[str, list[dict]]:
    """A grounded answer and its citations from PipesHub's internal-search chat."""
    with pipeshub.conversations.stream_chat(query=PROMPT.format(question=question), chat_mode="internal_search") as stream:
        for event in stream:
            if event.event == "RUN_ERROR":
                raise RuntimeError((event.data or {}).get("message", "PipesHub answer stream failed"))
            if event.event == "RUN_FINISHED":
                messages = (((event.data or {}).get("result") or {}).get("conversation") or {}).get("messages") or []
                break
        else:
            raise RuntimeError("the answer stream ended before the answer was finished")
    final = messages[-1] if messages else {}
    citations, seen = [], set()
    for cit in final.get("citations") or []:
        meta = (cit.get("citationData") or {}).get("metadata") or {}
        if meta.get("recordId") in seen:
            continue
        seen.add(meta.get("recordId"))
        citations.append({
            "title": meta.get("recordName") or "source",
            "source": meta.get("connectorInstanceName") or meta.get("connector") or "knowledge base",
            "url": link(meta.get("webUrl") or ""),
        })
    # The final message is the answer alone (the streamed text also narrates the agent's searching).
    return clean_answer(final.get("content") or ""), citations


@app.post("/api/parse")
def api_parse(body: ParseRequest) -> dict:
    return {"questions": parse_questionnaire(body.text)}


@app.post("/api/draft")
def api_draft(body: DraftRequest) -> dict:
    """One draft per question. A failed question is reported as ERROR; the others still come back."""
    out = []
    with client() as pipeshub:
        for q in body.questions:
            item = q.model_dump()
            try:
                evidence = find_evidence(q.question)
                answer, citations = draft_answer(pipeshub, q.question)
                item.update(draft_answer=answer, citations=citations, top_evidence=evidence,
                            review_status=review_status(answer, citations))
            except Exception as e:  # noqa: BLE001  one bad question must not lose the rest
                item.update(draft_answer="", citations=[], top_evidence=[], review_status="ERROR", error=str(e)[:300])
            out.append(item)
    return {"responses": out, "notice": "Every answer is a draft. A person must approve it before it goes to a customer."}


@app.get("/api/sample", response_class=PlainTextResponse)
def api_sample() -> str:
    return SAMPLE.read_text() if SAMPLE.exists() else ""


PAGE = """<!doctype html>
<meta charset="utf-8">
<title>Security questionnaire workbench</title>
<style>
  body { font: 15px/1.5 system-ui, sans-serif; max-width: 980px; margin: 40px auto; padding: 0 20px; color: #1b2433; }
  h1 { margin-bottom: 4px; }
  textarea { width: 100%; box-sizing: border-box; font: 13px/1.4 ui-monospace, monospace; padding: 10px; border: 1px solid #c9d1dc; border-radius: 6px; }
  button { font: inherit; padding: 7px 14px; border: 1px solid #0e7c86; border-radius: 6px; background: #fff; color: #0a5c64; cursor: pointer; }
  button.primary { background: #0e7c86; color: #fff; }
  button:disabled { opacity: .5; cursor: default; }
  .bar { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin: 10px 0; }
  .muted { color: #66708a; }
  .q { border: 1px solid #e0e5ec; border-radius: 8px; padding: 14px 16px; margin: 14px 0; }
  .q h3 { margin: 0 0 6px; font-size: 15px; }
  .q .id { color: #66708a; font-weight: 500; margin-right: 6px; }
  .q textarea { font: 14px/1.5 system-ui, sans-serif; min-height: 90px; margin: 8px 0; }
  .badge { font-size: 12px; font-weight: 600; padding: 2px 8px; border-radius: 10px; white-space: nowrap; }
  .NEEDS_REVIEW, .ERROR, .REJECTED { background: #fde8e8; color: #9b1c1c; }
  .DRAFT_SINGLE_SOURCE, .EDITED { background: #fdf3d8; color: #8a5a00; }
  .DRAFT_WITH_EVIDENCE { background: #e3f1ff; color: #0b4f8a; }
  .APPROVED { background: #def7ec; color: #03543f; }
  .WORKING { background: #eef1f5; color: #4a5568; }
  .src a { color: #0a5c64; font-weight: 600; } .src { font-size: 13px; margin: 2px 0; }
  details { font-size: 13px; margin-top: 6px; } .snip { color: #3d4757; margin: 4px 0 8px; }
</style>
<h1>Security questionnaire workbench</h1>
<p class="muted">Paste a questionnaire. Each question gets a draft answered from PipesHub with its sources.
Answers without a source stay <b>needs review</b>, and only the answers you approve are exported.</p>
<textarea id="input" rows="7" placeholder="id,section,question&#10;SEC-1,Access control,Do you support SAML single sign-on?&#10;&#10;or one question per line"></textarea>
<div class="bar">
  <button onclick="loadSample()">Load the sample questionnaire</button>
  <label><input type="file" id="file" accept=".csv,.txt" onchange="loadFile(this)" hidden><button onclick="document.getElementById('file').click()">Open a CSV…</button></label>
  <button class="primary" id="run" onclick="run()">Draft answers</button>
  <span id="summary" class="muted"></span>
  <span style="flex:1"></span>
  <button id="export" onclick="exportCsv()" disabled>Export approved (CSV)</button>
</div>
<div id="list"></div>
<script>
const rows = [];
const $ = id => document.getElementById(id);
const esc = s => String(s ?? '').replace(/[&<>"]/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch]));
const LABEL = {NEEDS_REVIEW: 'Needs review', DRAFT_SINGLE_SOURCE: 'Draft · one source', DRAFT_WITH_EVIDENCE: 'Draft · several sources',
  APPROVED: 'Approved', REJECTED: 'Rejected', EDITED: 'Edited · not approved', ERROR: 'Error', WORKING: 'Drafting…'};

async function loadSample() { $('input').value = await (await fetch('/api/sample')).text(); }
function loadFile(el) { const f = el.files[0]; if (f) f.text().then(t => $('input').value = t); }

async function run() {
  const res = await fetch('/api/parse', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({text: $('input').value})});
  const qs = (await res.json()).questions;
  if (!qs.length) return;
  rows.length = 0; $('list').innerHTML = '';
  qs.forEach((q, i) => { rows.push({...q, review_status: 'WORKING', i}); $('list').insertAdjacentHTML('beforeend', `<div class="q" id="q${i}"></div>`); render(i); });
  $('run').disabled = true;
  let next = 0;
  const worker = async () => { while (next < rows.length) await draft(next++); };
  await Promise.all([worker(), worker(), worker()]);  // three questions at a time
  $('run').disabled = false;
}

async function draft(i) {
  const r = rows[i]; r.review_status = 'WORKING'; render(i);
  try {
    const res = await fetch('/api/draft', {method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({questions: [{question_id: r.question_id, section: r.section, question: r.question}]})});
    if (!res.ok) throw new Error('HTTP ' + res.status);
    Object.assign(r, (await res.json()).responses[0]);
  } catch (e) { Object.assign(r, {review_status: 'ERROR', error: String(e), citations: [], top_evidence: []}); }
  r.answer = r.draft_answer || ''; r.drafted = r.review_status; render(i);
}

function setStatus(i, s) { rows[i].review_status = s; render(i); }
function edited(i, el) {
  const r = rows[i]; r.answer = el.value;
  if (r.review_status === 'APPROVED') { r.review_status = 'EDITED'; render(i, true); }
  summary();
}

function render(i, keepFocus) {
  const r = rows[i], el = $('q' + i), working = r.review_status === 'WORKING';
  if (keepFocus) { el.querySelector('.badge').outerHTML = badge(r); summary(); return; }
  el.innerHTML = `
    <div class="bar" style="margin:0"><h3 style="flex:1"><span class="id">${esc(r.question_id)}</span>${esc(r.question)}</h3>${badge(r)}</div>
    ${r.section ? `<div class="muted" style="font-size:13px">${esc(r.section)}</div>` : ''}
    ${working ? '<p class="muted">Searching PipesHub and drafting…</p>' : `
      ${r.error ? `<p class="muted">${esc(r.error)}</p>` : ''}
      <textarea oninput="edited(${i}, this)">${esc(r.answer)}</textarea>
      ${(r.citations || []).map(c => `<div class="src">${c.url ? `<a href="${esc(c.url)}" target="_blank">${esc(c.title)}</a>` : esc(c.title)} <span class="muted">· ${esc(c.source)}</span></div>`).join('')
        || '<div class="src muted">No sources cited.</div>'}
      <details><summary>What PipesHub found (${(r.top_evidence || []).length} records)</summary>
        ${(r.top_evidence || []).map(e => `<div class="src">${e.url ? `<a href="${esc(e.url)}" target="_blank">${esc(e.title)}</a>` : esc(e.title)} <span class="muted">· ${esc(e.source)}</span></div><div class="snip">${esc(e.snippet)}</div>`).join('')}
      </details>
      <div class="bar">
        <button onclick="setStatus(${i}, 'APPROVED')" ${r.review_status === 'APPROVED' ? 'disabled' : ''}>Approve</button>
        <button onclick="setStatus(${i}, 'REJECTED')">Reject</button>
        <button onclick="draft(${i})">Draft again</button>
      </div>`}`;
  summary();
}

function badge(r) { return `<span class="badge ${r.review_status}">${LABEL[r.review_status] || r.review_status}</span>`; }

function summary() {
  const n = s => rows.filter(r => r.review_status === s).length;
  $('summary').textContent = rows.length ? `${rows.length} questions · ${n('APPROVED')} approved · ${n('NEEDS_REVIEW') + n('ERROR')} need review · ${n('WORKING')} drafting` : '';
  $('export').disabled = !n('APPROVED');
}

function exportCsv() {
  const cell = v => '"' + String(v ?? '').replace(/"/g, '""') + '"';
  const lines = [['question_id', 'section', 'question', 'answer', 'sources'].map(cell).join(',')];
  rows.filter(r => r.review_status === 'APPROVED').forEach(r => lines.push([r.question_id, r.section, r.question, r.answer,
    (r.citations || []).map(c => c.url ? `${c.title} (${c.url})` : c.title).join('; ')].map(cell).join(',')));
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([lines.join('\\n') + '\\n'], {type: 'text/csv'}));
  a.download = 'approved-answers.csv'; a.click();
}
</script>
"""


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return PAGE


def self_test() -> None:
    qs = parse_questionnaire('ID,Section,Question\nSEC-1,Access,"Do you support SSO, and SAML?"\n,,\n,,Encrypt at rest?\n')
    assert qs == [{"question_id": "SEC-1", "section": "Access", "question": "Do you support SSO, and SAML?"},
                  {"question_id": "Q3", "section": "", "question": "Encrypt at rest?"}], qs
    assert parse_questionnaire("Do you encrypt data at rest?\n\nIs there an SLA?") == [
        {"question_id": "Q1", "section": "", "question": "Do you encrypt data at rest?"},
        {"question_id": "Q2", "section": "", "question": "Is there an SLA?"}]
    assert parse_questionnaire("  ") == []
    one, two = [{"title": "a"}], [{"title": "a"}, {"title": "b"}]
    assert review_status("Yes, SAML is supported.", []) == "NEEDS_REVIEW"
    assert review_status("**NEEDS REVIEW** no SLA document found.", two) == "NEEDS_REVIEW"
    assert review_status("Yes [1].", one) == "DRAFT_SINGLE_SOURCE"
    assert review_status("Yes [1][2].", two) == "DRAFT_WITH_EVIDENCE"
    assert clean_answer("Yes, SAML [1](http://h/record/a/preview#blockIndex=0) [2] (http://h/record/b). "
                        "Also OIDC [source](ref75).\n- PATs [3](/record/c)") == "Yes, SAML. Also OIDC.\n- PATs"
    print("self-test passed")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
        sys.exit()
    if not TOKEN:
        sys.exit("Set PIPESHUB_BEARER_AUTH to a Personal Access Token (Workspace -> Developer settings).")
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", "8080")))
