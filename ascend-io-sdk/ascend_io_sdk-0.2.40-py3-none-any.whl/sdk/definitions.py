"""Ascend resource definition classes."""

import abc
import google.protobuf.timestamp_pb2 as timestamp_pb2
import google.protobuf.wrappers_pb2 as wrappers_pb2
from typing import List, Dict, Optional
from collections import namedtuple

import ascend.protos.api.api_pb2 as api_pb2
import ascend.protos.ascend.ascend_pb2 as ascend_pb2
import ascend.protos.component.component_pb2 as component_pb2
import ascend.protos.connection.connection_pb2 as connection_pb2
import ascend.protos.core.core_pb2 as core_pb2
import ascend.protos.expression.expression_pb2 as expression_pb2
import ascend.protos.io.io_pb2 as io_pb2
import ascend.protos.operator.operator_pb2 as operator_pb2
import ascend.protos.pattern.pattern_pb2 as pattern_pb2

ComponentUuidType = namedtuple('ComponentUuidType', ['uuid', 'type'])
ComponentIdToUuidMap = Dict[str, ComponentUuidType]
ComponentUuidToIdMap = Dict[str, str]


class Definition(abc.ABC):
  """Base class for all definitions."""
  def __init__(self):
    pass


class Component(Definition):
  """Components are the functional units in a Dataflow.
   There are three main types of Components: ReadConnectors, Transforms, and WriteConnectors.
  """
  def __init__(self, id: str):
    self.id = id

  def dependencies(self) -> List[str]:
    raise NotImplementedError(self)

  def to_proto(self, id_map: ComponentIdToUuidMap):
    raise NotImplementedError(self)

  def legacy_type(self) -> str:
    raise NotImplementedError(self)


class ReadConnector(Component):
  """A read connector"""
  def __init__(self,
               id: str,
               name: str,
               container: io_pb2.Container,
               description: str = None,
               pattern: pattern_pb2.Pattern = None,
               update_periodical: core_pb2.Periodical = None,
               assigned_priority: component_pb2.Priority = None,
               last_manual_refresh_time: timestamp_pb2.Timestamp = None,
               aggregation_limit: wrappers_pb2.Int64Value = None,
               bytes: component_pb2.Source.FromBytes = None,
               records: component_pb2.Source.FromRecords = None,
               compute_configurations: List[expression_pb2.StageComputeConfiguration] = None):
    """
    Create a ReadConnector definition.

    Parameters:
    - id: identifier that is unique within Dataflow
    - name: user-friendly name
    - description: brief description
    - container (proto): a typed representation of the source of data
    - pattern (proto): defines the set of objects in the source that will be ingested
    - update_periodical: specifies source update frequency
    - assigned_priority: scheduling priority for the read connector
    - last_manual_refresh_time:
    - aggregation_limit:
    - bytes: defines the operator for parsing bytes read from the source (example - json
      or xsv parsing)
    - records: defines the schema for records read from a database or warehouse
    - compute_configurations: custom configuration overrides by stage. Currently supports the
      Read Stage for connections-type ReadConnectors
    Returns: a new ReadConnector instance.

    Note - a read connector can have either `bytes` or `records` defined, but not both.
    """
    super().__init__(id)
    self.name = name
    self.description = description
    self.pattern = pattern
    self.container = container
    self.update_periodical = update_periodical
    self.last_manual_refresh_time = last_manual_refresh_time
    self.assigned_priority = assigned_priority
    self.aggregation_limit = aggregation_limit
    self.bytes = bytes
    self.records = records
    self.compute_configurations = compute_configurations

  def dependencies(self) -> List[str]:
    return []

  def to_proto(self, id_map: ComponentIdToUuidMap):
    proto = api_pb2.ReadConnector(id=self.id, name=self.name, description=self.description, version=1, source=component_pb2.Source(container=self.container))
    if self.pattern is not None:
      proto.source.pattern.CopyFrom(self.pattern)
    if self.update_periodical is not None:
      proto.source.updatePeriodical.CopyFrom(self.update_periodical)
    if self.last_manual_refresh_time is not None:
      proto.source.last_manual_refresh_time.CopyFrom(self.last_manual_refresh_time)
    if self.assigned_priority is not None:
      proto.source.assigned_priority.CopyFrom(self.assigned_priority)
    if self.aggregation_limit is not None:
      proto.source.aggregation_limit.CopyFrom(self.aggregation_limit)
    if self.bytes is not None:
      proto.source.bytes.CopyFrom(self.bytes)
    if self.records is not None:
      proto.source.records.CopyFrom(self.records)
    if self.compute_configurations is not None:
      proto.source.compute_configurations.extend(self.compute_configurations)

    return proto

  def legacy_type(self) -> str:
    return "source"

  @staticmethod
  def from_proto(proto: api_pb2.ReadConnector) -> 'ReadConnector':
    rc = ReadConnector(id=proto.id, name=proto.name, description=proto.description, container=proto.source.container)
    if proto.source.HasField("bytes"):
      rc.bytes = proto.source.bytes
    elif proto.source.HasField("records"):
      rc.records = proto.source.records
    if proto.source.HasField("pattern"):
      rc.pattern = proto.source.pattern
    if proto.source.HasField("updatePeriodical"):
      rc.update_periodical = proto.source.updatePeriodical
    if proto.source.HasField("last_manual_refresh_time"):
      rc.last_manual_refresh_time = proto.source.last_manual_refresh_time
    if proto.source.HasField("assigned_priority"):
      rc.assigned_priority = proto.source.assigned_priority
    if proto.source.HasField("aggregation_limit"):
      rc.aggregation_limit = proto.source.aggregation_limit
    if len(proto.source.compute_configurations) > 0:
      rc.compute_configurations = proto.source.compute_configurations[:]
    return rc


class Transform(Component):
  """A transform"""
  def __init__(self,
               id: str,
               name: str,
               input_ids: List[str],
               operator: operator_pb2.Operator,
               description: str = None,
               assigned_priority: component_pb2.Priority = None):
    """
    Create a Transform definition.

    Parameters:
    - id: identifier that is unique within Dataflow
    - name: user-friendly name
    - description: brief description
    - input_ids: list of input component ids
    - operator: transform operator definition - example - SQL/PySpark/Scala transform
    - assigned_priority: scheduling priority for transform
    Returns: a new Transform instance.
    """
    super().__init__(id)
    self.name = name
    self.description = description
    self.input_ids = input_ids
    self.operator = operator
    self.assigned_priority = assigned_priority

  def dependencies(self) -> List[str]:
    return self.input_ids

  def to_proto(self, id_map: ComponentIdToUuidMap):
    try:
      inputs = [api_pb2.Transform.Input(type=id_map[dep].type, uuid=id_map[dep].uuid) for dep in self.dependencies()]
    except KeyError as e:
      raise KeyError(f"unresolved uuid for component {e}")
    proto = api_pb2.Transform(id=self.id,
                              name=self.name,
                              description=self.description,
                              version=1,
                              inputs=inputs,
                              view=component_pb2.View(operator=self.operator))
    if self.assigned_priority is not None:
      proto.view.assigned_priority.CopyFrom(self.assigned_priority)

    return proto

  def legacy_type(self) -> str:
    return "view"

  @staticmethod
  def from_proto(proto: api_pb2.Transform, uuid_map: ComponentUuidToIdMap) -> 'Transform':
    try:
      transform = Transform(id=proto.id,
                            name=proto.name,
                            description=proto.description,
                            operator=proto.view.operator,
                            input_ids=[uuid_map[input.uuid] for input in proto.inputs])
      if proto.view.HasField("assigned_priority"):
        transform.assigned_priority = proto.view.assigned_priority
      return transform
    except KeyError as e:
      raise KeyError(f"unresolved id for component {e}")


class WriteConnector(Component):
  """A write connector"""
  def __init__(self,
               id: str,
               name: str,
               input_id: str,
               container: io_pb2.Container,
               description: str = None,
               assigned_priority: component_pb2.Priority = None,
               bytes: component_pb2.Sink.ToBytes = None,
               records: component_pb2.Sink.ToRecords = None,
               compute_configurations: List[expression_pb2.StageComputeConfiguration] = None):
    """
    Create a WriteConnector definition.

    Parameters:
    - id: identifier that is unique within Dataflow
    - name: user-friendly name
    - description: brief description
    - input_id: input component id
    - container (proto): a typed representation of the destination of data
    - assigned_priority: scheduling priority of write connector
    - bytes: defines the operator for formatting bytes written to the object store destination
    - records: indicates that the destination is a structured record store like a database
      or a data warehouse
    - compute_configurations: custom configuration overrides by stage. Currently supports the
      Write Stage for connections-type WriteConnectors
    Returns: a new WriteConnector instance.

    Note - a write connector can have either `bytes` or `records` defined, but not both.
    """
    super().__init__(id)
    self.name = name
    self.description = description
    self.input_id = input_id
    self.container = container
    self.assigned_priority = assigned_priority
    self.bytes = bytes
    self.records = records
    self.compute_configurations = compute_configurations

  def dependencies(self) -> List[str]:
    return [self.input_id]

  def to_proto(self, id_map: ComponentIdToUuidMap):
    proto = api_pb2.WriteConnector(id=self.id, name=self.name, description=self.description, version=1, sink=component_pb2.Sink(container=self.container))
    try:
      proto.inputType = id_map[self.input_id].type
      proto.inputUUID = id_map[self.input_id].uuid
    except KeyError as e:
      raise KeyError(f"unresolved uuid for component {e}")

    if self.assigned_priority is not None:
      proto.sink.assigned_priority.CopyFrom(self.assigned_priority)
    if self.bytes is not None:
      proto.sink.bytes.CopyFrom(self.bytes)
    if self.records is not None:
      proto.sink.records.CopyFrom(self.records)
    if self.compute_configurations is not None:
      proto.sink.compute_configurations.extend(self.compute_configurations)

    return proto

  def legacy_type(self) -> str:
    return "sink"

  @staticmethod
  def from_proto(proto: api_pb2.WriteConnector, uuid_map: ComponentUuidToIdMap) -> 'WriteConnector':
    try:
      wc = WriteConnector(id=proto.id, name=proto.name, description=proto.description, container=proto.sink.container, input_id=uuid_map[proto.inputUUID])
      if proto.sink.HasField("bytes"):
        wc.bytes = proto.sink.bytes
      elif proto.sink.HasField("records"):
        wc.records = proto.sink.records
      if proto.sink.HasField("assigned_priority"):
        wc.assigned_priority = proto.sink.assigned_priority
      if len(proto.sink.compute_configurations) > 0:
        wc.compute_configurations = proto.sink.compute_configurations[:]
      return wc
    except KeyError as e:
      raise KeyError(f"unresolved id for component {e}")


class DataFeed(Definition):
  """A data feed"""
  def __init__(self,
               id: str,
               name: str,
               input_id: str,
               description: str = None,
               shared_with_all: bool = False,
               data_services_shared_with: List[str] = [],
               hidden_from_host_data_service: bool = False):
    """
    Create a DataFeed definition.

    Parameters:
    - id: identifier that is unique within Dataflow
    - name: user-friendly name
    - description: brief description
    - input_id: input component id
    - shared_with_all: if set to true, this data feed is shared with all data services,
    including the host data service
    - data_services_shared_with: a list of ids of data services that we want to share
    data with (not including the host data service)
    - hidden_from_host_data_service: if set to true, the host data service cannot subscribe
    to the contents of this data feed
    Returns: a new DataFeed instance.

    Note - if `shared_with_all` is set to true, the values of `data_services_shared_with` and
    `hidden_from_host_data_service` are ignored
    """
    self.id = id
    self.name = name
    self.description = description
    self.input_id = input_id
    self.shared_with_all = shared_with_all
    self.data_services_shared_with = data_services_shared_with
    self.hidden_from_host_data_service = hidden_from_host_data_service

  def to_proto(self, host_data_service_id: str, id_map: ComponentIdToUuidMap, ds_to_role_map: Dict[str, str]):
    proto = api_pb2.DataFeed(
        id=self.id,
        name=self.name,
        description=self.description,
    )
    try:
      proto.inputType = id_map[self.input_id].type
      proto.inputUUID = id_map[self.input_id].uuid
    except KeyError as e:
      raise KeyError(f"unresolved uuid for component {e}")

    if self.shared_with_all:
      proto.open = True
      proto.pubToRoles = ""
    else:
      proto.open = False
      unique_role_ids = set([])
      try:
        for ds in self.data_services_shared_with:
          if ds in ds_to_role_map:
            unique_role_ids.add(ds_to_role_map[ds])
        if not self.hidden_from_host_data_service:
          unique_role_ids.add(ds_to_role_map[host_data_service_id])
      except KeyError as e:
        raise KeyError(f"missing role for data service {e}")
      proto.pubToRoles = ','.join(unique_role_ids)

    return proto

  def legacy_type(self) -> str:
    return "pub"

  @staticmethod
  def from_proto(proto: api_pb2.DataFeed, host_data_service: str, role_to_ds_map: Dict[str, str], uuid_map: ComponentUuidToIdMap) -> 'DataFeed':
    try:
      df = DataFeed(id=proto.id, name=proto.name, description=proto.description, input_id=uuid_map[proto.inputUUID])
      if proto.open:
        df.shared_with_all = True
      else:
        role_uuids = [r.strip() for r in proto.pubToRoles.split(",")]
        df.data_services_shared_with = [role_to_ds_map[uuid] for uuid in role_uuids if uuid in role_to_ds_map]
        if host_data_service not in df.data_services_shared_with:
          df.hidden_from_host_data_service = True
      return df
    except KeyError as e:
      raise KeyError(f"unresolved uuid for component {e}")


class DataFeedConnector(Definition):
  """A data feed connector"""
  def __init__(self, id: str, name: str, input_data_service_id: str, input_dataflow_id: str, input_data_feed_id: str, description: str = None):
    """
    Create a DataFeedConnector definition.

    Parameters:
    - id: identifier that is unique within Dataflow
    - name: user-friendly name
    - description: brief description
    - input_data_service_id: id of the DataService that the input DataFeed belongs to
    - input_dataflow_id: id of the Dataflow that the input DataFeed belongs to
    - input_data_feed_id: input DataFeed id
    Returns: a new DataFeedConnector instance.
    """
    self.id = id
    self.name = name
    self.description = description
    self.input_data_service_id = input_data_service_id
    self.input_dataflow_id = input_dataflow_id
    self.input_data_feed_id = input_data_feed_id

  def to_proto(self, data_feed_uuid: str):
    return api_pb2.DataFeedConnector(id=self.id, name=self.name, description=self.description, pubUUID=data_feed_uuid)

  def legacy_type(self) -> str:
    return "sub"


class ComponentGroup(Definition):
  """A component group"""
  def __init__(self, id: str, name: str, component_ids: List[str], description: str = None):
    """
    Create a ComponentGroup definition.

    Parameters:
    - id: identifier that is unique within Dataflow
    - name: user-friendly name
    - description: brief description
    - component_ids: list of ids of components that make up the group
    Returns: a new ComponentGroup instance.
    """
    self.id = id
    self.name = name
    self.description = description
    self.component_ids = component_ids

  def to_proto(self, id_map: ComponentIdToUuidMap):
    try:
      content = [api_pb2.ComponentGroup.Input(type=id_map[id].type, uuid=id_map[id].uuid) for id in self.component_ids]
    except KeyError as e:
      raise KeyError(f"unresolved uuid for component {e}")
    return api_pb2.ComponentGroup(id=self.id, name=self.name, description=self.description, content=content)

  @staticmethod
  def from_proto(proto: api_pb2.ComponentGroup, uuid_map: ComponentUuidToIdMap) -> 'ComponentGroup':
    try:
      return ComponentGroup(id=proto.id, name=proto.name, description=proto.description, component_ids=[uuid_map[input.uuid] for input in proto.content])
    except KeyError as e:
      raise KeyError(f"unresolved id for component {e}")


class Dataflow(Definition):
  """ A Dataflow is a representation of the operations being performed on data, expressed
  as a dependency graph. Operations are expressed declaratively via components, and are
  broadly categorized as read connectors (data ingestion), transforms (transformation),
  and write connectors. Data feeds expose the results of transforms to other dataflows
  and data services. Data feed connectors are subscriptions to data feeds. Component groups
  offer users a convenient way to organize components that have a similar purpose.
  """
  def __init__(self,
               id: str,
               name: str,
               description: str = None,
               components: List[Component] = [],
               data_feed_connectors: List[DataFeedConnector] = [],
               data_feeds: List[DataFeed] = [],
               groups: List[ComponentGroup] = []):
    """
    Create a Dataflow definition.

    Parameters
    - id: identifier for the Dataflow that is unique within its DataService
    - name: user-friendly name
    - description: brief description
    - components: list of components
    - data_feed_connectors: list of data feeds
    - data_feeds: list of data feed connectors
    - groups: list of component groups
    Returns: a new Dataflow instance.
    """
    self.id = id
    self.name = name
    self.description = description
    self.components = components
    self.data_feeds = data_feeds
    self.data_feed_connectors = data_feed_connectors
    self.groups = groups

  def to_proto(self):
    return api_pb2.Dataflow(id=self.id, name=self.name, description=self.description)


class Credential(Definition):
  """A credential"""
  def __init__(self, id: str, name: str, credential: io_pb2.Credentials):
    """
    Create a Credential definition.

    Parameters:
    - id: a uuid that is auto-generated by Ascend
    - name: user-friendly name
    - credential: the credential values
    Returns: a new Credential instance.
    """
    self.id = id
    self.name = name
    self.credential = credential

  def to_proto(self):
    try:
      return api_pb2.Credentials(credential_id=self.id, name=self.name, credential=self.credential)
    except KeyError as e:
      raise KeyError(f"unresolved id for credential {e}")

  @staticmethod
  def from_proto(proto: api_pb2.Credentials) -> 'Credential':
    try:
      return Credential(id=proto.credential_id, name=proto.name, credential=proto.credential)
    except KeyError as e:
      raise KeyError(f"unresolved id for credential {e}")


class Connection(Definition):
  """A connection"""
  def __init__(self,
               id: str,
               name: str,
               type_id: str,
               credential_id: str,
               details: Dict[str, ascend_pb2.Value],
               access_mode: Optional[connection_pb2.AccessMode] = None):
    """
    Create a Connection definition.

    Parameters:
    - id: a uuid that is auto-generated by Ascend
    - name: user-friendly name
    - type_id: the type of connection
    - credential_id: the id of the credential to use
    - details: a dictionary of the connection details
    - access_mode: read-only (default), write-only, or read-write access mode of the connection
    Returns: a new Connection instance.
    """
    self.id = id
    self.name = name
    self.type_id = type_id
    self.credential_id = credential_id
    self.details = details
    self.access_mode = access_mode

  def to_proto(self):
    try:
      return io_pb2.Connection(id=connection_pb2.Id(value=self.id),
                               name=self.name,
                               type_id=connection_pb2.Type.Id(value=self.type_id),
                               credential_id=io_pb2.Credentials.Id(value=self.credential_id) if self.credential_id else None,
                               details=self.details,
                               access_mode=self.access_mode)
    except KeyError as e:
      raise KeyError(f"unresolved id for connection {e}")

  @staticmethod
  def from_proto(proto: io_pb2.Connection) -> 'Connection':
    try:
      details = {k: proto.details[k] for k in proto.details.keys()} if hasattr(proto, "details") else None
      access_mode = proto.access_mode if proto.HasField("access_mode") else None
      return Connection(id=proto.id.value,
                        name=proto.name,
                        type_id=proto.type_id.value,
                        credential_id=proto.credential_id.value,
                        details=details,
                        access_mode=access_mode)
    except KeyError as e:
      raise KeyError(f"unresolved id for component {e}")


class DataService(Definition):
  """A DataService is the highest-level organizational structure in Ascend, and the primary
  means of controlling access. It contains one or more Dataflows and can communicate with
  other Data Services via Data Feeds.
  """
  def __init__(self,
               id: str,
               name: str,
               description: str = None,
               credentials: Optional[List[Credential]] = None,
               connections: Optional[List[Connection]] = None,
               dataflows: List[Dataflow] = []):
    """
    Create a DataService definition.

    Parameters:
    - id: DataService identifier
    - name: name
    - description: brief description
    - dataflows: list of dataflows
    Returns: a new DataService instance.
    """
    self.id = id
    self.name = name
    self.description = description
    self.credentials = credentials
    self.connections = connections
    self.dataflows = dataflows

  def to_proto(self):
    return api_pb2.DataService(id=self.id, name=self.name, description=self.description)
