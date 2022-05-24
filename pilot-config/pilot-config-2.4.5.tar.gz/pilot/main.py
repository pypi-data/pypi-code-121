#!/usr/bin/env python3
import sys
import argparse
import pilotsetup
import build

argparser = argparse.ArgumentParser(description='Pilot Command-Line Interface')
subparsers = argparser.add_subparsers(dest='subparser_name')

parser_a = subparsers.add_parser('setup', help="Configure Pilot Firmware")
pilotsetup.arguments(parser_a)

parser_b = subparsers.add_parser('build', help="Compile additional software into firmware")
build.arguments(parser_b)

args = argparser.parse_args()
if ('subparser_name' in args):
  if (args.subparser_name == 'setup'):
    sys.exit(pilotsetup.main(args))
  elif (args.subparser_name == 'build'):
    sys.exit(build.main(args))
