#!/usr/bin/env python3

import argparse


def main(**kwargs):
    for k, v in kwargs.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--proximity", type=int, dest="proximity", default=None)
    parser.add_argument("-l", "--limits", type=int, nargs=3, dest="limits", default=None)
    kwargs = vars(parser.parse_args())
    main(**kwargs)