# Questions for the Acme Corp demo data

Three questions to try once the Demo connector has indexed. Each one needs the right records to
answer well. "Should cite" lists the records a good answer draws on, by the
titles they have in PipesHub.

| # | Question | Should cite |
| --- | --- | --- |
| 1 | When did we launch background exports, and why did we pick that date? | The background exports launch plan; ideally also the `#launch` go/no-go thread, PR #211 or the April release notes |
| 2 | How did the background exports launch campaign perform? | The background exports launch results |
| 3 | What is the next product we are launching after background exports? | The embargoed next-launch brief (Alice only) |

## What to look for

- **Question 1** crosses into engineering: the launch on 21 April waited for
  PR #211 to be in production for a week of real customer exports (it shipped
  on 14 April), and the `#launch` thread records engineering's go.
- **Question 2** should quote the results document's numbers for the two weeks
  after launch: a 41% open rate on the admin email, 312 background exports in
  the first week, and export tickets down from 14 to 2.
- **Question 3** is the permission lesson, below.

## Permissions

The next launch is embargoed in a restricted folder. Ask *"What is the next
product we are launching after background exports?"*:

- signed in as **Alice**, who is on the launch core team, the answer cites the
  embargoed brief (Acme Insights, announced on 9 September). The pack's
  instructions ask the agent to say it is embargoed; PipesHub's own agent,
  which doesn't have them, did not in our test runs;
- signed in as **Bob**, who isn't, the brief does not come back.

## Test runs

Two runs of each question on 26 September 2026, in PipesHub's own agent mode,
signed in as each sample user. PipesHub's agent does not have this pack's
instructions, so these runs check the data and the permissions rather than the
instructions. Agent answers vary from run to run; treat this as a guide.

| # | Signed in as | Result | What the runs cited |
| --- | --- | --- | --- |
| 1 | Alice | 2 of 2 | The launch plan and the `#launch` go/no-go thread, both runs. |
| 1 | Bob | 2 of 2 | The launch plan in both, and the `#launch` thread in one. |
| 2 | Alice | 2 of 2 | The launch results (with the launch plan in one run). |
| 2 | Bob | 2 of 2 | The launch results. |
| 3 | Alice | 2 of 2 | The embargoed brief: Acme Insights, announced on 9 September. Neither answer warned that it is embargoed; the pack's instructions ask the agent to. |
| 3 | Bob (no access) | 2 of 2 | No leak: the brief was never cited and Acme Insights never named. Both answers said the records don't show what launches next. |
