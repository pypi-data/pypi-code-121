#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.




from psym.client import SymphonyClient
from psym.common.data_class import KqiPerspective

from ..graphql.input.edit_kqi_perspective_input import EditKqiPerspectiveInput
from ..graphql.input.add_kqi_perspective_input import AddKqiPerspectiveInput
from ..graphql.input.edit_kqi_perspective_input import EditKqiPerspectiveInput
from ..graphql.mutation.add_kqi_perspective import addKqiPerspective
from ..graphql.mutation.edit_kqi_perspective import editKqiPerspective
from ..graphql.query.kqi_perspective import kqiPerspectives
from ..graphql.mutation.remove_kqi_perspective import removeKqiPerspective
from psym.common.constant import PAGINATION_STEP
from typing import Any, Dict, Iterator, List, Optional




def add_kqi_perspective(
    client: SymphonyClient, name: str
) -> KqiPerspective:
    """This function adds Kqi Perspective.

    :param name: Kqi Perspective name
    :type name: str

    :return: KqiPerspective object
    :rtype: :class:`~psym.common.data_class.kqiPerspective`

    **Example 1**

    .. code-block:: python

        new_Kqi_perspective = client.add_kqi_perspective(
            name="Kqi_perspective",

        )
    """
    kqi_perspective_input = AddKqiPerspectiveInput(name=name)
    result = addKqiPerspective.execute(client, input=kqi_perspective_input)
    return KqiPerspective(name=result.name, id=result.id)


def edit_kqi_perspective(
    client: SymphonyClient,
    kqiperspective: KqiPerspective,
    new_name: Optional[str] = None,
) -> None:
    """This function edits Kqi Perspective.

    :param Kqi_perspective: Kqi Perspective entity
    :type name: str
    :param new_name: Kqi Perspective name
    :type name: str

    :return: none object
    :rtype: :class:`~psym.common.data_class.KqiPerspective`

    **Example 1**

    .. code-block:: python

        new_Kqi_perspective_edited = client.edit_kqi_perspective(
            Kqi_perspective=KqiPerspective,
            new_name="Kqi_perspective_edited",

        )
    """
    params: Dict[str, Any] = {}
    if new_name is not None:
        params.update({"_name_": new_name})
    if new_name is not None:
        editKqiPerspective.execute(client, input=EditKqiPerspectiveInput(id=kqiperspective.id, name=new_name))


def get_kqi_perspectives(client: SymphonyClient) -> Iterator[KqiPerspective]:
    """ This funtion Get Kqi Perspectives


    :return: KqiPerspective object
    :rtype: Iterator[ :class:`~psym.common.data_class.kqiPerspective` ]

    **Example**

    .. code-block:: python

        kqi_perspectivees = client.get_kqi_perspectives()
        for kqi_perspective in kqi_perspectives:
            print(Kqi_perspective.name)
    """
    kqi_perspectives = kqiPerspectives.execute(client, first=PAGINATION_STEP)
    edges = kqi_perspectives.edges if kqi_perspectives else []
    while kqi_perspectives is not None and kqi_perspectives.pageInfo.hasNextPage:
        kqi_perspectives = kqiPerspectives.execute(
            client, after=kqi_perspectives.pageInfo.endCursor, first=PAGINATION_STEP
        )
        if kqi_perspectives is not None:
            edges.extend(kqi_perspectives.edges)

    for edge in edges:
        node = edge.node
        if node is not None:
            yield KqiPerspective(
                id=node.id,
                name=node.name,
            )


def delete_kqi_perspective(client: SymphonyClient, id: str) -> None:
    """This function delete Kqi Perspective.

    :param name: Kqi Perspective name
    :type name: :class:`~psym.common.data_class.KqiPerspective`
    :rtype: None

    **Example**

    .. code-block:: python

        client.delete_kqi_perspective(id=123456789)
    """
    removeKqiPerspective.execute(client, id=id)



