import argparse
import csv
import email
import mailbox
import pathlib
from email.message import EmailMessage
from email.utils import parseaddr
import email.policy

from src.visible_text_parser import VisibleTextParser

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
        args.output = args.input.with_suffix(".tsv")

    mbox = mailbox.mbox(
        args.input,
        factory=lambda f: email.message_from_binary_file(f, policy=email.policy.default),
        create=False
    )

    with args.output.open("wt") as fp:
        writer = csv.writer(fp, delimiter="\t")

        for message in mbox:
            _, sender_email = parseaddr(message["From"])
            if sender_email in args.filter:
                try:
                    message: EmailMessage
                    body: EmailMessage = message.get_body()
                    if body:
                        content = body.get_content()
                        if body.get_content_type() == "text/html":
                            parser = VisibleTextParser()
                            parser.feed(content)
                            text = parser.get_visible_text()
                        else:
                            text = content
                        writer.writerow([sender_email, message["subject"], text])
                except KeyError:
                    # todo: logging here
                    continue
    mbox.close()
