import argparse
import datetime
import json
import logging
import pathlib
from typing import Mapping
import uuid

import openai
from icalendar import Calendar
from tqdm.contrib.concurrent import thread_map

logging.getLogger().setLevel(logging.INFO)
MANDATORY_FIELDS = ["event_name", "organizer", "start_date", "end_date", "start_time", "end_time", "summary"]


def prompt_model(message: Mapping[str, str]):
    message_date = datetime.datetime.strptime(message["date"], "%a, %d %b %Y %H:%M:%S %z")
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"Please create a description of the event from the following email that was written in {message_date.year}, stating the event name, organizer, beginning and end date and time, if applicable, as well as a short summary of the event itself in iCalendar format."
            },
            {"role": "user", "content": message["content"].strip()}
        ],
        temperature=0.5,
        max_tokens=128
    )
    return completion


def calendar_from_completion(completion: openai.ChatCompletion) -> Calendar | None:
    if len(completion.choices) == 1 and completion.choices[0].finish_reason == "stop":
        content = completion.choices[0].message.content
        try:
            calendar = Calendar.from_ical(content)
            return calendar
        except ValueError:
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="The input path to read the messages from", type=pathlib.Path)
    parser.add_argument(
        "output", nargs="?",
        help="The output path save the mbox to", type=pathlib.Path,
        default=pathlib.Path(__file__).parent.parent / "data" / "calendars"
    )

    args = parser.parse_args()
    logging.info(f"Reading from {args.input}")

    with args.input.open() as fp:
        messages = [json.loads(line) for line in fp]
        completions = thread_map(prompt_model, messages, max_workers=5)
        num_valid = 0

        for chat_completion in completions:
            event_calendar = calendar_from_completion(chat_completion)
            if event_calendar:
                with (args.output / f"{uuid.uuid4()}.ics").open("wb") as output_fp:
                    output_fp.write(event_calendar.to_ical())
                    num_valid += 1

        logging.info(f"Written {num_valid} valid calendars from {len(completions)} messages")
