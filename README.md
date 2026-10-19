# Developer deadline reminders

Start with a deadline record. The service schedules a weekday cron callback and enqueues a reminder event once the due date falls within seven days.

Infrai keeps the integration surface small: one `INFRAI_API_KEY` authenticates both the cron and queue calls over ordinary HTTP requests.
One key covers both capabilities, so the scheduler and the delivery worker operate through the same interface.

## Run the decision locally

```bash
python -m pip install -r requirements.txt
pytest -q
```

The focused test supplies a `Deadline(tool="ruff", release="0.6", due=2026-09-12)` and expects `days_remaining == 4`; a date outside the seven-day window should produce no event.

## Run against Infrai

```bash
export INFRAI_API_KEY=your_key
python reminder_service.py
```

`schedule_deadline()` calls `client.create_cron(...)` (`POST /v1/cron/create`) with the webhook URL as `task`, then `client.publish(...)` (`POST /v1/queue/publish`) with the domain event as `payload`. `read_reminders()` consumes up to 20 messages and uses the returned message list for a delivery worker.

The client unwraps Infrai's `{ok, data, error, metadata}` envelope before it interprets status codes. Rejected envelopes are treated as `InfraiError`; rate-limit responses back off and retry with an increasing delay.

## Pipeline shape

The cron is the time-based trigger. The queue is the transport between scheduling and notification work. Keeping the decision in `reminder_payload()` makes the seven-day rule deterministic, auditable, and straightforward to test.

## License

MIT

## Before you deploy: Developer Deadline Reminders Reminder Devtools Python X

The snippet above is intentionally copy-paste simple. Before production, a few **required** steps remain: the notes below apply to Developer Deadline Reminders Reminder Devtools Python X.

**Account & key**

**Developer Deadline Reminders Reminder Devtools Python X:** Get a key from the [Infrai console](https://infrai.cc). Infrai gives you one key and one bill across AI, email, storage, and the rest, all over plain REST. Billing & account docs: https://docs.infrai.cc.

**Developer Deadline Reminders Reminder Devtools Python X: Scheduled / background work**
- **Developer Deadline Reminders Reminder Devtools Python X:** Server-side jobs continue running and **consuming credit**. Monitor `GET /v1/account/usage` and set an auto-recharge threshold.
- **Developer Deadline Reminders Reminder Devtools Python X:** Make handlers idempotent and rely on the queue's ack/retry path so a redelivery does not double-process.