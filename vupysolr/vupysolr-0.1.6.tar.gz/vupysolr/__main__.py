import json
import argparse

from . import get


def main():
    vupysolr_cli = argparse.ArgumentParser("vupysolr", description="")
    vupysolr_cli.add_argument("--url", type=str, help="URL of VuFind Solr server (default: http://localhost:8983/solr)", default="http://localhost:8983/solr")
    vupysolr_cli.add_argument("--core", type=str, help="Name of VuFind Solr core (default: biblio)", default="biblio")
    vupysolr_cli.add_argument("--id", type=str, help="ID of record to fetch (default: None)", default=None)
    vupysolr_cli.add_argument("--marc", type=bool, help="Get MARC data only (default: False)", nargs='?', const=True, default=False)
    vupysolr_cli.add_argument("--decode", type=bool, help="Decode MARC data (default: False)", nargs='?', const=True, default=False)
    vupysolr_cli.add_argument("--pretty", type=bool, help="Pretty print output (default: False)", nargs='?', const=True, default=False)
    vupysolr_args = vupysolr_cli.parse_args()
    if vupysolr_args.id is None:
        vupysolr_cli.print_help()
        return None
    if vupysolr_args.marc and vupysolr_args.decode is False:
        vupysolr_args.decode = True
    doc = get(vupysolr_args.id,
              url=vupysolr_args.url,
              core=vupysolr_args.core,
              marc=vupysolr_args.decode)
    if doc is not None:
        output = doc.raw
        if vupysolr_args.marc:
            output = doc.get("fullrecord")
        if output is not None:
            if vupysolr_args.pretty:
                print(json.dumps(output, ensure_ascii=False, indent=2))
            else:
                print(json.dumps(output, ensure_ascii=False))


if __name__ == '__main__':
    main()
