"""
Utility functions to create Ascend resource definitions from the corresponding protobuf
objects. The protobuf objects can be obtained via the 'imperative' API accessible through
the SDK client -
`client.get_data_service(<data_service_id>)`
`client.get_dataflow(<dataflow_id>)`
"""

from typing import Dict

import ascend.protos.api.api_pb2 as api_pb2
from ascend.sdk.client import Client
from ascend.sdk.definitions import (Credential, Connection, Dataflow, ReadConnector, Transform, WriteConnector, ComponentGroup, ComponentUuidToIdMap, DataFeed,
                                    DataFeedConnector, DataService)


def data_service_from_proto(client: Client, proto: api_pb2.DataService) -> 'DataService':
  """
  Build a DataService definition from the API DataService protobuf representation.
  This is a utility function that helps bridge the declarative and imperative forms
  of the SDK by transforming a DataService proto message to a DataService definition
  that can be 'applied'.

  Parameters:
  - client: SDK client
  - proto: DataService protobuf object
  Returns: a DataService definition
  """
  return DataService(
      id=proto.id,
      name=proto.name,
      description=proto.description,
      credentials=sorted([Credential.from_proto(credential_proto) for credential_proto in client.list_data_service_credentials(proto.id).data],
                         key=lambda c: c.name),
      connections=sorted([Connection.from_proto(connection_proto) for connection_proto in client.list_connections(proto.id).data], key=lambda c: c.name),
      dataflows=sorted([dataflow_from_proto(client, proto.id, dataflow_proto) for dataflow_proto in client.list_dataflows(proto.id).data], key=lambda c: c.id),
  )


def dataflow_from_proto(client: Client, data_service_id: str, proto: api_pb2.Dataflow) -> 'Dataflow':
  """
  Build a Dataflow definition from the API Dataflow protobuf representation.

  Parameters:
  - client: SDK client
  - data_service_id: DataService id
  - proto: Dataflow protobuf object
  Returns: a Dataflow definition
  """
  component_protos = sorted(client.list_dataflow_components(data_service_id, proto.id, deep=True).data, key=lambda c: c.id)

  uuid_map: ComponentUuidToIdMap = {}
  for c in component_protos:
    uuid_map[c.uuid] = c.id

  read_connectors = [
      ReadConnector.from_proto(client.get_read_connector(data_service_id, proto.id, c.id).data)
      if c.source.container.HasField('immediate') else ReadConnector.from_proto(c) for c in component_protos if c.type == "source"
  ]
  transforms = [Transform.from_proto(c, uuid_map) for c in component_protos if c.type == "view"]
  write_connectors = [WriteConnector.from_proto(c, uuid_map) for c in component_protos if c.type == "sink"]

  role_to_ds_map = _role_to_ds_map(client)
  data_feeds = [DataFeed.from_proto(c, data_service_id, role_to_ds_map, uuid_map) for c in component_protos if c.type == "pub"]

  data_feed_connectors = []
  groups = []
  for c in component_protos:
    if c.type == "sub":
      df = client.get_data_feed_for_data_feed_connector(data_service_id, proto.id, c.id).data
      data_feed_connectors.append(
          DataFeedConnector(id=c.id,
                            name=c.name,
                            description=c.description,
                            input_data_service_id=df.organization.id if df.organization.id else df.org_id,
                            input_dataflow_id=df.project.id if df.project.id else df.prj_id,
                            input_data_feed_id=df.id))
    elif c.type == "group":
      component_ids = sorted([uuid_map[input.uuid] for input in c.content if input.uuid in uuid_map])
      groups.append(ComponentGroup(id=c.id, name=c.name, description=c.description, component_ids=component_ids))

  return Dataflow(
      id=proto.id,
      name=proto.name,
      description=proto.description,
      components=read_connectors + transforms + write_connectors,
      data_feeds=data_feeds,
      data_feed_connectors=data_feed_connectors,
      groups=groups,
  )


def _role_to_ds_map(client: Client) -> Dict[str, str]:
  ds_uuid_to_id = {ds.uuid: ds.id for ds in client.list_data_services().data}
  roles = client.list_data_service_roles().data
  return {role.uuid: ds_uuid_to_id[role.org_id] for role in roles if role.org_id in ds_uuid_to_id and role.id == 'Everyone'}
