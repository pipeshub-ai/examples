# Questions for the Acme Corp demo data

Three questions to try once the Demo connector has indexed. Each one needs the right records to
answer well. "Should cite" lists the records a good answer draws on, by the
titles they have in PipesHub.

| # | Question | Should cite |
| --- | --- | --- |
| 1 | Is the Northwind Traders renewal at risk, and what is being done about it? | The Northwind Traders account plan and the call notes of 16 April; ideally also the `#deals` thread of 10 April |
| 2 | What discount did the deal desk approve for the Northwind renewal? | The deal desk decision on the Northwind renewal (Bob only) |
| 3 | How should I handle a renewal when the customer has an open support escalation? | The renewal playbook |

## What to look for

- **Question 1** has a history. From early April the renewal was at risk: the
  failing exports broke Northwind's monthly reporting, and on 10 April the
  `#deals` thread asked when the fix would land. After the fix shipped, the
  16 April call put it back on track, and the account plan was updated the
  same day. A good answer gives the current state first (on track, renewal
  expected on time) and says why it changed.
- **Question 2** is the permission lesson, below.
- **Question 3** should come from the renewal playbook, not from one account's
  history.

## Permissions

The deal desk's decisions are in a restricted folder. Ask *"What discount did
the deal desk approve for the Northwind renewal?"*:

- signed in as **Bob**, who is on the deal desk, the answer cites the deal
  desk decision: a 14% discount, conditional on a three-year term and an
  expansion to 600 seats;
- signed in as **Alice**, who isn't, the decision does not come back, and the
  answer should say it cannot find one rather than guess.

## Test runs

Two runs of each question on 26 September 2026, in PipesHub's own agent mode,
signed in as each sample user. PipesHub's agent does not have this pack's
instructions, so these runs check the data and the permissions rather than the
instructions. Agent answers vary from run to run; treat this as a guide.

| # | Signed in as | Result | What the runs cited |
| --- | --- | --- | --- |
| 1 | Alice | 2 of 2 | The account plan and the 16 April call notes, plus the `#deals` thread. Both answers said the renewal was at risk and is now back on track. |
| 1 | Bob | 2 of 2 | The account plan and the 16 April call notes. Both answers described the fix and the follow-up since; one said plainly that the risk had been mitigated. |
| 2 | Alice (no access) | 2 of 2 | No leak: neither answer gave a discount. Both said the records she can see don't state the approved figure. |
| 2 | Bob | 2 of 2 | The deal desk decision: 14% for a three-year term with expansion to 600 seats. |
| 3 | Alice | 2 of 2 | The renewal playbook. |
| 3 | Bob | 2 of 2 | The renewal playbook, once alongside the Northwind account plan. |

Every run passed. In question 1, the answers went on from the older at-risk
warning to the recovery after the fix, rather than stopping at the warning.
