import argparse


def parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert osu beatmaps into properly tagged mp3 files! \n" "https://github.com/hewlett-packard-lovecraft/osu2mp3"
    )

    parser.add_argument(
        "-i", "--input",
        action="store",
        default=".",
        dest="input",
        help="Specify input directory"
    )

    parser.add_argument(
        "-o", "--output",
        action="store",
        default="~",
        dest="output",
        help="Specify directory"
    )


    parser.add_argument(
        "-s", "--silent",
        action="store_true",
        default=False,
        dest="silent",
        help="Disable progressbar"
    )

    return parser
