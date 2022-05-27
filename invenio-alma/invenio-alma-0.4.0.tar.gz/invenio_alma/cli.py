# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Command line interface to interact with the Alma-Connector module."""

import sys
from csv import DictReader

# import logging
from os.path import isfile

import click
from click_option_group import optgroup
from elasticsearch_dsl import Q
from flask.cli import with_appcontext
from invenio_records_marc21 import current_records_marc21
from invenio_records_marc21.records.systemfields import MarcDraftProvider
from invenio_records_marc21.services.record.metadata import Marc21Metadata
from invenio_search import RecordsSearch
from sqlalchemy.orm.exc import StaleDataError

from .proxies import current_alma
from .services import AlmaSRUService
from .utils import create_record, get_identity_from_user_by_email

# logging.basicConfig()
# logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


class DuplicateRecordError(Exception):
    """Duplicate Record Exception."""

    def __init__(self, ac_number):
        """Constructor for class DuplicateRecordException."""
        msg = f"ac_number: {ac_number} already exists in the database"
        super().__init__(msg)


class CSV(click.ParamType):
    """CSV provides the ability to load a csv from a file."""

    name = "CSV"

    def __init__(self, header=None):
        """Constructor of CSV type."""
        super().__init__()
        self.header = header
        self.check_header = header is not None

    @property
    def headers(self):
        """Headers."""
        return self.header.split(",")

    def is_header_as_expected(self, csv_file):
        """Check if the header is as expected."""
        reader = DictReader(csv_file)
        first_row = next(reader)
        # because iterator has no previous method
        csv_file.seek(0)

        return all(name in first_row for name in self.headers)

    def convert(self, value, param, ctx) -> DictReader:
        """This method opens the files as a DictReader object."""
        if not isfile(value):
            click.secho("ERROR - please look up if the file path is correct.", fg="red")
            sys.exit()

        csv_file = open(value, mode="r", encoding="utf-8")
        reader = DictReader(csv_file)

        if self.check_header and not self.is_header_as_expected(csv_file):
            msg = f"ERROR - the header should have the form: {self.header}."
            click.secho(msg, fg="red")
            sys.exit()

        return reader


# TODO:
# move to invenio-records-marc21
def check_about_duplicate(ac_number):
    """Check if the record with the ac number is already within the database."""
    search = RecordsSearch(index="marc21records-marc21")
    search.query = Q("match", **{"metadata.fields.009": ac_number})
    results = search.execute()

    if len(results) > 0:
        raise DuplicateRecordError(ac_number=ac_number)


def handle_csv(alma_sru_service, csv_file, identity):
    """Process csv file."""
    for row in csv_file:
        if len(row["ac_number"]) == 0:
            continue

        handle_single_import(alma_sru_service, **row, identity=identity)


def handle_single_import(
    alma_sru_service, ac_number, file_path, identity, marcid=None, **_
):
    """Process a single import of a alma record by ac number."""
    if marcid:
        MarcDraftProvider.predefined_pid_value = marcid

    try:
        check_about_duplicate(ac_number)

        marc21_record = Marc21Metadata(alma_sru_service.get_record(ac_number))
        record = create_record(marc21_record, file_path, identity)

        print(f"record.id: {record.id}")
    except FileNotFoundError:
        print(f"FileNotFoundError search_value: {ac_number}")
    except DuplicateRecordError as error:
        print(error)
    except StaleDataError:
        print(f"StaleDataError    search_value: {ac_number}")


@click.group()
def alma():
    """Alma CLI."""


@alma.command()
@with_appcontext
@optgroup.group("Request Configuration", help="The Configuration for the request")
@optgroup.option("--search-key", type=click.STRING, required=True)
@optgroup.option("--domain", type=click.STRING, required=True)
@optgroup.option("--institution-code", type=click.STRING, required=True)
@optgroup.group("Manually set the values to search and import")
@optgroup.option("--ac-number", type=click.STRING)
@optgroup.option("--filename", type=click.STRING)
@optgroup.option("--user-email", type=click.STRING, default="alma@tugraz.at")
@optgroup.option("--marcid", type=click.STRING, default="")
@optgroup.group("Import by file list")
@optgroup.option("--csv-file", type=CSV())
def sru(
    search_key,
    domain,
    institution_code,
    ac_number,
    filename,
    user_email,
    marcid,
    csv_file,
):
    """Search on the SRU service of alma."""
    identity = get_identity_from_user_by_email(email=user_email)
    alma_sru_service = AlmaSRUService.build(search_key, domain, institution_code)

    if csv_file:
        handle_csv(alma_sru_service, csv_file, identity)
    else:
        handle_single_import(alma_sru_service, ac_number, filename, identity, marcid)


@alma.command("update-url-in-alma")
@with_appcontext
@click.option(
    "--csv-file",
    type=CSV(header="mms_id,new_url"),
    required=True,
    help="two columns: mms_id and new_url",
)
def update_url_in_alma(csv_file):
    """Update url in remote repository records.

    :params csv_file (file) with two columns mms_id and new_url
    """
    for row in csv_file:
        current_alma.alma_rest_service.update_field(
            row["mms_id"], "856.4._.u", row["new_url"]
        )


@alma.command()
@with_appcontext
@click.option("--mms-id", type=click.STRING, required=True)
@click.option(
    "--field-json-path", type=click.STRING, required=True, help="e.g. 100.1._.u"
)
@click.option("--subfield-value", type=click.STRING, default="")
@click.option("--new-subfield-value", type=click.STRING, required=True)
@click.option(
    "--new-subfield-template",
    type=click.STRING,
    help="the template is given as json path 100.2.1.u",
    default="",
)
def update_field(
    mms_id, field_json_path, subfield_value, new_subfield_value, new_subfield_template
):
    """Update field."""
    current_alma.alma_rest_service.update_field(
        mms_id,
        field_json_path,
        new_subfield_value,
        subfield_value,
        new_subfield_template,
    )


@alma.group()
def create():
    """Alma Create group."""


@create.command("alma-record")
@click.option("--marc-id", type=click.STRING, required=True)
def create_alma_record(marc_id):
    """Create alma record."""
    # TODO:
    # create a record within alma from an existing repository record with the
    # marcid=[MARCID]
    # use service provided by invenio-records-marc21 to get the record. current
    # package should not write a service for the marc21 datamodel

    # SKETCH:
    record = current_records_marc21.record_service.get_record(marc_id, type_="marcxml")
    mms_id = current_alma.alma_rest_service.create_record(record)
    # DISCUSS:
    # "035...a" vs "035. . .a" vs "035._._.a"
    current_records_marc21.record_service.add_field(marc_id, "035._._.a", mms_id)


@create.command("repository-record")
@click.option("--mms-id", type=click.STRING, required=True)
def create_repository_record(mms_id):  # pylint: disable=unused-argument
    """Create repository record."""
    print("not yet implemented")
    # TODO:
    # create a record within the repository from an existing alma record
    # with mms_id=[MMS_ID]
    # use service provided by invenio-records-marc21 to create the record

    # SKETCH
    # record = current_alma.record_service.get_record(mms_id)

    # TODO:
    # massage data to move 001 mms-id to 035__a (tugraz)mms-id

    # current_records_marc21.record_service.create_record()
