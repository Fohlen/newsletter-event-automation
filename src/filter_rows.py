import argparse
import csv
import pathlib

from fasttext import load_model


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="The input path to filter for", type=pathlib.Path)
    parser.add_argument(
        "model",
        nargs="?",
        help="The model to use for classification",
        default=pathlib.Path(__file__).parent.parent / "data" / "model_event.bin",
        type=pathlib.Path
    )
    parser.add_argument(
        "output", nargs="?", help="The output path save the mbox to", type=pathlib.Path
    )

    args = parser.parse_args()
    if args.output is None:
        args.output = args.input.with_stem(f"{args.input.stem}_filtered")

    model = load_model(str(args.model.absolute()))

    with args.input.open() as input_fp, args.output.open("wt") as output_fp:
        reader = csv.reader(input_fp, delimiter="\t")
        writer = csv.writer(output_fp, delimiter="\t")

        for row in reader:
            title = row[1].strip()[28:]
            labels, precision = model.predict(title)

            if "__label__event" in labels:
                writer.writerow(row)
