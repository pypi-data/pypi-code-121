# -*- coding: utf-8 -*-

import argparse
from segmenting import Segmenter
import sys
import pcre

parser = argparse.ArgumentParser()
parser.add_argument('--srx','-s', required=True)
parser.add_argument('--lang', required=True)
parser.add_argument('--log-level', default='INFO', help="log-level (INFO|WARN|DEBUG|FATAL|ERROR)")
parser.add_argument('--no_trim', action="store_true", default=False)
parser.add_argument('--delim', default="\n")
parser.add_argument('--pure_srx', action="store_true", default=False)
parser.add_argument('--debug', default=False, action="store_true")
args = parser.parse_args()

srx = Segmenter(args.srx, args.lang, pure_srx=args.pure_srx, debug=args.debug)

for l in sys.stdin:
    l = l.strip()
    segments=srx.segment(l, trim=not args.no_trim)
    print(args.delim.join(segments))