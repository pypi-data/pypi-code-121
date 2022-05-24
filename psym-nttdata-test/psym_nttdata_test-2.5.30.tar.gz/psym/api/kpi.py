#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.


from psym.client import SymphonyClient
from psym.common.data_class import Kpi, domain, KpiCategory

from ..graphql.input.edit_kpi_input import EditKpiInput
from ..graphql.input.add_kpi_input import AddKpiInput
from ..graphql.mutation.add_kpi import addKpi
from ..graphql.mutation.edit_kpi import editKpi
from ..graphql.mutation.remove_kpi import removeKpi
from ..graphql.query.kpis import kpis
from psym.common.constant import PAGINATION_STEP
from typing import Any, Dict, Iterator, List, Optional




def add_kpi(
    client: SymphonyClient, name: str, description: str, status: bool, domain: str, kpiCategory: str
) -> Kpi:
    """This function adds Kpi.

    :param name: Kpi name
    :type name: str
    :param description: description
    :type description: str
    :param status: status
    :type status: bool
    :param domainFk: domain Object
    :type domainFk: psym.common.data_class.domain.id
    :param kpiCategory: str
    :type kpiCategory: psym.common.data_class.kpi_category.id

    :return: Kpi object
    :rtype: :class:`~psym.common.data_class.Kpi`


    **Example 1**

    .. code-block:: python


        domain = client.add_domain(
            name="domain",
        )
        kpi_category = client.add_kpi_category(
            name="kpi_category",
        )

        new_Kpi = client.add_Kpi(
            name="Kpi_2",
            description="new kpi",
            status=True,
            domain=domain.id,
            kpiCategory=kpi_category.id
        )
        print(new_Kpi)
    """
    domain_input = AddKpiInput(name=name, description=description,
    status=status, 
    domainFk=domain,
    kpiCategoryFK=kpiCategory)

    result = addKpi.execute(client, input=domain_input)

    return Kpi(name=result.name, id=result.id, 
    description=result.description, 
    status=result.status, 
    domain=result.domainFk, 
    kpiCategory=result.kpiCategoryFK)

def edit_kpi(
    client: SymphonyClient,
    KPI: Kpi,
    new_name: Optional[str] = None,
    description: str = None,
    status: bool = None,
    domain: domain = None,
    kpiCategory: KpiCategory = None,
) -> None:
    """This function edits Kpi.

    :param Kpi: Kpi entity
    :type name: str
    :param new_name: Kpi name
    :type name: str

    :return: none object
    :rtype: :class:`~psym.common.data_class.Kpi`

    **Example 1**

    .. code-block:: python

        Kpi_edited = client.edit_Kpi(
            Kpi=Kpi,
            new_name="new_Kpi",
            description="new kpi_edited",
            status=True,
            domain=domain.id,
            kpiCategory=kpi_category.id)
    """
    params: Dict[str, Any] = {}
    if new_name is not None:
        params.update({"_name_": new_name})
    if new_name is not None:
        editKpi.execute(client, input=EditKpiInput(id=KPI.id, 
        name=new_name,
        description=description,
        status= status,
        domainFk=domain,
        kpiCategoryFK=kpiCategory
        ))


def get_kpis(client: SymphonyClient) -> Iterator[Kpi]:
    """ this funtion Get Kpis


    :return: Kpi object
    :rtype: Iterator[ :class:`~psym.common.data_class.Kpi` ]

    **Example**

    .. code-block:: python

        Kpis = client.get_Kpis()
        for Kpi in Kpis:
            print(Kpi.name)
    """
    kpis_ = kpis.execute(client, first=PAGINATION_STEP)
    edges = kpis_.edges if kpis_ else []
    while kpis_ is not None and kpis_.pageInfo.hasNextPage:
        kpis_ = kpis.execute(
            client, after=kpis_.pageInfo.endCursor, first=PAGINATION_STEP
        )
        if kpis_ is not None:
            edges.extend(kpis_.edges)

    for edge in edges:
        node = edge.node
        if node is not None:
            yield Kpi(
                id=node.id,
                name=node.name,
                description=node.description,
                status=node.status,
                domain=node.id,
                kpiCategory=node.id


            )


def remove_kpi(client: SymphonyClient, id: str) -> None:
    """This function delete Kpi.

    :param name: Kpi name
    :type name: :class:`~psym.common.data_class.Kpi`
    :rtype: None

    **Example**

    .. code-block:: python

        client.remove_kpi(id=123456789)
    """
    removeKpi.execute(client, id=id)







