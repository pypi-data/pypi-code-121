#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.


from psym.client import SymphonyClient
from psym.common.data_class import DocumentCategory
from .location_type import get_location_type_by_name
from psym.common.data_enum import Entity
from psym.exceptions import EntityNotFoundError


def get_document_category_by_names(
    client: SymphonyClient, location_type_name: str, doc_category_name: str
) -> DocumentCategory:
    """This function gets existing Document Category by its name.

    :param location_type_name:  Location type name
    :type location_type_name: str
    :param doc_category_name:  Document Category name
    :type doc_category_name: str

    :raises:
        * FailedOperationException: Internal symphony error
        * :class:`~psym.exceptions.EntityNotFoundError`: Document Category does not exist

    :return: DocumentCategory
    :rtype: :class:`~psym.common.data_class.DocumentCategory`

    **Example**

    .. code-block:: python

        client.get_doc_category_by_names(location_type_name="COUNTRY", doc_category_name="DATAFILLS")
    """

    location_type = get_location_type_by_name(client, name=location_type_name)

    result = None
    for item in location_type.document_categories:
        if item.name == doc_category_name:
            result = item

    if result is None:
        raise EntityNotFoundError(
            entity=Entity.DocumentCategory, entity_name=doc_category_name
        )

    return result
