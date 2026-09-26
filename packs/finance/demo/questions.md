# Questions for the Acme Corp demo data

Three questions to try once the Demo connector has indexed. Each one needs the right records to
answer well. "Should cite" lists the records a good answer draws on, by the
titles they have in PipesHub.

| # | Question | Should cite |
| --- | --- | --- |
| 1 | Why was Contoso's invoice wrong, and has the billing rule been fixed? | FIN-38, and FIN-37 or SUP-121 |
| 2 | How much can I spend on a purchase without my manager's approval? | The expense policy |
| 3 | What rate do we pay for card processing? | The payment processing agreement 2026 (Alice only) |

## What to look for

- **Question 1** separates two fixes: FIN-37 reissued Contoso's April invoice
  on 22 April, and FIN-38 fixed the VAT rule itself on 6 May (it ignored the
  reverse-charge flag for lines added mid-term), after which three other April
  invoices were found and reissued.
- **Question 2** should give the thresholds from the expense policy: up to
  $250 needs no approval, more than $250 and up to $2,500 needs the manager,
  and anything above that, or any software subscription, goes to finance
  through a FIN ticket. The answer should say plainly that up to $250 needs no
  approval.
- **Question 3** is the permission lesson, below.

## Permissions

The payment processing agreement is in a restricted folder. Ask *"What rate do
we pay for card processing?"*:

- signed in as **Alice**, who is a payments contract reader, the answer cites
  the agreement: 2.2% plus 20 cents per successful charge, on
  interchange-plus pricing for cards issued in the EU;
- signed in as **Bob**, who isn't, the agreement does not come back, and the
  answer should not estimate a rate from the budget review, which mentions
  card processing fees without the rate.

## Test runs

Two runs of each question on 26 September 2026, on the current demo data,
signed in as each sample user. PipesHub's agent does not have this pack's
instructions, so these runs check the data and the permissions rather than the
instructions. Agent answers vary from run to run; treat this as a guide.
Questions 1 and 2 ran in PipesHub's agent mode and in its search mode;
question 3 ran in search mode.

| # | Signed in as | Result | What the runs cited |
| --- | --- | --- | --- |
| 1 | Alice | 4 of 4 | FIN-37 and FIN-38 in every run, plus SUP-121 in search mode. |
| 1 | Bob | 4 of 4 | FIN-37 and FIN-38 in every run. |
| 2 | Alice | 4 of 4 | The expense policy: up to $250 per purchase without approval, the manager above that up to $2,500, finance above $2,500. |
| 2 | Bob | 4 of 4 | The expense policy, with the same limits. |
| 3 | Alice | 2 of 2 | The payment processing agreement. |
| 3 | Bob (no access) | 2 of 2 | No leak: both answers cited only the Q2 budget review and did not give the rate. |

Every answer was correct. In agent mode, one run of question 2 for each user
first failed the automated check. The answer said "without any approval", a
wording the check did not yet accept, and the check now accepts it. Six more
agent-mode runs of question 2 all gave the $250 limit and said no approval is
needed. No answer contained a link to the made-up demo sites.
