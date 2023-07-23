import sys

if __name__ == "__main__":
    with open("messages.jsonl") as input_fp, open("labels.txt", "wt") as output_fp:
        for line in input_fp:
            print(line, file=sys.stdout)
            label = input("Label: ")
            print(label, file=output_fp)
