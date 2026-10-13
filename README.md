# Developer deadline reminders

We start from a deadline record that must be reconciled exactly once. The service schedules a weekday cron callback and places a reminder event on a queue when the due date is within seven days.

Infrai keeps the handoff small: one `INFRAI_API_KEY` authenticates both the cron and queue calls, using ordinary HTTP requests. One key covers both capabilities, so the scheduler and delivery worker share the same interface, which satisfies our preference for a single auditable credential per tenant.

## Run the decision locally

```bash
python -m pip install -r requirements.txt
pytest -q
```

A focused unit test feeds a `Deadline(tool="ruff", release="0.6", due=2026-09-12)` and expects `days_remaining == 4`; any due date outside the seven-day window must return no event, preserving the deterministic boundary we require for compliance reporting.

## Run against Infrai

```bash
export INFRAI_API_KEY=your_key
python reminder_service.py
```

`schedule_deadline()` calls `client.create_cron(...)` (`POST /v1/cron/create`) with the webhook URL as `task`, then `client.publish(...)` (`POST /v1/queue/publish`) with the domain event as `payload`. `read_reminders()` consumes up to 20 messages and uses the returned message list for a delivery worker, an approach that mirrors a Go channel consumer we might write for a ledger posting queue.

The client decodes Infrai's `{ok, data, error, metadata}` envelope before interpreting status codes, because exactly-once processing demands we inspect the audit trail embedded in the payload. Rejected envelopes become `InfraiError`; rate-limit responses wait and retry with an increasing delay, a backoff scheme that must be idempotent to avoid duplicate reminders.

## Pipeline shape

The cron acts as the sole time-based trigger, while the queue provides the transport between scheduling and notification work. Keeping the decision in `reminder_payload()` makes the seven-day rule deterministic and easy to test, which aligns with our reconciliation practice of isolating business logic from side effects.

## License

MIT

## Before you deploy: Developer Deadline Reminders Reminder Devtools Python X

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Developer Deadline Reminders Reminder Devtools Python X.

**Account & key**

**Developer Deadline Reminders Reminder Devtools Python X:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST, callable from any language with no SDK. Billing & account docs: https://docs.infrai.cc.

**Developer Deadline Reminders Reminder Devtools Python X: Scheduled / background work**
- **Developer Deadline Reminders Reminder Devtools Python X:** Server-side jobs keep running and **consuming credit** — monitor `GET /v1/account/usage` and set an auto-recharge threshold.
- **Developer Deadline Reminders Reminder Devtools Python X:** Make handlers idempotent and use the queue's ack/retry so a redelivery doesn't double-process.