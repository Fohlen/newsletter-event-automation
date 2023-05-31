import argparse
import json
import logging
import pathlib
from typing import Mapping

import openai
from tqdm.contrib.concurrent import thread_map

logging.getLogger().setLevel(logging.INFO)


def is_flagged(message: Mapping[str, str]) -> bool:
    response = openai.Moderation.create(
        input=message["content"]
    )
    return response.results[0].flagged


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="The input path to filter for", type=pathlib.Path)
    parser.add_argument(
        "output", nargs="?", help="The output path save the mbox to", type=pathlib.Path
    )

    args = parser.parse_args()
    if args.output is None:
        args.output = args.input.with_stem(f"{args.input.stem}_moderated")

    logging.info(f"Reading from {args.input}")

    with args.input.open() as fp, args.output.open("wt") as output_fp:
        messages = [json.loads(line) for line in fp]
        flagging = thread_map(is_flagged, messages, max_workers=10)
        num_flagged = flagging.count(True)

        for flagged, message in zip(flagging, messages):
            if not flagged:
                print(json.dumps(message), file=output_fp)

        print(f"Wrote {len(messages) - num_flagged} out of {len(messages)}")
