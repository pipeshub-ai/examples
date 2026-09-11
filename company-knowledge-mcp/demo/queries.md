# Questions worth asking

The best questions for a company-knowledge assistant force it to **combine sources** — a decision recorded in a doc, argued in chat, and shipped in a pull request. Questions that a single document answers are fine, but they don't show what PipesHub adds.

Adapt these to your own data. Each one lists what a good answer should pull together.

## Engineering

- *Why did we change the retry logic in the billing worker?* — a PR, the incident or ticket that prompted it, the chat thread where it was discussed, and the design doc.
- *What changed between the last two releases of the mobile app?* — release notes, merged PRs, and any tickets they close.
- *Which incidents in the last six months touched the search service?* — incident tickets and postmortems, linked back to the components they name.
- *Who has worked on the ingestion pipeline recently?* — commit and PR authors, ticket assignees, thread participants.
- *What was the reasoning behind moving to a queue for exports?* — the design doc and the discussion around it.

## Sales

- *What's the current state of the Northwind account?* — CRM record, recent meeting notes, open opportunities, recent email threads.
- *What have we committed to Northwind in writing?* — proposals, contract addenda, and emails that promise dates or features.
- *What are the biggest risks in this quarter's pipeline?* — opportunity stages, stalled deals, and notes mentioning blockers.
- *Who are the decision-makers at Northwind and when did we last talk to each?* — contacts, calendar, and meeting notes.

## Support

- *Why is customer X seeing export timeouts, and is there an open engineering ticket?* — the support ticket, related past tickets, the engineering issue, and any release that touched exports.
- *Has anyone reported this error message before, and what fixed it?* — historical tickets and the resolution notes attached to them.
- *What workaround did we give customers during the March outage?* — the incident channel and the macros or docs written at the time.

## Marketing, Finance, HR

- *What did we learn from the Q2 launch campaign?* — the retro doc, analytics summary, and channel discussion.
- *What assumptions drive the latest revenue forecast?* — the forecast model doc and the finance thread reviewing it.
- *What's the policy on carrying over unused leave, and has it changed this year?* — the handbook, the policy update announcement, and the HR channel.

## A note on demo data

A ready-made demo company ("Acme Corp") with interconnected engineering, sales, and support data — so you can try these questions before connecting anything — is being built. Until it ships, the fastest way to try this on a fresh install is to upload a few related documents to a knowledge base: a design doc, the meeting notes that led to it, and the summary that followed.
