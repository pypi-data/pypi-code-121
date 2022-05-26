#!/usr/bin/env python
# coding: utf-8

from rich.console import Console

from .fmp import main as _main, opts


def main():
    args = opts()
    
    for file in args.files:
        if len(args.files) > 1:
            print()
            Console().rule(file)

        _main(file, **vars(args))
