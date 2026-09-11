# #eng-payments — 2026-03-15

**Marcus Webb** 08:41
Postmortem for yesterday's INC-2031 is up. Short version: every worker retried Stripe on the same 5s tick and we DDoS'd ourselves.

**Priya Natarajan** 08:47
I'll take the fix. Proposal: exponential backoff with full jitter, cap at 2 minutes, and bump max attempts to 6 since they'll be spread out. That's the pattern from the AWS architecture blog.

**Dana Okafor** 08:52
+1 on full jitter over equal jitter — with 12 replicas we want the spread. Can we also emit the actual delay as a histogram? I want to see the distribution on the dashboard, not guess.

**Priya Natarajan** 08:55
Yes, adding `billing_retry_delay_seconds`. PR #482 incoming this week.

**Marcus Webb** 09:02
Great. Dana, can you write up the resilience approach as a short design doc so we don't re-derive this next year?

**Dana Okafor** 09:03
On it — "Billing worker resilience", in the engineering Drive.
