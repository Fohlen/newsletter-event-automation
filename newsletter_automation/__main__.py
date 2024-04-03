import argparse
import datetime
import logging
from configparser import ConfigParser
from dataclasses import dataclass
from logging.config import fileConfig
from pathlib import Path
import pickle

from icalendar import Calendar
from numpy import rint
from tqdm import tqdm

from newsletter_automation.calendar import merge_calendars
from newsletter_automation.message import read_mbox
from newsletter_automation.prompt import prompt_model, calendar_from_model

root_dir = Path(__file__).parent.parent

fileConfig(str(root_dir / "logging.ini"))
log = logging.getLogger()


@dataclass
class Config:
    mbox: Path
    filter: Path
    calendar: Path
    sender_emails: list[str]
    truncate_subject_prefix: str
    truncate_content_suffix: str


@dataclass
class MessageStatistics:
    read: int
    filtered: int
    completed: int

    @property
    def success_rate(self) -> float:
        return self.completed / self.read

    def __str__(self):
        date_fmt = datetime.datetime.now().strftime("%y-%d-%m")
        return ",".join([
            date_fmt, str(self.read), str(self.filtered), str(self.completed), str(self.success_rate)
        ])


def read_newsletter_to_calendar(
        config: Config,
) -> Calendar:
    messages = list(read_mbox(
        config.mbox,
        config.sender_emails,
        config.truncate_subject_prefix,
        config.truncate_content_suffix
    ))
    log.info(f"Read {len(messages)} messages")

    with config.filter.open("rb") as filter_fp, config.calendar.open("rt") as calendar_fp:
        pipeline = pickle.load(filter_fp)
        predictions = pipeline.predict(
            [message["content"] for message in messages]
        )
        classification = rint(predictions).astype(int).reshape((-1))
        num_filtered = len(classification) - classification.sum()
        log.info(f"Filtered {num_filtered} out of {len(classification)} messages")

        calendars = []

        for message, is_event in tqdm(zip(messages, classification), total=len(messages)):
            if is_event:
                model = prompt_model(message)
                calendar = calendar_from_model(model)
                if calendar is not None:
                    calendars.append(calendar)

        log.info(f"Completed {len(calendars)} calenders")
        input_calendar = Calendar.from_ical(calendar_fp.read())
        log.info("Merging calendars")
        statistics = MessageStatistics(len(messages), num_filtered, len(calendars))
        log.info(statistics)
        return merge_calendars(calendars, input_calendar)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Automate your newsletter")
    parser.add_argument("--config", nargs="?", default=(root_dir / "config.ini"))
    args = parser.parse_args()

    log.info(f"Reading config from {args.config}")
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

    if conf.mbox.exists():
        log.info(f"Reading newsletter from mailbox {conf.mbox}")
        output_calendar = read_newsletter_to_calendar(conf)
        with conf.calendar.open("wt") as output_calendar_fp:
            output_calendar_fp.write(output_calendar.to_ical().decode())
    else:
        log.error(f"No mailbox at {conf.mbox}, exiting")
