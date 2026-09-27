// Sign in with PipesHub: an app other people use, where each person searches
// only what they are allowed to see. OAuth 2.0 authorization code flow with PKCE.
//
//   export PIPESHUB_URL=http://localhost:3000
//   export PIPESHUB_CLIENT_ID=... PIPESHUB_CLIENT_SECRET=...
//   npx tsx server.ts        # then open http://localhost:8888
import { createHash, randomBytes } from "node:crypto";
import { createServer, type IncomingMessage, type ServerResponse } from "node:http";

const PIPESHUB_URL = (process.env.PIPESHUB_URL ?? "http://localhost:3000").replace(/\/+$/, "");
const CLIENT_ID = process.env.PIPESHUB_CLIENT_ID ?? "";
const CLIENT_SECRET = process.env.PIPESHUB_CLIENT_SECRET ?? "";
const PORT = Number(process.env.PORT ?? 8888);
const REDIRECT_URI = process.env.REDIRECT_URI ?? `http://localhost:${PORT}/callback`;
// Search needs semantic:write; offline_access returns a refresh token.
const SCOPES = process.env.SCOPES ?? "openid profile semantic:write offline_access";

if (!CLIENT_ID || !CLIENT_SECRET) {
  console.error("Set PIPESHUB_CLIENT_ID and PIPESHUB_CLIENT_SECRET (Workspace -> Developer settings -> OAuth apps).");
  process.exit(1);
}

type Tokens = { access_token: string; refresh_token?: string };
// In memory, keyed by a random session cookie. A real app keeps these server-side too, never in the browser.
const pending = new Map<string, { verifier: string; session: string }>(); // OAuth state -> PKCE verifier
const sessions = new Map<string, Tokens>();

const b64url = (b: Buffer) => b.toString("base64url");

function sessionOf(req: IncomingMessage): string | undefined {
  return /(?:^|;\s*)sid=([^;]+)/.exec(req.headers.cookie ?? "")?.[1];
}

function page(res: ServerResponse, body: string, status = 200, headers: Record<string, string> = {}) {
  res.writeHead(status, { "Content-Type": "text/html; charset=utf-8", ...headers });
  res.end(`<!doctype html><meta charset="utf-8"><title>Sign in with PipesHub</title>
<body style="font-family:system-ui;max-width:42rem;margin:3rem auto;padding:0 1rem">${body}</body>`);
}

const esc = (s: string) => s.replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`);

// Step 1: send the person to PipesHub to sign in and approve, with a PKCE challenge.
function login(res: ServerResponse) {
  const session = b64url(randomBytes(24));
  const state = b64url(randomBytes(16));
  const verifier = b64url(randomBytes(32));
  pending.set(state, { verifier, session });
  const url = new URL("/api/v1/oauth2/authorize", PIPESHUB_URL);
  url.search = new URLSearchParams({
    response_type: "code",
    client_id: CLIENT_ID,
    redirect_uri: REDIRECT_URI,
    scope: SCOPES,
    state,
    code_challenge: b64url(createHash("sha256").update(verifier).digest()),
    code_challenge_method: "S256",
  }).toString();
  res.writeHead(302, { Location: url.toString(), "Set-Cookie": `sid=${session}; HttpOnly; SameSite=Lax; Path=/` });
  res.end();
}

async function tokenRequest(body: Record<string, string>): Promise<Tokens> {
  const r = await fetch(`${PIPESHUB_URL}/api/v1/oauth2/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ client_id: CLIENT_ID, client_secret: CLIENT_SECRET, ...body }),
  });
  if (!r.ok) throw new Error(`token request failed: ${r.status} ${await r.text()}`);
  return (await r.json()) as Tokens;
}

// Step 2: PipesHub redirects back with a code; exchange it (and the PKCE verifier) for tokens.
async function callback(req: IncomingMessage, res: ServerResponse, query: URLSearchParams) {
  const flow = pending.get(query.get("state") ?? "");
  pending.delete(query.get("state") ?? "");
  if (!flow || flow.session !== sessionOf(req)) return page(res, "<p>This sign-in link expired. <a href='/login'>Try again</a>.</p>", 400);
  if (query.get("error")) return page(res, `<p>Sign-in was not approved: ${esc(query.get("error") ?? "")}.</p><a href="/">Back</a>`, 400);
  const tokens = await tokenRequest({
    grant_type: "authorization_code",
    code: query.get("code") ?? "",
    redirect_uri: REDIRECT_URI,
    code_verifier: flow.verifier,
  });
  sessions.set(flow.session, tokens);
  res.writeHead(302, { Location: "/" });
  res.end();
}

// Step 3: call PipesHub as that person. Results are filtered to what they may see.
async function search(session: string, q: string): Promise<{ title: string; source: string }[]> {
  const call = (t: Tokens) =>
    fetch(`${PIPESHUB_URL}/api/v1/search`, {
      method: "POST",
      headers: { Authorization: `Bearer ${t.access_token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ query: q, limit: 10 }),
    });
  let tokens = sessions.get(session)!;
  let r = await call(tokens);
  if (r.status === 401 && tokens.refresh_token) {
    // The access token expired: use the refresh token once, then retry.
    tokens = { refresh_token: tokens.refresh_token, ...(await tokenRequest({ grant_type: "refresh_token", refresh_token: tokens.refresh_token })) };
    sessions.set(session, tokens);
    r = await call(tokens);
  }
  if (!r.ok) throw new Error(`search failed: ${r.status} ${await r.text()}`);
  const body = (await r.json()) as { searchResponse?: { searchResults?: { metadata?: Record<string, string> }[] } };
  const seen = new Set<string>();
  const results: { title: string; source: string }[] = [];
  for (const hit of body.searchResponse?.searchResults ?? []) {
    const m = hit.metadata ?? {};
    if (!m.recordId || seen.has(m.recordId)) continue;
    seen.add(m.recordId);
    results.push({ title: m.recordName ?? "(untitled)", source: m.connectorName ?? m.connector ?? "knowledge base" });
  }
  return results;
}

async function home(req: IncomingMessage, res: ServerResponse, query: URLSearchParams) {
  const session = sessionOf(req);
  if (!session || !sessions.has(session)) {
    return page(res, `<h1>Sign in with PipesHub</h1><p>Search your company's knowledge as yourself.</p><p><a href="/login">Sign in with PipesHub</a></p>`);
  }
  const q = query.get("q") ?? "";
  let list = "";
  if (q) {
    const results = await search(session, q);
    list = results.length
      ? `<ol>${results.map((r) => `<li>${esc(r.title)} <small>[${esc(r.source)}]</small></li>`).join("")}</ol>`
      : "<p>No results you can see.</p>";
  }
  page(res, `<h1>Search</h1><form><input name="q" value="${esc(q)}" size="40" autofocus> <button>Search</button></form>${list}<p><a href="/logout">Sign out</a></p>`);
}

createServer(async (req, res) => {
  const url = new URL(req.url ?? "/", `http://localhost:${PORT}`);
  try {
    if (url.pathname === "/login") return login(res);
    if (url.pathname === "/callback") return await callback(req, res, url.searchParams);
    if (url.pathname === "/logout") {
      const s = sessionOf(req);
      if (s) sessions.delete(s);
      res.writeHead(302, { Location: "/", "Set-Cookie": "sid=; Max-Age=0; Path=/" });
      return res.end();
    }
    if (url.pathname === "/") return await home(req, res, url.searchParams);
    page(res, "<p>Not found.</p>", 404);
  } catch (err) {
    console.error(err);
    page(res, `<p>Something went wrong: ${esc((err as Error).message)}</p><a href="/">Back</a>`, 500);
  }
}).listen(PORT, () => console.log(`Open http://localhost:${PORT}`));
