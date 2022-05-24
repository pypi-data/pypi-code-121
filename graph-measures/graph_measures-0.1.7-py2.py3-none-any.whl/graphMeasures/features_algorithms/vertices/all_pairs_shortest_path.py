import networkx as nx
import numpy as np

from features_infra.feature_calculators import NodeFeatureCalculator, FeatureMeta


class AllPairsShortestPathCalculator(NodeFeatureCalculator):
    def __init__(self, *args, **kwargs):
        super(AllPairsShortestPathCalculator, self).__init__(*args, **kwargs)

    def _calculate(self, include: set):
        features = dict(nx.algorithms.shortest_paths.unweighted.all_pairs_shortest_path(self._gnx))
        max_deg = max([a for i in features for a in features[i]]) + 1
        self._features = np.zeros((len(self._gnx.nodes), max_deg))
        for node in features:
            for deg in features[node]:
                self._features[node][deg] = features[node][deg]

    def is_relevant(self):
        # currently set to False
        return False
        # return True


feature_entry = {
    "all_pairs_shortest_path": FeatureMeta(AllPairsShortestPathCalculator, {"all_pairs_shortest_path"}),
}


if __name__ == "__main__":
    from measure_tests.specific_feature_test import test_specific_feature
    test_specific_feature(AllPairsShortestPathCalculator, is_max_connected=True)