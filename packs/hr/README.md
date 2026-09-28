# People Policy Copilot

**Give the current policy, not what the handbook said before it changed.** This Build Pack for People (HR) teams answers the policy questions employees ask every week: *what is the current policy, and has it changed since the handbook was written?* It searches the handbook, People announcements and HR service desk cases together, says where each part of the answer came from, and says when the handbook has not caught up. See [the questions it answers](#questions-it-answers).

This is a recipe, not a new application. It is PipesHub, one of the AI clients
you already use, and a short set of instructions for that client. You can try
it on the Acme Corp demo data without connecting anything, then point it at
your own tools.

## The problem

Policies change faster than handbooks. A change is announced in a channel, a
few people ask the service desk to confirm it, and the handbook is updated
weeks later. Until then, the handbook gives the wrong answer with complete
confidence. Some People material, such as compensation bands, is only for
managers.

**Who it's for:** People and HR teams answering policy questions, managers,
and every employee who has searched the handbook and wondered if it is still
right.

## What it reads

| Source | What it holds in the demo |
| --- | --- |
| Google Drive | The People folder: the employee handbook, the parental leave policy, the new-engineer onboarding checklist |
| Slack | The `#people` channel, including the 2 March announcement about carrying over annual leave |
| ServiceNow | The HR service desk: HR0001203, a question about carry-over |
| Google Drive (restricted) | The People managers folder, readable by people managers only |

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
with the extended Acme Corp demo data that adds the People folder, `#people` channel, HR service desk and People managers folder. That data is
in [pipeshub-ai#3585](https://github.com/pipeshub-ai/pipeshub-ai/pull/3585),
which is not merged yet; until it ships, the People Policy Copilot questions have
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
- **Omnigent:** the [omnigent/people-policy](omnigent/people-policy/) folder is a
  complete agent. Run it from this pack's folder (`packs/hr`) in two
  terminals, and set the PipesHub settings in both: the server reads them when
  it registers the agent, and the host passes them to the agent when it runs.

  ```bash
  # In both terminals
  export PIPESHUB_MCP_URL=http://localhost:3000/mcp   # https:// for a PipesHub on another machine
  export PIPESHUB_MCP_TOKEN=...   # your personal access token
  export OMNIGENT_RUNNER_ENV_PASSTHROUGH=PIPESHUB_MCP_URL,PIPESHUB_MCP_TOKEN

  # Terminal 1: the server, which registers the agent
  omnigent server --agent ./omnigent/people-policy/

  # Terminal 2: the host, which runs it
  omnigent host --server http://localhost:6767
  ```

  If an Omnigent server is already running, stop it first with
  `omnigent server stop`; otherwise `omnigent server` reuses it and the agent
  is not registered.

  Then open `http://localhost:6767` and choose **people-policy** from the agent
  menu in the message box (under *Agents → Other…*).

## Questions it answers

The full list, with the records each answer should cite and what test runs
cited, is in [demo/questions.md](demo/questions.md). Two of them:

- *"How many days of unused annual leave can I carry over into next year?"* Five, from the 2 March announcement, with the handbook's older three-day rule named as out of date.
- *"What is the salary band for a senior engineer?"* Bob, a people manager, gets the band. Alice isn't given the compensation document, because PipesHub never hands it to the agent; the instructions then ask the agent to point her to the People team (the recorded runs used PipesHub's own agent, so they show only that she didn't get the document).

## Why naive RAG isn't enough

The obvious alternative is to embed everything, take the top few matching
chunks for a question, and hand them to a model. On the demo data, two things
go wrong with that. Each was checked on a running instance with a plain
top-10 search.

1. **Both answers come back, and nothing says which is current.** For
   *"How many days of unused annual leave can I carry over into next year?"*,
   the top two records for both sample users were the `#people` announcement
   (five days) and the employee handbook (three days). A plain top-k hands the
   model both numbers with nothing to choose between them. The pack's
   instructions tell the agent to prefer the newer record, say the handbook is
   out of date, and cite both.
2. **Pay data must not leak.** For *"What is the salary band for a senior
   engineer?"*, Bob's first result was the compensation bands; Alice's top ten
   contained nothing about pay, because PipesHub filters by the person before
   ranking. An index that ignored permissions would hand the bands to anyone
   who asked.

## Make it yours

- **Point it at your own tools.** Connect your handbook's document store, your
  People channel and your HR service desk in PipesHub.
- **Name your sources of truth** in [AGENTS.md](AGENTS.md), for example
  "announcements in #people override the handbook until it is updated".
- **Keep pay data restricted.** Give compensation material its own group; the
  agent only sees what the signed-in person may see.
- **Keep it read-only.** For search only, create the personal access token
  with the `semantic:write`, `kb:read` and `connector:read` scopes, as the
  [MCP tutorial](../../company-knowledge-mcp/#customize-it) describes.

## A sixty-second demo

[demo/video-script.md](demo/video-script.md) is a shot-by-shot script for a
short screen recording on the demo data.

## Built something with it?

Open a [showcase issue](https://github.com/pipeshub-ai/examples/issues/new?template=showcase.yml)
and we'll feature it.
