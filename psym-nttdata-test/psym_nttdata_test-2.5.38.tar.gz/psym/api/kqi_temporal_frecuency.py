#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.




from psym.client import SymphonyClient
from psym.common.data_class import KqiTemporalFrecuency

from ..graphql.input.edit_kqi_temporal_frequency_input import EditKqiTemporalFrequencyInput
from ..graphql.input.add_kqi_temporal_frequency_input import AddKqiTemporalFrequencyInput
from ..graphql.mutation.add_kqi_temporal_frecuency import AddKqiTemporalFrequencyInput, addKqiTemporalFrequency
from ..graphql.mutation.edit_kqi_temporal_frecuency import EditKqiTemporalFrequencyInput, editKqiTemporalFrequency
from ..graphql.query.kqi_temporal_frecuency import kqiTemporalFrequencies
from ..graphql.mutation.remove_kqi_temporal_frecuency import removeKqiTemporalFrequency
from psym.common.constant import PAGINATION_STEP
from typing import Any, Dict, Iterator, List, Optional




def add_kqi_temporal_frecuency(
    client: SymphonyClient, name: str
) -> KqiTemporalFrecuency:
    """This function adds KqiTemporalFrecuency.

    :param name: KqiTemporalFrecuency name
    :type name: str

    :return: kqiTemporalFrecuency object
    :rtype: :class:`~psym.common.data_class.kqiTemporalFrecuency`

    **Example 2**

    .. code-block:: python

        new_kqi_temporal_frecuency = client.add_kqi_temporal_frecuency(
            name="kqi_temporal_frecuency",

        )
    """
    kpi_category_input = AddKqiTemporalFrequencyInput(name=name)
    if (len(name) != 0):
        result = addKqiTemporalFrequency.execute(client, input=kpi_category_input)
        return KqiTemporalFrecuency(name=result.name, id=result.id)
    else:
        print ("you cant leave the name parameter empty")

def edit_kqi_temporal_frecuency(
    client: SymphonyClient,
    kqitemporalfrecuency: KqiTemporalFrecuency,
    new_name: Optional[str] = None,
) -> None:
    """This function edits KqiTemporalFrecuency.

    :param kqi_temporal_frecuency: KqiTemporalFrecuency entity
    :type name: str
    :param new_name: KqiTemporalFrecuency name
    :type name: str

    :return: none object
    :rtype: :class:`~psym.common.data_class.kqiTemporalFrecuency`

    **Example 1**

    .. code-block:: python

        new_kqi_temporal_frecuency_edited = client.edit_kqi_temporal_frecuency(
            kqi_temporal_frecuency=kqiTemporalFrecuency,
            new_name="kqi_temporal_frecuency_edited",

        )
    """
    params: Dict[str, Any] = {}
    if new_name is not None:
        params.update({"_name_": new_name})
    if new_name is not None:
        editKqiTemporalFrequency.execute(client, input=EditKqiTemporalFrequencyInput(id=kqitemporalfrecuency.id, name=new_name))


def get_kqi_temporal_frecuencies(client: SymphonyClient) -> Iterator[KqiTemporalFrecuency]:
    """ this funtion Get KqiTemporalFrecuencies


    :return: kqiTemporalFrecuency object
    :rtype: Iterator[ :class:`~psym.common.data_class.kqiTemporalFrecuency` ]

    **Example**

    .. code-block:: python

        kqi_temporal_frecuencyes = client.get_kqi_temporal_frecuencies()
        for kqi_temporal_frecuency in kqi_temporal_frecuencies:
            print(kqi_temporal_frecuency.name)
    """
    kqi_temporal_frecuencies = kqiTemporalFrequencies.execute(client, first=PAGINATION_STEP)
    edges = kqi_temporal_frecuencies.edges if kqi_temporal_frecuencies else []
    while kqi_temporal_frecuencies is not None and kqi_temporal_frecuencies.pageInfo.hasNextPage:
        kqi_temporal_frecuencies = kqiTemporalFrequencies.execute(
            client, after=kqi_temporal_frecuencies.pageInfo.endCursor, first=PAGINATION_STEP
        )
        if kqi_temporal_frecuencies is not None:
            edges.extend(kqi_temporal_frecuencies.edges)

    for edge in edges:
        node = edge.node
        if node is not None:
            yield KqiTemporalFrecuency(
                id=node.id,
                name=node.name,
            )


def delete_kqi_temporal_frecuency(client: SymphonyClient, id: str) -> None:
    """This function delete KqiTemporalFrecuency.

    :param name: KqiTemporalFrecuency name
    :type name: :class:`~psym.common.data_class.kqiTemporalFrecuency`
    :rtype: None

    **Example**

    .. code-block:: python

        client.delete_kqi_temporal_frecuency(id=123456789)
    """
    removeKqiTemporalFrequency.execute(client, id=id)



