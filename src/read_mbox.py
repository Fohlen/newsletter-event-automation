import logging
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

logging.getLogger().setLevel(logging.INFO)


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
        "output", nargs="?", help="The output path save the mbox to", type=pathlib.Path
    )
    args = parser.parse_args()
    if args.output is None:
        args.output = args.input.with_suffix(".jsonl")

    logging.info(f"Reading mailbox {args.input}")
    mbox = mailbox.mbox(
        args.input,
        factory=email_mbox_factory,
        create=False
    )
    num_failed = 0

    with args.output.open("wt") as fp:
        for index, message in enumerate(mbox):
            _, sender_email = parseaddr(message["From"])
            if sender_email in args.filter:
                try:
                    message: EmailMessage
                    body: EmailMessage | None = message.get_body()
                    if body:
                        content = body.get_content()
                        if body.get_content_type() == "text/html":
                            parser = VisibleTextParser()
                            parser.feed(content)
                            content = parser.get_visible_text()

                        print(json.dumps({
                            "sender": sender_email,
                            "subject": message["subject"],
                            "content": content
                        }), file=fp)
                except KeyError:
                    logging.warning(f"Could not process message from {sender_email} at index {index}")
                    num_failed += 1
                    continue

    logging.info(f"Processed {index - num_failed} documents.")
    mbox.close()
