import argparse
import json
import os
import pathlib
from tempfile import gettempdir

DATA_FILENAME = gettempdir() + "document-counter.txt"


def update_document_id(new_id: int):
    with open(DATA_FILENAME, "w") as fd:
        fd.write(str(new_id) + "\n")


def retrieve_document_id() -> int:
    with open(DATA_FILENAME, "r") as fd:
        return int(fd.readline().strip())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="The input path to filter for", type=pathlib.Path)
    parser.add_argument(
        "output", nargs="?", help="The output path save the mbox to", type=pathlib.Path
    )
    args = parser.parse_args()
    if args.output is None:
        args.output = args.input.with_stem(f"{args.input.stem}_train").with_suffix(".txt")

    with args.input.open() as input_fp, args.output.open("at") as output_fp:
        if not os.path.exists(DATA_FILENAME):
            document_id = 0
        else:
            document_id = retrieve_document_id()

        for index, line in enumerate(input_fp):
            if index < document_id:
                continue
            else:
                update_document_id(index)

            message = json.loads(line)
            title = message["subject"]
            user_input = input(f"Contains event: {title}")
            if user_input in ["Y", "N"]:
                label = "__label__event" if user_input == "Y" else "__label__noevent"
                print(" ".join([label, title]), file=output_fp)
