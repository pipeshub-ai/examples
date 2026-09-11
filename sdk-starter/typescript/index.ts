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
  hits.forEach((hit, i) => {
    const name = hit.metadata?.recordName ?? "(untitled)";
    const source = hit.metadata?.connectorName ?? "knowledge base";
    const score = hit.score != null ? hit.score.toFixed(2) : "-";
    console.log(`  ${i + 1}. ${name}  [${source}, score ${score}]`);
    if (hit.metadata?.webUrl) console.log(`     ${hit.metadata.webUrl}`);
  });
}

async function ask(): Promise<void> {
  console.log("\n== Answer\n");
  const stream = await pipeshub.conversations.streamChat({ query, chatMode: "internal_search" });
  for await (const event of stream) {
    const payload = event.data ? JSON.parse(event.data) : {};
    switch (event.event) {
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
    const meta = c.metadata ?? {};
    const name: string = meta.recordName ?? meta.record_name ?? c.citationId ?? "source";
    if (seen.has(name)) continue;
    seen.add(name);
    const source = meta.connectorName ?? meta.connector_name ?? "knowledge base";
    console.log(`  - ${name}  [${source}]`);
  }
}

await search();
await ask();
