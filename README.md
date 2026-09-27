# What can I build with PipesHub?

[PipesHub](https://github.com/pipeshub-ai/pipeshub-ai) is an open-source platform that connects your company's knowledge — Google Drive, GitHub, Slack, Jira, Salesforce, Zendesk, and [many more](https://github.com/pipeshub-ai/pipeshub-ai#connectors) — to AI, with permissions enforced and every answer cited. This repository is the set of things you can build on it, each one a short tutorial that ends with something working.

## Start here

### [Company Knowledge MCP](company-knowledge-mcp/) — about 10 minutes

Give Claude Code, Cursor, Claude Desktop, or Codex secure access to your company's knowledge. One token, one command. Your assistant answers *"why did we change the payment service architecture?"* with the pull request, the ticket, the chat thread, and the design doc — each cited, and only if you're allowed to see them.

The ten minutes assumes PipesHub is already running with data indexed (requires 0.7.0 or later). If you're starting from nothing, the [quickstart](https://github.com/pipeshub-ai/pipeshub-ai#-quickstart-recommended) gets you a local instance first.

### Also in this repo

- [**SDK Starter**](sdk-starter/) — the two calls behind everything (semantic search, streaming cited answers) in Python, TypeScript and Go, for when you want this inside your own application.
- [**Private Enterprise Search**](private-enterprise-search/) — those same two calls behind a search box, as a one-file app you can build a front end on.
- [**Knowledge Base Upload**](knowledge-base-upload/) — upload your own files to a knowledge base from code and wait until they are searchable, in Go.
- [**Sign in with PipesHub**](sign-in-with-pipeshub/) — an app other people sign in to, where each person searches only what they may see (OAuth with PKCE), in TypeScript.

## Build for your team

The same platform, packaged as recipes for specific teams. Each Build Pack describes the problem, the data sources, an agent configuration, the questions it answers, and why a plain vector search couldn't. Packs marked *coming* aren't written yet. Once the Demo connector ships (in the first release after 0.8.0), you can try a pack on the Acme Corp demo data before connecting anything. Most packs also need the extended demo data in [pipeshub-ai#3585](https://github.com/pipeshub-ai/pipeshub-ai/pull/3585), which isn't merged yet; each pack's page says which of its questions do. Until then, any pack works with your own connected tools.

- [**Engineering Knowledge Copilot**](packs/engineering/) — *why did we build it this way?* Answers from incidents, pull requests, chat threads and design docs together, with a source for every claim. Works on your own connected data today; its demo walkthrough needs the Demo connector from the first release after 0.8.0.

- [**Support Investigation Copilot**](packs/support/) — *why is this customer seeing this? Has it happened before? Is there an engineering ticket?* Answers from customer cases, escalations, runbooks and the engineering and finance tickets behind them. Works on your own connected data today; its demo walkthrough needs the Demo connector from the first release after 0.8.0, and one of its three questions also needs the extended demo data in [pipeshub-ai#3585](https://github.com/pipeshub-ai/pipeshub-ai/pull/3585).

- [**Account Intelligence**](packs/sales/) — *what's the current state of this account? What have we committed to? Who are the decision-makers?* Answers from account plans, call notes, the deals channel, the customer's support history and deal desk decisions. Works on your own connected data today; its demo walkthrough needs the Demo connector from the first release after 0.8.0 and the extended demo data in [pipeshub-ai#3585](https://github.com/pipeshub-ai/pipeshub-ai/pull/3585).

- [**Marketing Launch Copilot**](packs/marketing/) — *when did this ship, what was it waiting for, and how did the launch do?* Answers from launch plans, results, the launch channel and the engineering records a launch depends on. Works on your own connected data today; its demo walkthrough needs the Demo connector from the first release after 0.8.0 and the extended demo data in [pipeshub-ai#3585](https://github.com/pipeshub-ai/pipeshub-ai/pull/3585).

- [**Finance Operations Copilot**](packs/finance/) — *why was this invoice wrong, what's the policy, what does the contract say?* Answers from finance tickets, policies, budget reviews and contracts. Works on your own connected data today; its demo walkthrough needs the Demo connector from the first release after 0.8.0 and the extended demo data in [pipeshub-ai#3585](https://github.com/pipeshub-ai/pipeshub-ai/pull/3585).

- [**People Policy Copilot**](packs/hr/) — *what is the current policy, and has it changed since the handbook was written?* Answers from the handbook, People announcements and HR cases, and says when the handbook is out of date. Works on your own connected data today; its demo walkthrough needs the Demo connector from the first release after 0.8.0 and the extended demo data in [pipeshub-ai#3585](https://github.com/pipeshub-ai/pipeshub-ai/pull/3585).

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
