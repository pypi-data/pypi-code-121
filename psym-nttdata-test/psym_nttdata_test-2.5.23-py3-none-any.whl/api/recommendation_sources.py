#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.


from psym.common.data_class import RecommendationSources
from psym.client import SymphonyClient

from ..graphql.input.edit_recommendations_sources_input import EditRecommendationsSourcesInput
from ..graphql.input.add_recommendations_sources_input import AddRecommendationsSourcesInput
from ..graphql.mutation.add_recommendations_sources import addRecommendationsSources
from ..graphql.mutation.edit_recommendations_sources import editRecommendationsSources
from ..graphql.mutation.remove_recommendations_sources import removeRecommendationSources
from ..graphql.query.recommendation_sources import RecommendationsSources
from psym.common.constant import PAGINATION_STEP
from typing import Any, Dict, Iterator, List, Optional




def add_recommendations_sources(
    client: SymphonyClient, name: str
) -> RecommendationSources:
    """This function adds recommendations Sources.

    :param name: recommendations Sources name
    :type name: str

    :return: recommendationsSources object
    :rtype: :class:`~psym.common.data_class.recommendationsSources`

    **Example 1**

    .. code-block:: python

        new_recommendations_sources = client.add_recommendations_sources(
            name="recommendations_sources",
        )
        print(new_recommendations_sources)
    """
    recommendations_sources_input = AddRecommendationsSourcesInput(name=name)
    if (len(name) != 0):
        result = addRecommendationsSources.execute(client, input=recommendations_sources_input)
        return RecommendationSources(name=result.name, id=result.id)
    else:
        print ("you cant leave the name parameter empty")

def edit_recommendations_sources(
    client: SymphonyClient,
    recommendation_sources: RecommendationSources,
    new_name: Optional[str] = None,
) -> None:
    """This function edits recommendations Sources.

    :param recommendations_sources: recommendations Sources entity
    :type name: str
    :param new_name: recommendations Sources name
    :type name: str

    :return: none object
    :rtype: :class:`~psym.common.data_class.recommendationsSources`

    **Example 1**

    .. code-block:: python

        new_recommendations_sources_edited = client.edit_recommendations_sources(
            recommendations_sources=recommendationsSources,
            new_name="recommendations_sources_edited",
        )

    """
    params: Dict[str, Any] = {}
    if new_name is not None:
        params.update({"_name_": new_name})
    if new_name is not None:
        editRecommendationsSources.execute(client, input=EditRecommendationsSourcesInput(id=recommendation_sources.id, name=new_name))


def get_recommendations_sources(client: SymphonyClient) -> Iterator[RecommendationsSources]:
    """ this funtion Get recommendations Sourceses


    :return: recommendationsSources object
    :rtype: Iterator[ :class:`~psym.common.data_class.recommendationsSources` ]

    **Example**

    .. code-block:: python

        recommendations_sources = client.get_recommendations_sources()
        for recommendations_sources in recommendations_sources:
            print(recommendations_sources.name)
    """
    recommendations_sourcesess_ = RecommendationsSources.execute(client, first=PAGINATION_STEP)
    edges = recommendations_sourcesess_.edges if recommendations_sourcesess_ else []
    while recommendations_sourcesess_ is not None and recommendations_sourcesess_.pageInfo.hasNextPage:
        recommendations_sourcesess_ = RecommendationsSources.execute(
            client, after=recommendations_sourcesess_.pageInfo.endCursor, first=PAGINATION_STEP
        )
        if recommendations_sourcesess_ is not None:
            edges.extend(recommendations_sourcesess_.edges)

    for edge in edges:
        node = edge.node
        if node is not None:
            yield RecommendationSources(
                id=node.id,
                name=node.name,
            )


def remove_recommendations_sources(client: SymphonyClient, id: str) -> None:
    """This function delete recommendations Sources.

    :param name: recommendations Sources name
    :type name: :class:`~psym.common.data_class.recommendationsSources`
    :rtype: None

    **Example**

    .. code-block:: python

        client.remove_recommendations_sources(id=123456789)
    """
    removeRecommendationSources.execute(client, id=id)

    