# Upload files to a knowledge base

**Put your own documents into PipesHub from code, and know when they're searchable.**

Connectors cover the systems your company already uses. For everything else — a folder of runbooks, exports from a tool without a connector, files your app generates — upload them to a knowledge base. This example does that in one short Go program.

## What it does

```bash
go run . "Team handbook" handbook.md onboarding.pdf
```

1. Finds the knowledge base called **Team handbook**, or creates it.
2. Uploads the files in one request, printing each file's result as the server streams it back. A file that is already there is skipped, so running it again is safe.
3. Waits until every file is indexed, so a search straight after finds them.

## Prerequisites

- Go 1.22 or later, and a PipesHub instance with an LLM and embedding model configured (indexing needs both).
- A **Personal Access Token with the `kb:write` scope.** Stock PipesHub doesn't offer `kb:write` to personal access tokens: its `MCP_SCOPES` setting lists read and search scopes only. Ask whoever runs your instance to add `kb:write` to `MCP_SCOPES`. Then create the token in **Workspace → Developer settings → Personal Access Tokens** with `kb:read` and `kb:write` selected.

```bash
export PIPESHUB_URL=http://localhost:3000      # your instance, no trailing path
export PIPESHUB_BEARER_AUTH=phpat_...          # the token with kb:write
```

## Run it

```bash
cd go
go run . "Team handbook" ~/docs/handbook.md ~/docs/onboarding.pdf
```

You should see:

```text
Created knowledge base "Team handbook"
Uploading 2 file(s)...
  uploaded handbook
  uploaded onboarding
Waiting for indexing....
Indexed 2 file(s).
```

Then ask about them with the [SDK starter](../sdk-starter/) or in the PipesHub chat. The knowledge base belongs to you; share it with others in PipesHub to let them search it.

## How it works

Three SDK calls on `client.KnowledgeBase`:

- `ListKnowledgeBases` / `CreateKnowledgeBase` to find or make the knowledge base.
- `UploadRecords` sends the files as one multipart request and answers with a stream of `file:succeeded` / `file:failed` events, then `done`.
- `GetKnowledgeHubChildNodes` (the knowledge base as the parent, flattened to its records) reports each record's `indexingStatus`. The program polls it until every file is `COMPLETED`, and stops on any status that won't get there.

## Customize it

- **Upload into a folder**: create one with `CreateFolder`, then pass its id as the last argument of `UploadRecords`.
- **Watch a directory**: call `upload` on new files, and let the duplicate check skip the ones already there.
- **Bigger batches**: `GetUploadLimits` tells you how many files and bytes one request may carry.
