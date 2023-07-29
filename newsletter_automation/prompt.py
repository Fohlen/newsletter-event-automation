from email.utils import parsedate_to_datetime
from typing import Optional

import openai
from icalendar import Calendar
from tenacity import retry, wait_random_exponential, stop_after_attempt

from newsletter_automation.message import Message


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def chat_completion_with_backoff(**kwargs) -> openai.ChatCompletion:
    return openai.ChatCompletion.create(**kwargs)


def prompt_model(message: Message) -> openai.ChatCompletion:
    message_date = parsedate_to_datetime(message["date"])
    completion = chat_completion_with_backoff(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": f"You are a helpful assistant and are given an email containing a event description from the year {message_date.year}. Your job is to create a machine-readable iCalendar file from this email. "
            },
            {"role": "user", "content": message["content"]}
        ],
        temperature=0,
        max_tokens=384,
        top_p=1
    )
    return completion


def calendar_from_completion(
        message: Message,
        completion: openai.ChatCompletion
) -> Optional[Calendar]:
    if len(completion.choices) == 1 and completion.choices[0].finish_reason == "stop":
        content = completion.choices[0].message.content
        try:
            calendar = Calendar.from_ical(content)
            for event in calendar.walk("VEVENT"):
                event.pop("uid")
                event.add("uid", message["id"])
            return calendar
        except ValueError:
            pass

    return None
