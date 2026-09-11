# PR #482 — Add jittered exponential backoff to the billing worker

**Repository:** acme/svc-billing-worker · **Author:** Priya Natarajan · **Merged:** 2026-03-21
**Closes:** INC-2031

## Summary
Replaces the fixed 5-second retry in `charge_retry.py` with exponential backoff (base 2s, cap 120s) plus full jitter. Retries across worker replicas are no longer synchronised.

## Why
During INC-2031 on 2026-03-14, all 12 billing worker replicas retried failed charges on the same 5-second cadence. The payments provider (Stripe) rate-limited us, which produced more failures, which produced more synchronised retries. See the postmortem and the #eng-payments thread from 2026-03-15.

## Changes
- `charge_retry.py`: `backoff = min(120, 2 ** attempt) * random.uniform(0, 1)`
- `worker_config.yaml`: `max_attempts` raised from 3 to 6 now that attempts are spread out
- Metrics: new `billing_retry_delay_seconds` histogram

## Reviewers
Approved by Marcus Webb and Dana Okafor.
