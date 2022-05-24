#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.


from psym.client import SymphonyClient
from psym.common.data_class import Vendor

from ..graphql.input.edit_vendor_input import EditVendorInput
from ..graphql.input.add_vendor_input import AddVendorInput
from ..graphql.mutation.add_vendor import addVendor
from ..graphql.mutation.edit_vendor import editVendor
from ..graphql.mutation.remove_vendor import removeVendor
from ..graphql.query.vendors import vendors
from psym.common.constant import PAGINATION_STEP
from typing import Any, Dict, Iterator, List, Optional




def add_vendor(
    client: SymphonyClient, name: str
) -> Vendor:
    """This function adds vendor.

    :param name: vendor name
    :type name: str

    :return: vendor object
    :rtype: :class:`~psym.common.data_class.vendor`


    **Example 1**

    .. code-block:: python

        new_vendor = client.add_vendor(
            name="vendor",
        )
        print(new_vendor)
    """
    vendor_input = AddVendorInput(name=name)
    if (len(name) != 0):
        result = addVendor.execute(client, input=vendor_input)
        return Vendor(name=result.name, id=result.id)
    else:
        print ("you cant leave the name parameter empty")

def edit_vendor(
    client: SymphonyClient,
    vendor: Vendor,
    new_name: Optional[str] = None,
) -> None:
    """This function edits vendor.

    :param vendor: vendor entity
    :type name: str
    :param new_name: vendor name
    :type name: str

    :return: none object
    :rtype: :class:`~psym.common.data_class.vendor`

    **Example 1**

    .. code-block:: python

        vendor_edited = client.edit_vendor(
            vendor=vendor,
            new_name="new_vendor")
    """
    params: Dict[str, Any] = {}
    if new_name is not None:
        params.update({"_name_": new_name})
    if new_name is not None:
        editVendor.execute(client, input=EditVendorInput(id=vendor.id, name=new_name))


def get_vendors(client: SymphonyClient) -> Iterator[Vendor]:
    """ this funtion Get vendors


    :return: vendor object
    :rtype: Iterator[ :class:`~psym.common.data_class.vendor` ]

    **Example**

    .. code-block:: python

        vendors = client.get_vendors()
        for vendor in vendors:
            print(vendor.name)
    """
    vendors_ = vendors.execute(client, first=PAGINATION_STEP)
    edges = vendors_.edges if vendors_ else []
    while vendors_ is not None and vendors_.pageInfo.hasNextPage:
        vendors_ = vendors.execute(
            client, after=vendors_.pageInfo.endCursor, first=PAGINATION_STEP
        )
        if vendors_ is not None:
            edges.extend(vendors_.edges)

    for edge in edges:
        node = edge.node
        if node is not None:
            yield Vendor(
                id=node.id,
                name=node.name,
            )


def remove_vendor(client: SymphonyClient, id: str) -> None:
    """This function delete vendor.

    :param name: vendor name
    :type name: :class:`~psym.common.data_class.vendor`
    :rtype: None

    **Example**

    .. code-block:: python

        client.remove_vendor(id=123456789)
    """
    removeVendor.execute(client, id=id)