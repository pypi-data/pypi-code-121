#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.


from psym.client import SymphonyClient
from psym.common.data_class import CounterFamily, Vendor, counter

from ..graphql.input.edit_counter_input import EditCounterInput
from ..graphql.input.add_counter_input import AddCounterInput
from ..graphql.mutation.add_counter import addCounter
from ..graphql.mutation.edit_counter import editCounter
from ..graphql.mutation.remove_counter import removeCounter
from ..graphql.query.counters import counters
from psym.common.constant import PAGINATION_STEP
from typing import Any, Dict, Iterator, List, Optional




def add_counter(
    client: SymphonyClient, name: str, externalID: str, networkManagerSystem: str,  counterFamily: str, vendor: str
) -> counter:
    """This function adds Counter.

    :param name: Counter name
    :type name: str
    :param id: ID
    :type id: str
    :param externalID: externalID
    :type externalID: str
    :param networkManagerSystem: networkManagerSystem
    :type networkManagerSystem: str
    :param counterFamily: domain Object
    :param vendor: str
    :type counterFamily: psym.common.data_class.counter_family
    :param vendor: str
    :type vendor: psym.common.data_class.vendor

    :return: counter object
    :rtype: :class:`~psym.common.data_class.counter `

    **Example 1**

    .. code-block:: python

        counter_family = client.add_counter_family(
            name="counter_family",
        )

        vendor = client.add_vendor(
            name="vendor",
        )

        counter = client.add_counter(
            name="counter",
            externalID="new counter",
            networkManagerSystem="counter",
            counterFamily=counter_family.id,
            vendor= vendor.id
        )
        print(counter)
    """
    domain_input = AddCounterInput(
        name=name, 
        externalID=externalID,
        networkManagerSystem=networkManagerSystem, 
        counterFamily=counterFamily,
        vendorFk=vendor)
    if (len(name) != 0) or (len(externalID) != 0) or (len(networkManagerSystem) != 0) or (len(counterFamily) != 0) or (len(vendor) != 0):
        result = addCounter.execute(client, input=domain_input)
        return counter(
            name=result.name, 
            id=result.id, 
            externalID=result.externalID, 
            networkManagerSystem=result.networkManagerSystem, 
            counterFamilyFk=result.counterFamily, 
            vendorFk=result.vendorFk)
    else:
        print ("one of the attributes is wrong, check the documentation.")

def edit_counter(
    client: SymphonyClient,
    counter: counter,
    new_name: Optional[str] = None,
    externalID: str = None,
    networkManagerSystem: str = None,
    vendor: Vendor = None,
) -> None:
    """This function edits Counter.

    :param Counter: Counter entity
    :type name: str
    :param new_name: Alarm Status name
    :type name: str
    :param externalID: externalID
    :type externalID: str
    :param networkManagerSystem: networkManagerSystem
    :type networkManagerSystem: str
    :param counterFamily: domain Object
    :type counterFamily: psym.common.data_class.counter_family
    :param vendor: str
    :type vendor: psym.common.data_class.vendor

    :return: none object
    :rtype: :class:`~psym.common.data_class.alarmStatus`

    **Example 1**

    .. code-block:: python

        u = counter
        Counter_edited=client.edit_counter(
            counter=u,
            new_name=new_name,
            externalID="new counter",
            networkManagerSystem="counter",
            vendor= vendor.id
        )
    """
    params: Dict[str, Any] = {}
    if new_name is not None:
        params.update({"_name_": new_name})
    if new_name is not None:
        editCounter.execute(client, input=EditCounterInput(
        id=counter.id, 
        name=new_name,
        externalID=externalID,
        networkManagerSystem=networkManagerSystem,
        vendorFk=vendor,
        ))

def get_counters(client: SymphonyClient) -> Iterator[counter]:
    """ this funtion Get Alarm statuses


    :return: counter object
    :rtype: Iterator[ :class:`~psym.common.data_class.counter` ]

    **Example**

    .. code-block:: python


        counters = client.get_counters()
        for counters in counters:
            print(counter.name)
    """
    counters_ = counters.execute(client, first=PAGINATION_STEP)
    edges = counters_.edges if counters_ else []
    while counters_ is not None and counters_.pageInfo.hasNextPage:
        counters_ = counters.execute(
            client, after=counters_.pageInfo.endCursor, first=PAGINATION_STEP
        )
        if counters_ is not None:
            edges.extend(counters_.edges)

    for edge in edges:
        node = edge.node
        if node is not None:
            yield counter(
                id=node.id,
                name=node.name,
                externalID=node.externalID,
                networkManagerSystem=node.networkManagerSystem,
                counterFamilyFk=node.counterFamily,
                vendorFk=node.vendorFk
            )


def remove_counter(client: SymphonyClient, id: str) -> None:
    """This function delete Counter.

    :param name: Counter name
    :type name: :class:`~psym.common.data_class.counter`
    :rtype: None

    **Example**

    .. code-block:: python

        client.remove_counter(id=123456789)
    """
    removeCounter.execute(client, id=id)









