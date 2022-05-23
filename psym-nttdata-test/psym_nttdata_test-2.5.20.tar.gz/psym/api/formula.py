#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.


from psym.client import SymphonyClient
from psym.common.data_class import  NetworkType, formula, Kpi, tech

from ..graphql.input.edit_formula_input import EditFormulaInput
from ..graphql.input.add_formula_input import AddFormulaInput
from ..graphql.mutation.add_formula import addFormula
from ..graphql.mutation.edit_formula import editFormula
from ..graphql.mutation.remove_formula import removeFormula
from ..graphql.query.formulas import formulas
from psym.common.constant import PAGINATION_STEP
from typing import Any, Dict, Iterator, List, Optional




def add_formula(
    client: SymphonyClient, textFormula: str, status: bool,  tech: str, networkType: str,  kpi: str
) -> formula:
    """This function adds formula.

    :param textFormula: formula name
    :type textFormula: str
    :param description: description
    :type description: str
    :param status: status
    :type status: bool
    :param techFk: domain Object
    :type techFk: psym.common.data_class.tech
    :param networkTypeFk: str
    :type networkTypeFk: psym.common.data_class.network_type
    :param kpiFk: str
    :type kpiFk: psym.common.data_class.kpi

    :return: formula object
    :rtype: :class:`~psym.common.data_class.formula`

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

        domain = client.add_domain(
            name="domain",
        )

        tech = client.add_Tech(
            name="new_Tech", 
            domain=domain.id
            
        network_type = client.add_network_type(
            name="network_type",
        )

        new_formula = client.add_formula(
            textFormula="formula_1",
            status=True,
            kpi=Kpi.id,
            tech=tech.id,
            networkType=network_type.id
        )
    """
    formula_input = AddFormulaInput(
    textFormula=textFormula, 
    status=status, 
    techFk= tech,
    networkTypeFk= networkType,
    kpiFk= kpi
   
   )
    result = addFormula.execute(client, input=formula_input)
    return formula(textFormula=result.textFormula, 
    id=result.id,  
    status=result.status, 
    techFk=result.techFk,
    networkTypeFk=result.networkTypeFk,
    kpiFk=result.kpiFk
)

def edit_formula(
    client: SymphonyClient,
    formula: formula,
    new_name: Optional[str] = None,
    status: bool = None,
    tech: tech = None,
    networkType: NetworkType = None,
    kpi: Kpi = None
) -> None:
    """This function edits formula.

    :param formula: formula entity
    :type name: str
    :param new_name: formula name
    :type name: str

    :return: none object
    :rtype: :class:`~psym.common.data_class.formula`

    **Example 1**

    .. code-block:: python

        formula_edited = client.edit_formula(
            formula=formula,
            new_name="new_formula_edited",
            status=True,
            kpi=Kpi.id,
            tech=tech.id,
            networkType=network_type.id
            )
    """
    params: Dict[str, Any] = {}
    if new_name is not None:
        params.update({"_name_": new_name})
    if new_name is not None:
        editFormula.execute(client, input=EditFormulaInput(
        id=formula.id, 
        textFormula=new_name,
        status= status,
        networkTypeFk=networkType,
        kpiFk=kpi,
        techFk=tech
        ))


def get_formulas(client: SymphonyClient) -> Iterator[Kpi]:
    """ this funtion Get formulas


    :return: formula object
    :rtype: Iterator[ :class:`~psym.common.data_class.formula` ]

    **Example**

    .. code-block:: python

        formulas = client.get_formulas()
        for formula in formulas:
            print(formula.name)
    """
    formulas_ = formulas.execute(client, first=PAGINATION_STEP)
    edges = formulas_.edges if formulas_ else []
    while formulas_ is not None and formulas_.pageInfo.hasNextPage:
        formulas_ = formulas.execute(
            client, after=formulas_.pageInfo.endCursor, first=PAGINATION_STEP
        )
        if formulas_ is not None:
            edges.extend(formulas_.edges)

    for edge in edges:
        node = edge.node
        if node is not None:
            yield formula(
                id=node.id,
                textFormula=node.textFormula,
                status=node.status,
                networkTypeFk=node.networkTypeFk,
                kpiFk=node.kpiFk,
                techFk=node.techFk

            )


def remove_formula(client: SymphonyClient, id: str) -> None:
    """This function delete formula.

    :param name: formula name
    :type name: :class:`~psym.common.data_class.formula`
    :rtype: None

    **Example**

    .. code-block:: python

        client.remove_formula(id=123456789)
    """
    removeFormula.execute(client, id=id)








