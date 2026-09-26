# Questions for the Acme Corp demo data

Three questions to try once the Demo connector has indexed. Each one needs the right records to
answer well. "Should cite" lists the records a good answer draws on, by the
titles they have in PipesHub.

| # | Question | Should cite |
| --- | --- | --- |
| 1 | How many days of unused annual leave can I carry over into next year? | The `#people` announcement of 2 March or HR0001203; ideally also the handbook, to show it is out of date |
| 2 | What should a new engineer do in their first week? | New engineer onboarding: first week checklist |
| 3 | What is the salary band for a senior engineer? | Compensation bands 2026 (Bob only) |

## What to look for

- **Question 1** is the one to show first. The handbook says three days. The
  `#people` announcement of 2 March says five, starting with leave left over
  at the end of 2026, and HR0001203 confirms the announcement is the current
  policy until the handbook is updated. A good answer says five, and says why
  the handbook disagrees.
- **Question 2** should come from the onboarding checklist, under its *First
  week* heading: ship a small change with your buddy, read the on-call handbook (the on-call shadow week is in the
  second month, not the first), and read the team's last two postmortems.
- **Question 3** is the permission lesson, below.

## Permissions

The compensation bands are in a restricted folder. Ask *"What is the salary band
for a senior engineer?"*:

- signed in as **Bob**, who is a people manager, the answer cites Compensation
  bands 2026: $152,000 to $168,000 for a senior engineer (L5), United States
  base salary;
- signed in as **Alice**, who isn't, the bands do not come back. In our test
  runs the answer said it couldn't find a compensation document; the pack's
  instructions also ask the agent to point her to the People team rather than
  estimate.

## Test runs

Two runs of each question on 26 September 2026, in PipesHub's own agent mode,
signed in as each sample user. PipesHub's agent does not have this pack's
instructions, so these runs check the data and the permissions rather than the
instructions. Agent answers vary from run to run; treat this as a guide.
Question 2 was run again, four times per person, after the demo data gave the
checklist its current title and opening.

| # | Signed in as | Result | What the runs cited |
| --- | --- | --- | --- |
| 1 | Alice | 2 of 2 | The `#people` announcement. Both answers said five days and that the handbook update is pending. |
| 1 | Bob | 2 of 2 | The `#people` announcement or HR0001203, with the same answer. |
| 2 | Alice | 4 of 4 | The onboarding checklist, in every run. (Before the checklist was retitled: 1 of 2; the miss gave its steps without a citation.) |
| 2 | Bob | 4 of 4 | The onboarding checklist, in every run. (Before the checklist was retitled: 1 of 2; the miss was a generic first-week plan with no citation.) |
| 3 | Alice (no access) | 2 of 2 | No leak: neither answer named a band. Both said they couldn't find a compensation document. |
| 3 | Bob | 2 of 2 | Compensation bands 2026: $152,000 to $168,000 for a senior engineer. |

Every run passed on the current data. Question 2 was the weak one before: its
checklist used to be titled "Onboarding checklist — engineers", and in two of
four runs the agent answered without citing it.
