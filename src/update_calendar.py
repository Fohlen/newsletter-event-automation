import argparse
import datetime
import hashlib
import logging
import pathlib

from icalendar import Calendar


def hash_from_summary(summary: str) -> str:
    input_text = summary.strip().lower()
    m = hashlib.md5(input_text.encode("utf-8"))
    return m.hexdigest()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input", nargs="?",
        help="The input path to read calendars from", type=pathlib.Path,
        default=pathlib.Path(__file__).parent.parent / "data" / "calendars"
    )
    parser.add_argument(
        "output", help="The output path to merge the calendar", nargs="?",
        type=pathlib.Path, default=pathlib.Path(__file__).parent.parent / "schoener-wohnen-verteiler.ics"
    )

    args = parser.parse_args()
    logging.info(f"Reading from {args.input}")

    if args.output.exists():
        with args.output.open("rb") as fp:
            calendar = Calendar.from_ical(fp.read())
    else:
        calendar = Calendar()
        calendar.add('prodid', '-//schoener-woehnen//github.com//')
        calendar.add('version', '2.0')

    event_ids = set()
    for event in calendar.walk("VEVENT"):
        event_ids.add(event.get("UID"))

    for calendar_path in args.input.glob("*.ics"):
        with calendar_path.open() as fp:
            cal = Calendar.from_ical(fp.read())
            for event in cal.walk("VEVENT"):
                event.pop("UID", None)
                event.pop("DTSTAMP", None)

                uid = "-".join([
                    event.get('DTSTART').to_ical().decode(),
                    hash_from_summary(event.get('SUMMARY'))
                ])
                event.add("DTSTAMP", datetime.datetime.now())
                event.add("UID", uid)

                if uid not in event_ids:
                    calendar.add_component(event)

    with args.output.open("wb") as fp:
        fp.write(calendar.to_ical())
