# Support Investigation Copilot

**Answer "has this happened before, and is it fixed?" while the customer is still waiting.** This Build Pack for support teams answers the questions a support agent has when a customer reports a problem: *has this happened before, who else hit it, is there an engineering ticket, and what do I tell the customer?* It searches customer cases, escalations, runbooks and the engineering records behind them together, and it says where each part of the answer came from. See [the questions it answers](#questions-it-answers).

This is a recipe, not a new application. It is PipesHub, one of the AI clients
you already use, and a short set of instructions for that client. You can try
it on the Acme Corp demo data without connecting anything, then point it at
your own tools.

## The problem

A customer's problem is rarely new, but the history of it is spread out. The
customer case is in the help desk. The escalation is a ticket in another
project. The discussion is in a chat channel. The workaround and the current
procedure are in a runbook. The fix is an engineering issue and a pull request,
and sometimes a finance ticket if money was involved. An agent answering the
customer has to find all of that, often while the customer waits.

**Who it's for:** support agents, support leads, and anyone handling an
escalation or a customer who asks "is this fixed yet?"

## What it reads

| Source | What it holds in the demo |
| --- | --- |
| ServiceNow | Customer cases, including three export-timeout cases (CS0004471 Northwind Traders, CS0004478 Contoso, CS0004480 Fabrikam) |
| Jira | Support escalations (SUP-114, SUP-121, SUP-098) and the finance tickets a billing problem led to (FIN-37, FIN-38, which come with the extended demo data in [pipeshub-ai#3585](https://github.com/pipeshub-ai/pipeshub-ai/pull/3585)) |
| Slack | The `#support-escalations` channel |
| Google Drive | The Support folder, including the export runbook |
| GitHub | The engineering side of an escalation: issue #207 and PR #211 in `acme/svc-export` |

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
Questions 1 and 3 work on the demo data as it ships: the export cases,
SUP-114, issue #207, PR #211 and the Export runbook are all in it. Question 2
also needs the finance tickets from the extended demo data in
[pipeshub-ai#3585](https://github.com/pipeshub-ai/pipeshub-ai/pull/3585),
which is not merged yet.

1. **Load the demo.** In PipesHub, go to **Workspace → Connectors**, pick
   **Demo**, add it as a team connector and enable it. If you set PipesHub up
   with `bootstrap-first-run.sh`, `PIPESHUB_DEMO_DATA=1` in its env file does
   the same. Indexing takes a minute or two. The
   [demo data page](https://docs.pipeshub.com/demo-data) has the details,
   including the two sample employees, Alice and Bob.
2. **Connect your client.** Follow steps 1 and 2 of the
   [Company Knowledge MCP](../../company-knowledge-mcp/) tutorial: create a
   personal access token and add PipesHub to Claude Code, Cursor, Codex or
   Claude Desktop.
3. **Add the instructions** for your client, below.
4. **Ask the questions** in [demo/questions.md](demo/questions.md).

### Instructions for your client

The instructions are in [AGENTS.md](AGENTS.md). Put them where your client
reads project instructions:

- **Claude Code:** append [claude-code/CLAUDE.md.snippet](claude-code/CLAUDE.md.snippet)
  to your project's `CLAUDE.md`.
- **Codex:** copy [AGENTS.md](AGENTS.md) into your project root.
- **Cursor:** add the text of [AGENTS.md](AGENTS.md) as a project rule.
- **Omnigent:** the [omnigent/support-investigation](omnigent/support-investigation/) folder is a
  complete agent. Run it from this pack's folder (`packs/support`) in two
  terminals, and set the PipesHub settings in both: the server reads them when
  it registers the agent, and the host passes them to the agent when it runs.

  ```bash
  # In both terminals
  export PIPESHUB_MCP_URL=http://localhost:3000/mcp   # https:// for a PipesHub on another machine
  export PIPESHUB_MCP_TOKEN=...   # your personal access token
  export OMNIGENT_RUNNER_ENV_PASSTHROUGH=PIPESHUB_MCP_URL,PIPESHUB_MCP_TOKEN

  # Terminal 1: the server, which registers the agent
  omnigent server --agent ./omnigent/support-investigation/

  # Terminal 2: the host, which runs it
  omnigent host --server http://localhost:6767
  ```

  If an Omnigent server is already running, stop it first with
  `omnigent server stop`; otherwise `omnigent server` reuses it and the agent
  is not registered.

  Then open `http://localhost:6767` and choose **support-investigation** from the agent
  menu in the message box (under *Agents → Other…*).

## Questions it answers

The full list, with the records each answer should cite and what test runs
cited, is in [demo/questions.md](demo/questions.md). Two of them:

- *"Which customers reported export timeouts, and what fixed it?"* The answer joins three ServiceNow cases, the SUP-114 escalation in Jira, and the engineering fix, PR #211 on GitHub, with the runbook that describes how exports work now.
- *"What happened with Contoso's invoice that showed VAT on an exempt line?"* The answer follows SUP-121 into finance: the invoice was reissued on 22 April (FIN-37) and the billing rule behind it was fixed on 6 May (FIN-38).

## Why naive RAG isn't enough

The obvious alternative is to embed everything, take the top few matching
chunks for a question, and hand them to a model. On the demo data, one thing
goes wrong with that, and one thing works. Both were checked on a running
instance with a plain top-10 search.

1. **The answer is spread out, and a plain search mixes in noise.** For *"Which
   customers reported export timeouts, and what fixed it?"*, Alice's top
   results included an unrelated billing incident (INC-2031, fourth) and a
   search-indexing incident (INC-2018). The fix, PR #211, ranked eighth for
   Alice and twelfth for Bob, and the Northwind Traders case was not in either
   list at all. A model given the top five would name two of the three
   customers, and would know the fix only as a pull request number mentioned in
   SUP-114. The pack's instructions tell the agent to follow each record to the
   ones it names, from the cases to SUP-114 to PR #211; in the live runs every
   answer cited PR #211 and the Northwind case.
2. **Where plain search is enough.** For *"A customer says their workspace
   export timed out. What should I check?"*, the runbook ranked first for both
   sample users. The older cases that describe the timeout ranked below it,
   and the pack's instructions still tell the agent to prefer the runbook and
   say when a case predates the fix.

## Make it yours

- **Point it at your own tools.** Connect your help desk, issue tracker, chat
  and runbooks in PipesHub.
- **Add your ticket prefixes** to [AGENTS.md](AGENTS.md) so the agent knows
  what to follow, for example "our escalations start with ESC-".
- **Name your runbook folder** in the instructions if you keep one, so the
  agent prefers it for "what should I do" questions.
- **Keep it read-only.** For search only, create the personal access token
  with the `semantic:write`, `kb:read` and `connector:read` scopes, as the
  [MCP tutorial](../../company-knowledge-mcp/#customize-it) describes.

## A sixty-second demo

[demo/video-script.md](demo/video-script.md) is a shot-by-shot script for a
short screen recording on the demo data.

## Built something with it?

Open a [showcase issue](https://github.com/pipeshub-ai/examples/issues/new?template=showcase.yml)
and we'll feature it.
