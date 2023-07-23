import html
import logging
from logging.config import fileConfig
import argparse
import json
import email
import mailbox
import pathlib
from email.message import EmailMessage, Message
from email.utils import parseaddr
import email.policy
from typing import IO, Any

from src.visible_text_parser import VisibleTextParser

fileConfig('../logging.ini')
logger = logging.getLogger()


def email_mbox_factory(file: IO[Any]) -> Message | None:
    return email.message_from_binary_file(file, policy=email.policy.default)




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="The input path to filter for", type=pathlib.Path)
    parser.add_argument(
        "--filter", help="The addresses to filter for",
        type=str, nargs="?", default=["schoener-wohnen-tuebingen@lists.posteo.de"]
    )
    parser.add_argument(
        "--truncate-subject-prefix",
        help="The prefix to remove from the subject. Everything before will be truncated.",
        type=str, default="[schoener-wohnen-tuebingen] "
    )
    parser.add_argument(
        "--truncate-content-suffix",
        help="The suffix to remove from the content. Everything after will be truncated.",
        type=str, default="___________________________"
    )
    parser.add_argument(
        "output", nargs="?", help="The output path to save the messages to", type=pathlib.Path
    )
    args = parser.parse_args()
    if args.output is None:
        args.output = args.input.with_suffix(".jsonl")

    logging.info(f"Reading mailbox {args.input}")
    # NOTE: EmailMessage is not invariant
    mbox = mailbox.mbox(
        args.input,
        factory=email_mbox_factory,  # type: ignore
        create=False
    )
    num_failed = 0

    with args.output.open("wt") as fp:
        for index, message in enumerate(mbox):
            _, sender_email = parseaddr(message["From"])
            if sender_email in args.filter:
                try:
                    body: EmailMessage | None = message.get_body()  # type: ignore
                    if body:
                        content = body.get_content()
                        if body.get_content_type() == "text/html":
                            html_parser = VisibleTextParser()
                            html_parser.feed(content)
                            content = html_parser.get_visible_text()

                        subject = html.unescape(
                            message["subject"][len(args.truncate_subject_prefix):]
                        ).strip()

                        try:
                            content_suffix_index = content.index(args.truncate_content_suffix)
                            content = content[:content_suffix_index]
                        except ValueError:
                            pass

                        print(json.dumps({
                            "sender": sender_email,
                            "subject": subject,
                            "date": message["date"],
                            "content": html.unescape(content).strip()
                        }), file=fp)
                except KeyError:
                    logging.error(f"Could not process message from {sender_email} at index {index}")
                    num_failed += 1
                    continue

    logging.info(f"Processed {index - num_failed} documents.")
    mbox.close()
