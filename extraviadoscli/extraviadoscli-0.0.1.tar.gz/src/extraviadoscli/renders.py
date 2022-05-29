import dataclasses
import datetime
import csv
import logging
import json
import sys


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        return json.JSONEncoder.default(self, obj)


def as_csv(outfile, mpps, writeheaders=True):
    mpps = map(dataclasses.asdict, mpps)
    fieldnames = (
        "slug",
        "mp_name",
        "mp_height",
        "mp_weight",
        "mp_physical_build",
        "mp_complexion",
        "mp_sex",
        "mp_dob",
        "mp_age_when_disappeared",
        "mp_eyes_description",
        "mp_hair_description",
        "mp_outfit_description",
        "mp_identifying_characteristics",
        "circumstances_behind_dissapearance",
        "missing_from",
        "missing_date",
        "found",
        "alert_type",
        "po_state",
        "po_post_url",
        "po_post_publication_date",
        "po_poster_url",
        "is_multiple",
    )
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    if writeheaders:
        writer.writeheader()
    writer.writerows(mpps)


def as_json(outfile, mpps):
    mpps = list(map(dataclasses.asdict, mpps))
    json.dump(mpps, outfile, cls=CustomJSONEncoder)


def render_mpps(args, mpps):
    if args.outfile:
        logging.info("saving MPPs in %s", args.outfile)
        outfile = open(args.outfile, args.mode, encoding="UTF-8")
    else:
        outfile = sys.stdout

    if args.format == "json":
        as_json(outfile, mpps)
    elif args.format == "csv":
        as_csv(outfile, mpps, writeheaders=not args.csv_no_headers)

    if args.outfile:
        outfile.close()
