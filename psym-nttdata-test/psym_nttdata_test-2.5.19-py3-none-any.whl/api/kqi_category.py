#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.




from psym.client import SymphonyClient
from psym.common.data_class import KqiCategory

from ..graphql.input.edit_kqi_category_input import EditKqiCategoryInput
from ..graphql.input.add_kqi_category_input import AddKqiCategoryInput
from ..graphql.mutation.add_kqi_category import addKqiCategory
from ..graphql.mutation.edit_kqi_category import EditKqiCategory
from ..graphql.input.edit_kqi_category_input import EditKqiCategoryInput
from ..graphql.query.kqi_category import kqiCategories
from ..graphql.mutation.remove_kqi_category import removeKqiCategory
from psym.common.constant import PAGINATION_STEP
from typing import Any, Dict, Iterator, List, Optional



def add_kqi_category(
    client: SymphonyClient, name: str
) -> KqiCategory:
    """This function adds Kqi Category.

    :param name: Kqi Category name
    :type name: str

    :return: kqiCategory object
    :rtype: :class:`~psym.common.data_class.kqiCategory`

    **Example 1**

    .. code-block:: python

        new_kqi_category = client.add_kqi_category(
            name="kqi_category",

        )
    """
    kqi_category_input = AddKqiCategoryInput(name=name)
    if (len(name) != 0):
        result = addKqiCategory.execute(client, input=kqi_category_input)
        return KqiCategory(name=result.name, id=result.id)
    else:
        print ("you cant leave the name parameter empty")


def edit_kqi_category(
    client: SymphonyClient,
    kpicategory: KqiCategory,
    new_name: Optional[str] = None,
) -> None:
    """This function edits Kqi Category.

    :param kqi_category: Kqi Category entity
    :type name: str
    :param new_name: Kqi Category name
    :type name: str

    :return: none object
    :rtype: :class:`~psym.common.data_class.kqiCategory`

    **Example 1**

    .. code-block:: python

        new_kqi_category_edited = client.edit_kqi_category(
            kqi_category=kqiCategory,
            new_name="kqi_category_edited",

        )
        print(new_kqi_category_edited)
    """
    params: Dict[str, Any] = {}
    if new_name is not None:
        params.update({"_name_": new_name})
    if new_name is not None:
        EditKqiCategory.execute(client, input=EditKqiCategoryInput(id=kpicategory.id, name=new_name))


def get_kqi_categories(client: SymphonyClient) -> Iterator[KqiCategory]:
    """ this funtion Get Kqi Categories


    :return: kqiCategory object
    :rtype: Iterator[ :class:`~psym.common.data_class.kqiCategory` ]

    **Example**

    .. code-block:: python

        kqi_categoryes = client.get_kqi_categories()
        for kqi_category in kqi_categories:
            print(kqi_category.name)
    """
    kqi_categories = kqiCategories.execute(client, first=PAGINATION_STEP)
    edges = kqi_categories.edges if kqi_categories else []
    while kqi_categories is not None and kqi_categories.pageInfo.hasNextPage:
        kqi_categories = kqiCategories.execute(
            client, after=kqi_categories.pageInfo.endCursor, first=PAGINATION_STEP
        )
        if kqi_categories is not None:
            edges.extend(kqi_categories.edges)

    for edge in edges:
        node = edge.node
        if node is not None:
            yield KqiCategory(
                id=node.id,
                name=node.name,
            )


def delete_kqi_category(client: SymphonyClient, id: str) -> None:
    """This function delete Kqi Category.

    :param name: Kqi Category name
    :type name: :class:`~psym.common.data_class.kqiCategory`
    :rtype: None

    **Example**

    .. code-block:: python

        client.delete_kqi_category(id=123456789)
    """
	
    removeKqiCategory.execute(client, id=id)



