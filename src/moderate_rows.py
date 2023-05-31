import argparse
import csv
import pathlib


import openai
from tqdm.contrib.concurrent import thread_map


def is_flagged(row: tuple[str, str, str]) -> bool:
    text = row[2]
    response = openai.Moderation.create(
        input=text
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

    with args.input.open() as fp, args.output.open("wt") as output_fp:
        reader = csv.reader(fp, delimiter="\t")
        writer = csv.writer(output_fp, delimiter="\t")
        rows = list(reader)
        flagging = thread_map(is_flagged, rows, max_workers=10)

        for flagged, row in zip(flagging, rows):
            if not flagged:
                writer.writerow(row)
