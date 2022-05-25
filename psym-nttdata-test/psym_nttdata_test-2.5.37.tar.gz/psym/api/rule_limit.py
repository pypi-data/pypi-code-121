#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.


from psym.client import SymphonyClient
from psym.common.data_class import Kpi, ruleLimit

from ..graphql.input.edit_rule_limit_input import EditRuleLimitInput
from ..graphql.input.add_rule_limit_input import AddRuleLimitInput
from ..graphql.mutation.add_rule_limit import addRuleLimit
from ..graphql.mutation.edit_rule_limit import editRuleLimit
from ..graphql.mutation.remove_rule_limit import removeRuleLimit
from psym.common.constant import PAGINATION_STEP
from typing import Any, Dict, Iterator, List, Optional




def add_rule_limit(
    client: SymphonyClient, 
            number: int,
            limitType: str,
            comparator: str,
            rule: str,
) -> ruleLimit:
    """This function adds Rule Limit.

    :param number: number
    :type number: str
    :param id: ID
    :type id: str
    :param limitType: limitType
    :type limitType: str
    :param rule: rule
    :type rule: psym.common.data_class.rule
    :param comparator: comparator
    :type comparator: psym.common.data_class.comparator

    :return: ruleLimit object
    :rtype: :class:`~psym.common.data_class.ruleLimit`


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

        threshold = client.add_Threshold(
            name="Threshold",
            description="threshold",
            status=True,
            kpi=Kpi.id
        )
        rule_type = client.add_rule_type(
            name="rule_type",
        )
        event_severity = client.add_event_severity(
            name="event_severity",
        )
        rule = client.add_rule(
            name="rule_1",
            additionalInfo="none",
            eventTypeName="none",
            gracePeriod=2,
            specificProblem="none",
            status=True,
            threshold=threshold.id,
            ruleType=rule_type.id,
            eventSeverity=event_severity.id,
            )

        comparator = client.add_comparator(
            name="comparator",
        )

        new_rule_limit = client.add_rule_limit(
            number=1,
            limitType="none",
            comparator=comparator.id,
            rule=rule.id

        )
    """
    rule_limit_input = AddRuleLimitInput(            
            number= number,
            limitType=limitType,
            comparator=comparator,
            rule=rule,)
    if (number ==int) or (len(limitType) != 0) or (len(comparator) != 0) or (len(rule) != 0) :
        result = addRuleLimit.execute(client, input=rule_limit_input)
        return ruleLimit(            
                id=result.id,
                number=result.number,
                limitType=result.limitType,
                comparator=result.comparator,
                rule=result.rule,)
    else:
        print ("one of the attributes is wrong, check the documentation.")


def edit_rule_limit(
    client: SymphonyClient,
    rule_limit: ruleLimit,
    new_number: Optional[int] = None,
    limitType: str= None,
    comparator: str= None,
    rule: str= None,
) -> None:
    """This function edits Rule Limit.

    :param rule_limit: Rule Limit entity
    :type name: str
    :param new_number: Rule Limit number
    :type name: int

    :return: none object
    :rtype: :class:`~psym.common.data_class.ruleLimit`

    **Example 1**

    .. code-block:: python

        new_rule_limit = client.edit_rule_limit(
            rule_limit=ruleLimit,
            new_number=new_number,
            limitType="none",
            comparator=comparator.id,
            rule=rule.id


        )
    """
    params: Dict[str, Any] = {}
    if new_number is not None:
        params.update({"_name_": new_number})
    if new_number is not None:
        editRuleLimit.execute(client, input=EditRuleLimitInput(
        id=rule_limit.id, 
        number= new_number,
        limitType=limitType,
        comparator=comparator,
        rule=rule))


def remove_rule_limit(client: SymphonyClient, id: str) -> None:
    """This function delete Rule Limit.

    :param name: Rule Limit name
    :type name: :class:`~psym.common.data_class.ruleLimit`
    :rtype: None

    **Example**

    .. code-block:: python

        client.remove_rule_limit(id=123456798)
    """
    removeRuleLimit.execute(client, id=id)