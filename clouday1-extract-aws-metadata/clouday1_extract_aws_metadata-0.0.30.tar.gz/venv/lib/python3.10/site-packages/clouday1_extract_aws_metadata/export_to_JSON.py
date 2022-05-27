import os
import json


def export_to_JSON(cytoscape_node_data, cytoscape_edge_data):
    filtered_cytoscape_data = []
    filtered_cytoscape_data.append(cytoscape_node_data)
    filtered_cytoscape_data.append(cytoscape_edge_data)
    script_dir = os.path.dirname('.')
    file_path_write = os.path.join(
        script_dir, 'data/data.json')
    with open(file_path_write, 'w') as outfile:
        outfile.write(json.dumps(filtered_cytoscape_data))
        outfile.close()
