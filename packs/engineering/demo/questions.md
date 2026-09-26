# Five questions for the Acme Corp demo data

These are the questions to try once the Demo connector has indexed. Each one
needs more than one system to answer well. "Should cite" lists the records a
good answer draws on, by the titles they have in PipesHub.

The results column is one run in PipesHub's agent mode, signed in as the
sample user Bob, on 26 September 2026. Agent answers vary from run to run, so
treat it as a guide rather than a guarantee.

| # | Question | Should cite | What the run cited |
| --- | --- | --- | --- |
| 1 | Why was the payment service architecture changed, and how was the decision made? | INC-2031; the `#eng-payments` thread of 15 March; the "Billing worker resilience" design doc; PR #482 | The incident, the thread and PR #482. It left out the design doc. |
| 2 | Who reviewed and approved PR #482 in the billing worker, and what did Dana ask for before it merged? | PR #482 and its two review comments (Dana Okafor, Marcus Webb) | PR #482 only, but the answer was right: both reviewers approved, and Dana asked for an explicit 120-second bucket in the `billing_retry_delay_seconds` histogram. |
| 3 | What caused the export timeouts on large workspaces, and how did we fix it? | Issue #207; PR #211; SUP-114; the `#eng-exports` thread of 4 April | Issue #207, PR #211 and SUP-114. |
| 4 | Has the billing worker retry change worked since it shipped, and what follow-up was agreed? | The payments team sync of 7 April; Priya's `#eng-payments` message of 22 March | Both, plus INC-2031 and PR #482. |
| 5 | What's our policy on being on-call over a public holiday? | The engineering on-call handbook | The handbook. |

## What to look for

- **Question 1** is the one to show first. The answer is spread across an
  incident in Jira, a Slack thread, a design doc in Drive and a pull request
  in GitHub, and no single one of them tells the whole story.
- **Question 1 also has a gap in it.** The design doc says the options (fixed
  interval, backoff without jitter, equal jitter, full jitter) were weighed in
  the Slack thread, but the thread itself only compares full jitter with equal
  jitter. A careful answer says so. In the run above the agent repeated the
  design doc's version, which is why the pack's instructions ask it to flag
  disagreements between sources.
- **Question 3** starts with customers: three ServiceNow cases (Northwind
  Traders, Contoso, Fabrikam) escalated as SUP-114, tracked as issue #207 and
  fixed by PR #211.

## Permissions

The demo has one restricted area, the pricing committee's folder and channel.
It isn't an engineering question, but it shows that every agent in this pack
only sees what the signed-in person may see. Ask *"What is the enterprise
pricing strategy for 2026?"*:

- signed in as **Bob**, who is on the pricing committee, a search returns the
  "Enterprise pricing strategy 2026" document and the committee's thread;
- signed in as **Alice**, who isn't, neither of them comes back.

Both were checked with a plain search on the same day.
