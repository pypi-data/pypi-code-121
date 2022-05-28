import re
import sys
import os
import argparse
from p_cmd_runr import p_cmd_runr as pcr
from p_cmd_runr import file_manip as fm



def main():
    """
    Description:
        Implements the functionality of the general purpose command runner (gp_cmd_runr.py) executable script/module.
        If you create a tmp folder, the script will attempt to move the output files to that tmp folder.
    """
    parser = argparse.ArgumentParser(prog="gp_cmd_runr.py", description="general purpose command runner", \
                               epilog="""*** NO RESPONSIBILITY OR LIABILITY DISCLAIMER ***
IN NO EVENT SHALL THE AUTHOR BE LIABLE TO YOU OR ANY THIRD PARTIES FOR ANY SPECIAL, 
PUNITIVE, INCIDENTAL, INDIRECT OR CONSEQUENTIAL DAMAGES OF ANY KIND, 
OR ANY DAMAGES WHATSOEVER, INCLUDING, WITHOUT LIMITATION, 
THOSE RESULTING FROM LOSS OF USE, LOST DATA OR PROFITS, OR ANY LIABILITY, 
ARISING OUT OF OR IN CONNECTION WITH THE USE OF THIS SCRIPT.""")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-r", "--raw", dest="filemanip", const=None, action='store_const', help="no manipulation of output file(s)")
    group.add_argument("-n", "--normal", dest="filemanip", const=fm.deflate_file, action='store_const', help="remove duplicate '\\n' between lines in output file(s). this normal appearance is the default behavior")
    group.add_argument("-f", "--flatten", dest="filemanip", const=fm.flatten_file, action='store_const', help="only have output file(s) containing a single '\\n' between lines")
    parser.add_argument("-d", "--dry_run", help="display loaded configuration, but do not execute", action="store_true")
    parser.add_argument("-t", "--timeout", help="sets command execution to non-blocking. default is blocking", action="store_true")
    parser.add_argument("-p", "--print_output", action="store_true", help="flag to print command output to the screen. default is not to print")
    parser.add_argument("-c", "--config", nargs="+", help="one or more local configuration files. default is config.txt")
    parser.set_defaults(filemanip=fm.deflate_file)
    args = parser.parse_args()
    cgol = []
    if args.config:
        if len(args.config) > 1:
            print(f"\nusing configuration files {args.config}")
        else:
            print(f"\nusing configuration file {args.config}")
        for c in args.config:
            cgol.append(pcr.ConfigGrabber(c))
    else:
        cgol.append(pcr.ConfigGrabber())

    if not args.dry_run:
        for cgo in cgol:
            nodes = pcr.get_all_nodes(cgo)
            fp = pcr.boxjumper(cgo, len(cgo), print_output=args.print_output, blocking= not args.timeout)
            if fp:
                fp.close()
            pcr.move_to_tmp(nodes, args.filemanip)
    else:
        print(f"blocking is {not args.timeout}")
        print(f"print output is {args.print_output}")
        if args.filemanip == fm.deflate_file:
            print("normal output\n")
        elif args.filemanip == fm.flatten_file:
            print("flattened output\n")
        elif args.filemanip == None:
            print("raw output\n")
        else:
            print("unkown file manipulation option")
        for cgo in cgol:
            print(cgo.filename)
            print(cgo)

    

if __name__ == "__main__":
    main()
