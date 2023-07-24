import argparse
import logging
from configparser import ConfigParser
from dataclasses import dataclass
from logging.config import fileConfig
from pathlib import Path
import pickle

from icalendar import Calendar
from numpy import rint

from newsletter_automation.calendar import merge_calendars
from newsletter_automation.message import read_mbox
from newsletter_automation.prompt import prompt_model, calendar_from_completion

cwd = Path.cwd()

fileConfig(str(cwd / "logging.ini"))
logger = logging.getLogger()


@dataclass
class Config:
    mbox: Path
    filter: Path
    calendar: Path
    sender_emails: list[str]
    truncate_subject_prefix: str
    truncate_content_suffix: str


def read_newsletter_to_calendar(
        config: Config
) -> Calendar:
    messages = list(read_mbox(
        config.mbox,
        config.sender_emails,
        config.truncate_subject_prefix,
        config.truncate_content_suffix
    ))

    with config.filter.open("rb") as filter_fp, config.calendar.open("rt") as calendar_fp:
        pipeline = pickle.load(filter_fp)
        predictions = pipeline.predict(
            [message["content"] for message in messages]
        )
        classification = rint(predictions).astype(int).reshape((-1))

        calendars = []

        for message, is_event in zip(messages, classification):
            if is_event:
                completion = prompt_model(message)
                calendar = calendar_from_completion(message, completion)
                if calendar is not None:
                    calendars.append(calendar)

        input_calendar = Calendar.from_ical(calendar_fp.read())
        return merge_calendars(calendars, input_calendar)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Automate your newsletter")
    parser.add_argument("--config", nargs="?", default=(cwd / "config.ini"))
    args = parser.parse_args()

    cfg = ConfigParser()
    cfg.read(args.config)
    conf = Config(
        mbox=Path(cfg.get("path", "mbox")),
        filter=Path(cfg.get("path", "filter")),
        calendar=Path(cfg.get("path", "calendar")),
        sender_emails=cfg.get("email", "sender").split(","),
        truncate_subject_prefix=cfg.get("email", "truncate_subject_prefix"),
        truncate_content_suffix=cfg.get("email", "truncate_content_suffix"),
    )

    output_calendar = read_newsletter_to_calendar(conf)
    with conf.calendar.open("wt") as output_calendar_fp:
        output_calendar_fp.write(output_calendar.to_ical())
