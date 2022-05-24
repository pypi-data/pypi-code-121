from featurestore.core.schema import FeatureSchema, Schema

from .base_job import BaseJob


class ExtractSchemaJob(BaseJob):
    def _response_method(self, job_id):
        response = self._stub.GetExtractSchemaJobOutput(job_id)
        return Schema(
            ExtractSchemaJob._features_schema_from_proto(response.schema), True
        )

    @staticmethod
    def _features_schema_from_proto(schema):
        return [
            FeatureSchema(
                feature_schema.name,
                feature_schema.data_type,
                nested_features_schema=ExtractSchemaJob._features_schema_from_proto(
                    feature_schema.nested
                ),
            )
            for feature_schema in schema
        ]
