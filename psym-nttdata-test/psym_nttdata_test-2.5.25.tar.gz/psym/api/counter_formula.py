#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.


from psym.client import SymphonyClient
from psym.common.data_class import counterFormula, formula, counter

from ..graphql.input.edit_counter_formula_input import EditCounterFormulaInput
from ..graphql.input.add_counter_formula_input import AddCounterFormulaInput
from ..graphql.mutation.add_counter_formula import addCounterFormula
from ..graphql.mutation.edit_counter_formula import editCounterFormula
from ..graphql.mutation.remove_counter_formula import removeCounterFormula
from psym.common.constant import PAGINATION_STEP
from typing import Any, Dict, Iterator, List, Optional




def add_counter_formula(
    client: SymphonyClient,  mandatory: bool, counter: str,  formula: str
) -> counterFormula:
    """This function adds Counter Formula.
    
    :param mandatory: mandatory
    :type mandatory: str
    :param id: ID
    :type id: str
    :param counter: counter
    :type counter: `~psym.common.data_class.counter`
    :param formula: formula
    :type formula: `~psym.common.data_class.formula`
    

    :return: CounterFormula object
    :rtype: :class:`~psym.common.data_class.counterFormula`

   
    **Example 1**

    .. code-block:: python

        counter_family = client.add_counter_family(
            name="counter_family",
        )

        new_vendor = client.add_vendor(
            name="vendor",
        )

        counter = client.add_counter(
            name="counter",
            externalID="new counter",
            networkManagerSystem="counter",
            counterFamily=counter_family.id,
            vendor= vendor.id
        )

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
        
        new_Tech = client.add_Tech(
            name="new_Tech", 
            domain=domain.id
            )

        network_type = client.add_network_type(
            name="network_type",
        )

        new_formula = client.add_formula(
            textFormula="formula_1",
            status=True,
            kpi=Kpi_created.id,
            tech=tech_created.id,
            networkType=network_type.id
        )

        new_counter_formula = client.add_counter_formula(
            name="counter_formula",
            mandatory=True,
            counter=counter.id,
            formula=formula.id
        )
        print(new_counter_formula)
    """
    domain_input = AddCounterFormulaInput(
    mandatory=mandatory,
    counterFk=counter,
    formulaFk=formula)
    result = addCounterFormula.execute(client, input=domain_input)
    return counterFormula(mandatory=result.mandatory,
    id=result.id,  
    counter=result.counterFk, 
    formula=result.formulaFk)

def edit_counter_formula(
    client: SymphonyClient,
    CounterFormula: counterFormula,
    new_mandatory: Optional[bool] = None,
    formula:formula= None,
    counter: counter = None,
) -> None:
    """This function edits counterFormula.

    :param mandatory: mandatory
    :type mandatory: str
    :param id: ID
    :type id: str
    :param counter: counter
    :type counter: psym.common.data_class.counter
    :param formula: formula
    :type formula: psym.common.data_class.formula

    :return: none object
    :rtype: :class:`~psym.common.data_class.counterFormula`

    **Example 1**

    .. code-block:: python

        counter_formula_edited = client.edit_counter_formula(
            CounterFormula=CounterFormula,
            new_mandatory=new_mandatory,
            counter=counter.id,
            formula=formula.id
            )
    """
    params: Dict[str, Any] = {}
    if new_mandatory is not None:
        params.update({"mandatory": new_mandatory})
    if new_mandatory is not None:
        editCounterFormula.execute(client, input=EditCounterFormulaInput(
            id=CounterFormula.id, 
            mandatory=new_mandatory,
            counterFk=counter,
            formulaFk=formula))

def delete_counter_formula(client: SymphonyClient, id: str) -> None:
    """This function deletes CounterFormula.

    :param id: CounterFormula ID
    :type id: str

    :raises:
        FailedOperationException: Internal symphony error

    **Example**

    .. code-block:: python

        client.delete_counter_formula(id="12345678")
    """
    removeCounterFormula.execute(client, id=id)
