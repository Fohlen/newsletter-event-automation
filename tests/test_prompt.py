import datetime
import json

import pytest

from newsletter_automation.message import Message
from newsletter_automation.prompt import prompt_model, calendar_from_model, CalendarModel


@pytest.fixture
def message_a(data_dir):
    return data_dir / "message_a.json"


@pytest.mark.integration
def test_prompt(message_a):
    with message_a.open() as message_fp:
        message: Message = json.load(message_fp)
        entry = prompt_model(message)
        assert entry.start.day == 16
        assert entry.start.month == 12
        assert entry.start.year == 2022


def test_calender_from_entry(data_dir):
    entry_a = (data_dir / "entry_a.json")
    with entry_a.open() as entry_fp:
        entry_data = json.load(entry_fp)
        entry_data["start"] = datetime.datetime.fromisoformat(entry_data["start"])
        entry = CalendarModel(**entry_data)

        calendar = calendar_from_model(entry)
        events = list(calendar.walk("VEVENT"))
        assert calendar is not None
        assert len(events) == 1
        assert events[-1].get("uid") is not None
