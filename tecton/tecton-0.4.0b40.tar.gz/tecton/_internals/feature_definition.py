from typing import Dict

from tecton._internals.fco import Fco
from tecton_proto.args.feature_view_pb2 import FeatureViewArgs
from tecton_proto.args.repo_metadata_pb2 import SourceInfo
from tecton_proto.common.id_pb2 import Id


class FeatureDefinition(Fco):
    """
    Represents the base class for Declarative FeatureViews and FeatureTables
    """

    _args: FeatureViewArgs
    _source_info: SourceInfo

    @property
    def _id(self) -> Id:
        return self._args.feature_view_id

    @property
    def name(self) -> str:
        """
        Name of this Tecton Object.
        """
        return self._args.info.name

    def __getitem__(self, features):
        from tecton.feature_services.feature_service_args import FeaturesConfig

        return FeaturesConfig(feature_view=self, namespace=self.name, features=features)

    def with_name(self, namespace: str):
        from tecton.feature_services.feature_service_args import FeaturesConfig

        return FeaturesConfig(feature_view=self).with_name(namespace)

    def with_join_key_map(self, join_key_map: Dict[str, str]):
        from tecton.feature_services.feature_service_args import FeaturesConfig

        return FeaturesConfig(feature_view=self).with_join_key_map(join_key_map)
