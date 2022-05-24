#!/usr/bin/python3

__version__ = "0.0.1"

from ptlibs import ptjsonlib, ptmisclib
import argparse
import sys
import requests
import json


class ptvulnsearcher:
    def __init__(self, args):
        self.ptjsonlib = ptjsonlib.ptjsonlib(args.json)
        self.json_no = self.ptjsonlib.add_json("ptvulnsearcher")
        self.use_json = args.json
        self.args = args

    def run(self):
        if self.args.search or self.args.cve:
            vulns = search_cve(self.args.search, self.args.cve)
            if self.args.json:
                print(vulns)
            else:
                vulns = json.loads(vulns)
                ptmisclib.ptprint_(ptmisclib.out_ifnot(
                    f"Found {len(vulns)} CVE Records", "INFO", self.use_json))
                for vuln in vulns:
                    cve = vuln["cve"]
                    desc = vuln["description"]
                    score = vuln["cvss_score"] if vuln["cvss_score"] else "Not defined"
                    vector = vuln["cvss_string"] if vuln["cvss_string"] else "Not defined"
                    ptmisclib.ptprint_(
                        ptmisclib.out_ifnot(f" ", "", self.use_json))
                    ptmisclib.ptprint_(ptmisclib.out_title_ifnot(
                        f"{cve}", self.use_json))
                    ptmisclib.ptprint_(
                        ptmisclib.out_ifnot(f'\n{ptmisclib.get_colored_text("Description:", color="TITLE")} {desc}', "", self.use_json))
                    ptmisclib.ptprint_(
                        ptmisclib.out_ifnot(f'{ptmisclib.get_colored_text("CVSS Score:", color="TITLE")} {score}', "", self.use_json))
                    ptmisclib.ptprint_(
                        ptmisclib.out_ifnot(f'{ptmisclib.get_colored_text("CVSS Vector:", color="TITLE")} {vector}', "", self.use_json))
            sys.exit(0)
        ptmisclib.ptprint_(ptmisclib.out_if(
            self.ptjsonlib.get_all_json(), "", self.use_json))


def get_help():
    return [
        {"description": [
            "Tool for searching CVE (Common Vulnerabilities and Exposures)"]},
        {"usage": ["ptvulnsearcher <options>"]},
        {"usage_example": [
            "ptvulnsearcher -s Apache v2.2",
        ]},
        {"options": [
            ["-s", "--search", "<search>", "Search keywords"],
            ["-cve", "--cve", "<cve>", "Search specific CVE"],
            ["-j",  "--json", "",  "Output in JSON format"],
            ["-v",  "--version", "", "Show script version and exit"],
            ["-h", "--help", "", "Show this help message and exit"],
        ]
        }]


def search_cve(search_string, search_cve):
    api_url = "https://as.penterep.com:8443/api/v1/cve/search"
    parameters = {"search": search_string, "cve": search_cve}
    response = requests.get(api_url, params=parameters)
    response_json = response.json()

    return json.dumps(response_json['data'], indent=2)


def parse_args():
    parser = argparse.ArgumentParser(
        add_help=False, usage=f"{SCRIPTNAME} <options>")
    parser.add_argument("-s", "--search", type=str)
    parser.add_argument("-cve", "--cve", type=str)
    parser.add_argument("-j", "--json", action="store_true")
    parser.add_argument("-v", "--version", action="version",
                        version=f"%(prog)s {__version__}")

    if len(sys.argv) == 1 or "-h" in sys.argv or "--help" in sys.argv:
        ptmisclib.help_print(get_help(), SCRIPTNAME, __version__)
        sys.exit(0)

    args = parser.parse_args()
    ptmisclib.print_banner(SCRIPTNAME, __version__, args.json)
    return args


def main():
    global SCRIPTNAME
    SCRIPTNAME = "ptvulnsearcher"
    args = parse_args()
    script = ptvulnsearcher(args)
    script.run()


if __name__ == "__main__":
    main()
