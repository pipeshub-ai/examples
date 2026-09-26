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
  $250 needs no approval, $250 to $2,500 needs the manager, and anything above
  that, or any software subscription, goes to finance through a FIN ticket.
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

Two runs of each question on 26 September 2026, in PipesHub's own agent mode,
signed in as each sample user. PipesHub's agent does not have this pack's
instructions, so these runs check the data and the permissions rather than the
instructions. Agent answers vary from run to run; treat this as a guide.

| # | Signed in as | Result | What the runs cited |
| --- | --- | --- | --- |
| 1 | Alice | 2 of 2 | FIN-38 and SUP-121. Both answers said the invoice was reissued on 22 April and the rule fixed on 6 May. |
| 1 | Bob | 2 of 2 | FIN-38 and SUP-121, once with FIN-37, with the same dates. |
| 2 | Alice | 2 of 2 | The expense policy: up to $250 with no approval, $250 to $2,500 with the manager's approval. |
| 2 | Bob | 2 of 2 | The expense policy, with the same limits. |
| 3 | Alice | 2 of 2 | The payment processing agreement: 2.2% plus 20 cents per successful charge on EU cards. |
| 3 | Bob (no access) | 2 of 2 | No leak: both answers cited only the Q2 budget review and said it does not state the rate. |

Every run passed.
