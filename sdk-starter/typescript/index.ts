/**
 * Search your company's knowledge, then ask a question and stream a cited answer.
 *
 * Usage:
 *   export PIPESHUB_URL=http://localhost:3000
 *   export PIPESHUB_BEARER_AUTH=<personal access token>
 *   npm install && npx tsx index.ts "what's our on-call policy?"
 */

import { Pipeshub } from "@pipeshub-ai/sdk";

const query = process.argv.slice(2).join(" ") || "what's our on-call policy?";
const baseUrl = (process.env.PIPESHUB_URL ?? "http://localhost:3000").replace(/\/$/, "");
const token = process.env.PIPESHUB_BEARER_AUTH;

if (!token) {
  console.error("Set PIPESHUB_BEARER_AUTH to a Personal Access Token (Workspace -> Developer settings).");
  process.exit(1);
}

const pipeshub = new Pipeshub({
  serverURL: `${baseUrl}/api/v1`,
  security: { bearerAuth: token },
});

async function search(): Promise<void> {
  console.log(`\n== Search: ${query}\n`);
  const res = await pipeshub.semanticSearch.search({ query, limit: 5 });
  const hits = res.searchResponse?.searchResults ?? [];
  if (hits.length === 0) {
    console.log("  No results. Connect a source or upload documents to a knowledge base first.");
    return;
  }
  // Hits are per chunk, so the same record can appear several times; show each record once, best score first.
  const seen = new Set<string>();
  let shown = 0;
  for (const hit of hits) {
    const id = hit.metadata?.recordId ?? "";
    if (seen.has(id)) continue;
    seen.add(id);
    shown += 1;
    const name = hit.metadata?.recordName ?? "(untitled)";
    const source = hit.metadata?.connectorName ?? "knowledge base";
    const score = hit.score != null ? hit.score.toFixed(2) : "-";
    console.log(`  ${shown}. ${name}  [${source}, score ${score}]`);
    if (hit.metadata?.webUrl) console.log(`     ${hit.metadata.webUrl}`);
  }
}

async function* iterSse(body: ReadableStream<Uint8Array>): AsyncGenerator<[string | undefined, string]> {
  const reader = body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let event: string | undefined;
  let data: string[] = [];
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let idx: number;
    while ((idx = buffer.indexOf("\n")) >= 0) {
      const line = buffer.slice(0, idx).replace(/\r$/, "");
      buffer = buffer.slice(idx + 1);
      if (line === "") {
        if (event || data.length) yield [event, data.join("\n")];
        event = undefined; data = [];
      } else if (line.startsWith("event:")) {
        event = line.slice(6).trim();
      } else if (line.startsWith("data:")) {
        data.push(line.slice(5).replace(/^ /, ""));
      }
    }
  }
}

/**
 * Start a conversation and stream the answer token by token, then list its citations.
 * This reads the Server-Sent Events stream directly rather than through the SDK: the
 * SDK's generated stream parser types each event's `data` as a string, but the server
 * sends JSON objects, so it fails on the first event.
 */
async function ask(): Promise<void> {
  console.log("\n== Answer\n");
  const res = await fetch(`${baseUrl}/api/v1/conversations/stream`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify({ query, chatMode: "internal_search" }),
  });
  if (!res.ok || !res.body) throw new Error(`stream failed: ${res.status}`);
  for await (const [event, raw] of iterSse(res.body)) {
    const payload = raw ? JSON.parse(raw) : {};
    switch (event) {
      case "TEXT_MESSAGE_CONTENT":
        process.stdout.write(payload.delta ?? "");
        break;
      case "RUN_FINISHED":
        console.log("\n");
        printCitations(payload.result ?? {});
        break;
      case "RUN_ERROR":
        console.log(`\n\nError: ${payload.message ?? "stream failed"}`);
        break;
    }
  }
}

function printCitations(result: Record<string, any>): void {
  const messages: any[] = result.conversation?.messages ?? [];
  const citations: any[] = messages.at(-1)?.citations ?? [];
  if (citations.length === 0) return;
  console.log("== Sources\n");
  const seen = new Set<string>();
  for (const c of citations) {
    const meta = c.citationData?.metadata ?? {};
    const name: string = meta.recordName ?? c.citationId ?? "source";
    if (seen.has(name)) continue;
    seen.add(name);
    const source = meta.connectorName ?? meta.connector ?? "knowledge base";
    console.log(`  - ${name}  [${source}]` + (meta.webUrl ? `  ${meta.webUrl}` : ""));
  }
}

await search();
await ask();
