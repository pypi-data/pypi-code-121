#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.


from psym.client import SymphonyClient
from psym.common.data_class import alarmStatus
from psym.common.data_enum import Entity
from psym.exceptions import EntityNotFoundError

from ..graphql.input.edit_alarm_status_input import EditAlarmStatusInput
from ..graphql.input.add_alarm_status_input import AddAlarmStatusInput
from ..graphql.mutation.add_alarm_status import addAlarmStatus
from ..graphql.mutation.edit_alarm_status import editAlarmStatus
from ..graphql.mutation.remove_alarm_status import removeAlarmStatus
from ..graphql.query.alarm_statuses import alarmStatuses
from psym.common.constant import PAGINATION_STEP
from typing import Any, Dict, Iterator, List, Optional




def add_alarm_status(
    client: SymphonyClient, name: str
) -> alarmStatus:
    """This function adds Alarm Status.

    :param name: Alarm Status name
    :type name: str

    :return: alarmStatus object
    :rtype: :class:`~psym.common.data_class.alarmStatus`

    **Example 1**

    .. code-block:: python

        new_alarm_statuses = client.add_alarm_status(name="new_alarm_status")

    **Example 2**

    .. code-block:: python

        new_alarm_status = client.add_alarm_status(
            name="alarm_status",
        )
        print(new_alarm_status)
    """
    if (name == ""):
        print ("you cant leave the name parameter empty")
    elif name!=str:
        print ("the input must be a text, example name=''new name''")
    else:
        alarm_status_input = AddAlarmStatusInput(name=name)        
        result = addAlarmStatus.execute(client, input=alarm_status_input)
        return alarmStatus(name=result.name, id=result.id)

c
def edit_alarm_status(
    client: SymphonyClient,
    alarm_status: alarmStatus,
    new_name: Optional[str] = None,
) -> None:
    """This function edits Alarm Status.

    :param alarm_status: Alarm Status entity
    :type name: str
    :param new_name: Alarm Status name
    :type name: str

    :return: none object
    :rtype: :class:`~psym.common.data_class.alarmStatus`

    **Example 1**

    .. code-block:: python

        alarm_status_edited = client.edit_alarm_status(alarm_status=alarmStatus ,new_name="new_alarm_status")

    **Example 2**

    .. code-block:: python

        new_alarm_status = client.edit_alarm_status(
            alarm_status=alarmStatus,
            new_name="alarm_status",

        )
    """
    params: Dict[str, Any] = {}
    if new_name is not None:
        params.update({"_name_": new_name})
    if new_name is not None:
        result=editAlarmStatus.execute(client, input=EditAlarmStatusInput(id=alarm_status.id, name=new_name))
    return alarmStatus(name=result.name, id=result.id)

def get_alarm_statuses(client: SymphonyClient) -> Iterator[alarmStatus]:
    """ this funtion Get Alarm statuses


    :return: alarmStatus object
    :rtype: Iterator[ :class:`~psym.common.data_class.alarmStatus` ]

    **Example**

    .. code-block:: python

        alarm_statuses = client.get_alarm_statuses()
        for alarm_status in alarm_statuses:
            print(alarm_status.name)
    """
    alarm_statusess_ = alarmStatuses.execute(client, first=PAGINATION_STEP)
    edges = alarm_statusess_.edges if alarm_statusess_ else []
    while alarm_statusess_ is not None and alarm_statusess_.pageInfo.hasNextPage:
        alarm_statusess_ = alarmStatuses.execute(
            client, after=alarm_statusess_.pageInfo.endCursor, first=PAGINATION_STEP
        )
        if alarm_statusess_ is not None:
            edges.extend(alarm_statusess_.edges)

    for edge in edges:
        node = edge.node
        if node is not None:
            yield alarmStatus(
                id=node.id,
                name=node.name,
            )


def remove_alarm_status(client: SymphonyClient, id: str) -> None:
    """This function delete Alarm Status.

    :param name: Alarm Status name
    :type name: :class:`~psym.common.data_class.alarmStatus`
    :rtype: None

    **Example**

    .. code-block:: python

        remove_alarm_status=client.remove_alarm_status(id=123456789)
    """
    removeAlarmStatus.execute(client, id=id)
