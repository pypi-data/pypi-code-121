import re
import sys
import os
import argparse
from p_cmd_runr import p_cmd_runr as pcr
from p_cmd_runr import file_manip as fm



def main():
    """
    Description:
        Will return any B#/Routing Case overlaps that may exist.
        If you create a tmp folder, the script will attempt to move the output files to that tmp folder.
    """
    parser = argparse.ArgumentParser(prog="find_overlap.py", description="Finds potentional overlaps in LERG B-number definitions")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-f", "--filename", dest="filename", required=False, default="input.txt", help="name of file to process. defaults to input.txt if not specified.")
    group.add_argument("-l", "--local", nargs="+", help="find overlaps in provided file(s) without contacting MSC(s).")
    parser.add_argument("-t", "--timeout", help="sets command execution to non-blocking. default is blocking", action="store_true")
    parser.add_argument("-p", "--print_output", action="store_true", help="flag to print command output to the screen. default is not to print")
    parser.add_argument("-c", "--config", default="config.txt", help="name of configuration file. defaults to config.txt if not specified.")
    args = parser.parse_args()

    if args.local:
        for fn in args.local:
            print(f"Checking overlaps in {fn}")
            find_overlap(fn)
    else:
        print(f"Processing {args.filename}")
        inf = args.filename
        config = args.config
        outf = "defs_to_query.txt"
        build_queries_from_definitions(infilename=inf, outfilename=outf)
        if os.stat(outf).st_size <= len("mml\r\n"):
            build_queries_from_definitions(infilename=inf, outfilename=outf, segment="ANBSP")
        cgo = pcr.ConfigGrabber(filename=config)
        nodes = pcr.get_nodes(cgo)
        fp = None
        fp = pcr.boxjumper(cgo, len(cgo), print_output=args.print_output, blocking= not args.timeout)
        if fp:
            fp.close()
        for node in nodes:
            with os.scandir() as entries:
                for entry in entries:
                    if entry.name.startswith(node) and not entry.is_dir(follow_symlinks=False):
                        print(f"Checking overlaps in {entry.name}")
                        find_overlap(entry.name)
            entries.close()

        pcr.move_to_tmp(nodes, fm.deflate_file)
   


def build_queries_from_definitions(infilename, outfilename="defs_to_query.txt", segment="ANBSI"):
    dr = re.compile(segment + ":B=((\w+)-(\w+))", re.I)

    with open(outfilename, mode="wt", encoding="utf-8") as ofp:
        n = ofp.write("mml\n")
        with open(infilename, mode="rt", encoding="utf-8") as ifp:
            found = False
            lines = ifp.readlines()
            while(len(lines)):
                line = lines.pop(0)
                do = dr.search(line)
                if do:
                    found = True
                    if "ANBSI" in do.group(0).upper():
                        ofp.write("ANBSP:B=" + do.group(1) + ";\n")
                    else:
                        ofp.write(do.group(0) + ";\n")
            if found:
                ofp.write("exit;\nexit")

        

def find_overlap(filename):
    rh = re.compile("ANBSP:B=((\w+)-(\w+))", re.I)
    rp = re.compile("((\w+)-(\w+))\s+RC=(\w+)", re.I)
    rq = re.compile("END", re.I)
    rq2 = re.compile("^\s*$")
    
    with open(filename, mode="rt", encoding="utf-8") as fp:
        lines = fp.readlines()
        lines = fm.flatten(lines)
        while(len(lines)):
            line = lines.pop(0)
            ho = rh.search(line)
            if ho:
                next_line = lines.pop(0)
                while not (rq.search(next_line) or rq2.search(next_line)):
                    po = rp.search(next_line)
                    if po:
                        if len(ho.group(1)) > len(po.group(1)):
                            print("Overlap:\n{}\n{}\n".format(ho.group(0), po.group(0)))
                    try:
                        next_line = lines.pop(0)
                    except:
                        pass                    
     


if __name__ == "__main__":
    main()
