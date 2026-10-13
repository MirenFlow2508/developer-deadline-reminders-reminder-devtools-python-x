from datetime import date

from reminder_service import Deadline, reminder_payload


def test_deadline_within_week_becomes_notification():
    deadline = Deadline("ruff", "0.6", date(2026, 9, 12), "tooling")
    event = reminder_payload(deadline, date(2026, 9, 8))
    assert event == {
        "tool": "ruff",
        "release": "0.6",
        "owner": "tooling",
        "due": "2026-09-12",
        "days_remaining": 4,
    }


def test_distant_deadline_is_ignored():
    deadline = Deadline("ruff", "0.6", date(2026, 10, 1), "tooling")
    assert reminder_payload(deadline, date(2026, 9, 8)) is None
