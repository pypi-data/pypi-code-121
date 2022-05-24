#!/usr/bin/env python3
# Copyright (c) 2004-present Facebook All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

from typing import Optional

from psym.client import SymphonyClient
from psym.common.data_class import Flow, FlowDraft, FlowInstance
from psym.graphql.enum.flow_new_instances_policy import FlowNewInstancesPolicy
from psym.graphql.input.add_flow_draft_input import AddFlowDraftInput
from psym.graphql.input.import_flow_draft_input import ImportFlowDraftInput
from psym.graphql.input.publish_flow_input import PublishFlowInput
from psym.graphql.input.start_block_input import StartBlockInput
from psym.graphql.input.start_flow_input import StartFlowInput
from psym.graphql.mutation.add_flow_draft import AddFlowDraftMutation
from psym.graphql.mutation.import_flow_draft import ImportFlowDraftMutation
from psym.graphql.mutation.publish_flow import PublishFlowMutation
from psym.graphql.mutation.start_flow import StartFlowMutation


def add_flow_draft(client: SymphonyClient, name: str) -> FlowDraft:
    """This function add flow draft

    :param name: Name of the flow draft
    :type name: str

    :raises:
        * FailedOperationException: Internal symphony error

    :return: FlowDraft object
    :rtype: :class:`~psym.common.data_class.FlowDraft`

    **Example**

    .. code-block:: python

        draft = client.add_flow_draft(name="Transport Deployment")
    """
    flow_draft = AddFlowDraftMutation.execute(
        client, AddFlowDraftInput(name=name, endParamDefinitions=[])
    )
    return FlowDraft(id=flow_draft.id, name=flow_draft.name)


def import_flow_draft(
    client: SymphonyClient, id: str, name: str, start_block_cid: Optional[str]
) -> FlowDraft:
    """This function imports an existing flow draft with draft details and blocks

    :param id: Id of flow draft to edit
    :type id: str
    :param name: New name of the flow draft
    :type name: str
    :param start_block_cid: Client ID of the start block to create in flow draft
    :type start_block_cid: str, optional

    :raises:
        * FailedOperationException: Internal symphony error

    :return: FlowDraft object
    :rtype: :class:`~psym.common.data_class.FlowDraft`

    **Example**

    .. code-block:: python

        draft = client.add_flow_draft(name="Transport Deployment")
        new_draft = client.import_flow_draft(id=draft.id, name=draft.name, start_block_cid="Start")
    """
    start_block_input = (
        StartBlockInput(cid=start_block_cid, paramDefinitions=[])
        if start_block_cid
        else None
    )
    flow_draft = ImportFlowDraftMutation.execute(
        client,
        ImportFlowDraftInput(
            id=id,
            name=name,
            endParamDefinitions=[],
            startBlock=start_block_input,
            endBlocks=[],
            decisionBlocks=[],
            gotoBlocks=[],
            subflowBlocks=[],
            triggerBlocks=[],
            actionBlocks=[],
            trueFalseBlocks=[],
            connectors=[],
        ),
    )
    return FlowDraft(id=flow_draft.id, name=flow_draft.name)


def publish_flow(client: SymphonyClient, flow_draft_id: str) -> Flow:
    """This function publishes flow draft which creates flow with flow draft content and delete the flow draft

    :param flow_draft_id: Id of flow draft to publish
    :type flow_draft_id: str

    :raises:
        * FailedOperationException: Internal symphony error

    :return: Flow object
    :rtype: :class:`~psym.common.data_class.Flow`

    **Example**

    .. code-block:: python

        draft = client.add_flow_draft(name="Transport Deployment")
        new_draft = client.import_flow_draft(id=draft.id, name=draft.name, start_block_name="Start")
        flow = client.publish_flow(flow_draft_id=new_draft.id, flowInstancesPolicy.ENABLED)
    """
    flow = PublishFlowMutation.execute(
        client,
        PublishFlowInput(
            flowDraftID=flow_draft_id,
            flowInstancesPolicy=FlowNewInstancesPolicy.ENABLED,
        ),
    )
    return Flow(id=flow.id, name=flow.name)


def start_flow(client: SymphonyClient, flow_id: str) -> FlowInstance:
    """This function starts a flow and create flow instance of it

    :param flow_id: Id of flow to start
    :type flow_id: str

    :raises:
        * FailedOperationException: Internal symphony error

    :return: FlowInstance object
    :rtype: :class:`~psym.common.data_class.FlowInstance`

    **Example**

    .. code-block:: python

        draft = client.add_flow_draft(name="Transport Deployment")
        new_draft = client.import_flow_draft(id=draft.id, name=draft.name, start_block_name="Start")
        flow = client.publish_flow(flow_draft_id=new_draft.id)
        flow_instance = client.start_flow(flow_id=flow.id)
    """
    flow_instance = StartFlowMutation.execute(
        client, StartFlowInput(flowID=flow_id, params=[])
    )
    return FlowInstance(id=flow_instance.id, status=flow_instance.status)
