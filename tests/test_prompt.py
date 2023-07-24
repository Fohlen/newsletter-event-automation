import json
from collections import namedtuple

import pytest

from newsletter_automation.message import Message
from newsletter_automation.prompt import prompt_model, calendar_from_completion


@pytest.fixture
def message_a(data_dir):
    return data_dir / "message_a.json"


@pytest.mark.integration
def test_prompt(message_a):
    with message_a.open() as message_fp:
        message: Message = json.load(message_fp)

        completion = prompt_model(message)
        assert len(completion.choices) == 1
        assert completion.choices[-1].finish_reason == "stop"


def test_calendar_from_completion(data_dir, message_a):
    completion_a = (data_dir / "completion_a.json")
    with message_a.open() as message_fp, completion_a.open() as completion_fp:
        message = json.load(message_fp)
        # NOTE: Thanks SO https://stackoverflow.com/a/15882327
        completion = json.load(completion_fp, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))

        calendar = calendar_from_completion(message, completion)
        events = list(calendar.walk("VEVENT"))
        assert calendar is not None
        assert len(events) == 1
        assert events[-1].get("uid") is not None
