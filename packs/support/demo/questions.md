# Questions for the Acme Corp demo data

Three questions to try once the Demo connector has indexed. Questions 1 and 3
work on the demo data as it ships; question 2 needs the finance tickets from
the extended demo data in [pipeshub-ai#3585](https://github.com/pipeshub-ai/pipeshub-ai/pull/3585), which is not merged yet. Each one needs the
right records to answer well. "Should cite" lists the records a good answer draws on, by the
titles they have in PipesHub.

| # | Question | Should cite |
| --- | --- | --- |
| 1 | Which customers reported export timeouts, and what fixed it? | Any of PR #211, issue #207 or the Export runbook, and ideally the three ServiceNow cases and SUP-114 |
| 2 | What happened with Contoso's invoice that showed VAT on an exempt line? | FIN-37 or FIN-38, and ideally SUP-121; the answer should say the invoice was reissued or credited |
| 3 | A customer says their workspace export timed out. What should I check? | The Export runbook |

## What to look for

- **Question 1** starts with three customers (Northwind Traders, Contoso and
  Fabrikam), follows their cases into the SUP-114 escalation, and ends at the
  engineering fix, PR #211, which moved large exports to a background queue on
  14 April.
- **Question 2** crosses into finance: the support escalation SUP-121 is
  closed, but says only that finance resolved it and names their tickets. What
  was done, and when, is in those tickets: the reissued invoice (FIN-37,
  22 April) and the fix to the billing rule itself (FIN-38, 6 May). A good
  answer follows SUP-121 there.
- **Question 3** should come from the runbook, which describes how exports
  work since the fix, not from the older cases that describe the timeout.

## Permissions

The support records are readable by the demo's Support readers group, and both
sample users are in it, so this pack has no permission lesson of its own.
Everything it returns is still filtered by the signed-in person: someone who is
not in the Support readers group would not see these cases. The Engineering
pack's pricing question shows the difference between two people directly.

## Test runs

Two runs of each question on 26 September 2026, in PipesHub's own agent mode,
signed in as each sample user. PipesHub's agent does not have this pack's
instructions, so these runs check the data and the permissions rather than the
instructions. Agent answers vary from run to run; treat this as a guide.
Question 2 was run again, four times per person, after the demo data changed
SUP-121 to point to the finance tickets instead of repeating their dates.

| # | Signed in as | Result | What the runs cited |
| --- | --- | --- | --- |
| 1 | Alice | 2 of 2 | PR #211 and the Contoso, Northwind and Fabrikam cases, once with SUP-114. |
| 1 | Bob | 2 of 2 | PR #211, SUP-114 and the Northwind case, once with the Contoso and Fabrikam cases too. |
| 2 | Alice | 3 of 4 | The miss was a correct answer without citation markers. (Before the change: 1 of 2; the miss cited only SUP-121.) |
| 2 | Bob | 4 of 4 | Every run passed. (Before the change: 1 of 2; the miss was a correct answer that said "reissuing" and a credit note, which the scorer then missed.) |
| 3 | Alice | 2 of 2 | The export runbook. |
| 3 | Bob | 2 of 2 | The export runbook, once with SUP-114. |

Question 2 is the least reliable here: in the re-run, one of Alice's four
answers was correct but carried no citation markers, so it counts as a miss.
The pack's instruction to follow a support ticket to the finance tickets it
names is aimed at this question.
