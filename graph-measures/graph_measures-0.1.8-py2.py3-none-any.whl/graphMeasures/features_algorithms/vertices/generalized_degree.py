import networkx as nx
import numpy as np

from features_infra.feature_calculators import NodeFeatureCalculator, FeatureMeta


class GeneralizedDegreeCalculator(NodeFeatureCalculator):
    def __init__(self, *args, **kwargs):
        super(GeneralizedDegreeCalculator, self).__init__(*args, **kwargs)

    def _calculate(self, include: set):
        features = nx.algorithms.cluster.generalized_degree(self._gnx)
        max_deg = max([a for i in features for a in features[i]]) + 1
        self._features = np.zeros((len(self._gnx.nodes), max_deg))
        for node in features:
            for deg in features[node]:
                self._features[node][deg] = features[node][deg]

    def is_relevant(self):
        # Networkx raises a NetworkXNotImplemented exception for directed graphs.
        return not self._gnx.is_directed()


feature_entry = {
    "generalized_degree": FeatureMeta(GeneralizedDegreeCalculator, {"generalized_degree"}),
}


if __name__ == "__main__":
    from measure_tests.specific_feature_test import test_specific_feature
    test_specific_feature(GeneralizedDegreeCalculator, is_max_connected=True)