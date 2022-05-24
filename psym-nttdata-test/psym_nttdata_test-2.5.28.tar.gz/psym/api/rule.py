#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.


from psym.client import SymphonyClient
from psym.common.data_class import rule, threshold, eventSeverity, ruleType

#from ..graphql.input.edit_rule_input import EditRuleInput 
from ..graphql.input.add_rule_input import AddRuleInput
from ..graphql.mutation.add_rule import addRule
#from ..graphql.mutation.edit_rule import editRule
#from ..graphql.mutation.remove_rule import removerule
#from ..graphql.query.rules import rules
from psym.common.constant import PAGINATION_STEP
from typing import Any, Dict, Iterator, List, Optional




def add_rule(
    client: SymphonyClient, 
    name: str,
    gracePeriod: int,
    ruleType: str,
    eventTypeName: str,
    specificProblem: str,
    additionalInfo: str,
    status: bool,
    eventSeverity: str,
    threshold: str
) -> rule:
    """This function adds Rule.

    :param name: name
    :type name: str
    :param gracePeriod: gracePeriod
    :type gracePeriod: str
    :param eventTypeName: eventTypeName
    :type eventTypeName: str
    :param specificProblem: specificProblem
    :type specificProblem: str
    :param additionalInfo: additionalInfo
    :type additionalInfo: str
    :param status: status
    :type status: bool
    :param ruleType: str
    :type ruleType: psym.common.data_class.rule_type
    :param eventSeverity: str
    :type eventSeverity: psym.common.data_class.event_severity
    :param threshold: str
    :type threshold: psym.common.data_class.threshold

    :return: rule object
    :rtype: :class:`~psym.common.data_class.rule`

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
        new_rules = client.add_rule(
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

    """
    rule_input = AddRuleInput(
    name=name,
    gracePeriod=gracePeriod,
    ruleType=ruleType,
    eventTypeName=eventTypeName,
    specificProblem=specificProblem,
    additionalInfo=additionalInfo,
    status=status,
    eventSeverity=eventSeverity,
    threshold=threshold
    )
    result = addRule.execute(client, input=rule_input)
    return rule(
    name=result.name, 
    id=result.id, 
    gracePeriod=result.gracePeriod,
    ruleType=result.ruleType,
    eventTypeName=result.eventTypeName,
    specificProblem=result.specificProblem,
    additionalInfo=result.additionalInfo,
    status=result.status,
    eventSeverity=result.eventSeverity,
    threshold=result.threshold
    )
