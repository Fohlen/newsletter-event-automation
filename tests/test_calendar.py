from icalendar import Calendar

from newsletter_automation.calendar import merge_calendars


def test_calendar(data_dir):
    calendar_paths = data_dir.glob("event_*.ics")
    calendars = []
    for calendar_path in calendar_paths:
        with calendar_path.open() as calendar_fp:
            calendars.append(Calendar.from_ical(calendar_fp.read()))

    merged_calender = merge_calendars(calendars)
    events = list(merged_calender.walk("VEVENT"))
    assert len(events) == 3
    assert [event.get("uid") is not None for event in events]
    assert len(set([event.get("summary") for event in events])) == 3
