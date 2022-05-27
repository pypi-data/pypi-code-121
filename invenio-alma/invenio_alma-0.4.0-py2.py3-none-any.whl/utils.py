# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Common utils functions."""

import time
from os.path import basename

from flask_principal import Identity
from invenio_access import any_user
from invenio_access.utils import get_identity
from invenio_accounts import current_accounts
from invenio_records_marc21 import current_records_marc21
from invenio_records_marc21.services.services import Marc21RecordFilesService


def get_identity_from_user_by_email(email: str = None) -> Identity:
    """Get the user specified via email or ID."""
    if email is None:
        raise ValueError("the email has to be set to get a identity")

    user = current_accounts.datastore.get_user(email)

    if user is None:
        raise LookupError(f"user with {email} not found")

    identity = get_identity(user)

    # TODO: this is a temporary solution. this should be done with data from the db
    identity.provides.add(any_user)

    return identity


def add_file_to_record(
    marcid: str,
    file_path: str,
    file_service: Marc21RecordFilesService,
    identity: Identity,
) -> None:
    """Add the file to the record."""
    filename = basename(file_path)
    data = [{"key": filename}]

    with open(file_path, mode="rb") as file_pointer:
        file_service.init_files(id_=marcid, identity=identity, data=data)
        file_service.set_file_content(
            id_=marcid, file_key=filename, identity=identity, stream=file_pointer
        )
        file_service.commit_file(id_=marcid, file_key=filename, identity=identity)


def create_record(marc21_metadata, file_path, identity):
    """Create the record."""
    service = current_records_marc21.records_service

    draft = service.create(metadata=marc21_metadata, identity=identity, files=True)

    add_file_to_record(
        marcid=draft._record["id"],  # pylint: disable=protected-access
        file_path=file_path,
        file_service=service.draft_files,
        identity=identity,
    )

    # to prevent the race condition bug.
    # see https://github.com/inveniosoftware/invenio-rdm-records/issues/809
    time.sleep(0.5)

    return service.publish(id_=draft.id, identity=identity)
