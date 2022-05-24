import os
import sys
import features_algorithms
# from features_algorithms import accelerated_graph_features
from features_algorithms import vertices
import features_infra
import graph_infra
import features_meta

for path_name in [os.path.join(os.path.dirname(__file__)),
                  os.path.join(os.path.dirname(__file__), 'features_algorithms'),
                  os.path.join(os.path.dirname(__file__), 'features_algorithms', 'accelerated_graph_features'),
                  os.path.join(os.path.dirname(__file__), 'features_algorithms', 'vertices'),
                  os.path.join(os.path.dirname(__file__), 'features_infra'),
                  os.path.join(os.path.dirname(__file__), 'graph_infra'),
                  os.path.join(os.path.dirname(__file__), 'features_meta')
                  ]:
    sys.path.append(path_name)
