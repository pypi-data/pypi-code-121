import logging
from argparse import ArgumentParser

from yog.host.manage import apply_necronomicon


def main():
    args = ArgumentParser()
    args.add_argument("host")
    args.add_argument("--root-dir", default="./")

    opts = args.parse_args()
    logging.info(f"Invoked with: {opts}")
    apply_necronomicon(opts.host, opts.root_dir)