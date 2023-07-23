import email
import email.policy
import html
import logging
import mailbox
from email.utils import parseaddr
from logging.config import fileConfig
from pathlib import Path
from typing import TypedDict, Sequence, IO, Any

from src.visible_text_parser import VisibleTextParser

fileConfig('../logging.ini')
logger = logging.getLogger()


class Message(TypedDict):
    sender: str
    subject: str
    date: str
    content: str


def email_mbox_factory(file: IO[Any]) -> Message | None:
    return email.message_from_binary_file(file, policy=email.policy.default)


def read_mbox(
        mbox_path: Path,
        sender_emails: list[str],
        truncate_subject_prefix: str,
        truncate_content_suffix: str
) -> Sequence[Message]:
    mbox = mailbox.mbox(
        mbox_path,
        factory=email_mbox_factory,  # type: ignore
        create=False
    )
    num_failed = 0

    for message in mbox:
        _, sender_email = parseaddr(message["From"])
        if sender_email in sender_emails:
            try:
                body: EmailMessage | None = message.get_body()  # type: ignore
                if body:
                    content = body.get_content()
                    if body.get_content_type() == "text/html":
                        html_parser = VisibleTextParser()
                        html_parser.feed(content)
                        content = html_parser.get_visible_text()

                    subject = html.unescape(
                        message["subject"][len(truncate_subject_prefix):]
                    ).strip()

                    try:
                        content_suffix_index = content.index(truncate_content_suffix)
                        content = content[:content_suffix_index]
                    except ValueError:
                        pass

                    yield {
                        "sender": sender_email,
                        "subject": subject,
                        "date": message["date"],
                        "content": html.unescape(content).strip()
                    }
            except KeyError:
                logging.error(f"Could not process message from {sender_email}")
                num_failed += 1

    logging.debug(f"{num_failed} messages failed")
