# Engineering Knowledge Copilot

**Stop asking the one person who remembers why the code is the way it is.**
This Build Pack for engineering teams answers the question every new engineer
and every on-call engineer asks sooner or later: *why did we build it this
way?* It searches your incidents, pull requests, chat threads and design docs
together, and it says where each part of the answer came from. See
[the questions it answers](#questions-it-answers).

This is a recipe, not a new application. It is PipesHub, one of the AI clients
you already use, and a short set of instructions for that client. You can try
it on the Acme Corp demo data without connecting anything, then point it at
your own tools.

## The problem

The reason behind a piece of engineering is rarely in one place. An incident
ticket records what broke. A chat thread records the argument about how to fix
it. A design doc records the decision. A pull request records what actually
shipped and what the reviewers asked for. Someone who wasn't there has to find
all four, in four tools, and piece them together. Usually they ask the one
person who remembers, if that person is still around.

**Who it's for:** engineers joining a team, engineers on call for a system
they didn't build, and anyone reviewing a change to code with history.

## What it reads

| Source | What it holds in the demo |
| --- | --- |
| Jira | Incidents (INC-2031, INC-2018) and support escalations (SUP-114) |
| GitHub | Two repositories: pull requests, review comments and issues |
| Slack | The `#eng-payments` and `#eng-exports` channels, where fixes were discussed |
| Google Drive | Design docs, the on-call handbook, release notes and team meeting notes |
| ServiceNow | The customer cases behind a support escalation |

With your own data, these are your connectors in PipesHub. Any mix works; the
questions get more interesting the more of the story is connected.

## How it fits together

```
your client (Claude Code, Cursor, Codex, Omnigent)
   │   the instructions in AGENTS.md: when to search, what to cite
   ▼
PipesHub MCP server  ── your personal access token ──►  only what you may see
   │
   ▼
one index over Jira, GitHub, Slack, Drive, ServiceNow ... with permissions
```

The client does the reasoning. PipesHub does the search across every
connected system, filters it by what the signed-in person may see, and returns
records with their sources. The pack's instructions tell the client when to
search, to follow one record to the next, and to cite what it used.

## Try it on the demo data

You need a PipesHub release that includes the **Demo** connector (the first
release after 0.8.0; on 0.8.0 and earlier it is not in the connectors list).

1. **Load the demo.** In PipesHub, go to **Workspace → Connectors**, pick
   **Demo**, add it as a team connector and enable it. If you set PipesHub up
   with `bootstrap-first-run.sh`, `PIPESHUB_DEMO_DATA=1` in its env file does
   the same. Indexing takes a minute or two. The
   [demo data page](https://docs.pipeshub.com/demo-data) has the details,
   including the two sample employees, Alice and Bob.
2. **Connect your client.** Follow steps 1 and 2 of the
   [Company Knowledge MCP](../../company-knowledge-mcp/) tutorial: create a
   personal access token and add PipesHub to Claude Code, Cursor, Codex or
   Claude Desktop. It takes about five minutes.
3. **Add the engineering instructions** for your client, below.
4. **Ask the questions** in [demo/questions.md](demo/questions.md).

### Instructions for your client

The instructions are in [AGENTS.md](AGENTS.md). Put them where your client
reads project instructions:

- **Claude Code:** append [claude-code/CLAUDE.md.snippet](claude-code/CLAUDE.md.snippet)
  to your project's `CLAUDE.md`.
- **Codex:** copy [AGENTS.md](AGENTS.md) into your project root.
- **Cursor:** add the text of [AGENTS.md](AGENTS.md) as a project rule.
- **Omnigent:** the [omnigent/engineering-knowledge](omnigent/engineering-knowledge/) folder is a
  complete agent. Run it from this pack's folder (`packs/engineering`) in two
  terminals, and set the PipesHub settings in both: the server reads them when
  it registers the agent, and the host passes them to the agent when it runs.

  ```bash
  # In both terminals
  export PIPESHUB_MCP_URL=http://localhost:3000/mcp   # https:// for a PipesHub on another machine
  export PIPESHUB_MCP_TOKEN=...   # your personal access token
  export OMNIGENT_RUNNER_ENV_PASSTHROUGH=PIPESHUB_MCP_URL,PIPESHUB_MCP_TOKEN

  # Terminal 1: the server, which registers the agent
  omnigent server --agent ./omnigent/engineering-knowledge/

  # Terminal 2: the host, which runs it
  omnigent host --server http://localhost:6767
  ```

  If an Omnigent server is already running, stop it first with
  `omnigent server stop`; otherwise `omnigent server` reuses it and the agent
  is not registered.

  Then open `http://localhost:6767` and choose **engineering-knowledge** from
  the agent menu in the message box (under *Agents → Other…*).

## Questions it answers

The full list, with the records each answer should cite and what a test run
cited, is in [demo/questions.md](demo/questions.md). Two of them:

- *"Why was the payment service architecture changed, and how was the decision
  made?"* The answer joins the INC-2031 incident in Jira, the `#eng-payments`
  thread where the fix was argued, the "Billing worker resilience" design doc
  and PR #482 on GitHub.
- *"What caused the export timeouts on large workspaces, and how did we fix
  it?"* The answer starts from three customer cases, follows the SUP-114
  escalation to issue #207, and ends at PR #211, which moved large exports to
  a background queue.

## Why naive RAG isn't enough

The obvious alternative is to embed everything, take the top few matching
chunks for a question, and hand them to a model. On the demo data, three
things go wrong with that. Each was checked on a running instance.

1. **The top matches mix stories and miss the decision.** For the payment
   service question, a plain top-10 search returned 20 chunks from 12 records.
   They included records about a different change entirely (PR #211 and the
   export runbook), while the 15 March Slack thread where the fix was decided
   was not among them. An agent that searches again for the records its
   results name (INC-2031, PR #482) can put the four pieces together; a single
   top-k pass does not.
2. **Not everyone may see everything.** The pricing committee's documents are
   restricted. The same search returns the 2026 pricing strategy for Bob, who
   is on the committee, and nothing from it for Alice, who is not. Because
   PipesHub filters by the person before ranking, every client connected with
   Alice's token gets Alice's view.
3. **The written record has gaps, and a summary hides them.** The design doc
   says the four retry options were weighed in the Slack thread, but the thread
   only compares two of them. A model summarising the top chunks repeats the
   design doc. The pack's instructions ask the agent to point out exactly this
   kind of disagreement; in our test run it still repeated the design doc once,
   so check this answer when you try it.

## Make it yours

- **Point it at your own tools.** Connect your GitHub, Jira, Slack and Drive in
  PipesHub. The instructions are not specific to the demo.
- **Adjust the instructions.** Add your own ticket prefixes and repository
  names to [AGENTS.md](AGENTS.md) so the agent knows what to follow, for
  example "our incident tickets start with OPS-".
- **Keep it read-only.** For search only, create the personal access token
  with the `semantic:write`, `kb:read` and `connector:read` scopes, as the
  [MCP tutorial](../../company-knowledge-mcp/#customize-it) describes.
- **Narrow the search.** `pipeshub_search` accepts connector filters, which
  helps in a repository that only cares about one system.

## A sixty-second demo

[demo/video-script.md](demo/video-script.md) is a shot-by-shot script for a
short screen recording on the demo data.

## Built something with it?

Open a [showcase issue](https://github.com/pipeshub-ai/examples/issues/new?template=showcase.yml)
and we'll feature it.
