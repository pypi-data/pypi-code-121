from abc import abstractmethod, ABC
from typing import List, Mapping, Union

import networkx as nx
import pandas as pd

import log_datasets.datasets
from utils.window_utils import TumblingWindowCreator, SlidingWindowCreator, WindowsCreator


# from log_datasets.datasets import NovaDataset


class GraphCreator(ABC):
    def __init__(self, logs: pd.DataFrame, templates: pd.DataFrame, include_last: bool, include_all_event_ids: bool):
        self.logs = logs
        self.templates = templates
        self.include_last = include_last
        self.include_all_event_ids = include_all_event_ids

    @abstractmethod
    def create_graphs(self) -> List[Mapping[str, Union[str, Mapping[str, Mapping[str, float]]]]]:
        pass

    @abstractmethod
    def get_window_creator(self) -> WindowsCreator:
        pass


class GraphFromTimeWindowCreator(GraphCreator, ABC):
    def __init__(self, logs: pd.DataFrame, templates: pd.DataFrame, include_last: bool, include_all_event_ids: bool,
                 window_size: int):
        GraphCreator.__init__(self, logs, templates, include_last, include_all_event_ids)
        self.window_size = window_size

    def create_graphs(self) -> List[Mapping[str, Union[str, Mapping[str, Mapping[str, float]]]]]:
        windows = self.get_window_creator().create_windows()
        windows['event_ids'] = windows.apply(lambda window: get_events_ids_for_window(self.logs, window), axis=1)
        result = []
        for index, row in windows.iterrows():
            # Hack fix, think of a better one later
            r = [] if pd.isnull(row['event_ids']) else row['event_ids'].split(',')
            result.append({
                'start': str(row['start']),
                'end': str(row['end']),
                'graph_dict': create_graph_as_dict(
                    event_ids=r,
                    include_last=self.include_last,
                    all_event_ids=list(self.templates['EventId']) if self.include_all_event_ids else []),
                'positional_embeddings': create_position_embeddings(r, self.include_last)
            })

        return result


class GraphFromTumblingWindowCreator(GraphFromTimeWindowCreator):
    def __init__(self, logs: pd.DataFrame, templates: pd.DataFrame, include_last: bool, include_all_event_ids: bool,
                 window_size: int):
        GraphFromTimeWindowCreator.__init__(self, logs, templates, include_last, include_all_event_ids, window_size)

    def get_window_creator(self) -> WindowsCreator:
        return TumblingWindowCreator(
            min_timestamp=self.logs['timestamp'].min(),
            max_timestamp=self.logs['timestamp'].max(),
            size=self.window_size
        )


class GraphFromSlidingWindowCreator(GraphFromTimeWindowCreator):
    def __init__(self, logs: pd.DataFrame, templates: pd.DataFrame, include_last: bool, include_all_event_ids: bool,
                 window_size: int, window_slide: int):
        GraphFromTimeWindowCreator.__init__(self, logs, templates, include_last, include_all_event_ids, window_size)
        self.window_slide = window_slide

    def get_window_creator(self) -> WindowsCreator:
        return SlidingWindowCreator(
            min_timestamp=self.logs['timestamp'].min(),
            max_timestamp=self.logs['timestamp'].max(),
            size=self.window_size,
            slide=self.window_slide
        )


class GraphFromSessionWindowCreator(GraphCreator):
    def __init__(self, logs: pd.DataFrame, templates: pd.DataFrame, include_last: bool, include_all_event_ids: bool):
        GraphCreator.__init__(self, logs, templates, include_last, include_all_event_ids)

    def create_graphs(self) -> List[Mapping[str, Union[str, Mapping[str, Mapping[str, float]]]]]:
        windows_df = self.logs[['session_id', 'event_id']]
        windows_df['event_ids'] = windows_df.groupby('session_id')['event_id'].transform(lambda x: ','.join(x))
        windows_df = windows_df[['session_id', 'event_ids']].drop_duplicates()
        print(windows_df.head())
        result = []
        for index, row in windows_df.iterrows():
            # Hack fix, think of a better one later
            r = [] if pd.isnull(row['event_ids']) else row['event_ids'].split(',')
            result.append({
                'session_id': row['session_id'],
                'graph_dict': create_graph_as_dict(
                    event_ids=r,
                    include_last=self.include_last,
                    all_event_ids=list(self.templates['EventId']) if self.include_all_event_ids else []
                ),
                'positional_embeddings': create_position_embeddings(r, self.include_last)
            })

        return result

    def get_window_creator(self) -> WindowsCreator:
        pass


def get_events_ids_for_window(logs_df, window):
    return ",".join(list(logs_df[
                             (logs_df['timestamp'] >= window['start'])
                             & (logs_df['timestamp'] < window['end'])
                             ]['event_id']))


def create_graph_as_dict(event_ids: list, include_last: bool, all_event_ids=None) -> dict:
    """
    Method that creates a graph represented as a dictionary based on the occurrences of event ids in a window/session
    :param all_event_ids:
    :param include_last: A bool value that represents whether the last event ID should be included in the graph generation
    :param event_ids: List of the event ids extracted from the logs that occurred in a given window/session
    :return: A dictionary for representation of the graph (nodes and edges),
    where the key is a source node in the graph, and the value is another dictionary where the key
    is the destination node, and the value is the weight of the edge.
    Example: {"A": {"B": 5}} means that the graph has two nodes A,B and there is a directed edge from A to B with weight 5.
    """
    if all_event_ids is None:
        all_event_ids = list()
    graph_dict = {}
    end = len(event_ids) - 1 if include_last else len(event_ids) - 2
    for i in range(end):
        node1 = event_ids[i]
        node2 = event_ids[i + 1]
        if node1 in graph_dict:
            edge_dict = graph_dict[node1]
            if node2 in edge_dict:
                edge_dict[node2] = edge_dict[node2] + 1
            else:
                edge_dict[node2] = 1
        else:
            graph_dict[node1] = dict()
            graph_dict[node1][node2] = 1
    # Add the template event IDs that were not found in window in the graph as nodes without connections
    for event_id in all_event_ids:
        if event_id not in event_ids:
            graph_dict[event_id] = {}
    return normalize_weights(graph_dict)


def create_position_embeddings(event_ids: list, include_last: bool) -> dict:
    """
    Method that creates the position embeddings for the event_ids. The position embeddings represent numerical information
    for the order of occurrence of the event IDs in a log sequence (session). The last event_id detected in the session
    has embedding of 1 and the first event_id in the sequence has the embedding N where N is the count of unique event
    IDs in the sequence
    :param event_ids: List of the event ids extracted from the logs that occurred in a given window/session
    :param include_last: A bool value that represents whether the last event ID should be included in the graph generation
    :return: dictionary where the keys are the event IDs and the values are the corresponding position embeddings for
    the key
    """
    end = len(event_ids) if include_last else len(event_ids) - 1
    embeddings = {event_id: 0 for event_id in event_ids[:end]}
    counter = 1
    for event_id in reversed(event_ids[:end]):
        if embeddings[event_id] == 0:
            embeddings[event_id] = counter
        counter += 1
    normalize_positional_embeddings(embeddings)
    return embeddings


def create_networkx_graph(graph_dict: dict, positional_embeddings: dict, anomalous_logs: list):
    nodes = set()
    edges_list = []
    graph = nx.DiGraph()
    for start, edges in graph_dict.items():
        nodes.add(start)
        for end, weight in edges.items():
            nodes.add(end)
            edges_list.append((start, end, {"weight": [weight]}))
    for node in nodes:
        attributes = {'name': node}
        if len(positional_embeddings) > 0:
            attributes['x'] = [positional_embeddings.get(node, -1)]
        if len(anomalous_logs) > 0:
            attributes['y'] = 1 if node in anomalous_logs else 0
        graph.add_node(node, **attributes)
    graph.add_edges_from(edges_list)
    return graph


def nx2pyvis(nx_graph, pyvisnet, default_node_size=1, default_edge_weight=1):
    edges = nx_graph.edges(data=True)
    nodes = nx_graph.nodes(data=True)

    if len(edges) > 0:
        for e in edges:
            if 'size' not in nodes[e[0]].keys():
                nodes[e[0]]['size'] = default_node_size
            nodes[e[0]]['size'] = int(nodes[e[0]]['size'])
            if 'size' not in nodes[e[1]].keys():
                nodes[e[1]]['size'] = default_node_size
            nodes[e[1]]['size'] = int(nodes[e[1]]['size'])
            pyvisnet.add_node(e[0], **nodes[e[0]], title="Hi")
            pyvisnet.add_node(e[1], **nodes[e[1]], title="Hi")

            if 'weight' not in e[2].keys():
                e[2]['weight'] = default_edge_weight
            # e[2]['weight'] = e[2]['weight']
            edge_dict = e[2]
            edge_dict["value"] = edge_dict.pop("weight")
            pyvisnet.add_edge(e[0], e[1], **edge_dict)

    for node in nx.isolates(nx_graph):
        if 'size' not in nodes[node].keys():
            nodes[node]['size'] = default_node_size
        pyvisnet.add_node(node, **nodes[node], title="Hi")

    return pyvisnet


def normalize_weights(graph: dict) -> dict:
    sum = 0
    for start, edges in graph.items():
        for end, weight in edges.items():
            sum += weight

    for start, edges in graph.items():
        for end, weight in edges.items():
            graph[start][end] /= sum

    return graph


def normalize_positional_embeddings(embeddings: dict):
    minn = 1
    maxx = max(embeddings.values())
    for node, position in embeddings.items():
        embeddings[node] = (position - minn) / (maxx - minn)


if __name__ == '__main__':
    nova_dataset = log_datasets.datasets.NovaDataset("../../data")
    nova_dataset.initialize_dataset()
    networkx_graphs = nova_dataset.create_networkx_graphs(window_type="sliding", window_size=60000, window_slide=3000,
                                                          test_id=2, include_last=True, include_all_event_ids=False,
                                                          include_positional_embeddings=True)

    for graph in networkx_graphs:
        print(graph.nodes.data(), graph.edges.data())
    # graph_dicts = nova_dataset.create_graphs(window_type="sliding", window_size=60000, window_slide=3000, test_id=1,
    #                                          include_last=True, include_all_event_ids=True)
    # for graph_dict in graph_dicts:
    #     print(graph_dict)
    # # print(create_graph_as_dict("A,B,C,B,C,A,D".split(","), False, list()))
    # # print(create_position_embeddings("A,B,C,B,C,A,D".split(","), False))

    # logs = "A,B,C,B,C,A,D".split(",")
    # graph_dict = create_graph_as_dict(logs, True)
    # positional_embeddings = create_position_embeddings(logs, True)
    # print(graph_dict)
    # print(positional_embeddings)
    # networkx_graph = create_networkx_graph(graph_dict, positional_embeddings)
    # print(networkx_graph.nodes)
    # print(networkx_graph.nodes.data())
