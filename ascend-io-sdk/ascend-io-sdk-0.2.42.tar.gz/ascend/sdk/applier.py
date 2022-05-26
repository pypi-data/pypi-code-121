"""Ascend resource applier classes - used for applying resource definitions."""

import glog
import networkx as nx
from typing import List, Dict
import uuid

import ascend.protos.api.api_pb2 as api_pb2
from ascend.sdk.client import Client
from ascend.sdk.common import components_ordered_by_dependency, dataflows_ordered_by_dependency
from ascend.sdk.definitions import (Component, Connection, Credential, Dataflow, ReadConnector, Transform, WriteConnector, ComponentGroup, ComponentIdToUuidMap,
                                    ComponentUuidType, DataFeed, DataFeedConnector, DataService)
from openapi_client.exceptions import ApiException


class DataServiceApplier:
  """DataServiceApplier is a utility class that accepts a DataService definition and
  'applies' it - ensuring that the DataService is created if it does not already exist,
  deleting any existing Dataflows, components, and members of the DataService that
  are not part of the supplied definition, and applying any configuration changes needed
  to match the definition.
  """
  def __init__(self, client: Client):
    """Creates a new DataServiceApplier."""
    self.client = client

  def apply(self, data_service: DataService, delete=True, dry_run=False, after_credentials=None, after_connections=None):
    """
    Create or update the specified DataService.

    Parameters:
    - data_service: DataService definition
    - delete (optional): If set to `True` (which is the default) - delete any Dataflow
    that is not part of `data_service`. At the Dataflow level, remove any components
    that are not part of the Dataflow definition.
    - dry_run (optional): If set to `True` (`False` by default) - skips any create or
    update operations
    """
    glog.info(f"Apply DataService{' (dry_run)' if dry_run else ''}: {data_service.id}")
    exists = False
    try:
      self.client.get_data_service(data_service.id)
      exists = True
    except ApiException as e:
      if e.status != 404:
        raise e

    if exists:
      glog.info(f"Update DataService: {data_service.id}")
      if not dry_run:
        _tracked_call(self.client.update_data_service, data_service.id, data_service.to_proto())
    else:
      if not dry_run:
        glog.info(f"Create DataService: {data_service.id}")
        _tracked_call(self.client.create_data_service, data_service.to_proto())

    if data_service.credentials is not None:
      for i, cred in enumerate(data_service.credentials):
        data_service.credentials[i] = CredentialApplier(self.client).apply(data_service.id, cred, dry_run)
    if after_credentials:
      after_credentials()

    if data_service.connections is not None:
      for i, conn in enumerate(data_service.connections):
        data_service.connections[i] = ConnectionApplier(self.client).apply(data_service.id, conn, dry_run)
    if after_connections:
      after_connections()

    # Handle dataflows carefully, as we want to first create/apply everything, and only after
    # sweep through and clean up (in reverse order)
    dataflows = dataflows_ordered_by_dependency(data_service.id, data_service.dataflows)
    for df in dataflows:
      DataflowApplier(self.client).apply(data_service.id, df, False, dry_run)
    if delete:
      for df in reversed(dataflows):
        DataflowApplier(self.client)._sweep(data_service.id, df, dry_run)
    try:
      if delete:
        self._sweep(data_service, dry_run)
    except ApiException as e:
      # tolerate 404s during dry runs, since they're likely to happen
      if e.status != 404 or not dry_run:
        raise e

  def _sweep(self, data_service: DataService, dry_run=False):
    """ Delete any dataflows, credential, or connections that are not part of 'data_service'
    """
    glog.info(f"Sweeping DataService: {data_service.id}")

    expected = [dataflow.id for dataflow in data_service.dataflows]
    # TODO - does not yet account for dependencies between dataflows
    for df in self.client.list_dataflows(data_service.id).data:
      if df.id not in expected:
        glog.info(f"Delete Dataflow: (ds={data_service.id} df={df.id})")
        if not dry_run:
          self.client.delete_dataflow(data_service.id, df.id)

    # TODO - decide on what uniquely defines connections
    if data_service.connections is not None:
      expected = [connection.name for connection in data_service.connections]
      for connection in self.client.list_connections(data_service.id).data:
        if connection.name not in expected:
          glog.info(f"Delete Connection: (ds={data_service.id} id={connection.id.value} {connection.name})")
          if not dry_run:
            self.client.delete_connection(data_service.id, connection.id.value)

    if data_service.credentials is not None:
      expected = [credential.name for credential in data_service.credentials]
      for credential in self.client.list_data_service_credentials(data_service.id).data:
        if credential.name not in expected:
          if len(credential.owner_orgs) != 1:
            glog.info("Skip Delete for Credential shared with multiple data services:"
                      f" (ds={data_service.id} credential_id={credential.credential_id} {credential.name}")
            continue
          glog.info(f"Delete Credential: (ds={data_service.id} credential_id={credential.credential_id} {credential.name})")
          if not dry_run:
            self.client.delete_data_service_credentials(data_service.id, credential.credential_id)


class CredentialApplier:
  def __init__(self, client: Client):
    self.client = client

  def apply(self, data_service_id, credential: Credential, dry_run=False):
    glog.info(f"Apply Credential: (ds={data_service_id} credential_id={credential.id} name={credential.name})")
    existing = None

    # There is no "get credential" call, so this is a bit ineficient
    for c in self.client.list_data_service_credentials(data_service_id).data:
      if credential.id == c.credential_id or credential.name == c.name:
        existing = c
        break

    credential_p = credential.to_proto()
    if existing and existing.credential_id != "":
      credential.id = credential.credential.id.value = existing.credential_id
      glog.info(f"Update Credential: (ds={data_service_id} credential_id={credential.id} name={credential.name})")
      if not dry_run:
        existing = self.client.update_data_service_credentials(data_service_id, credential.id, credential_p).data
    else:
      glog.info(f"Create Credential: (ds={data_service_id} credential_id={credential.id} name={credential.name})")
      if not dry_run:
        existing = self.client.create_data_service_credentials(data_service_id, credential_p).data

    if existing:
      # Special copy here to preserve cred values in the object we return
      credential_p.credential_id = existing.credential_id
      credential_p.credential.id.CopyFrom(existing.credential.id)
    return Credential.from_proto(credential_p)


class ConnectionApplier:
  def __init__(self, client: Client):
    self.client = client

  def apply(self, data_service_id, connection: Connection, dry_run=False):
    glog.info(f"Apply Connection: (ds={data_service_id} id={connection.id} name={connection.name})")
    existing = None

    # we have no unique ID, so just go by name for now... additionally, updating fails,
    # so if we find something with the same name, just return that
    for c in self.client.list_connections(data_service_id).data:
      if connection.id == c.id or connection.name == c.name:
        existing = c
        break

    if existing and existing.id.value != "":
      connection.id = existing.id.value
      glog.info(f"Update Connection: (ds={data_service_id} id={connection.id} name={connection.name})")
      if not dry_run:
        res = self.client.update_connection(data_service_id, connection.id, connection.to_proto())
        # glog.info(res)
        # short term hack as we aren't getting full results from the API on creation (See FP2021-49)
        existing = self.client.get_connection(data_service_id, res.data.id.value).data
    else:
      try:
        # backward compatible check, if it is uuid, set to empty string so existing env without friendly id code still works
        uuid.UUID(connection.id)
        connection.id = ""
      except Exception as e:
        glog.debug(f"non uuid string, treat it as friendly id {connection.id}")
      glog.info(f"Create Connection: (ds={data_service_id} id={connection.id} name={connection.name})")
      if not dry_run:
        existing = self.client.create_connection(data_service_id, connection.to_proto()).data

    if existing:
      return Connection.from_proto(existing)
    return connection


class DataflowApplier:
  """DataflowApplier is a utility class that accepts a Dataflow definition and 'applies'
  it - ensuring that a Dataflow is created if it does not already exist and binding it to
  the DataService identified by `data_service_id`, deleting any components and members of
  the Dataflow that are not part of the supplied definition, and applying any configuration
  changes needed to match the definition.
  """
  def __init__(self, client: Client):
    """Creates a new DataflowApplier."""
    self.client = client

  def apply(self, data_service_id: str, dataflow: Dataflow, delete=True, dry_run=False):
    """Accepts a Dataflow definition, and ensures that it is created, bound to the DataService
    identified by `data_service_id`, and has all of the constituent elements included in the
    Dataflow definition - components (read connectors, transforms, write connectors), component
    groups, data feeds, and data feed connectors. The specified DataService must already exist.

    Parameters:
    - data_service_id: DataService id
    - dataflow: Dataflow definition
    - delete: if set to `True` (default=`True`) - delete any components, data feeds,
    data feed connectors, or groups not defined in `dataflow`
    - dry_run: If set to `True` (default=`False`) - skips any create or update operations
    """
    self._apply_dataflow(data_service_id, dataflow, dry_run)

    id_map: ComponentIdToUuidMap = {}
    for dfc in dataflow.data_feed_connectors:
      resource = DataFeedConnectorApplier(self.client).apply(data_service_id, dataflow.id, dfc, dry_run)
      id_map[dfc.id] = ComponentUuidType(type=dfc.legacy_type(), uuid=resource.uuid)

    for component in components_ordered_by_dependency(dataflow.components):
      applier = ComponentApplier(self.client, id_map, dry_run)
      resource = applier.apply(data_service_id, dataflow.id, component)
      id_map[component.id] = ComponentUuidType(type=component.legacy_type(), uuid=resource.uuid)

    for df in dataflow.data_feeds:
      resource = DataFeedApplier(self.client, id_map).apply(data_service_id, dataflow.id, df, dry_run)
      id_map[df.id] = ComponentUuidType(type=df.legacy_type(), uuid=resource.uuid)

    for group in dataflow.groups:
      # validate groups are non-overlapping ?
      GroupApplier(self.client, id_map).apply(data_service_id, dataflow.id, group, dry_run)

    try:
      if delete:
        self._sweep(data_service_id, dataflow, dry_run)
    except ApiException as e:
      # tolerate 404s during dry runs, since they're likely to happen
      if e.status != 404 or not dry_run:
        raise e

  def _apply_dataflow(self, data_service_id: str, dataflow: Dataflow, dry_run=False):
    """ Create a dataflow if it does not already exist, otherwise update it.
    """
    glog.info(f"Apply Dataflow{' (dry_run)' if dry_run else ''}: (ds={data_service_id} df={dataflow.id})")
    exists = False
    try:
      self.client.get_dataflow(data_service_id, dataflow.id)
      exists = True
    except ApiException as e:
      if e.status != 404:
        raise e

    if exists:
      glog.info(f"Update Dataflow: (ds={data_service_id} df={dataflow.id})")
      if not dry_run:
        self.client.update_dataflow(data_service_id, dataflow.id, dataflow.to_proto())
    else:
      glog.info(f"Create Dataflow: (ds={data_service_id} df={dataflow.id})")
      if not dry_run:
        self.client.create_dataflow(data_service_id, dataflow.to_proto())

  def _sweep(self, data_service_id: str, dataflow: Dataflow, dry_run=False):
    """ Delete any components, data feeds, data feed connectors, or component groups
    that are not part of `dataflow`
    """
    glog.info(f"Sweeping Dataflow: (ds={data_service_id} df={dataflow.id})")

    expected_groups = [group.id for group in dataflow.groups]
    for group in self.client.list_component_groups(data_service_id, dataflow.id).data:
      if group.id not in expected_groups:
        glog.info(f"Delete ComponentGroup: (ds={data_service_id} df={dataflow.id} {group.id})")
        if not dry_run:
          self.client.delete_component_group(data_service_id, dataflow.id, group.id)

    expected_data_feeds = [data_feed.id for data_feed in dataflow.data_feeds]
    for data_feed in self.client.list_data_feeds(data_service_id, dataflow.id).data:
      if data_feed.id not in expected_data_feeds:
        glog.info(f"Delete DataFeed: (ds={data_service_id} df={dataflow.id} {data_feed.id})")
        if not dry_run:
          self.client.delete_data_feed(data_service_id, dataflow.id, data_feed.id)

    uuid_to_id: Dict[str, str] = {}
    id_to_type: Dict[str, str] = {}
    components = []
    for component in self.client.list_dataflow_components(data_service_id, dataflow.id).data:
      if component.type not in ["source", "view", "sink"]:
        continue
      components.append(component)
      uuid_to_id[component.uuid] = component.id
      id_to_type[component.id] = component.type

    g = nx.DiGraph()
    for component in components:
      g.add_node(component.id)
      if component.type == "view":
        for input in component.inputs:
          if input.type in ["source", "view"]:
            g.add_edge(component.id, uuid_to_id[input.uuid])
      elif component.type == "sink":
        if component.inputType in ["source", "view"]:
          g.add_edge(component.id, uuid_to_id[component.inputUUID])

    expected_components = [component.id for component in dataflow.components]
    for component_id in list(nx.topological_sort(g)):
      if component_id not in expected_components:
        if id_to_type[component_id] == "source":
          glog.info(f"Delete ReadConnector: (ds={data_service_id} df={dataflow.id} {component_id})")
          if not dry_run:
            self.client.delete_read_connector(data_service_id, dataflow.id, component_id)
        elif id_to_type[component_id] == "view":
          glog.info(f"Delete Transform: (ds={data_service_id} df={dataflow.id} {component_id})")
          if not dry_run:
            self.client.delete_transform(data_service_id, dataflow.id, component_id)
        elif id_to_type[component_id] == "sink":
          glog.info(f"Delete WriteConnector: (ds={data_service_id} df={dataflow.id} {component_id})")
          if not dry_run:
            self.client.delete_write_connector(data_service_id, dataflow.id, component_id)

    expected_dfcs = [dfc.id for dfc in dataflow.data_feed_connectors]
    for dfc in self.client.list_data_feed_connectors(data_service_id, dataflow.id).data:
      if dfc.id not in expected_dfcs:
        glog.info(f"Delete DataFeedConnector: (ds={data_service_id} df={dataflow.id} {dfc.id})")
        if not dry_run:
          self.client.delete_data_feed_connector(data_service_id, dataflow.id, dfc.id)


class GroupApplier:
  def __init__(self, client: Client, id_map: ComponentIdToUuidMap):
    self.client = client
    self.id_map = id_map

  def apply(self, data_service_id, dataflow_id, group: ComponentGroup, dry_run=False):
    glog.info(f"Apply ComponentGroup: (ds={data_service_id} df={dataflow_id} {group.id})")
    exists = False
    try:
      self.client.get_component_group(data_service_id, dataflow_id, group.id)
      exists = True
    except ApiException as e:
      if e.status != 404:
        raise e

    if exists:
      glog.info(f"Update ComponentGroup: (ds={data_service_id} df={dataflow_id} {group.id})")
      if not dry_run:
        return self.client.update_component_group(data_service_id, dataflow_id, group.id, group.to_proto(self.id_map)).data
      else:
        return api_pb2.ComponentGroup()
    else:
      glog.info(f"Create ComponentGroup: (ds={data_service_id} df={dataflow_id} {group.id})")
      if not dry_run:
        return self.client.create_component_group(data_service_id, dataflow_id, group.to_proto(self.id_map)).data
      else:
        return api_pb2.ComponentGroup()

  @staticmethod
  def build(client: Client, data_service_id: str, dataflow_id: str) -> 'GroupApplier':
    id_map = _component_id_to_uuid_map(client, data_service_id, dataflow_id)
    return GroupApplier(client, id_map)


class DataFeedApplier:
  def __init__(self, client: Client, id_map: ComponentIdToUuidMap):
    self.client = client
    self.id_map = id_map

  def apply(self, data_service_id, dataflow_id, data_feed: DataFeed, dry_run=False):
    glog.info(f"Apply DataFeed: (ds={data_service_id} df={dataflow_id} {data_feed.id})")
    exists = False
    try:
      self.client.get_data_feed(data_service_id, dataflow_id, data_feed.id)
      exists = True
    except ApiException as e:
      if e.status != 404:
        raise e

    ds_uuid_to_id = {ds.uuid: ds.id for ds in self.client.list_data_services().data}
    roles = self.client.list_data_service_roles().data
    ds_to_role_map = {ds_uuid_to_id[role.org_id]: role.uuid for role in roles if role.id == 'Everyone' and role.org_id in ds_uuid_to_id}

    if exists:
      glog.info(f"Update DataFeed: (ds={data_service_id} df={dataflow_id} {data_feed.id})")
      if not dry_run:
        return self.client.update_data_feed(data_service_id, dataflow_id, data_feed.id, data_feed.to_proto(data_service_id, self.id_map, ds_to_role_map)).data
      else:
        return api_pb2.DataFeed()
    else:
      glog.info(f"Create DataFeed: (ds={data_service_id} df={dataflow_id} {data_feed.id})")
      if not dry_run:
        return self.client.create_data_feed(data_service_id, dataflow_id, data_feed.to_proto(data_service_id, self.id_map, ds_to_role_map)).data
      else:
        return api_pb2.DataFeed()

  @staticmethod
  def build(client: Client, data_service_id: str, dataflow_id: str) -> 'DataFeedApplier':
    id_map = _component_id_to_uuid_map(client, data_service_id, dataflow_id)
    return DataFeedApplier(client, id_map)


class DataFeedConnectorApplier:
  def __init__(self, client: Client):
    self.client = client

  def apply(self, data_service_id, dataflow_id, data_feed_connector: DataFeedConnector, dry_run=False):
    try:
      data_feed = self.client.get_data_feed(data_feed_connector.input_data_service_id, data_feed_connector.input_dataflow_id,
                                            data_feed_connector.input_data_feed_id).data
    except ApiException as e:
      if e.status == 404 and dry_run and \
        data_feed_connector.input_data_service_id == data_service_id:  # noqa: E121
        # with dry_run it is possible we haven't created the host DataService yet
        data_feed = api_pb2.DataFeed()
      else:
        raise e

    dfc_repr = f"(ds={data_service_id} df={dataflow_id} {data_feed_connector.id})"
    glog.info(f"Apply DataFeedConnector: {dfc_repr}")
    exists = False
    try:
      self.client.get_data_feed_connector(data_service_id, dataflow_id, data_feed_connector.id)
      exists = True
    except ApiException as e:
      if e.status != 404:
        raise e

    if exists:
      glog.info(f"Update DataFeedConnector: {dfc_repr}")
      if not dry_run:
        return self.client.update_data_feed_connector(data_service_id, dataflow_id, data_feed_connector.id, data_feed_connector.to_proto(data_feed.uuid)).data
      else:
        return api_pb2.DataFeedConnector()
    else:
      glog.info(f"Create DataFeedConnector: {dfc_repr}")
      if not dry_run:
        return self.client.create_data_feed_connector(data_service_id, dataflow_id, data_feed_connector.to_proto(data_feed.uuid)).data
      else:
        return api_pb2.DataFeedConnector()


class ComponentApplier:
  def __init__(self, client: Client, id_map: ComponentIdToUuidMap, dry_run=False):
    self.client = client
    self.id_map = id_map
    self.dry_run = dry_run

  def _component_exists(self, data_service_id, dataflow_id, component) -> bool:
    try:
      if isinstance(component, ReadConnector):
        self.client.get_read_connector(data_service_id, dataflow_id, component.id)
      elif isinstance(component, WriteConnector):
        self.client.get_write_connector(data_service_id, dataflow_id, component.id)
      elif isinstance(component, Transform):
        self.client.get_transform(data_service_id, dataflow_id, component.id)
      else:
        raise TypeError("Component has type {}, but expected one of: ReadConnector, WriteConnector, Transform".format(type(component)))
      return True
    except ApiException as e:
      if e.status == 404:
        return False
      else:
        raise e

  def _create_component(self, data_service_id, dataflow_id, component: Component):
    proto = component.to_proto(self.id_map)
    api_method = None
    default = None
    if isinstance(component, ReadConnector):
      glog.info(f"Create ReadConnector: (ds={data_service_id} df={dataflow_id} {component.id})")
      api_method = self.client.create_read_connector
      default = api_pb2.ReadConnector()
    elif isinstance(component, WriteConnector):
      glog.info(f"Create WriteConnector: (ds={data_service_id} df={dataflow_id} {component.id})")
      api_method = self.client.create_write_connector
      default = api_pb2.WriteConnector()
    elif isinstance(component, Transform):
      glog.info(f"Create Transform: (ds={data_service_id} df={dataflow_id} {component.id})")
      api_method = self.client.create_transform
      default = api_pb2.Transform()
    if api_method is None:
      raise TypeError(f"Unhandled component type: {type(component)}")
    if not self.dry_run:
      return _tracked_call(api_method, data_service_id, dataflow_id, proto).data
    else:
      return default

  def _delete_component(self, data_service_id, dataflow_id, component_id: str):
    api_method = None
    component_type = self.id_map[component_id].type
    if component_type == 'source':
      glog.info(f"Delete ReadConnector: (ds={data_service_id} df={dataflow_id} {component_id})")
      api_method = self.client.delete_read_connector
    elif component_type == 'sink':
      glog.info(f"Delete WriteConnector: (ds={data_service_id} df={dataflow_id} {component_id})")
      api_method = self.client.delete_write_connector
    elif component_type == 'view':
      glog.info(f"Delete Transform: (ds={data_service_id} df={dataflow_id} {component_id})")
      api_method = self.client.delete_transform
    if api_method is None:
      raise TypeError(f"Unhandled component type: {component_type}")
    if not self.dry_run:
      return _tracked_call(api_method, data_service_id, dataflow_id, component_id).data

  def _update_component(self, data_service_id, dataflow_id, component: Component):
    proto = component.to_proto(self.id_map)
    api_method = None
    default = None
    if isinstance(component, ReadConnector):
      glog.info(f"Update ReadConnector: (ds={data_service_id} df={dataflow_id} {component.id})")
      api_method = self.client.update_read_connector
      default = api_pb2.ReadConnector()
    elif isinstance(component, WriteConnector):
      glog.info(f"Update WriteConnector: (ds={data_service_id} df={dataflow_id} {component.id})")
      api_method = self.client.update_write_connector
      default = api_pb2.WriteConnector()
    elif isinstance(component, Transform):
      glog.info(f"Update Transform: (ds={data_service_id} df={dataflow_id} {component.id})")
      api_method = self.client.update_transform
      default = api_pb2.Transform()
    if api_method is None:
      raise TypeError(f"Unhandled component type: {type(component)}")
    if not self.dry_run:
      return _tracked_call(api_method, data_service_id, dataflow_id, component.id, proto).data
    else:
      return default

  def apply(self, data_service_id, dataflow_id, component: Component):
    """
    Applies the provided component and
    :param data_service_id:
    :param dataflow_id:
    :param component:
    :return:
    """
    glog.info(f"Apply Component: (ds={data_service_id} df={dataflow_id} {component.id})")
    if self._component_exists(data_service_id, dataflow_id, component):
      return self._update_component(data_service_id, dataflow_id, component)
    else:
      if component.id in self.id_map:
        self._delete_component(data_service_id, dataflow_id, component.id)
      return self._create_component(data_service_id, dataflow_id, component)

  @staticmethod
  def build(client: Client, data_service_id: str, dataflow_id: str) -> 'ComponentApplier':
    id_map = _component_id_to_uuid_map(client, data_service_id, dataflow_id)
    return ComponentApplier(client, id_map)


def _component_id_to_uuid_map(client: Client, data_service_id: str, dataflow_id: str) -> ComponentIdToUuidMap:
  id_map: ComponentIdToUuidMap = {}
  components = client.list_dataflow_components(data_service_id, dataflow_id).data
  for c in components:
    id_map[c.id] = ComponentUuidType(type=c.type, uuid=c.uuid)

  return id_map


def _tracked_call(method, *args, **kwargs):
  '''call method, logging arguments if it throws an exception'''
  try:
    return method(*args, **kwargs)
  except Exception as e:
    glog.warn(f'{method.__name__} call failed, (args={args}, kwargs={kwargs}): {e}')
    raise e
