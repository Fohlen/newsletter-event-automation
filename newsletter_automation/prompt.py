import datetime
import uuid
from email.utils import parsedate_to_datetime
from typing import Optional

import instructor
from openai import OpenAI
from icalendar import Calendar, Event
from pydantic import BaseModel
from tenacity import Retrying, wait_random_exponential, stop_after_attempt

from newsletter_automation.message import Message


class CalendarModel(BaseModel):
    title: str
    summary: str
    description: str
    location: str
    start: datetime.datetime
    end: Optional[datetime.datetime] = None


def prompt_model(message: Message) -> CalendarModel:
    client = instructor.from_openai(OpenAI())
    message_date = parsedate_to_datetime(message["date"])

    # Extract structured data from natural language
    return client.chat.completions.create(
        model="gpt-4-turbo-preview",
        response_model=CalendarModel,
        messages=[
            {"role": "system", "content": f"The original message was written in {message_date.year}"},
            {"role": "user", "content": message["content"]}
        ],
        max_retries=Retrying(  # type: ignore
            stop=stop_after_attempt(6),
            wait=wait_random_exponential(min=1, max=60),
        )
    )


def calendar_from_model(entry: CalendarModel) -> Calendar:
    cal = Calendar()
    cal.add('PRODID', entry.title)
    cal.add('VERSION', '2.0')

    event = Event()
    event.add('SUMMARY', entry.summary)
    event.add('DTSTART', entry.start)
    event.add('LOCATION', entry.location)
    event.add('DESCRIPTION', entry.description)
    event.add('UID', uuid.uuid4())

    if entry.end is not None:
        event.add("DTEND", entry.end)
    else:
        end_of_day = datetime.datetime.combine(entry.start, datetime.time.max)
        event.add("DTEND", end_of_day)

    cal.add_component(event)

    return cal
