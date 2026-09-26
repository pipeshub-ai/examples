# Finance Operations Copilot

**A Build Pack for finance teams.** It answers the questions finance operations handles every week: *why was this invoice wrong and is it fixed, what is the spending policy, and what does the contract say?* It searches finance tickets, the support escalations behind them, policies, budget reviews and contracts together, and it says where each part of the answer came from.

This is a recipe, not a new application. It is PipesHub, one of the AI clients
you already use, and a short set of instructions for that client. You can try
it on the Acme Corp demo data without connecting anything, then point it at
your own tools.

## The problem

A billing error starts as a customer complaint in support, becomes a finance
ticket to fix one invoice, and a second ticket to fix the rule that caused it.
Policies live in a document that people rarely find, and contract terms are in
a folder that only some people may read. Answering "is it fixed?" or "what's
the limit?" means finding the right one.

**Who it's for:** finance operations, accounts receivable and payable, and
anyone who asks finance the same policy question twice.

## What it reads

| Source | What it holds in the demo |
| --- | --- |
| Jira | The FIN project: FIN-37 (reissue an invoice), FIN-38 (the VAT rule), FIN-40 (a vendor renewal) |
| Jira and Slack | The support escalation behind a billing error (SUP-121) and its `#support-escalations` message |
| Google Drive | The Finance folder: the expense policy and the Q2 2026 budget review |
| Google Drive (restricted) | The Payments contracts folder, readable by payments contract readers only |

With your own data, these are your connectors in PipesHub. Any mix works.

## How it fits together

```
your client (Claude Code, Cursor, Codex, Omnigent)
   │   the instructions in AGENTS.md: when to search, what to cite
   ▼
PipesHub MCP server  ── your personal access token ──►  only what you may see
   │
   ▼
one index over every connected system, with permissions
```

The client does the reasoning. PipesHub does the search across every
connected system, filters it by what the signed-in person may see, and returns
records with their sources. The pack's instructions tell the client when to
search, what to follow and what to cite.

## Try it on the demo data

You need a PipesHub release that includes the **Demo** connector (the first
release after 0.8.0; on 0.8.0 and earlier it is not in the connectors list),
with the extended Acme Corp demo data that adds the Finance folder, FIN project and payments contract folder. That data is
in [pipeshub-ai#3585](https://github.com/pipeshub-ai/pipeshub-ai/pull/3585),
which is not merged yet; until it ships, the Finance Operations Copilot questions have
nothing to find.

1. **Load the demo.** In PipesHub, go to **Workspace → Connectors**, pick
   **Demo**, add it as a team connector and enable it. If you set PipesHub up
   with `bootstrap-first-run.sh`, `PIPESHUB_DEMO_DATA=1` in its env file does
   the same. Indexing takes a minute or two. The
   [demo data page](https://docs.pipeshub.com/demo-data) has the details,
   including the two sample employees, Alice and Bob.
2. **Connect your client.** Follow steps 1 and 2 of the
   [Company Knowledge MCP](../../company-knowledge-mcp/) tutorial: create a
   personal access token and add PipesHub to Claude Code, Cursor, Codex or
   Claude Desktop. To see the permission lesson, create the token while signed
   in as the sample user named in [demo/questions.md](demo/questions.md).
3. **Add the instructions** for your client, below.
4. **Ask the questions** in [demo/questions.md](demo/questions.md).

### Instructions for your client

The instructions are in [AGENTS.md](AGENTS.md). Put them where your client
reads project instructions:

- **Claude Code:** append [claude-code/CLAUDE.md.snippet](claude-code/CLAUDE.md.snippet)
  to your project's `CLAUDE.md`.
- **Codex:** copy [AGENTS.md](AGENTS.md) into your project root.
- **Cursor:** add the text of [AGENTS.md](AGENTS.md) as a project rule.
- **Omnigent:** the [omnigent/finance-operations](omnigent/finance-operations/)
  folder is a complete agent. From this pack's folder (`packs/finance`), run it the same way as the
  company-knowledge agent in the MCP tutorial:

  ```bash
  export PIPESHUB_MCP_URL=http://localhost:3000/mcp   # https:// for a PipesHub on another machine
  export PIPESHUB_MCP_TOKEN=...   # your personal access token
  export OMNIGENT_RUNNER_ENV_PASSTHROUGH=PIPESHUB_MCP_URL,PIPESHUB_MCP_TOKEN

  omnigent server --agent ./omnigent/finance-operations/   # terminal 1
  omnigent host --server http://localhost:6767        # terminal 2
  ```

  Then open `http://localhost:6767` and choose **finance-operations** from the agent
  menu in the message box (under *Agents → Other…*).

## Questions it answers

The full list, with the records each answer should cite and what test runs
cited, is in [demo/questions.md](demo/questions.md). Two of them:

- *"Why was Contoso's invoice wrong, and has the billing rule been fixed?"* The answer separates the fix to one invoice (FIN-37) from the fix to the rule (FIN-38, 6 May), starting from the support escalation.
- *"What rate do we pay for card processing?"* Alice, a payments contract reader, gets the rate from the contract; Bob gets no answer rather than a guess.

## Why naive RAG isn't enough

The obvious alternative is to embed everything, take the top few matching
chunks for a question, and hand them to a model. On the demo data, two things
go wrong with that. Each was checked on a running instance with a plain
top-10 search.

1. **The root cause ranks low.** For *"Why was Contoso's invoice wrong, and
   has the billing rule been fixed?"*, the support ticket SUP-121 ranked first
   for both sample users, but it only says that finance resolved it and names
   their tickets. FIN-38, the ticket that says what the billing rule got wrong
   and when it was fixed, ranked sixth for Alice, below an unrelated case about
   billing addresses. A model given the top five would not know what the rule
   got wrong, when it was fixed, or that three other April invoices had the
   same error. The pack's instructions tell the agent to follow a ticket to the
   ones it names.
2. **Contract terms must not leak, and near misses must not be taken for the
   answer.** For *"What rate do we pay for card processing?"*, Alice's first
   result was the payment processing agreement. Bob's results did not contain
   it, because PipesHub filters by the person before ranking. His top results
   were the Q2 budget review, which mentions processing fees but not the rate,
   and then two pricing documents about what customers pay, which a model
   could mistake for the answer. The pack's instructions say to take contract
   terms only from a contract the person can see; in the live runs, both of
   Bob's answers said the budget review does not state the rate.

## Make it yours

- **Point it at your own tools.** Connect your finance tracker, document store and
  chat in PipesHub.
- **Add your ticket prefixes and policy names** to [AGENTS.md](AGENTS.md), for
  example "purchase requests are PR- tickets; the expense policy is in Drive →
  Finance".
- **Keep contracts restricted.** Give contracts their own group in PipesHub;
  the agent only sees what the signed-in person may see.
- **Keep it read-only.** For search only, create the personal access token
  with the `semantic:write`, `kb:read` and `connector:read` scopes, as the
  [MCP tutorial](../../company-knowledge-mcp/#customize-it) describes.

## A sixty-second demo

[demo/video-script.md](demo/video-script.md) is a shot-by-shot script for a
short screen recording on the demo data.

## Built something with it?

Open a [showcase issue](https://github.com/pipeshub-ai/examples/issues/new?template=showcase.yml)
and we'll feature it.
