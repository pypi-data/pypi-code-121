'''The entry point for SCA2D. This file runs when you run `sca2d` in terminal'''

import os
import sys
import argparse
import json
from sca2d import Analyser
from sca2d.messages import print_messages, count_messages, gitlab_summary

def parse_args():
    """
    This sets up the argumant parsing using the argparse module. It will automatically
    create a help message describing all options. Run `sca2d -h` in your terminal to see
    this description.
    """
    parser = argparse.ArgumentParser(description="SCA2D - A static code analyser for OpenSCAD.")
    parser.add_argument("file_or_dir_name",
                        metavar="<file_or_dir_name>",
                        type=str,
                        help="The .scad file to analyse or the directory to analyse.")
    parser.add_argument("--output-tree",
                        help="Output the parse tree to <filename>.sca2d",
                        action="store_true")
    parser.add_argument("--colour",
                        help=("Use colour when outputting the warning messages."
                              "May not work as expected in all terminals."),
                        action="store_true")
    parser.add_argument("--verbose",
                        help=("Put SCA2D into verbose mode."),
                        action="store_true")
    parser.add_argument("--debug",
                        help=("Also print SCA2D debug messages"),
                        action="store_true")
    parser.add_argument("--gitlab-report",
                        help=("Output a gitlab code quality report"),
                        action="store_true")
    return parser.parse_args()


def _run_on_file(args, analyser):
    [parsed, all_messages] = analyser.analyse_file(args.file_or_dir_name,
                                                   output_tree=args.output_tree)
    print_messages(all_messages, args.file_or_dir_name, args.colour, args.debug)
    return [parsed, all_messages]

def _get_all_scad_files(dir_name):
    scad_files = []
    for root, _, files in os.walk(dir_name):
        for name in files:
            if name.endswith('.scad'):
                scad_filename = os.path.join(root, name)
                scad_files.append(scad_filename)
    return scad_files


def _run_on_dir(args, analyser):
    parsed = True
    all_messages = []
    scad_files = _get_all_scad_files(args.file_or_dir_name)
    for scad_filename in scad_files:
        [file_parsed, file_messages] = analyser.analyse_file(scad_filename,
                                                             output_tree=args.output_tree)
        print_messages(file_messages, scad_filename, args.colour, args.debug)
        parsed = parsed and file_parsed
        all_messages += file_messages
    return [parsed, all_messages]

def main():
    '''
    creates a sca2d analyser and then analyses the input file. Printing
    analysis to the screen
    '''
    args = parse_args()
    analyser = Analyser(verbose=args.verbose)
    if os.path.isfile(args.file_or_dir_name):
        [_, all_messages] = _run_on_file(args, analyser)

    elif os.path.isdir(args.file_or_dir_name):
        [_, all_messages] = _run_on_dir(args, analyser)
    else:
        print("Cannot find file or directory!")
        sys.exit(-1)

    message_summary = count_messages(all_messages)
    print(message_summary)

    if args.gitlab_report:
        with open("gl-code-quality-report.json", "w") as json_file:
            json.dump(gitlab_summary(all_messages), json_file)

    if (message_summary.fatal + message_summary.error) > 0:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
