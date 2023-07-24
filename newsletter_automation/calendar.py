import datetime
from typing import Sequence, Optional

from icalendar import Calendar


def merge_calendars(
        calendars: Sequence[Calendar],
        output: Optional[Calendar] = None
) -> Calendar:
    if output is None:
        output = Calendar()
        output.add('prodid', '-//schoener-woehnen//github.com//')
        output.add('version', '2.0')

    message_ids = set()
    for event in output.walk("VEVENT"):
        message_ids.add(event.get("UID"))

    for calendar in calendars:
        for event in calendar.walk("VEVENT"):
            event.add("DTSTAMP", datetime.datetime.now())

            if event.get("uid") not in message_ids:
                output.add_component(event)

    return output
