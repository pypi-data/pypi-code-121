#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.


from psym.client import SymphonyClient
from psym.common.data_class import ruleType
from psym.exceptions import EntityNotFoundError

from ..graphql.input.edit_rule_type_input import EditRuleTypeInput
from ..graphql.input.add_rule_type_input import AddRuleTypeInput
from ..graphql.mutation.add_rule_type import addRuleType
from ..graphql.mutation.edit_rule_type import editRuleType
from ..graphql.mutation.remove_rule_type import removeRuleType
from ..graphql.query.rule_types import ruleTypes
from psym.common.constant import PAGINATION_STEP
from typing import Any, Dict, Iterator, List, Optional
from psym.common.data_enum import Entity



def add_rule_type(
    client: SymphonyClient, name: str
) -> ruleType:
    """This function adds Rule Type.

    :param name: Rule Type name
    :type name: str

    :return: ruleType object
    :rtype: :class:`~psym.common.data_class.ruleType`)

    **Example 2**

    .. code-block:: python

        new_rule_type = client.add_rule_type(
            name="rule_type",

        )
    """
    rule_type_input = AddRuleTypeInput(name=name)
    if (len(name) != 0): 
        result = addRuleType.execute(client, input=rule_type_input)
        return ruleType(name=result.name, id=result.id)
    else:
        print ("you cant leave the name parameter empty")

def edit_rule_type(
    client: SymphonyClient,
    rule_type: ruleType,
    new_name: Optional[str] = None,
) -> None:
    """This function edits Rule Type.

    :param rule_type: Rule Type entity
    :type name: str
    :param new_name: Rule Type name
    :type name: str

    :return: none object
    :rtype: :class:`~psym.common.data_class.ruleType`

    **Example 1**

    .. code-block:: python

        new_rule_type_Edited = client.edit_rule_type(
            rule_type=ruleType,
            new_name="rule_type_edited",

        )
    """
    params: Dict[str, Any] = {}
    if new_name is not None:
        params.update({"_name_": new_name})
    if new_name is not None:
        editRuleType.execute(client, input=EditRuleTypeInput(id=rule_type.id, name=new_name))

def get_rule_types(client: SymphonyClient) -> Iterator[ruleType]:
    """ this funtion Get Rule Types


    :return: ruleType object
    :rtype: Iterator[ :class:`~psym.common.data_class.ruleType` ]

    **Example**

    .. code-block:: python

        rule_types = client.get_rule_types()
        for rule_type in rule_types:
            print(rule_type.name)
    """
    rule_types_ = ruleTypes.execute(client, first=PAGINATION_STEP)
    edges = rule_types_.edges if rule_types_ else []
    while rule_types_ is not None and rule_types_.pageInfo.hasNextPage:
        rule_types_ = ruleTypes.execute(
            client, after=rule_types_.pageInfo.endCursor, first=PAGINATION_STEP
        )
        if rule_types_ is not None:
            edges.extend(rule_types_.edges)

    for edge in edges:
        node = edge.node
        if node is not None:
            yield ruleType(
                id=node.id,
                name=node.name,
            )

def remove_rule_type(client: SymphonyClient, id: str) -> None:
    """This function delete Rule Type.

    :param name: Rule Type name
    :type name: :class:`~psym.common.data_class.ruleType`
    :rtype: None

    **Example**

    .. code-block:: python

        client.remove_rule_type(id=123456798)
    """
    removeRuleType.execute(client, id=id)


