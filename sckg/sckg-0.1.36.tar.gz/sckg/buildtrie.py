import pygtrie as pygtrie

from kgdt.models.graph import GraphData
from kgdt.utils import SaveLoad
from tqdm import tqdm


class Buildtrim(SaveLoad):
    def __init__(self):
        self.tree = pygtrie.CharTrie()

    def build_trim(self, graph_path):
        graph: GraphData = GraphData.load(graph_path)
        for node_id in tqdm(graph.get_node_ids()):
            node = graph.get_node_info_dict(node_id)
            concept = node['properties']['concept_name']
            self.tree[concept] = node_id







