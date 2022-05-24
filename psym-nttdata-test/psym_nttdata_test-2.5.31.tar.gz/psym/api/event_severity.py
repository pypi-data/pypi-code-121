#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.


from psym.client import SymphonyClient
from psym.common.data_class import ruleType

from ..graphql.input.edit_event_severity_input import EditEventSeverityInput
from ..graphql.input.add_event_severity_input import AddEventSeverityInput
from ..graphql.mutation.add_event_severity import addEventSeverity
from ..graphql.mutation.edit_event_severity import editEventSeverity
from ..graphql.mutation.remove_event_severity import removeEventSeverity
from ..graphql.query.eventSeverities import eventSeverities
from psym.common.constant import PAGINATION_STEP
from typing import Any, Dict, Iterator, List, Optional




def add_event_severity(
    client: SymphonyClient, name: str
) -> ruleType:
    """This function adds Event Severity.

    :param name: Event Severity name
    :type name: str

    :return: eventSeverity object
    :rtype: :class:`~psym.common.data_class.eventSeverity`

    **Example 1**

    .. code-block:: python

        new_event_severity = client.add_event_severity(
            name="event_severity",
        )
        print(new_event_severity)
    """
    event_severity_input = AddEventSeverityInput(name=name)
    if (name == ""):
      print ("you cant leave the name parameter empty")
    elif name!=str:
      print ("the input must be a text, example name=''new name''")
    else:
        result = addEventSeverity.execute(client, input=event_severity_input)
        return ruleType(name=result.name, id=result.id)

def edit_event_severity(
    client: SymphonyClient,
    event_severity: ruleType,
    new_name: Optional[str] = None,
) -> None:
    """This function edits Event Severity.

    :param event_severity: Event Severity entity
    :type name: str
    :param new_name: Event Severity name
    :type name: str

    :return: none object
    :rtype: :class:`~psym.common.data_class.eventSeverity`

    **Example 1**

    .. code-block:: python

        new_event_severity = client.edit_event_severity(
            event_severity=new_event_severity,
            new_name="event_severity_edited",

        )
    """
    params: Dict[str, Any] = {}
    if new_name is not None:
        params.update({"_name_": new_name})
    if new_name is not None:
        editEventSeverity.execute(client, input=EditEventSeverityInput(id=event_severity.id, name=new_name))

def get_event_severities(client: SymphonyClient) -> Iterator[ruleType]:
    """ this funtion Get Event Severities


    :return: eventSeverity object
    :rtype: Iterator[ :class:`~psym.common.data_class.eventSeverity` ]

    **Example**

    .. code-block:: python

        event_severities = client.get_event_severities()
        for event_severity in event_severities:
            print(event_severity.name)
    """
    event_severitys_ = eventSeverities.execute(client, first=PAGINATION_STEP)
    edges = event_severitys_.edges if event_severitys_ else []
    while event_severitys_ is not None and event_severitys_.pageInfo.hasNextPage:
        event_severitys_ = eventSeverities.execute(
            client, after=event_severitys_.pageInfo.endCursor, first=PAGINATION_STEP
        )
        if event_severitys_ is not None:
            edges.extend(event_severitys_.edges)

    for edge in edges:
        node = edge.node
        if node is not None:
            yield ruleType(
                id=node.id,
                name=node.name,
            )


def remove_event_severity(client: SymphonyClient, id: str) -> None:
    """This function delete Event Severity.

    :param name: Event Severity name
    :type name: :class:`~psym.common.data_class.eventSeverity`
    :rtype: None

    **Example**

    .. code-block:: python

        client.remove_event_severity(id=123456789)
    """
    removeEventSeverity.execute(client, id=id)


