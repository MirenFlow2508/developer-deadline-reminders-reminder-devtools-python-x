from dataclasses import dataclass
from datetime import date

from reminder_client import InfraiClient

REMINDER_QUEUE = "developer-deadline-reminders"


@dataclass(frozen=True)
class Deadline:
    tool: str
    release: str
    due: date
    owner: str


def reminder_payload(deadline: Deadline, today: date) -> dict | None:
    days = (deadline.due - today).days
    if 0 <= days <= 7:
        return {
            "tool": deadline.tool,
            "release": deadline.release,
            "owner": deadline.owner,
            "due": deadline.due.isoformat(),
            "days_remaining": days,
        }
    return None


def schedule_deadline(deadline: Deadline, webhook: str, client: InfraiClient) -> str:
    job = client.create_cron("0 9 * * 1-5", webhook)
    event = reminder_payload(deadline, date.today())
    if event:
        client.publish(REMINDER_QUEUE, event)
    return job["job_id"]


def read_reminders(client: InfraiClient) -> list[dict]:
    data = client.consume(queue=REMINDER_QUEUE, max_messages=20, visibility_timeout=60)
    return data.get("messages") or data.get("items") or []


if __name__ == "__main__":
    deadline = Deadline("python", "3.13.0", date(2026, 9, 15), "release-eng")
    job_id = schedule_deadline(deadline, "https://example.com/hooks/devtools-reminder", InfraiClient())
    print({"job_id": job_id, "queued": len(read_reminders(InfraiClient()))})
