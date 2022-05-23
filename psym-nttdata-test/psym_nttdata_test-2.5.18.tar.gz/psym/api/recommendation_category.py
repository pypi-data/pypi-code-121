#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.



from psym.common.data_class import RecommendationsCategory
from psym.client import SymphonyClient

from ..graphql.input.edit_recommendations_category_input import EditRecommendationsCategoryInput
from ..graphql.input.add_recommendations_category_input import AddRecommendationsCategoryInput
from ..graphql.mutation.add_recommendations_category import addRecommendationsCategory
from ..graphql.mutation.edit_recommendations_category import editRecommendationsCategory
from ..graphql.mutation.remove_recommendations_category import removeRecommendationCategory
from ..graphql.query.recommendation_categories import RecommendationsCategories
from psym.common.constant import PAGINATION_STEP
from typing import Any, Dict, Iterator, List, Optional




def add_recommendations_category(
    client: SymphonyClient, name: str
) -> RecommendationsCategory:
    """This function adds Recommendations Category.

    :param name: Recommendations Category name
    :type name: str

    :return: recommendationsCategory object
    :rtype: :class:`~psym.common.data_class.recommendationsCategory`

    **Example 1**

    .. code-block:: python

        new_recommendations_category = client.add_recommendations_category(
            name="recommendations_category",
        )
        print(new_recommendations_category)
    """
    recommendations_category_input = AddRecommendationsCategoryInput(name=name)
    if (len(name) != 0):
        result = addRecommendationsCategory.execute(client, input=recommendations_category_input)
        return RecommendationsCategory(name=result.name, id=result.id)
    else:
        print ("you cant leave the name parameter empty")

def edit_recommendations_category(
    client: SymphonyClient,
    recommendation_category: RecommendationsCategory,
    new_name: Optional[str] = None,
) -> None:
    """This function edits Recommendations Category.

    :param recommendations_category: Recommendations Category entity
    :type name: str
    :param new_name: Recommendations Category name
    :type name: str

    :return: none object
    :rtype: :class:`~psym.common.data_class.recommendationsCategory`

    **Example 1**

    .. code-block:: python

        new_recommendations_category_edited = client.edit_recommendations_category(
            recommendations_category=recommendationsCategory,
            new_name="recommendations_category_edited",
        )
    """
    params: Dict[str, Any] = {}
    if new_name is not None:
        params.update({"_name_": new_name})
    if new_name is not None:
        editRecommendationsCategory.execute(client, input=EditRecommendationsCategoryInput(id=recommendation_category.id, name=new_name))


def get_recommendations_categories(client: SymphonyClient) -> Iterator[RecommendationsCategory]:
    """ this funtion Get Recommendations Categories


    :return: recommendationsCategory object
    :rtype: Iterator[ :class:`~psym.common.data_class.recommendationsCategory` ]

    **Example**

    .. code-block:: python

        recommendations_categoryes = client.get_recommendations_categories()
        for recommendations_category in recommendations_categories:
            print(recommendations_category.name)
    """
    recommendations_categoryess_ = RecommendationsCategories.execute(client, first=PAGINATION_STEP)
    edges = recommendations_categoryess_.edges if recommendations_categoryess_ else []
    while recommendations_categoryess_ is not None and recommendations_categoryess_.pageInfo.hasNextPage:
        recommendations_categoryess_ = RecommendationsCategories.execute(
            client, after=recommendations_categoryess_.pageInfo.endCursor, first=PAGINATION_STEP
        )
        if recommendations_categoryess_ is not None:
            edges.extend(recommendations_categoryess_.edges)

    for edge in edges:
        node = edge.node
        if node is not None:
            yield RecommendationsCategory(
                id=node.id,
                name=node.name,
            )


def remove_recommendations_category(client: SymphonyClient, id: str) -> None:
    """This function delete Recommendations Category.

    :param name: Recommendations Category name
    :type name: :class:`~psym.common.data_class.recommendationsCategory`
    :rtype: None

    **Example**

    .. code-block:: python

        client.remove_recommendations_category(id=123456789)
    """
    removeRecommendationCategory.execute(client, id=id)

