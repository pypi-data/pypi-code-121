"""This module provides the tools to convert a PDGID to particle name and vice versa.
The PDGID data is stored in a json file named `pdgid_data.json`.
"""

import argparse
import logging
import re
import sys
import json
import pkg_resources

DATA_FILE = pkg_resources.resource_filename("pdgid", "data/pdgid_data.json")
DESCRIPTION = """Get particle name from PDGID and vice versa.
Run without argument to print PDGID table.
The particle name can often be written in many forms (e.g. "Vμ", "nu_mu", "ν_μ", "muon neutrino", etc...)
"""


def parse_args(list_of_args: list) -> argparse.Namespace:
    """Get command-line arguments"""
    parser = argparse.ArgumentParser(
        description=DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "particle",
        metavar="id/name",
        type=str,
        nargs="?",
        help="a particle name or its pdgid",
    )
    # A bit of hackery to allow space in particle name
    # Perhaps not a good feature
    parser.add_argument("rest", nargs=argparse.REMAINDER, help=argparse.SUPPRESS)
    merged_args = [" ".join(list_of_args)]
    return parser.parse_args(merged_args)


def get_id_data() -> tuple:
    """Get pdgid_data from json file.
    Return two dictionaries, one to go from PDGID to name and vice versa.
    """
    with open(DATA_FILE, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    id_to_name = {int(pdgid): names[0] for pdgid, names in data.items()}
    name_to_id = {name: int(pdgid) for pdgid, names in data.items() for name in names}
    return id_to_name, name_to_id


def add_special_cases(id_to_name: dict, name_to_id: dict) -> None:
    """Handle particles that are annoyingly unique.
    So far it's dark matter and gluons.
    """
    name_to_id["Dark[\\s-]*Matters?"] = "51 (S = 0)\n52 (S = 1/2)\n53 (S = 1)"
    name_to_id["g(luons?)?"] = "21 or 9"
    id_to_name[name_to_id["g(luons?)?"]] = "gluon"
    id_to_name[21] = "gluon (also 9)"
    id_to_name[9] = "gluon (also 21)"


def print_particle(
    args: argparse.Namespace, id_to_name: dict, name_to_id: dict
) -> None:
    """If no command-line argument is given, print PDGID table.
    If argument is numeric, use `print_name` to show particle name.
    Else, use `print_pdgid` to show particle PDGID.
    """

    if not args.particle:
        # Hacky printing of dict. If dependency management wasn't such hell
        # in python `prettytable` could be used here instead.
        sorted_table = sorted(
            [(id_, names) for id_, names in id_to_name.items() if isinstance(id_, int)]
        )
        pretty_table = "\n".join(
            [f"{id_}: {names}" for id_, names in sorted_table if id_ > 0]
        )
        print(pretty_table)
        return

    if args.particle.lstrip("-").isnumeric():
        print_name(id_to_name, int(args.particle))
    else:
        print_pdgid(args.particle, name_to_id, id_to_name)


def print_name(id_to_name: dict, pdgid: int) -> None:
    """Try and find name in id_to_name and print it"""
    if pdgid in id_to_name:
        print(id_to_name[pdgid])
    elif abs(pdgid) in id_to_name:
        print(f"Antiparticle of {id_to_name[abs(pdgid)]}")
    else:
        logging.error("Unknown PDGID: %s", pdgid)


def print_pdgid(input_name: str, name_to_id: dict, id_to_name: dict) -> None:
    """Try and find PDGID in name_to_id and print it"""
    for name, pdgid in name_to_id.items():
        if re.match(f"^{name}$", input_name, *extra_re_args(input_name)):
            print(f"{pdgid} [{id_to_name[pdgid]}]")
            return
    logging.error("Unknown particle name: %s", input_name)


def extra_re_args(name: str) -> list:
    """Extra arguments to be passed to the call to `re.match`
    Currently just checks if `name` should be case sensitive.
    """
    if name.lower() in ["g", "a0", "a^0"]:
        return []
    return [re.IGNORECASE]


def main() -> None:
    """This is the function called by the pdgid executable"""
    args = parse_args(sys.argv[1:])
    logging.basicConfig(format="%(levelname)s - %(message)s")
    id_to_name, name_to_id = get_id_data()
    add_special_cases(id_to_name, name_to_id)
    print_particle(args, id_to_name, name_to_id)
