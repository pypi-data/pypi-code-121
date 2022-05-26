import networkx as nx
import numpy as np

from features_infra.feature_calculators import NodeFeatureCalculator, FeatureMeta


class AllPairsShortestPathLengthCalculator(NodeFeatureCalculator):
    def __init__(self, *args, **kwargs):
        super(AllPairsShortestPathLengthCalculator, self).__init__(*args, **kwargs)

    def _calculate(self, include: set):
        features = dict(nx.algorithms.shortest_paths.unweighted.all_pairs_shortest_path_length(self._gnx))
        max_deg = max([a for i in features for a in features[i]]) + 1
        self._features = np.zeros((len(self._gnx.nodes), max_deg))
        for node in features:
            for deg in features[node]:
                self._features[node][deg] = features[node][deg]

    def is_relevant(self):
        return True


feature_entry = {
    "all_pairs_shortest_path_length": FeatureMeta(AllPairsShortestPathLengthCalculator, {"all_pairs_shortest_path_length"}),
}


if __name__ == "__main__":
    from measure_tests.specific_feature_test import test_specific_feature
    test_specific_feature(AllPairsShortestPathLengthCalculator, is_max_connected=True)