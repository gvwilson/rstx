import sys


def main():
    for filename in sys.argv[1:]:
        text = open(filename, "r").read()
        text = clean(text)
        open(filename, "w").write(text)


def clean(text):
    return text.replace("\n\n# mccole: /", "# mccole: /")


if __name__ == "__main__":
    main()
