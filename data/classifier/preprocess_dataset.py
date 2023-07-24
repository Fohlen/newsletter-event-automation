import json
from pathlib import Path

from newsletter_automation.message import read_mbox

if __name__ == "__main__":
    path = Path("~/Downloads/mbox/bla.mbox/mbox")
    messages = list(read_mbox(
        path,
        ["schoener-wohnen@lists.mtmedia.org"],
        "[schoener-wohnen]",
        "___________________________"
    ))

    with Path("messages.jsonl").open("wt") as fp:
        for message in messages:
            print(json.dumps(message), file=fp)
