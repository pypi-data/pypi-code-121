#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.




from psym.client import SymphonyClient
from psym.common.data_class import KpiCategory

from ..graphql.input.edit_kpi_category_input import EditKpiCategoryInput
from ..graphql.input.add_kpi_category_input import AddKpiCategoryInput
from ..graphql.mutation.add_kpi_category import AddKpiCategory
from ..graphql.mutation.edit_kpi_category import EditKpiCategory
from ..graphql.input.edit_kpi_category_input import EditKpiCategoryInput
from ..graphql.query.kpi_category import kpiCategoryQuery
from ..graphql.mutation.remove_kpi_category import removeKpiCategory
from psym.common.constant import PAGINATION_STEP
from typing import Any, Dict, Iterator, List, Optional



def add_kpi_category(
    client: SymphonyClient, name: str
) -> KpiCategory:
    """This function adds Kpi Category.

    :param name: Kpi Category name
    :type name: str

    :return: kpiCategory object
    :rtype: :class:`~psym.common.data_class.kpiCategory`

    **Example 1**

    .. code-block:: python

        new_kpi_category = client.add_kpi_category(
            name="kpi_category",
        )
        print(new_kpi_category)
    """
    kpi_category_input = AddKpiCategoryInput(name=name)
    if (len(name) != 0):
        result = AddKpiCategory.execute(client, input=kpi_category_input)
        return KpiCategory(name=result.name, id=result.id)
    else:
        print ("you cant leave the name parameter empty")


def edit_kpi_category(
    client: SymphonyClient,
    kpicategory: KpiCategory,
    new_name: Optional[str] = None,
) -> None:
    """This function edits Kpi Category.

    :param kpi_category: Kpi Category entity
    :type name: str
    :param new_name: Kpi Category name
    :type name: str

    :return: none object
    :rtype: :class:`~psym.common.data_class.kpiCategory`

    **Example 1**

    .. code-block:: python

        new_kpi_category_edited = client.edit_kpi_category(
            kpi_category=kpiCategory,
            new_name="kpi_category_edited",

        )
        print(new_kpi_category_edited)

    """
    params: Dict[str, Any] = {}
    if new_name is not None:
        params.update({"_name_": new_name})
    if new_name is not None:
        EditKpiCategory.execute(client, input=EditKpiCategoryInput(id=kpicategory.id, name=new_name))


def get_kpi_categories(client: SymphonyClient) -> Iterator[KpiCategory]:
    """ this funtion Get Kpi Categories


    :return: kpiCategory object
    :rtype: Iterator[ :class:`~psym.common.data_class.kpiCategory` ]

    **Example**

    .. code-block:: python

        kpi_categoryes = client.get_kpi_categories()
        for kpi_category in kpi_categories:
            print(kpi_category.name)
    """
    kpi_categories = kpiCategoryQuery.execute(client, first=PAGINATION_STEP)
    edges = kpi_categories.edges if kpi_categories else []
    while kpi_categories is not None and kpi_categories.pageInfo.hasNextPage:
        kpi_categories = kpiCategoryQuery.execute(
            client, after=kpi_categories.pageInfo.endCursor, first=PAGINATION_STEP
        )
        if kpi_categories is not None:
            edges.extend(kpi_categories.edges)

    for edge in edges:
        node = edge.node
        if node is not None:
            yield KpiCategory(
                id=node.id,
                name=node.name,
            )


def delete_kpi_category(client: SymphonyClient, id: str) -> None:
    """This function delete Kpi Category.

    :param name: Kpi Category name
    :type name: :class:`~psym.common.data_class.kpiCategory`
    :rtype: None

    **Example**

    .. code-block:: python

        client.delete_kpi_category(id=123456789)
    """
    removeKpiCategory.execute(client, id=id)



