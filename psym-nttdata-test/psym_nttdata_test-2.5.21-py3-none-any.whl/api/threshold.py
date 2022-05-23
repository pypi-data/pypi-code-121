#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.


from psym.client import SymphonyClient
from psym.common.data_class import Kpi, threshold

from ..graphql.input.edit_threshold_input import EditThresholdInput
from ..graphql.input.add_threshold_input import AddThresholdInput
from ..graphql.mutation.add_threshold import addThreshold
from ..graphql.mutation.edit_threshold import editThreshold
from ..graphql.mutation.remove_threshold import removeThreshold
from ..graphql.query.thresholds import thresholds
from psym.common.constant import PAGINATION_STEP
from typing import Any, Dict, Iterator, List, Optional




def add_threshold(
    client: SymphonyClient, name: str, description: str, status: bool ,kpi: str
) -> threshold:
    """This function adds Threshold.

    :param name: Threshold name
    :type name: str
    :param description: description
    :type description: str
    :param status: status
    :type status: bool
    :param kpi: str
    :type kpi: psym.common.data_class.kpi

    :return: Threshold object
    :rtype: :class:`~psym.common.data_class.Threshold`

    **Example 1**

    .. code-block:: python

        domain = client.add_domain(
            name="domain",
        )
        kpi_category = client.add_kpi_category(
            name="kpi_category",
        )

        Kpi = client.add_Kpi(
            name="Kpi_2",
            description="new kpi",
            status=True,
            domain=domain.id,
            kpiCategory=kpi_category.id
        )

        new_Threshold = client.add_Threshold(
            name="Threshold",
            description="threshold",
            status=True,
            kpi=Kpi.id
        )
    """
    threshold_input = AddThresholdInput(name=name, description=description, status=status, kpi=kpi)
    if (len(name) != 0):
        result = addThreshold.execute(client, input=threshold_input)
        return threshold(name=result.name, description=result.description, status=result.status, id=result.id, kpi=result.kpi)
    else:
        print ("you cant leave the name parameter empty")


def edit_threshold(
    client: SymphonyClient,
    threshold: threshold,
    new_name: Optional[str] = None,
    description: str = None,
    status: bool = None,
) -> None:
    """This function edits Threshold.

    :param Threshold: Threshold entity
    :type name: str
    :param new_name: Threshold name
    :type name: str

    :return: none object
    :rtype: :class:`~psym.common.data_class.Threshold`

    **Example 1**

    .. code-block:: python

        Threshold_edited = client.edit_threshold(
            threshold=Threshold,
            new_name=new_name,
            description="threshold",
            status=True
            )
    """
    params: Dict[str, Any] = {}
    if new_name is not None:
        params.update({"_name_": new_name})
    if new_name is not None:
        editThreshold.execute(client, input=EditThresholdInput(id=threshold.id, 
        name=new_name, 
        description=description,
        status=status))

def get_thresholds(client: SymphonyClient) -> Iterator[threshold]:
    """ this funtion Get Thresholds


    :return: Threshold object
    :rtype: Iterator[ :class:`~psym.common.data_class.Threshold` ]

    **Example**

    .. code-block:: python

        Thresholds = client.get_Thresholds()
        for threshold in Thresholds:
            print(threshold.name)
    """
    threshold_ = thresholds.execute(client, first=PAGINATION_STEP)
    edges = threshold_.edges if threshold_ else []
    while threshold_ is not None and threshold_.pageInfo.hasNextPage:
        threshold_ = thresholds.execute(
            client, after=threshold_.pageInfo.endCursor, first=PAGINATION_STEP
        )
        if threshold_ is not None:
            edges.extend(threshold_.edges)

    for edge in edges:
        node = edge.node
        if node is not None:
            yield threshold(
                id=node.id,
                name=node.name,
                description=node.description,
                status=node.status,
                kpi=node.id

            )


def remove_threshold(client: SymphonyClient, id: str) -> None:
    """This function delete Threshold.

    :param name: Threshold name
    :type name: :class:`~psym.common.data_class.Threshold`
    :rtype: None

    **Example**

    .. code-block:: python

        client.remove_threshold(id=123456789)
    """
    removeThreshold.execute(client, id=id)


