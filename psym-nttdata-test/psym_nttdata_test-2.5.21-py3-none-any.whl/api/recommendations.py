#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.


from psym.client import SymphonyClient
from psym.common.data_class import recommendations

from ..graphql.input.edit_recommendations_input import EditRecommendationsInput
from ..graphql.input.add_recommendations_input import AddRecommendationsInput
from ..graphql.mutation.add_recommendations import addRecommendations
from ..graphql.mutation.edit_recommendations import editRecommendations
from ..graphql.mutation.remove_recommendations import removeRecommendations
from ..graphql.query.recommendations import Recommendations
from psym.common.constant import PAGINATION_STEP
from typing import Any, Dict, Iterator, List, Optional




def add_recommendations(
    client: SymphonyClient, 
    externalID: str,
    resource: str,
    alarmType: str,
    shortDescription: str,
    LongDescription: str,
    command: str,
    runbook: str,
    priority: str,
    status: bool,
    used: int,
    vendor: str,
    RecomendationSources: str,
    RecomendationsCategory: str,
    userCreated: int,
    userApproved: int,
) -> recommendations:
    """This function adds recommendations.

    :param externalID: externalID
    :type externalID: str
    :param resource: resource
    :type resource: str
    :param shortDescription: shortDescription
    :type shortDescription: str
    :param LongDescription: LongDescription
    :type LongDescription: str
    :param command: command
    :type command: str
    :param runbook: runbook
    :type runbook: str
    :param priority: priority
    :type priority: str
    :param status: status
    :type status: bool
    :param used: used
    :type used: int
    :param vendor: vendor
    :type vendor: str
    :param RecomendationSources: RecomendationSources
    :type RecomendationSources::`~psym.graphql.enum.RecomendationSources
    :param RecomendationsCategory: RecomendationsCategory
    :type RecomendationsCategory: `~psym.graphql.enum.RecomendationsCategory
    :param userCreated: userCreated
    :type userCreated:`~psym.graphql.enum.user`
    :param userApproved: userApproved
    :type userApproved:`~psym.graphql.enum.user`

    :return: recommendations object
    :rtype: :class:`~psym.common.data_class.recommendations`


    **Example 1**

    .. code-block:: python

        recommendations_sources = client.add_recommendations_sources(
            name="recommendations_sources",
        )
        recommendations_category = client.add_recommendations_category(
            name="recommendations_category",
        )
        vendor = client.add_vendor(
            name="vendor",
        )

        user_created=client.get_user_by_email(email="user@nttdata.com")

        new_recommendations = client.add_recommendations(
            externalID="new_externalID",
            resource="resoruce",
            alarmType="alarmType",
            LongDescription="LongDescription",
            shortDescription="shortDescription",
            command="command",
            runbook="runbook",
            priority=2,
            status=False,
            used=2,
            vendor=vendor.id,
            RecomendationSources=recommendation_sources.id,
            RecomendationsCategory=recommendation_category.id,
            userCreated=user_created.id,
            userApproved=user_created.id
        )
        print(new_recommendations)
    """
    recommendations_input = AddRecommendationsInput(
    externalID=externalID,
    resource=resource,
    alarmType=alarmType,
    shortDescription=shortDescription,
    longDescription=LongDescription,
    priority=priority,
    status=status,
    recommendationsSources=RecomendationSources,
    recommendationsCategory=RecomendationsCategory,
    userCreate=userCreated,
    vendor=vendor,
    command=command,
    runbook=runbook,
    used=used,
    userApprobed=userApproved,
    )
    result = addRecommendations.execute(client, input=recommendations_input)
    return recommendations(
    id=result.id,
    externalID=result.externalID,
    resource=result.resource,
    alarmType=result.alarmType,
    shortDescription=result.shortDescription,
    LongDescription=result.longDescription,
    command=result.command,
    runbook=result.runbook,
    priority=result.priority,
    status=result.status,
    used=result.used,
    vendor=result.vendor,
    RecomendationSources=result.recommendationsSources,
    RecomendationsCategory=result.recommendationsCategory,
    userCreated=result.userCreate,
    userApproved=result.userApprobed
    )

def edit_recommendations(
    client: SymphonyClient,
    recommendations:recommendations,
    new_externalID:str=None,
    resource:str=None,
    alarmType:str=None,
    shortDescription:str=None,
    LongDescription:str=None,
    command:str=None,
    runbook:str=None,
    priority:int=None,
    status:bool=None,
    used:int=None,
    vendor:str=None,
    RecomendationSources:str=None,
    RecomendationsCategory:str=None,
    userApproved:str=None
) ->None:
    """This function edits recommendations.

    :param recommendations: recommendations entity
    :type name: str
    :param new_name: recommendations name
    :type name: str

    :return: none object
    :rtype: :class:`~psym.common.data_class.recommendations`

    **Example 1**

    .. code-block:: python

        recommendations_edited = client.edit_recommendations(
            recommendations=recommendations 
            new_externalID=new_externalID,
            resource="resoruce_2",
            alarmType="alarmType_2",
            LongDescription="LongDescription_2",
            shortDescription="shortDescription_2",
            command="command_2",
            runbook="runbook_2",
            priority=2,
            status=False,
            used=2,
            vendor=vendor.id,
            RecomendationSources=recommendation_sources.id,
            RecomendationsCategory=recommendation_category.id,
            userCreated=user_created.id,
            userApproved=user_created.id
            
            )
    """
    params: Dict[str, Any] = {}
    if new_externalID is not None:
        params.update({"_name_": new_externalID})
    if new_externalID is not None:
        editRecommendations.execute(client, input=EditRecommendationsInput(
            id=recommendations.id,
            externalID=new_externalID,
            resource=resource,
            alarmType=alarmType,
            shortDescription=shortDescription,
            longDescription=LongDescription,
            priority=priority,
            status=status,
            recommendationsSources=RecomendationSources,
            recommendationsCategory=RecomendationsCategory,
            vendor=vendor,
            command=command,
            runbook=runbook,
            used=used,
            userApprobed=userApproved))

def get_recommendations(client: SymphonyClient) -> Iterator[recommendations]:
    """Get the list of Recommendations
    :raises:
        FailedOperationException: Internal symphony error
    :return: Users Iterator
    :rtype: Iterator[ :class:`~psym.common.data_class.recommendations` ]
    **Example**
    .. code-block:: python
        recommendations_ = recommendations.get_recommendations()
        for recommendation in recommendations:
            print(recommendations.name)
    """
    result = Recommendations.execute(client)
    if result is None:
        return
    for edge in result.edges:
        node = edge.node
        if node is not None:
            yield recommendations(
                id=node.id,
                externalID=node.externalID,
                resource=node.resource,
                alarmType=node.alarmType,
                shortDescription=node.shortDescription,
                LongDescription=node.longDescription,
                command=node.command,
                runbook=node.resource,
                priority=node.priority,
                status=node.status,
                used=node.used,
                vendor=node.vendor,
                RecomendationSources=node.recommendationsSources,
                RecomendationsCategory=node.recommendationsCategory,
                userCreated=node.userCreate,
                userApproved=node.userApprobed

            )

def remove_recommendations(client: SymphonyClient, id: str) -> None:
    """This function delete recommendations.

    :param name: recommendations name
    :type name: :class:`~psym.common.data_class.recommendations`
    :rtype: None

    **Example**

    .. code-block:: python

        client.remove_recommendations(id=123456789)
    """	
    removeRecommendations.execute(client, id=id)
