from datetime import datetime, timedelta, timezone, time
from email.utils import parsedate_to_datetime
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Optional
import uuid

from icalendar import Calendar, Event
from pydantic import BaseModel

from newsletter_automation.message import Message

TEMPLATE_PATH = Path(__file__).parent / "template.yaml"


class CalendarModel(BaseModel):
    title: str
    summary: str
    description: str
    location: str
    start: datetime
    end: Optional[datetime] = None


def _llm_executable() -> str:
    venv_llm = Path(sys.executable).parent / "llm"
    if venv_llm.exists():
        return str(venv_llm)
    return shutil.which("llm") or "llm"


def prompt_model(message: Message) -> CalendarModel:
    message_date = parsedate_to_datetime(message["date"])

    cmd = [
        _llm_executable(),
        "-t",
        str(TEMPLATE_PATH),
        "-p",
        "year",
        str(message_date.year),
        "--no-stream",
        "--no-log",
    ]
    try:
        result = subprocess.run(
            cmd,
            input=message["content"],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"llm command failed ({exc.returncode}): {exc.stderr.strip()}") from exc

    entry = CalendarModel.model_validate_json(result.stdout)

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
