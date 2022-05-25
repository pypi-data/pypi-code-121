#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.


from psym.client import SymphonyClient
from psym.common.data_class import CounterFamily

from ..graphql.input.edit_counter_family_input import EditCounterFamilyInput
from ..graphql.input.add_counter_family_input import AddCounterFamilyInput
from ..graphql.mutation.add_counter_family import addCounterFamily
from ..graphql.mutation.edit_counter_family import editCounterFamily
from ..graphql.mutation.remove_counter_family import removeCounterFamily
from ..graphql.query.counter_families import counterFamilies
from psym.common.constant import PAGINATION_STEP
from typing import Any, Dict, Iterator, List, Optional




def add_counter_family(
    client: SymphonyClient, name: str
) -> CounterFamily:
    """This function adds Counter Family.

    :param name: Counter Family name
    :type name: str

    :return: CounterFamily object
    :rtype: :class:`~psym.common.data_class.counterFamily`

    **Example 1**

    .. code-block:: python

        new_counter_family = client.add_counter_family(
            name="counter_family",
        )
        print(new_counter_family)
    """
    counter_family_input = AddCounterFamilyInput(name=name)
    if (name == ""):
      print ("you cant leave the name parameter empty")
    elif name!=str:
      print ("the input must be a text, example name=''new name''")
    else:
        result = addCounterFamily.execute(client, input=counter_family_input)
        return CounterFamily(name=result.name, id=result.id)


def edit_counter_family(
    client: SymphonyClient,
    counter_family: CounterFamily,
    new_name: Optional[str] = None,
) -> None:
    """This function edits Counter Family.

    :param counter_family: Counter Family entity
    :type name: str
    :param new_name: Counter Family name
    :type name: str

    :return: none object
    :rtype: :class:`~psym.common.data_class.counterFamily`

    **Example 1**

    .. code-block:: python

        counter_family_edited = client.edit_counter_family(
            counter_family=new_counter_family,
            new_name="counter_family_edited",
        )
        print(counter_family_edited)
    """
    params: Dict[str, Any] = {}
    if new_name is not None:
        params.update({"_name_": new_name})
    if new_name is not None:
        editCounterFamily.execute(client, input=EditCounterFamilyInput(id=counter_family.id, name=new_name))


def get_counter_families(client: SymphonyClient) -> Iterator[CounterFamily]:
    """ this funtion Get Counter Families


    :return: alarmStatus object
    :rtype: Iterator[ :class:`~psym.common.data_class.counterFamily` ]

    **Example**

    .. code-block:: python

        get_counter_familiies = client.get_counter_families()
        for get_counter_family in get_counter_familiies:
            print(get_counter_familiy.name)
    """
    counter_familiess_ = counterFamilies.execute(client, first=PAGINATION_STEP)
    edges = counter_familiess_.edges if counter_familiess_ else []
    while counter_familiess_ is not None and counter_familiess_.pageInfo.hasNextPage:
        counter_familiess_ = counterFamilies.execute(
            client, after=counter_familiess_.pageInfo.endCursor, first=PAGINATION_STEP
        )
        if counter_familiess_ is not None:
            edges.extend(counter_familiess_.edges)

    for edge in edges:
        node = edge.node
        if node is not None:
            yield CounterFamily(
                id=node.id,
                name=node.name,
            )


def remove_counter_family(client: SymphonyClient, id: str) -> None:

    """This function delete Counter Family.

    :param name: Counter Family name
    :type name: :class:`~psym.common.data_class.counterFamily`
    :rtype: None

    **Example**

    .. code-block:: python

        remove_counterFamilyclient.remove_counter_family(id=123456789)
    """
    removeCounterFamily.execute(client, id=id)
    