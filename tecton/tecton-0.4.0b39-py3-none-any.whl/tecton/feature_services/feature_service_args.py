from typing import Dict
from typing import List
from typing import Optional

from tecton._internals.feature_definition import FeatureDefinition


class FeaturesConfig(object):
    """
    Configuration used to specify a list of features.

    By default, you can add all of the features in a FeatureView/FeatureTable to a FeatureService by passing
    the FeatureView/FeatureTable into the ``features`` parameter of a FeatureService.
    However, if you want to specify a subset, you can use this class.

    You can use the double-bracket notation ``my_feature_view[[<features>]]``
    as a short-hand for generating a FeaturesConfig from a FeatureView. This is the preferred way to select a subset of
    of the features contained in a FeatureView. As an example:

    .. highlight:: python
    .. code-block:: python

       from tecton.compat import FeatureService
       from feature_repo.features import my_feature_view_1, my_feature_view_2

       my_feature_service = FeatureService(
           name='my_feature_service',
           features=[
               # Add all features from my_feature_view_1 to this FeatureService
               my_feature_view_1,
               # Add a single feature from my_feature_view_2, 'my_feature'
               my_feature_view_2[['my_feature']]
           ]
       )

    :param namespace: (Optional) A namespace used to prefix the features joined from this FeatureView.
        By default, namespace is set to the FeatureView name.
    :param features: The subset of features to select from the FeatureView.
    :param override_join_keys: (advanced) map of spine join key to feature view join key overrides.
    :param feature_view: The Feature View.
    """

    def __init__(
        self,
        *,
        feature_view: FeatureDefinition,
        namespace: str = None,
        features: Optional[List[str]] = None,
        override_join_keys: Optional[Dict[str, str]] = None,
    ):
        self._fv = feature_view
        assert self._fv is not None, "The `feature_view` field must be set."
        self.namespace = namespace or self._fv.name
        self.features = features
        self.override_join_keys = override_join_keys
        self.id = self._fv._id

    def with_name(self, namespace: str) -> "FeaturesConfig":
        self.namespace = namespace
        return self

    def with_join_key_map(self, join_key_map: Dict[str, str]) -> "FeaturesConfig":
        # As of FWV5, we map from spine key to feature view key. For backwards compatibility with FWV3,
        # self.override_join_keys is a map from feature view key to spine key. So we need to flip the input dict.
        self.override_join_keys = {v: k for k, v in join_key_map.items()}
        return self
