# Sign in with PipesHub

**Build an app other people use, where each person searches only what they're allowed to see.**

A personal access token is right for your own scripts. An app for your team is different: each person signs in, approves what the app may do, and every search runs as them. So the answers respect their permissions, not yours. That's OAuth 2.0 with the authorization code flow and PKCE, and this example is a working version in one TypeScript file with no web framework.

## What you'll build

A small web app on `http://localhost:8888`:

1. **Sign in with PipesHub** sends the person to PipesHub to sign in and approve the app's access.
2. PipesHub sends them back with a one-time code, which the app exchanges for their tokens. PKCE ties the code to this browser session, so an intercepted code is useless.
3. A search box runs searches **as that person**. Two people searching the same words see different results if they can see different documents.
4. When the access token expires, the app uses the refresh token once and retries. **Sign out** forgets the tokens.

## Prerequisites

- Node.js 20 or later, and a running PipesHub instance.
- An **OAuth app**. In PipesHub, go to **Workspace → Developer settings → OAuth Apps → New app**:
  - **Redirect URI:** `http://localhost:8888/callback`
  - **Scopes:** `openid`, `profile`, `semantic:write` (search), `offline_access` (refresh tokens)

  Keep the client secret on the server. It never goes to the browser.

```bash
export PIPESHUB_URL=http://localhost:3000       # your instance, no trailing path
export PIPESHUB_CLIENT_ID=...
export PIPESHUB_CLIENT_SECRET=...
```

## Run it

```bash
cd typescript
npm install
npx tsx server.ts
```

Open `http://localhost:8888`, sign in, approve, and search. To see permissions at work, sign in as two different people (in two browsers) and search for the same thing.

## How it works

| Step | Request |
|---|---|
| Send the person to sign in | `GET /api/v1/oauth2/authorize?response_type=code&client_id=…&redirect_uri=…&scope=…&state=…&code_challenge=…&code_challenge_method=S256` |
| Exchange the code | `POST /api/v1/oauth2/token` with `grant_type=authorization_code`, the code, the redirect URI, the client id and secret, and the PKCE `code_verifier` |
| Search as them | `POST /api/v1/search` with `Authorization: Bearer <their access token>` |
| Refresh | `POST /api/v1/oauth2/token` with `grant_type=refresh_token` |

The app keeps tokens in server memory, keyed by an `HttpOnly` session cookie, and checks that the `state` returned to `/callback` belongs to the same browser that started the sign-in.

## Customize it

- **Ask a question as well**: add `conversation:chat` and `conversation:write` to the app's scopes and `SCOPES`, then call `/api/v1/conversations/stream` with the person's token, as in the [SDK starter](../sdk-starter/).
- **Use the SDK**: pass the person's access token as `bearerAuth` to `@pipeshub-ai/sdk`. Everything else in the [SDK starter](../sdk-starter/) works unchanged.
- **Deploy it**: store sessions somewhere shared (a database or Redis) instead of memory, serve it over HTTPS, and register the production redirect URI on the OAuth app.
- **Not `client_credentials`**: that grant has no person behind it, so PipesHub can't filter results by who is asking. Use it only for jobs that don't read company content.
