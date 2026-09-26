# Account Intelligence

**A Build Pack for sales teams.** It answers the question an account executive asks before every renewal call: *what is the current state of this account, and what have we committed to?* It searches account plans, call notes, deal threads, the customer's support history and deal desk decisions together, and it says where each part of the answer came from.

This is a recipe, not a new application. It is PipesHub, one of the AI clients
you already use, and a short set of instructions for that client. You can try
it on the Acme Corp demo data without connecting anything, then point it at
your own tools.

## The problem

An account's real state is spread across the account plan, the notes from the
last call, the deal channel, and the customer's support cases. The status
changes as the story moves: a renewal goes at risk because of a support
problem and comes back once the fix lands, and the reason for each change is
in a different place. Discounts and other commitments live in a deal desk
decision that only some people may see.

**Who it's for:** account executives and account managers preparing for a
renewal, a quarterly business review or an escalation call, and sales leaders
reviewing the pipeline.

## What it reads

| Source | What it holds in the demo |
| --- | --- |
| Google Drive | The Sales folder: account plans (Northwind Traders, Contoso), call notes, the renewal playbook |
| Slack | The `#deals` channel, including the Northwind renewal-risk thread of 10 April |
| Google Drive (restricted) | The Deal desk folder, readable by the deal desk only |
| ServiceNow and Jira | The customer's support cases and escalations (CS0004471, SUP-114, SUP-121) |

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
with the extended Acme Corp demo data that adds the Sales folder and `#deals` channel. That data is
in [pipeshub-ai#3585](https://github.com/pipeshub-ai/pipeshub-ai/pull/3585),
which is not merged yet; until it ships, the Account Intelligence questions have
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
- **Omnigent:** the [omnigent/account-intelligence](omnigent/account-intelligence/)
  folder is a complete agent. From this folder, run it the same way as the
  company-knowledge agent in the MCP tutorial:

  ```bash
  export PIPESHUB_MCP_URL=http://localhost:3000/mcp
  export PIPESHUB_MCP_TOKEN=...   # your personal access token
  export OMNIGENT_RUNNER_ENV_PASSTHROUGH=PIPESHUB_MCP_URL,PIPESHUB_MCP_TOKEN

  omnigent server --agent ./omnigent/account-intelligence/   # terminal 1
  omnigent host --server http://localhost:6767        # terminal 2
  ```

  Then open `http://localhost:6767` and choose **account-intelligence** from the agent
  menu in the message box (under *Agents → Other…*).

## Questions it answers

The full list, with the records each answer should cite and what test runs
cited, is in [demo/questions.md](demo/questions.md). Two of them:

- *"Is the Northwind Traders renewal at risk, and what is being done about it?"* Not any more: it was at risk in early April because of the export timeouts, and after the fix the 16 April call put it back on track. The answer joins the account plan, the call notes and the `#deals` thread.
- *"What discount did the deal desk approve for the Northwind renewal?"* Bob, on the deal desk, gets the decision; Alice gets no answer, because PipesHub filters by the person before the agent sees anything.

## Why naive RAG isn't enough

The obvious alternative is to embed everything, take the top few matching
chunks for a question, and hand them to a model. On the demo data, two things
go wrong with that. Each was checked on a running instance with a plain
top-10 search.

1. **The older story ranks above the newer one.** For *"Is the Northwind
   Traders renewal at risk, and what is being done about it?"*, Bob's first
   result was the `#deals` thread of 10 April, which says the renewal is at
   risk. The 16 April call notes, which say it is back on track, ranked fourth
   for both sample users, and Alice's third result was an unrelated web page.
   A model given the top three could report a risk that has already passed.
   The pack's instructions tell the agent to look for the newest record on the
   account, say its date, and say what changed.
2. **Deal terms must not leak.** For *"What discount did the deal desk approve
   for the Northwind renewal?"*, Bob's first result was the deal desk decision.
   Alice's results did not contain it, because PipesHub filters by the person
   before ranking. An index that ignored permissions would hand the discount to
   anyone who asked.

## Make it yours

- **Point it at your own tools.** Connect your document store, chat and help desk
  in PipesHub. If your account plans live in a CRM that PipesHub connects to,
  add it too.
- **Name your channels and folders** in [AGENTS.md](AGENTS.md), for example
  "deal discussions are in #deals; account plans are in Drive → Sales".
- **Keep restricted areas restricted.** The pack relies on PipesHub's
  permissions; give deal desk material its own group rather than an
  instruction to the agent.
- **Keep it read-only.** For search only, create the personal access token
  with the `semantic:write`, `kb:read` and `connector:read` scopes, as the
  [MCP tutorial](../../company-knowledge-mcp/#customize-it) describes.

## A sixty-second demo

[demo/video-script.md](demo/video-script.md) is a shot-by-shot script for a
short screen recording on the demo data.

## Built something with it?

Open a [showcase issue](https://github.com/pipeshub-ai/examples/issues/new?template=showcase.yml)
and we'll feature it.
