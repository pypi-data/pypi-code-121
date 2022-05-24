from .. import CoreService_pb2 as pb
from .. import FeatureSetProtoApi_pb2 as FeatureSetApi
from ..schema import FeatureSchema, FeatureSchemaSpecialData, Schema


class FeatureSetSchema:
    def __init__(self, stub, feature_set):
        self._feature_set = feature_set
        self._stub = stub

    def get(self):
        return Schema.create_from(self._feature_set)

    def is_compatible_with(self, new_schema, compare_data_types=True):
        request = pb.FeatureSetSchemaCompatibilityRequest()
        request.original_schema.extend(self.get()._to_proto_schema())
        request.new_schema.extend(new_schema._to_proto_schema())
        request.compare_data_types = compare_data_types
        response = self._stub.IsFeatureSetSchemaCompatible(request)
        return response.is_compatible

    def patch_from(self, new_schema, compare_data_types=True):
        request = pb.FeatureSetSchemaPatchRequest()
        request.original_schema.extend(self.get()._to_proto_schema())
        request.new_schema.extend(new_schema._to_proto_schema())
        request.compare_data_types = compare_data_types
        response = self._stub.FeatureSetSchemaPatch(request)
        return Schema(self._create_schema_from_proto(response.schema), True)

    @staticmethod
    def _create_schema_from_proto(schema):
        create_special_data_object = lambda special_data: FeatureSchemaSpecialData(
            spi=special_data.spi,
            pci=special_data.pci,
            rpi=special_data.rpi,
            demographic=special_data.demographic,
            sensitive=special_data.sensitive,
        )
        return [
            FeatureSchema(
                feature_schema.name,
                feature_schema.data_type,
                nested_features_schema=FeatureSetSchema._create_schema_from_proto(
                    feature_schema.nested
                ),
                special_data=create_special_data_object(feature_schema.special_data),
                _feature_type=FeatureSetApi.FeatureType.Name(
                    feature_schema.feature_type
                ),
                description=feature_schema.description,
                classifier=feature_schema.classifier,
            )
            for feature_schema in schema
        ]
