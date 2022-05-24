class Recommendation:
    def __init__(self, stub, source_feature_set, match_result):
        from .feature_set import FeatureSet  # To avoid circular import reference

        self._source = source_feature_set
        self._target = FeatureSet(stub, match_result.target_feature_set)
        self._joins = {join.classifier: join.columns for join in match_result.joins}

    def __repr__(self):
        return str(
            {
                "source": {
                    "project_name": self._source.project,
                    "feature_set_name": self._source.feature_set_name,
                },
                "target": {
                    "project_name": self._target.project,
                    "feature_set_name": self._target.feature_set_name,
                },
                "joins": self._joins,
            }
        )
