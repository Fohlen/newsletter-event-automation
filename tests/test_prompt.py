import datetime
import json
import subprocess
from unittest.mock import patch

import pytest

from newsletter_automation.message import Message
from newsletter_automation.prompt import prompt_model, calendar_from_model, CalendarModel, TEMPLATE_PATH


@pytest.fixture
def message_a(data_dir):
    return data_dir / "message_a.json"


@pytest.mark.integration
def test_prompt(message_a) -> None:
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


def test_prompt_model_cli(message_a, data_dir):
    with message_a.open() as message_fp, (data_dir / "entry_a.json").open() as entry_fp:
        message: Message = json.load(message_fp)
        entry_payload = json.load(entry_fp)
        entry_payload["start"] = "2020-12-16T20:00:00Z"

    completed = subprocess.CompletedProcess(
        args=["llm"],
        returncode=0,
        stdout=json.dumps(entry_payload),
        stderr="",
    )

    with patch("newsletter_automation.prompt.subprocess.run", return_value=completed) as mock_run:
        entry = prompt_model(message)

    mock_run.assert_called_once()
    cmd = mock_run.call_args.args[0]
    assert "-t" in cmd and str(TEMPLATE_PATH) in cmd
    assert "-p" in cmd and "year" in cmd and "2022" in cmd
    assert mock_run.call_args.kwargs["input"] == message["content"]
    assert entry.start.year == 2022
    assert entry.start.month == 12
    assert entry.start.day == 16
