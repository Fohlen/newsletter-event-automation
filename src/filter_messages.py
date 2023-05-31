import argparse
import json
import logging
import pathlib

from fasttext import load_model

logging.getLogger().setLevel(logging.INFO)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="The input path to filter for", type=pathlib.Path)
    parser.add_argument(
        "model",
        nargs="?",
        help="The model to use for classification",
        default=pathlib.Path(__file__).parent.parent / "data" / "model" / "model_event.bin",
        type=pathlib.Path
    )
    parser.add_argument(
        "output", nargs="?", help="The output path save the mbox to", type=pathlib.Path
    )

    args = parser.parse_args()
    if args.output is None:
        args.output = args.input.with_stem(f"{args.input.stem}_filtered")

    logging.info(f"Reading from {args.input}")

    model = load_model(str(args.model.absolute()))

    with args.input.open() as input_fp, args.output.open("wt") as output_fp:
        num_unfiltered = 0

        for index, line in enumerate(input_fp):
            message = json.loads(line)

            title = message["subject"]
            labels, precision = model.predict(title)

            if "__label__event" in labels:
                print(line.strip(), file=output_fp)
                num_unfiltered += 1

        logging.info(f"Wrote {num_unfiltered} out of {index} messages.")
