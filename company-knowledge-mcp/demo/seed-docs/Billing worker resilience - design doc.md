# Billing worker resilience

**Author:** Dana Okafor · **Status:** Approved · **Last updated:** 2026-03-19

## Context
The billing worker charges subscription renewals through Stripe. INC-2031 showed that our retry strategy could turn a brief upstream failure into a self-inflicted outage, because all replicas retried in lockstep.

## Decision
Retries use **exponential backoff with full jitter**: delay = random(0, min(cap, base × 2^attempt)), with base 2 seconds and cap 120 seconds. Max attempts is 6. This spreads retry load across time and across replicas, so a transient provider error decays instead of amplifying.

## Alternatives considered
- **Fixed interval (previous behaviour)** — rejected; it caused INC-2031.
- **Exponential backoff without jitter** — rejected; replicas that fail together still retry together, just later.
- **Equal jitter** — considered; full jitter gives better spread at our replica count, per the analysis in the AWS Architecture Blog post "Exponential Backoff And Jitter".

## Observability
`billing_retry_delay_seconds` (histogram) and `billing_retry_attempt_total` (counter) are on the Payments dashboard.

## Implemented in
PR #482 (acme/svc-billing-worker), merged 2026-03-21.
