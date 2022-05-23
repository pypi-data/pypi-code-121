#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.


from psym.client import SymphonyClient
from psym.common.data_class import NetworkType, domain

from ..graphql.input.edit_network_type_input import EditNetworkTypeInput
from ..graphql.input.add_network_type_input import AddNetworkTypeInput
from ..graphql.mutation.add_network_type import addNetworkType
from ..graphql.mutation.edit_network_type import editNetworkType
from ..graphql.mutation.remove_network_type import removeNetworkType
from ..graphql.query.network_types import networkTypes
from psym.common.constant import PAGINATION_STEP
from typing import Any, Dict, Iterator, List, Optional




def add_network_type(
    client: SymphonyClient, name: str
) -> NetworkType:
    """This function adds Network Type.

    :param name: Network Type name
    :type name: str

    :return: networkType object
    :rtype: :class:`~psym.common.data_class.networkType`


    **Example 1**

    .. code-block:: python

        new_network_type = client.add_network_type(
            name="network_type",
        )
        print(new_network_type)
    """
    network_type_input = AddNetworkTypeInput(name=name)
    if (len(name) != 0):
        result = addNetworkType.execute(client, input=network_type_input)
        return NetworkType(name=result.name, id=result.id)
    else:
        print ("you cant leave the name parameter empty")

def edit_network_type(
    client: SymphonyClient,
    network_type: NetworkType,
    new_name: Optional[str] = None,
) -> None:
    """This function edits Network Type.

    :param network_type: Network Type entity
    :type name: str
    :param new_name: Network Type name
    :type name: str

    :return: none object
    :rtype: :class:`~psym.common.data_class.networkType`

    **Example 1**

    .. code-block:: python

        new_network_type = client.edit_network_type(
            network_type=networkType,
            new_name="network_type_edit",

        )
    """
    params: Dict[str, Any] = {}
    if new_name is not None:
        params.update({"_name_": new_name})
    if new_name is not None:
        editNetworkType.execute(client, input=EditNetworkTypeInput(id=network_type.id, name=new_name))


def get_network_types(client: SymphonyClient) -> Iterator[NetworkType]:
    """ this funtion Get Network Types


    :return: networkType object
    :rtype: Iterator[ :class:`~psym.common.data_class.networkType` ]

    **Example**

    .. code-block:: python

        network_types = client.get_network_types()
        for network_type in network_types:
            print(network_type.name)
    """
    network_types_ = networkTypes.execute(client, first=PAGINATION_STEP)
    edges = network_types_.edges if network_types_ else []
    while network_types_ is not None and network_types_.pageInfo.hasNextPage:
        network_types_ = networkTypes.execute(
            client, after=network_types_.pageInfo.endCursor, first=PAGINATION_STEP
        )
        if network_types_ is not None:
            edges.extend(network_types_.edges)

    for edge in edges:
        node = edge.node
        if node is not None:
            yield NetworkType(
                id=node.id,
                name=node.name,
            )


def remove_network_type(client: SymphonyClient, id: str) -> None:
    """This function delete Network Type.

    :param name: Network Type name
    :type name: :class:`~psym.common.data_class.networkType`
    :rtype: None

    **Example**

    .. code-block:: python

        client.remove_network_type(id=12346789)
    """
    removeNetworkType.execute(client, id=id)