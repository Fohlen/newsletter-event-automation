import pytest

from newsletter_automation.__main__ import Config, read_newsletter_to_calendar


@pytest.mark.integration
def test_read_newsletter_to_calendar(data_dir):
    root_dir = data_dir.parent.parent

    conf = Config(
        data_dir / "mbox",
        root_dir / "data" / "classifier" / "pipeline.pkl",
        data_dir / "example.ics",
        ["schoener-wohnen@lists.mtmedia.org"],
        "[schoener-wohnen]",
        "___________________________"
    )

    merged_calendar = read_newsletter_to_calendar(conf)
    events = list(merged_calendar.walk("VEVENT"))
    assert len(events) == 12
