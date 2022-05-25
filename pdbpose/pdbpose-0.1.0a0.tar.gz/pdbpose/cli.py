from argparse import ArgumentParser, Namespace
from .pdbe import chains


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("uniprot")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    for chain in chains(args.uniprot):
        print(chain)
