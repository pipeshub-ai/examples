# Build with the PipesHub SDK

**Add permission-aware company knowledge to your own Python or TypeScript application.**

This is the smallest useful program you can write against PipesHub: search your company's knowledge, then ask a question and stream back a cited answer. It's the foundation for anything that needs "what does my company know about X?" as a function call — internal tools, Slack bots, support consoles, custom agents.

## What you'll build

A short script that:

1. Authenticates with a Personal Access Token
2. Runs a semantic search and prints the top results with their sources
3. Starts a conversation, streams the answer token by token, and prints the citations at the end

Both versions do the same thing:

| | |
|---|---|
| [`python/`](python/) | `pipeshub-sdk` on PyPI — [`main.py`](python/main.py) |
| [`typescript/`](typescript/) | `@pipeshub-ai/sdk` on npm — [`index.ts`](typescript/index.ts) |

A Go SDK also exists ([`pipeshub-ai/pipeshub-sdk-go`](https://github.com/pipeshub-ai/pipeshub-sdk-go)); the same two calls apply.

## Prerequisites

- A running PipesHub instance with an LLM provider configured and at least one source connected or some documents uploaded to a knowledge base. The [quickstart](https://github.com/pipeshub-ai/pipeshub-ai#-quickstart-recommended) gives you a local one at `http://localhost:3000`.
- A **Personal Access Token**: in PipesHub, go to **Workspace → Developer settings → Personal Access Tokens → New token**. The default scopes are enough.

Export the two values the SDK needs:

```bash
export PIPESHUB_URL=http://localhost:3000        # your instance, no trailing path
export PIPESHUB_BEARER_AUTH=phpat_eyJhbGciOi...         # the token you just minted
```

The SDKs read `PIPESHUB_BEARER_AUTH` automatically. `PIPESHUB_URL` is used by the scripts to build the API base URL.

## Run it

### Python

```bash
cd python
uv run main.py "what's our on-call policy?"        # or: pip install pipeshub-sdk && python main.py "..."
```

### TypeScript

```bash
cd typescript
npm install
npx tsx index.ts "what's our on-call policy?"
```

You should see a ranked list of matching records — each with a title, the app it came from, and a relevance score — followed by a streamed answer and the sources it drew on.

## How it works

Two calls do all the work.

**Search** returns ranked records with metadata about where each came from. It is permission-filtered *before* ranking, so a user only ever sees results they're allowed to see:

```python
res = pipeshub.semantic_search.search(query="on-call policy", limit=10)
```

**Streaming chat** starts a conversation and returns Server-Sent Events. The stream carries token chunks as they're generated, then a final `RUN_FINISHED` event with the complete persisted conversation — including citations:

```python
with pipeshub.conversations.stream_chat(query="what's our on-call policy?", chat_mode="internal_search") as stream:
    for event in stream:
        ...
```

Everything else — connectors, knowledge bases, agents, users — is on the same client object. The generated SDK reference lists every operation: [Python](https://github.com/pipeshub-ai/pipeshub-sdk-python#available-resources-and-operations) · [TypeScript](https://github.com/pipeshub-ai/pipeshub-sdk-typescript#available-resources-and-operations).

## Why not just call an LLM with your documents?

Because the hard part isn't the model. It's deciding *which* documents this particular user is allowed to see, finding the ones that are related across systems even when they use different names for the same thing, and being able to show where every claim came from. The two SDK calls above give you all three without building any of it. The [company-knowledge-mcp](../company-knowledge-mcp/#why-naive-rag-isnt-enough) example walks through a concrete failure case.

## Customize it

- **Narrow the search** with `filters={"apps": ["drive"]}` or `filters={"kb": [...]}` to search one connector or knowledge base.
- **Use a service account instead of a personal token** for a shared internal tool. Create an OAuth app in **Developer settings → OAuth Apps** and use the `client_credentials` grant; the SDK's `oauth2` security scheme handles the token exchange.
- **Point at PipesHub Cloud** by changing `PIPESHUB_URL` — nothing else in the code changes.

## Next steps

- Wrap the streaming call in a Slack bot, a CLI, or an internal web page — that's already a working internal assistant.
- Let an AI coding assistant use the same retrieval directly: [company-knowledge-mcp](../company-knowledge-mcp/).
- Put it behind a search box for the whole team: [private-enterprise-search](../private-enterprise-search/).
