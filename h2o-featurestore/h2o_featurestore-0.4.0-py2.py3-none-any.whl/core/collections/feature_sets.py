import re

from google.protobuf.empty_pb2 import Empty

from .. import CoreService_pb2 as pb
from ..entities.feature_set import FeatureSet
from ..filter import FilterBuilder, convert_json_query_to_proto
from ..filter.collections import FeatureSet as FeatureSetCollection
from ..schema import Schema
from ..utils import Utils


class FeatureSets:
    def __init__(self, stub, project):
        self._project = project
        self._stub = stub

    def register(
        self,
        schema,
        feature_set_name,
        description="",
        primary_key=None,
        secondary_key=None,
        time_travel_column=None,
        time_travel_column_format="yyyy-MM-dd HH:mm:ss",
        secret=False,
        partition_by=None,
        time_travel_column_as_partition=False,
    ):
        if not isinstance(schema, Schema):
            raise ValueError(
                "Parameter `schema` should be of type `featurestore.core.schema.Schema`"
            )
        request = pb.RegisterFeatureSetRequest()
        request.schema.extend(schema._to_proto_schema())
        request.project.CopyFrom(self._project)
        if primary_key is not None:
            request.primary_key = primary_key
        if secondary_key is not None:
            request.secondary_key = secondary_key
        if time_travel_column is not None:
            request.time_travel_column = time_travel_column
        request.secret = secret
        request.description = description
        if partition_by is not None:
            request.partition_by.extend(partition_by)
        if time_travel_column_as_partition is True or partition_by is None:
            request.time_travel_column_as_partition = True
        request.time_travel_column_format = time_travel_column_format
        request.feature_set_name = feature_set_name
        response = self._stub.RegisterFeatureSet(request)
        self._reload_project()
        return FeatureSet(self._stub, response.feature_set)

    def get(self, feature_set_name, version=None):
        request = pb.GetFeatureSetRequest()
        request.project.CopyFrom(self._project)
        request.feature_set_name = feature_set_name
        if version is not None:
            if not re.search("^\d+\\.\d+$", str(version)):
                raise Exception('Version parameter must be in a format "major.minor".')
            request.version = str(version)
        response = self._stub.GetFeatureSet(request)
        return FeatureSet(self._stub, response.feature_set)

    @staticmethod
    def _build_feature_set_list_query(tags=None, filters=None):
        query = None
        if isinstance(filters, FilterBuilder):
            query = filters.build()
        elif filters:
            query = convert_json_query_to_proto(filters)
        if tags:
            if isinstance(tags, (list, tuple)):
                text_filter = FeatureSetCollection.tags.in_(*tags)
            else:
                text_filter = FeatureSetCollection.tags == tags
            if query:
                query.filters.extend([text_filter])
            else:
                query = FilterBuilder().add(text_filter).build()
        return query

    def list(self, tags=None, filters=None):
        request = pb.ListFeatureSetsRequest()
        request.project.CopyFrom(self._project)
        if tags or filters:
            query = FeatureSets._build_feature_set_list_query(tags, filters)
            request.query.CopyFrom(query)
        response = self._stub.ListFeatureSets(request)
        return [FeatureSet(self._stub, fs) for fs in response.feature_sets]

    def list_feature_classifiers(self):
        request = Empty()
        response = self._stub.ListFeatureClassifiers(request)
        return response.feature_classifiers

    def __repr__(self):
        return Utils.pretty_print_proto(self._project)

    def _reload_project(self):
        request = pb.GetProjectRequest()
        request.project_name = self._project.name
        response = self._stub.GetProject(request)
        self._project = response.project
