# INC-2031 Postmortem — Synchronised billing retries overloaded the payments provider

**Date of incident:** 2026-03-14 09:12–10:40 UTC · **Severity:** SEV-2 · **Owner:** Marcus Webb (Payments)

## Impact
Roughly 3,400 subscription renewals were delayed by up to 90 minutes. No charges were lost or duplicated.

## Timeline
- 09:12 Stripe returned elevated 429 (rate limit) responses after a brief upstream blip.
- 09:13 All 12 billing worker replicas began retrying on a fixed 5-second schedule.
- 09:20 Retry volume was 12× steady state; Stripe's rate limiting tightened further.
- 09:45 On-call (Marcus) paused the workers to let the queue drain.
- 10:40 Workers resumed at reduced concurrency; backlog cleared.

## Root cause
The billing worker used a fixed, un-jittered retry interval. When a transient upstream failure hit every replica at once, every replica retried at the same moment, turning a small blip into a sustained overload — a classic thundering-herd.

## Action items
1. Replace fixed retry with exponential backoff and jitter — **done in PR #482** (Priya).
2. Add a retry-delay histogram so this pattern is visible on the dashboard — done in PR #482.
3. Document the resilience approach — see "Billing worker resilience" design doc (Dana).
