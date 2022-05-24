import networkx as nx
from typing import Dict, List

from ascend.sdk.definitions import Component, Dataflow


def _component_id_map_from_list(components: List[Component]) -> Dict[str, Component]:
  id_to_component: Dict[str, Component] = {}
  for component in components:
    if not component.id:
      raise ValueError("empty component id")
    elif component.id in id_to_component:
      raise ValueError(f"duplicate component id {component.id} in component list")
    else:
      id_to_component[component.id] = component
  return id_to_component


def components_ordered_by_dependency(components: List[Component]) -> List[Component]:
  id_to_component = _component_id_map_from_list(components)

  g = nx.DiGraph()
  for component in components:
    g.add_node(component.id)
    for dep in component.dependencies():
      # A data feed connector will not be in the component list.
      if dep in id_to_component:
        g.add_edge(component.id, dep)

  return [id_to_component[component_id] for component_id in reversed(list(nx.topological_sort(g)))]


def dataflows_ordered_by_dependency(data_service_id: str, dataflows: List[Dataflow]) -> List[Dataflow]:
  g = nx.DiGraph()
  for dataflow in dataflows:
    g.add_node(dataflow.id)
    for data_feed_connector in dataflow.data_feed_connectors:
      if data_feed_connector.input_data_service_id == data_service_id:
        g.add_edge(dataflow.id, data_feed_connector.input_dataflow_id)

  id_to_dataflow = {dataflow.id: dataflow for dataflow in dataflows}
  return [id_to_dataflow[df_id] for df_id in reversed(list(nx.topological_sort(g)))]
