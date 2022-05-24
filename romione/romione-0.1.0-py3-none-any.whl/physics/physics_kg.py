from pathlib import Path
import networkx as nx
from romione.graph.node_utils import update_graph_from_yaml

self_dir = Path(__file__).parent

physics_kg = nx.DiGraph()
for kg_file in self_dir.glob("*.yml"):
	physics_kg = update_graph_from_yaml(
		physics_kg, kg_file, symbols_key="Symbols", eqns_key="Equations"
	)