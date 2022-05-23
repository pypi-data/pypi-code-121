# Copyright 2020-2022 Daniel Harding
# Distributed as part of the pyflame project under the terms of the MIT license

import os.path
import shlex
import sys

from argparse import ArgumentParser


from pyflame.render import stack_counts_to_svg
from pyflame.sampler import Sampler


def _preprocess_stack(stack):
    stack_iter = iter(stack)
    for name, filename, firstlineno in stack_iter:
        if filename == __file__:
            break
    return list(stack_iter)


def main():
    parser = ArgumentParser(
        prog="python -m pyflame",
        description="Run a Python script and generate a flamegraph from its execution",
        allow_abbrev=False,
    )
    parser.add_argument(
        "-p", "--flamegraph-script-path",
        metavar="path",
        help="the path to the flamegraph.pl script (if not specified, search using the"
            " PATH environment variable)",
    )
    parser.add_argument(
        "-a", "--flamegraph-extra-args",
        metavar="arg_string",
        help="a string specifying extra command line arguments to pass when invoking"
            " flamegraph.pl",
    )
    parser.add_argument(
        "-s", "--sample-interval",
        metavar="interval",
        type=float,
        default=0.001,
        help="the amount of time the sampler thread will wait between capturing stack"
            "traces, in seconds (default: 0.001)",
    )
    parser.add_argument(
        "-o", "--output-path",
        metavar="path",
        help='the location to save the flamegraph (if not specified, save in the'
            ' current directory using the name of the Python script with an ".svg"'
            ' extension appended)',
    )
    parser.add_argument(
        "script_path",
        help="the Python script to run",
    )
    parser.add_argument(
        "script_args",
        metavar="args",
        nargs="*",
        help="optional arguments to pass to the script",
    )
    args = parser.parse_args()

    if args.flamegraph_extra_args is not None:
        flamegraph_extra_args = shlex.split(args.flamegraph_extra_args)
    else:
        flamegraph_extra_args = None

    if args.output_path is not None:
        output_path = args.output_path
    else:
        output_path = os.path.basename(args.script_path) + '.svg'
    output_path = os.path.abspath(output_path)

    sys.path.insert(0, os.path.dirname(args.script_path))
    with open(args.script_path, 'rb') as f:
        code = compile(f.read(), args.script_path, 'exec')

    globs = {
        '__file__': args.script_path,
        '__name__': '__main__',
        '__package__': None,
        '__cached__': None,
    }

    sys.argv[:] = [args.script_path] + args.script_args

    sampler = Sampler(args.sample_interval)
    try:
        exec(code, globs, globs)
    finally:
        stack_counts = sampler.stop()
        svg = stack_counts_to_svg(
            stack_counts,
            args.flamegraph_script_path,
            flamegraph_extra_args,
            preprocess_stack=_preprocess_stack,
        )
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg)
