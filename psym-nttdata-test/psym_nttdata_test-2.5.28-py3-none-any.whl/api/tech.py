#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.


from psym.client import SymphonyClient
from psym.common.data_class import domain, tech, tech

from ..graphql.input.edit_tech_input import EditTechInput
from ..graphql.input.add_tech_input import AddTechInput
from ..graphql.mutation.add_tech import addTech
from ..graphql.mutation.edit_tech import editTech
from ..graphql.mutation.remove_tech import removeTech
from ..graphql.query.techs import techs
from psym.common.constant import PAGINATION_STEP
from typing import Any, Dict, Iterator, List, Optional




def add_tech(
    client: SymphonyClient, name: str, domain: str
) -> tech:
    """This function adds Tech.

    :param name: Name
    :type name: str
    :param domain: domain Object
    :type domain: psym.common.data_class.domain
    :return: Tech object
    :rtype: :class:`~psym.common.data_class.Tech`

    **Example 1**

    .. code-block:: python

        domain = client.add_domain(
            name="domain",
        )
        
        new_Tech = client.add_Tech(
            name="new_Tech", 
            domain=domain.id
            )
        print(new_Tech)
    """
    tech_input = AddTechInput(name=name, domainFk=domain)
    if (len(name) != 0):
        result = addTech.execute(client, input=tech_input)
        return tech(name=result.name, id=result.id, domainFK=result.domainFk)
    else:
        print ("you cant leave the name parameter empty")


def edit_tech(
    client: SymphonyClient,
    tech: tech,
    new_name: Optional[str] = None,
    domain: domain = None,
) -> None:
    """This function edits Tech.

    :param Tech: Tech entity
    :type name: str
    :param new_name: Tech name
    :type name: str

    :return: none object
    :rtype: :class:`~psym.common.data_class.Tech`

    **Example 1**

    .. code-block:: python


        Tech_edited = client.edit_Tech(
            Tech=Tech ,
            new_name="new_Tech",
            domain=domain.id)
    """
    params: Dict[str, Any] = {}
    if new_name is not None:
        params.update({"_name_": new_name})
    if new_name is not None:
        editTech.execute(client, input=EditTechInput(id=tech.id, name=new_name, domainFk=domain))

def get_tech(client: SymphonyClient) -> Iterator[tech]:
    """ this funtion Get Techs


    :return: Tech object
    :rtype: Iterator[ :class:`~psym.common.data_class.tech` ]

    **Example**

    .. code-block:: python

        Tech = client.get_techs()
        for Tech in Techs:
            print(Tech.name)
    """
    tech_ = techs.execute(client, first=PAGINATION_STEP)
    edges = tech_.edges if tech_ else []
    while tech_ is not None and tech_.pageInfo.hasNextPage:
        tech_ = techs.execute(
            client, after=tech_.pageInfo.endCursor, first=PAGINATION_STEP
        )
        if tech_ is not None:
            edges.extend(tech_.edges)
    for edge in edges:
        node = edge.node
        if node is not None:
            yield tech(
                id=node.id,
                name=node.name,
                domainFK=node.id

            )


def remove_tech(client: SymphonyClient, id: str) -> None:
    """This function delete Tech.

    :param name: Tech name
    :type name: :class:`~psym.common.data_class.Tech`
    :rtype: None

    **Example**

    .. code-block:: python

        client.remove_tech(id=123456789)
    """
    removeTech.execute(client, id=id)


