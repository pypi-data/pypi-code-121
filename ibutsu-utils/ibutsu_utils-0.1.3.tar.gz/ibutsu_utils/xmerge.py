import sys
from argparse import ArgumentParser
from pathlib import Path
from xml.etree import ElementTree


def parse_args():
    """Parse command line arguments"""
    parser = ArgumentParser()
    parser.add_argument("-o", "--output", help="Output to a file. Defaults to stdout without this.")
    parser.add_argument("input", nargs="+", help="Input files")
    return parser.parse_args()


def merge_files(filenames):
    """Actually merge the XML files and return the merged XML"""
    main_xml = None
    for filename in filenames:
        if not Path(filename).resolve().exists():
            print("WARNING: {} does not exist".format(filename), file=sys.stderr)
            break
        next_xml = ElementTree.parse(filename).getroot()
        if main_xml is None:
            main_xml = next_xml
        else:
            main_xml.extend(next_xml)
            for key, value in next_xml.items():
                if type(value) in [int, float]:
                    updated_value = main_xml.attrib.get(key, 0) + value
                else:
                    updated_value = value
                main_xml.set(key, updated_value)
    if main_xml is not None:
        return ElementTree.tostring(main_xml).decode("utf-8")


def main():
    args = parse_args()
    output_xml = merge_files(args.input)
    if not output_xml:
        return
    if args.output:
        with open(args.output, "w") as outfile:
            outfile.write(output_xml)
    else:
        print(output_xml)


if __name__ == "__main__":
    main()
