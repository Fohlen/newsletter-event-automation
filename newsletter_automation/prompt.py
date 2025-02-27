from datetime import datetime, timedelta, timezone, time
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
    start: datetime
    end: Optional[datetime] = None


def prompt_model(message: Message) -> CalendarModel:
    client = instructor.from_openai(OpenAI())
    message_date = parsedate_to_datetime(message["date"])

    # Extract structured data from natural language
    entry = client.chat.completions.create(
        model="gpt-4o-mini",
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

    if entry.start.year != message_date.year:
        entry.start = entry.start.replace(year=message_date.year)

    if entry.end is not None and entry.end.year != message_date.year:
        entry.end = entry.end.replace(year=message_date.year)

    return entry


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

    end_of_day = datetime.combine(entry.start, time.max).replace(tzinfo=timezone(offset=timedelta()))

    if entry.end is not None:
        entry_end_date = entry.end.replace(tzinfo=timezone(offset=timedelta()))
        end_date = min(end_of_day, entry_end_date)
    else:
        end_date = end_of_day

    event.add("DTEND", end_date)

    cal.add_component(event)

    return cal
