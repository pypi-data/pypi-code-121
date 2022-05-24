#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.


from psym.client import SymphonyClient
from psym.common.data_class import domain

from ..graphql.input.edit_domain_input import EditDomainInput
from ..graphql.input.add_domain_input import AddDomainInput
from ..graphql.mutation.add_domain import addDomain
from ..graphql.mutation.edit_domain import editDomain
from ..graphql.mutation.remove_domain import removeDomain
from ..graphql.query.domain import domains
from psym.common.constant import PAGINATION_STEP
from typing import Any, Dict, Iterator, List, Optional




def add_domain(
    client: SymphonyClient, name: str
) -> domain:
    """This function adds Domain.

    :param name: Domain name
    :type name: str

    :return: domain object
    :rtype: :class:`~psym.common.data_class.domain`

    **Example 1**

    .. code-block:: python

        new_domain = client.add_domain(
            name="domain",
        )
        print(new_domain)
    """
    domain_input = AddDomainInput(name=name)
    if (len(name) != 0):
        result = addDomain.execute(client, input=domain_input)
        return domain(name=result.name, id=result.id)
    else:
        print ("you cant leave the name parameter empty")
        
def edit_domain(
    client: SymphonyClient,
    domain: domain,
    new_name: Optional[str] = None,
) -> None:
    """This function edits Domain.

    :param domain: Domain entity
    :type name: str
    :param new_name: Domain name
    :type name: str

    :return: none object
    :rtype: :class:`~psym.common.data_class.domain`

    **Example 1**

    .. code-block:: python

        domain_edited = client.edit_domain(domain=domain ,new_name="new_domain")

    **Example 2**

    .. code-block:: python

        domain_edited = client.edit_domain(
            domain=new_domain,
            new_name="domain_edited",
        )
        print(domain_edited)
    """
    params: Dict[str, Any] = {}
    if new_name is not None:
        params.update({"_name_": new_name})
    if new_name is not None:
        editDomain.execute(client, input=EditDomainInput(id=domain.id, name=new_name))

def get_domains(client: SymphonyClient) -> Iterator[domain]:
    """ This funtion Get Domains


    :return: domain object
    :rtype: Iterator[ :class:`~psym.common.data_class.domain` ]

    **Example**

    .. code-block:: python

        domains = client.get_domains()
        for domain in domains:
            print(domain.name)
    """
    domains_ = domains.execute(client, first=PAGINATION_STEP)
    edges = domains_.edges if domains_ else []
    while domains_ is not None and domains_.pageInfo.hasNextPage:
        domains_ = domains.execute(
            client, after=domains_.pageInfo.endCursor, first=PAGINATION_STEP
        )
        if domains_ is not None:
            edges.extend(domains_.edges)

    for edge in edges:
        node = edge.node
        if node is not None:
            yield domain(
                id=node.id,
                name=node.name,
            )


def remove_domain(client: SymphonyClient, id: str) -> None:
    """This function delete Domain.

    :param name: Domain name
    :type name: :class:`~psym.common.data_class.domain`
    :rtype: None

    **Example**

    .. code-block:: python

        client.remove_domain(id=12345679)
    """
    removeDomain.execute(client, id=id)