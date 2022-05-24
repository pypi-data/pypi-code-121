import abc
import os
from typing import Dict, List, Optional, Tuple

import jinja2
import yaml
from google.protobuf.json_format import MessageToDict, ParseDict

from ascend.sdk import definitions
import ascend.sdk.drd.jinja as jinja
from ascend.protos.resource import resource_pb2

ROOT_PATH = (None, None, None)
API_VERSION = 6

ResourcePath = Tuple[str, str, str]


class ResourceDefinition:
  def __init__(self, resource, resource_type, resource_id):
    self.resource = MessageToDict(resource)
    self.rd = self.resource[resource_type]
    self.resource_name = coalesce(self.resource.get('name'), self.rd.get('name'))
    self.resource_desc = coalesce(self.resource.get('description'), self.rd.get('description'))
    self.resource_id = coalesce(resource_id, self.resource.get('id'), self.rd.get('id'))
    if self.resource_id is None:
      raise ValueError(f"Illegal resource, missing id: {self.resource}")
    self.exportable = True

  @property
  def path(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    raise NotImplementedError(self)

  @property
  def name(self):
    return self.rd.get('name') or self.resource.get('name')

  @property
  def description(self):
    return self.resource.get('description') or self.rd.get('description', '')

  def dependencies(self):
    raise NotImplementedError(self)

  def to_definition(self):
    raise NotImplementedError(self)

  def delete_deps(self):
    return []

  def dependees(self):
    return []

  @staticmethod
  def from_resource_proto(m: resource_pb2.Resource, override_path=(None, None, None)) -> 'ResourceDefinition':  # noqa
    if m.version > API_VERSION:
      raise ValueError(f'Version out of date (found {m.version}, ' f'running {API_VERSION})')
    # sh.debug(m)
    t = m.WhichOneof('type')
    typed_resource = getattr(m, t)
    if isinstance(typed_resource, resource_pb2.DataService):
      resource = DataServiceDef(m, override_path)
    elif isinstance(typed_resource, resource_pb2.Dataflow):
      resource = DataflowDef(m, override_path)
    elif isinstance(typed_resource, resource_pb2.Component):
      resource = ComponentDef(m, override_path)
    elif isinstance(typed_resource, resource_pb2.Group):
      resource = GroupDef(m, override_path)
    elif isinstance(typed_resource, resource_pb2.DataFeed):
      resource = DataFeedDef(m, override_path)
    else:
      raise KeyError(f"Unrecognizable resource {m}")
    return resource

  def list(self):
    pass

  def delete(self):
    pass

  def contained(self) -> List['ResourceDefinition']:
    return []

  def __repr__(self):
    return f'<{type(self)}>: {self.resource_id}'


class ComponentDetailsDef(abc.ABC):
  def __init__(self, rd, comp_def):
    self.rd = rd
    self.comp_def = comp_def

  def input_ids(self):
    return []

  @property
  @abc.abstractmethod
  def api_type(self):
    pass


class ReadConnectorDef(ComponentDetailsDef):
  def api_type(self):
    return 'source'

  def to_definition(self):
    proto = resource_pb2.ReadConnector()
    ParseDict(self.rd, proto)

    rc = definitions.ReadConnector(id=self.comp_def.resource_id,
                                   name=self.comp_def.resource_name,
                                   description=self.comp_def.resource_desc,
                                   container=proto.container)
    if proto.HasField("bytes"):
      rc.bytes = proto.bytes
    elif proto.HasField("records"):
      rc.records = proto.records
    if proto.HasField("pattern"):
      rc.pattern = proto.pattern
    if proto.HasField("updatePeriodical"):
      rc.update_periodical = proto.updatePeriodical
    if proto.HasField("last_manual_refresh_time"):
      rc.last_manual_refresh_time = proto.last_manual_refresh_time
    if proto.HasField("assigned_priority"):
      rc.assigned_priority = proto.assigned_priority
    if proto.HasField("aggregation_limit"):
      rc.aggregation_limit = proto.aggregation_limit

    return rc


class TransformDef(ComponentDetailsDef):
  def input_ids(self):
    return self.rd['inputIds']

  def api_type(self):
    return 'view'

  def to_definition(self):
    proto = resource_pb2.Transform()
    ParseDict(self.rd, proto)

    t = definitions.Transform(id=self.comp_def.resource_id,
                              name=self.comp_def.resource_name,
                              description=self.comp_def.resource_desc,
                              operator=proto.operator,
                              input_ids=self.input_ids())
    if proto.HasField("assigned_priority"):
      t.assigned_priority = proto.assigned_priority

    return t


class WriteConnectorDef(ComponentDetailsDef):
  def input_ids(self):
    return [self.rd['inputId']]

  def api_type(self):
    return 'sink'

  def to_definition(self):
    proto = resource_pb2.WriteConnector()
    ParseDict(self.rd, proto)

    wc = definitions.WriteConnector(id=self.comp_def.resource_id,
                                    name=self.comp_def.resource_name,
                                    description=self.comp_def.resource_desc,
                                    container=proto.container,
                                    input_id=self.input_ids()[0])
    if proto.HasField("bytes"):
      wc.bytes = proto.bytes
    elif proto.HasField("records"):
      wc.records = proto.records
    if proto.HasField("assigned_priority"):
      wc.assigned_priority = proto.assigned_priority
    return wc


class DataFeedDef(ResourceDefinition):
  def __init__(self, resource: resource_pb2.Resource, override_path):
    self.data_service_id, resource_id, _ = override_path
    super().__init__(resource, 'dataFeed', resource_id)
    self.dataflow_id, self.input_id = self.rd['inputId'].split('.')
    self.exportable = False

  @property
  def path(self):
    return (self.data_service_id, self.resource_id, None)

  def dependees(self):
    if self.rd.get('groupId') is not None:
      return [(self.data_service_id, self.dataflow_id, self.rd['groupId'])]
    else:
      return []

  def dependencies(self):
    return [(self.data_service_id, self.dataflow_id, self.input_id)]

  def api_type(self):
    return 'pub'


class GroupDef(ResourceDefinition):
  def __init__(self, resource: resource_pb2.Resource, override_path):
    self.data_service_id, self.dataflow_id, resource_id = override_path
    super().__init__(resource, 'group', resource_id)
    self.exportable = False

  @property
  def api_type(self):
    return 'group'

  def to_definition(self):
    return definitions.ComponentGroup(id=self.resource_id, name=self.resource_name, description=self.resource_desc, component_ids=[])

  def dependencies(self):
    return [(self.data_service_id, self.dataflow_id, None)]

  @property
  def path(self):
    return (self.data_service_id, self.dataflow_id, self.resource_id)

  @property
  def api_path(self):
    return '/'.join([self.data_service_id, self.dataflow_id, self.api_type, self.resource_id])


class ComponentDef(ResourceDefinition):
  TYPES = {
      'readConnector': ReadConnectorDef,
      'transform': TransformDef,
      'writeConnector': WriteConnectorDef,
  }

  def __init__(self, resource: resource_pb2.Resource, override_path):
    self.data_service_id, self.dataflow_id, resource_id = override_path
    super().__init__(resource, 'component', resource_id)
    self.type, = filter(lambda t: t in self.rd, ComponentDef.TYPES)
    self.details = ComponentDef.TYPES[self.type](self.rd[self.type], self)

  def dependees(self):
    if self.rd.get('groupId') is not None:
      return [(self.data_service_id, self.dataflow_id, self.rd['groupId'])]
    else:
      return []

  @property
  def path(self):
    return (self.data_service_id, self.dataflow_id, self.resource_id)

  @property
  def api_path(self):
    return '/'.join([self.data_service_id, self.dataflow_id, self.details.api_type, self.resource_id])

  def dependencies(self):
    inputs = []
    for input_id in self.details.input_ids():
      pieces = input_id.split('.')
      if len(pieces) == 2:
        # data feed reference
        inputs.append((*pieces, None))
      elif len(pieces) == 1:
        # normal
        inputs.append((self.data_service_id, self.dataflow_id, pieces[0]))
      else:
        raise Exception(f'Invalid id format: {input_id} for {self.resource_id}')
    return inputs + [(self.data_service_id, None, None), (self.data_service_id, self.dataflow_id, None)]

  def delete_deps(self):
    return self.dependencies()


class DataflowDef(ResourceDefinition):
  def __init__(self, resource: dict, override_path):
    self.data_service_id, resource_id, _ = override_path
    super().__init__(resource, 'dataflow', resource_id)

  def to_definition(self) -> definitions.Dataflow:
    return definitions.Dataflow(id=self.resource_id, name=self.resource_name, description=self.resource_desc)

  @property
  def path(self):
    return (self.data_service_id, self.resource_id, None)

  def delete_deps(self):
    result = set()
    for comp_rd in self.rd.get('components', []):
      m = resource_pb2.Resource()
      d = {'component': comp_rd}
      ParseDict(d, m)
      component = ResourceDefinition.from_resource_proto(m, self.path)
      result |= set(component.dependencies())
    return list(result - set([(self.data_service_id, self.resource_id, None)]))

  def contained(self):
    res_defs = []
    for component in self.rd.get('components', []):
      m = resource_pb2.Resource()
      d = {'component': component}
      ParseDict(d, m)
      res_defs.append(ResourceDefinition.from_resource_proto(m, self.path))
    for group in self.rd.get('groups', []):
      m = resource_pb2.Resource()
      d = {'group': group}
      ParseDict(d, m)
      res_defs.append(ResourceDefinition.from_resource_proto(m, self.path))
    return res_defs

  def dependencies(self):
    return [(self.data_service_id, None, None)]


class DataServiceDef(ResourceDefinition):
  def __init__(self, resource: dict, override_path):
    resource_id, _, _ = override_path
    super().__init__(resource, 'dataService', resource_id)

  def to_definition(self) -> definitions.DataService:
    return definitions.DataService(id=self.resource_id, name=self.resource_name, description=self.resource_desc)

  @property
  def path(self):
    return (self.resource_id, None, None)

  def dependencies(self):
    return []

  def delete_deps(self):
    result = set()
    for df_rd in self.rd.get('dataFeeds', []):
      m = resource_pb2.Resource()
      d = {'dataFeed': df_rd}
      ParseDict(d, m)
      data_feed = ResourceDefinition.from_resource_proto(m, self.path)
      result.add((data_feed.data_service_id, None, None))
    return list(result - set([(self.resource_id, None, None)]))

  def contained(self):
    res_defs = []
    for dataflow in self.rd.get('dataflows', []):
      m = resource_pb2.Resource()
      d = {'dataflow': dataflow}
      ParseDict(d, m)
      res_defs.append(ResourceDefinition.from_resource_proto(m, self.path))
    for data_feed in self.rd.get('dataFeeds', []):
      m = resource_pb2.Resource()
      d = {'dataFeed': data_feed}
      ParseDict(d, m)
      res_defs.append(ResourceDefinition.from_resource_proto(m, self.path))
    return res_defs


def extend_rd(rd_path, child):
  if rd_path[0] is None:
    return (child, None, None)
  elif rd_path[1] is None:
    return (rd_path[0], child, None)
  elif rd_path[2] is None:
    return (rd_path[0], rd_path[1], child)
  else:
    raise ValueError(f"No child possible for {rd_path}")


def resource_path_for(path: str) -> ResourcePath:
  if path == '.':
    return ROOT_PATH
  else:
    rd_pref = path.split('.')
    fill = tuple(None for _ in range(3 - len(rd_pref)))
    rd_path = (*rd_pref, *fill)
    return rd_path


class LoadOpts:
  def __init__(self, input: str, config: dict = {}, recursive=True):
    self.input = input
    self.recursive = recursive
    self.config = config


class ResourceDefinitionLoader:
  def __init__(self):
    pass

  def load_defs(self, rd_path, options: LoadOpts) -> 'ResourceDefinitions':
    return ResourceDefinitions(self._load_defs_recur(options.input, options.input, rd_path, options))

  def _load_defs_recur(self, origin, path, rd_path, options) -> Dict[ResourcePath, ResourceDefinition]:
    path_to_def: Dict[ResourcePath, ResourceDefinition] = {}
    p = path
    if os.path.isdir(path):
      p = os.path.join(path, '__metadata__.yaml')
      if not os.path.exists(p):
        if origin == path:
          raise ValueError(f"Path {p} does not exist!")
        else:
          # if we are not at the top level, we will skip
          # directories missing a metadata file
          return {}
    _, ext = os.path.splitext(p)
    if ext != '.yaml':
      # only load yaml files
      if origin == path:
        raise ValueError(f"Resource definitions must be yaml files (found {p})")
      return {}
    ascend_dir, _ = os.path.split(p)
    try:
      with open(p, 'r') as f:
        raw_template = f.read()
      env = jinja.setup_jinja_env(loader=jinja2.FileSystemLoader(ascend_dir))
      data = env.from_string(raw_template).render(config=options.config, resourceParentDirectory=ascend_dir)
      res_proto = resource_pb2.Resource()
      d = yaml.load(data, Loader=yaml.SafeLoader)
      ParseDict(d, res_proto)
    except Exception as e:
      raise Exception(f"Unable to load resource definition from {p}") from e
    res_def = ResourceDefinition.from_resource_proto(res_proto, rd_path)
    path_to_def[res_def.path] = res_def
    if options.recursive:
      path_to_def.update(self._load_contained_defs(res_def))
      if os.path.isdir(path):
        child_paths = os.listdir(path)
        for child_path in child_paths:
          if child_path == '__metadata__.yaml':
            continue
          name, _ = os.path.splitext(child_path)
          path_to_def.update(self._load_defs_recur(origin, os.path.join(path, child_path), extend_rd(rd_path, name), options))

    return path_to_def

  def _load_contained_defs(self, res_def) -> Dict[ResourcePath, ResourceDefinition]:
    path_to_def: Dict[ResourcePath, ResourceDefinition] = {}
    contained = res_def.contained()
    if len(contained) > 0:
      for c in contained:
        path_to_def[c.path] = c
        path_to_def.update(self._load_contained_defs(c))
    return path_to_def


class ResourceDefinitions:
  def __init__(self, path_to_def: Dict[ResourcePath, ResourceDefinition] = {}):
    self.path_to_def = path_to_def

  def update(self, path_to_def: Dict[ResourcePath, ResourceDefinition]):
    self.path_to_def.update(path_to_def)

  def to_dataflow_definitions(self) -> List[definitions.Dataflow]:
    """
    Convert a set of dataflow resource definitions (DRD) to Dataflow definitions.
    It is assumed that all of the Dataflows belong to a *single* DataService.
    :return: list of Dataflow definitions
    """
    dataflows = []
    for path, rd in self.path_to_def.items():
      if isinstance(rd, DataflowDef):
        dataflow = rd.to_definition()
        groups = {child.resource_id: child.to_definition() for child in self._children(path, rd) if isinstance(child, GroupDef)}
        components = []
        for child in self._children(path, rd):
          if isinstance(child, ComponentDef):
            components.append(child.details.to_definition())
            if child.rd.get('groupId'):
              groups[child.rd.get('groupId')].component_ids.append(child.resource_id)

        dataflow.components = components
        dataflow.groups = list(groups.values())

        dataflows.append(dataflow)

    return dataflows

  def _children(self, rd_path: ResourcePath, resource_def: ResourceDefinition):
    if rd_path == ROOT_PATH:

      def ds_child(child_rd_path):
        return (child_rd_path[0] is not None and child_rd_path[1] is None and child_rd_path[2] is None)  # noqa W503

      return [rd for path, rd in self.path_to_def.items() if ds_child(path)]
    elif isinstance(resource_def, DataServiceDef):

      def df_child(child_rd_path):
        return (child_rd_path[0] == rd_path[0] and child_rd_path[1] is not None and child_rd_path[2] is None)  # noqa W503

      return [rd for path, rd in self.path_to_def.items() if df_child(path)]
    elif isinstance(resource_def, DataflowDef):

      def res_child(child_rd_path):
        return (child_rd_path[0] == rd_path[0] and child_rd_path[1] == rd_path[1] and child_rd_path[2] is not None)  # noqa W503

      return [rd for path, rd in self.path_to_def.items() if res_child(path)]
    else:
      return []


def flatten(ll):
  return [e for lx in ll for e in lx]


def filter_none(lst):
  return list(filter(lambda v: v is not None, lst))


def compose(f, g):
  return lambda x: f(g(x))


def coalesce(*lst):
  return next(filter(lambda e: e is not None, lst), None)
