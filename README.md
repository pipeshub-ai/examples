# What can I build with PipesHub?

Your company's answers are spread across Google Drive, Slack, Jira, GitHub and the other tools your teams use, and your AI assistants either can't see them or can see too much. [PipesHub](https://github.com/pipeshub-ai/pipeshub-ai) is an open-source platform that connects all of it — Google Drive, GitHub, Slack, Jira, Salesforce, Zendesk, and [many more](https://github.com/pipeshub-ai/pipeshub-ai#connectors) — to AI, with permissions enforced and every answer cited.

Each folder in this repository solves one problem, as a short tutorial that ends with something working. Find your problem below.

## Pick your problem

| Your problem | What you'll have at the end | Start here |
| --- | --- | --- |
| *"My coding assistant can't see our docs, tickets or chat, so it guesses."* | Claude Code, Cursor, Claude Desktop or Codex answering from your company's knowledge, with a source for every claim and only what you're allowed to see. About 10 minutes. | [Company Knowledge MCP](company-knowledge-mcp/) |
| *"I want 'what does the company know about X?' as a function call in my own tool or bot."* | A small program that searches and streams a cited answer, in Python, TypeScript or Go. | [SDK Starter](sdk-starter/) |
| *"We need one search box across every tool, that respects permissions, on our own servers."* | A one-file search page: a cited answer next to the matching records, each linking to the original. | [Private Enterprise Search](private-enterprise-search/) |
| *"Some of our documents live in no tool a connector covers."* | Your own files uploaded to a knowledge base from code, and a program that waits until they're searchable. | [Knowledge Base Upload](knowledge-base-upload/) |
| *"I'm building an app my whole team uses, and each person must see only their own documents."* | A web app where people sign in with PipesHub and every search runs as them (OAuth with PKCE). | [Sign in with PipesHub](sign-in-with-pipeshub/) |

### By team

Each Build Pack is a recipe for one team: the problem, the sources it reads, instructions for your AI client, the questions it answers and the records a good answer cites.

| Team | The question it answers | Pack |
| --- | --- | --- |
| Engineering | *"Why did we build it this way?"* — from incidents, pull requests, chat threads and design docs together. | [Engineering Knowledge Copilot](packs/engineering/) |
| Support | *"Has this happened before, who else hit it, and is it fixed?"* — from customer cases, escalations, runbooks and the engineering tickets behind them. | [Support Investigation Copilot](packs/support/) |
| Sales | *"What's the real state of this account before my renewal call, and what have we committed to?"* — from account plans, call notes, deal threads and support history. | [Account Intelligence](packs/sales/) |
| Marketing | *"When did it ship, what was the launch waiting for, and how did it do?"* — from launch plans, results, the launch channel and the engineering records. | [Marketing Launch Copilot](packs/marketing/) |
| Finance | *"Why was this invoice wrong, is it fixed, and what does the policy or contract say?"* — from finance tickets, policies, budget reviews and contracts. | [Finance Operations Copilot](packs/finance/) |
| People (HR) | *"What is the current policy, and is the handbook out of date?"* — from the handbook, People announcements and HR cases. | [People Policy Copilot](packs/hr/) |

Every pack works with your own connected tools today. To try one on the Acme Corp demo data first, you need the Demo connector (the first release after 0.8.0); most packs also need the extended demo data in [pipeshub-ai#3585](https://github.com/pipeshub-ai/pipeshub-ai/pull/3585), which isn't merged yet, and each pack's page says which of its questions do.

## Before you start

- **A running PipesHub** with at least one source connected and indexed. The tutorials' times start there. If you're starting from nothing, the [quickstart](https://github.com/pipeshub-ai/pipeshub-ai#-quickstart-recommended) gets you a local instance first. The MCP tutorial needs 0.7.0 or later.
- **A Personal Access Token** from **Workspace → Developer settings → Personal Access Tokens**. Sign in with PipesHub uses an OAuth app instead; its page says how to create one.

## Run one now

Already have PipesHub and a token? This connects Claude Code in one command (the [full tutorial](company-knowledge-mcp/) covers Cursor, Claude Desktop and Codex too):

```bash
export PIPESHUB_MCP_URL=http://localhost:3000/mcp     # https://<your-instance>/mcp for a remote PipesHub
export PIPESHUB_MCP_TOKEN=phpat_...                   # your Personal Access Token
claude mcp add --transport http pipeshub "$PIPESHUB_MCP_URL" \
  --header "Authorization: Bearer $PIPESHUB_MCP_TOKEN"
```

Then ask Claude Code something only your company would know, such as *"why did we change the payment service architecture?"*, and check that the answer names its sources.

## Why not just do RAG?

Every build here has a section called *"why naive RAG isn't enough."* The short version: connecting an AI to company data is easy; doing it so that people only see what they're allowed to, so that answers join records across systems that call the same thing by different names, and so that every claim points back to a source — that's the hard part, and it's what PipesHub does. The [MCP build](company-knowledge-mcp/#why-naive-rag-isnt-enough) walks through one concrete question that breaks naive RAG in four ways.

## Built something?

We feature community builds. Open a [showcase issue](https://github.com/pipeshub-ai/examples/issues/new?template=showcase.yml) — it takes five minutes — and add the badge to your README:

[![Built with PipesHub](https://img.shields.io/badge/Built%20with-PipesHub-0E7C86?style=flat-square)](https://github.com/pipeshub-ai/pipeshub-ai)

```markdown
[![Built with PipesHub](https://img.shields.io/badge/Built%20with-PipesHub-0E7C86?style=flat-square)](https://github.com/pipeshub-ai/pipeshub-ai)
```

## Related

- [pipeshub-ai/pipeshub-ai](https://github.com/pipeshub-ai/pipeshub-ai) — the platform
- [pipeshub-ai/mcp-server](https://github.com/pipeshub-ai/mcp-server) — full MCP tool reference and per-client setup, including OAuth apps for shared use
- SDKs: [Python](https://github.com/pipeshub-ai/pipeshub-sdk-python) · [TypeScript](https://github.com/pipeshub-ai/pipeshub-sdk-typescript) · [Go](https://github.com/pipeshub-ai/pipeshub-sdk-go)
- [Documentation](https://docs.pipeshub.com)

## License

Apache 2.0, the same as PipesHub.
