# What can I build with PipesHub?

[PipesHub](https://github.com/pipeshub-ai/pipeshub-ai) is an open-source platform that connects your company's knowledge — Google Drive, GitHub, Slack, Jira, Salesforce, Zendesk, and [many more](https://github.com/pipeshub-ai/pipeshub-ai#connectors) — to AI, with permissions enforced and every answer cited. This repository is the set of things you can build on it, each one a short tutorial that ends with something working.

## Start with what you're building

| | Build | Time |
|---|---|---|
| **01** | [**Company Knowledge MCP**](company-knowledge-mcp/) — give Claude Code, Cursor, Claude Desktop, or Codex secure access to your company's knowledge. One token, one config file. | ~10 min |
| **02** | [**Private Enterprise Search**](private-enterprise-search/) — a permission-aware, citation-backed search page across everything, on your own infrastructure. One file. | ~15 min |
| **03** | [**SDK Starter**](sdk-starter/) — add "what does my company know about X?" to your own Python or TypeScript application. Two calls. | ~10 min |

All three assume you have a running PipesHub instance. The [quickstart](https://github.com/pipeshub-ai/pipeshub-ai#-quickstart-recommended) gives you one locally with Docker in a few minutes.

## Build for your team

The same platform, packaged as recipes for specific teams. Each Build Pack describes the problem, the data sources, an agent configuration, the questions it answers, and why a plain vector search couldn't. **Coming soon** — Engineering first, then Sales and Support.

- **Engineering** — Engineering Knowledge Copilot: *why did we make this architectural decision? What changed between these two releases? Which incidents touched this component?*
- **Sales** — Account Intelligence: *what's the current state of this account? What have we committed to? Who are the decision-makers?*
- **Support** — Support Investigation Copilot: *why is this customer seeing this? Has it happened before? Is there an engineering ticket?*
- **Marketing**, **Finance**, **HR** — Campaign Intelligence, Finance Knowledge Assistant, Employee Policy Assistant.

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
