#!/usr/bin/env python3
"""Calculate entropy"""

import sys
import argparse
import getpass
from math import log

ENCODING = "utf8"

class Entropy:
    """Container class for calculating entropy"""

    def __init__(self, array: bytes = None, base: float = 2) -> None:
        self.array = array or b""
        self._base = base

    def update(self, array: bytes) -> None:
        """Add new data to the array"""
        self.array += array

    def _p(self, i: int) -> float:
        return self.array.count(i) / len(self.array)

    def shannon(self) -> float:
        """Calculate Shannon entropy"""
        H = 0.0
        for i in set(self.array):
            H -= self._p(i) * log(self._p(i), self._base)
        return H

    def metric(self) -> float:
        """Calculate normalised Shannon entropy"""
        return self.shannon() / len(self.array)

def main() -> None:
    """Entry point"""
    parser = argparse.ArgumentParser(description="Calculate entropy")
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument("-f", "--file")
    input_group.add_argument("-t", "--text")
    input_group.add_argument("-p", "--password", action="store_true")
    parser.add_argument("-b", "--base", type=float, default=2)
    entropy_group = parser.add_argument_group("entropies (at least one is required)")
    entropy_group.add_argument("-s", "--shannon", action="store_true")
    entropy_group.add_argument("-m", "--metric", action="store_true")
    args = parser.parse_args()

    if not (args.shannon or args.metric):
        parser.print_usage()
        print("You must use at least one of --shannon, --metric")
        sys.exit(1)

    entropy = Entropy(base=args.base)

    if args.file:
        with open(args.file, "rb") as fd:
            entropy.update(fd.read())
    elif args.text:
        entropy.update(bytes(args.text, ENCODING))
    elif args.password:
        entropy.update(bytes(getpass.getpass(), ENCODING))
    else:
        entropy.update(bytes(input(), ENCODING))

    if args.shannon:
        print(entropy.shannon())
    if args.metric:
        print(entropy.metric())

if __name__ == "__main__":
    main()
