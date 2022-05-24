import json
import time

from .. import CoreService_pb2 as pb
from .. import FeatureSetProtoApi_pb2 as FeatureSetApi
from .. import OnlineApi_pb2 as OnlineApi
from .. import TimeToLiveApi_pb2 as TimeToLiveApi
from .. import interactive_console
from ..collections.ingest_history import IngestHistory
from ..credentials import CredentialsHelper
from ..data_source_wrappers import SparkDataFrame
from ..entities.feature import Feature
from ..retrieve_holder import RetrieveHolder
from ..schema import Schema
from ..utils import Utils
from .feature_set_schema import FeatureSetSchema
from .ingest_job import IngestJob
from .materialization_online_job import MaterializationOnlineJob
from .recommendation import Recommendation
from .user import User


class FeatureSet:
    def __init__(self, stub, feature_set):
        fs = pb.FeatureSet()
        fs.CopyFrom(feature_set)
        self._feature_set = fs
        self._stub = stub
        self._feature_set_header = FeatureSetApi.FeatureSetHeader()
        self._feature_set_header.project_id = self._feature_set.project_id
        self._feature_set_header.feature_set_id = self._feature_set.id
        self._feature_set_header.feature_set_version = self._feature_set.version

    @property
    def project(self):
        return self._feature_set.project

    @property
    def feature_set_name(self):
        return self._feature_set.feature_set_name

    @property
    def version(self):
        return self._feature_set.version

    @property
    def version_change(self):
        return self._feature_set.version_change

    @property
    def time_travel_column(self):
        return self._feature_set.time_travel_column

    @property
    def partition_by(self):
        return self._feature_set.partition_by

    @property
    def time_travel_column_format(self):
        return self._feature_set.time_travel_column_format

    @property
    def feature_set_type(self):
        return FeatureSetApi.FeatureSetType.Name(self._feature_set.feature_set_type)

    @feature_set_type.setter
    def feature_set_type(self, value):
        valid_values = FeatureSetApi.FeatureSetType.keys()
        if value.upper() in valid_values:
            update_request = pb.FeatureSetTypeUpdateRequest()
            update_request.new_value = FeatureSetApi.FeatureSetType.Value(value.upper())
            update_request.header.CopyFrom(self._feature_set_header)
            self._stub.UpdateFeatureSetType(update_request)
            self.refresh()
        else:
            raise Exception(
                "Invalid feature set type. Supported values are: "
                + ", ".join(map(str, valid_values))
            )

    @property
    def description(self):
        return self._feature_set.description

    @description.setter
    def description(self, value):
        update_request = pb.FeatureSetStringFieldUpdateRequest()
        update_request.new_value = value
        update_request.header.CopyFrom(self._feature_set_header)
        self._stub.UpdateFeatureSetDescription(update_request)
        self.refresh()

    @property
    def owner(self):
        return User(self._feature_set.owner)

    @owner.setter
    def owner(self, email):
        request = pb.GetUserByMailRequest()
        request.email = email
        response = self._stub.GetUserByMail(request)
        user = response.user
        update_request = pb.FeatureSetUserFieldUpdateRequest()
        update_request.new_value.CopyFrom(user)
        update_request.header.CopyFrom(self._feature_set_header)
        self._stub.UpdateFeatureSetOwner(update_request)
        self.refresh()

    @property
    def author(self):
        return User(self._feature_set.author)

    @property
    def created_date_time(self):
        return Utils.timestamp_to_string(self._feature_set.created_date_time)

    @property
    def last_update_date_time(self):
        return Utils.timestamp_to_string(self._feature_set.last_update_date_time)

    @property
    def application_name(self):
        return self._feature_set.application_name

    @application_name.setter
    def application_name(self, value):
        update_request = pb.FeatureSetStringFieldUpdateRequest()
        update_request.new_value = value
        update_request.header.CopyFrom(self._feature_set_header)
        self._stub.UpdateFeatureSetApplicationName(update_request)
        self.refresh()

    @property
    def deprecated(self):
        return self._feature_set.deprecated

    @deprecated.setter
    def deprecated(self, value):
        update_request = pb.FeatureSetBooleanFieldUpdateRequest()
        update_request.new_value = value
        update_request.header.CopyFrom(self._feature_set_header)
        self._stub.UpdateFeatureSetDeprecated(update_request)
        self.refresh()

    @property
    def deprecated_date(self):
        return Utils.timestamp_to_string(self._feature_set.deprecated_date)

    @property
    def data_source_domains(self):
        return self._feature_set.data_source_domains

    @data_source_domains.setter
    def data_source_domains(self, value):
        if not isinstance(value, list):
            raise ValueError(
                "data_source_domains accepts only list of strings as a value"
            )
        update_request = pb.FeatureSetStringArrayFieldUpdateRequest()
        update_request.new_value.extend(value)
        update_request.header.CopyFrom(self._feature_set_header)
        self._stub.UpdateFeatureSetDataSourceDomains(update_request)
        self.refresh()

    @property
    def tags(self):
        return self._feature_set.tags

    @tags.setter
    def tags(self, value):
        if not isinstance(value, list):
            raise ValueError("tags accepts only list of strings as a value")
        update_request = pb.FeatureSetStringArrayFieldUpdateRequest()
        update_request.new_value.extend(value)
        update_request.header.CopyFrom(self._feature_set_header)
        self._stub.UpdateFeatureSetTags(update_request)
        self.refresh()

    @property
    def process_interval(self):
        return self._feature_set.process_interval

    @process_interval.setter
    def process_interval(self, value):
        update_request = pb.FeatureSetIntFieldUpdateRequest()
        update_request.new_value = value
        update_request.header.CopyFrom(self._feature_set_header)
        self._stub.UpdateFeatureSetProcessInterval(update_request)
        self.refresh()

    @property
    def process_interval_unit(self):
        return pb.ProcessIntervalUnit.Name(self._feature_set.process_interval_unit)

    @process_interval_unit.setter
    def process_interval_unit(self, value):
        valid_units = pb.ProcessIntervalUnit.keys()
        if value.upper() in valid_units:
            update_request = pb.FeatureSetProcessIntervalUnitUpdateRequest()
            update_request.new_value = pb.ProcessIntervalUnit.Value(value.upper())
            update_request.header.CopyFrom(self._feature_set_header)
            self._stub.UpdateFeatureSetProcessIntervalUnit(update_request)
            self.refresh()
        else:
            raise Exception(
                "Invalid process interval unit. Supported values are: "
                + ", ".join(map(str, valid_units))
            )

    @property
    def flow(self):
        return self._feature_set.flow

    @flow.setter
    def flow(self, value):
        update_request = pb.FeatureSetStringFieldUpdateRequest()
        update_request.new_value = value
        update_request.header.CopyFrom(self._feature_set_header)
        self._stub.UpdateFeatureSetFlow(update_request)
        self.refresh()

    @property
    def features(self):
        return {
            feature.name: Feature(self._stub, self, feature, feature.name)
            for feature in self._feature_set.features
        }

    @property
    def primary_key(self):
        return self._feature_set.primary_key

    @primary_key.setter
    def primary_key(self, value):
        update_request = pb.FeatureSetStringFieldUpdateRequest()
        update_request.new_value = value
        update_request.header.CopyFrom(self._feature_set_header)
        self._stub.UpdateFeatureSetPrimaryKey(update_request)
        self.refresh()

    @property
    def secondary_key(self):
        return self._feature_set.secondary_key

    @secondary_key.setter
    def secondary_key(self, value):
        update_request = pb.FeatureSetStringFieldUpdateRequest()
        update_request.new_value = value
        update_request.header.CopyFrom(self._feature_set_header)
        self._stub.UpdateFeatureSetSecondaryKey(update_request)
        self.refresh()

    @property
    def statistics(self):
        return Statistics(self._feature_set)

    @property
    def time_to_live(self):
        return TimeToLive(self._stub, self)

    @property
    def special_data(self):
        return FeatureSetSpecialData(self._stub, self)

    @property
    def time_travel_scope(self):
        return FeatureSetScope(self._feature_set)

    @property
    def application_id(self):
        return self._feature_set.application_id

    @application_id.setter
    def application_id(self, value):
        update_request = pb.FeatureSetStringFieldUpdateRequest()
        update_request.new_value = value
        update_request.header.CopyFrom(self._feature_set_header)
        self._stub.UpdateFeatureSetApplicationId(update_request)
        self.refresh()

    @property
    def feature_set_state(self):
        return self._feature_set.feature_set_state

    @feature_set_state.setter
    def feature_set_state(self, value):
        update_request = pb.FeatureSetStringFieldUpdateRequest()
        update_request.new_value = value
        update_request.header.CopyFrom(self._feature_set_header)
        self._stub.UpdateFeatureSetState(update_request)
        self.refresh()

    @property
    def online(self):
        return Online(self._feature_set)

    @property
    def secret(self):
        return self._feature_set.secret

    @secret.setter
    def secret(self, value):
        update_request = pb.FeatureSetBooleanFieldUpdateRequest()
        update_request.new_value = value
        update_request.header.CopyFrom(self._feature_set_header)
        self._stub.UpdateFeatureSetSecret(update_request)
        self.refresh()

    @property
    def custom_data(self):
        return self._feature_set.custom_data

    @property
    def feature_classifiers(self):
        return self._feature_set.feature_classifiers

    @custom_data.setter
    def custom_data(self, value):
        update_request = pb.FeatureSetCustomDataUpdateRequest()
        update_request.new_value.CopyFrom(value)
        update_request.header.CopyFrom(self._feature_set_header)
        self._stub.UpdateFeatureSetCustomData(update_request)
        self.refresh()

    def create_new_version(self, schema=None, affected_features=None, reason=""):
        if schema is None and affected_features is None:
            raise ValueError(
                "Schema or affected_features must be defined. Both values are supported as well"
            )
        request = pb.CreateNewFeatureSetVersionRequest()
        request.feature_set.CopyFrom(self._feature_set)
        request.reason = reason
        if schema:
            request.schema.extend(schema._to_proto_schema())
        else:
            request.schema.extend(self.schema.get()._to_proto_schema())
        if affected_features:
            request.affected_features.extend(affected_features)
        response = self._stub.CreateNewFeatureSetVersion(request)
        return FeatureSet(self._stub, response.feature_set)

    def refresh(self):
        request = pb.GetFeatureSetsLastMinorForCurrentMajorRequest()
        request.header.CopyFrom(self._feature_set_header)
        self._feature_set = self._stub.GetFeatureSetsLastMinorForCurrentMajor(
            request
        ).feature_set
        self._feature_set_header.feature_set_version = self._feature_set.version
        return self

    def delete(self, wait_for_completion=False):
        request = pb.DeleteFeatureSetRequest()
        request.feature_set.CopyFrom(self._feature_set)
        self._stub.DeleteFeatureSet(request)
        exists_request = pb.FeatureSetExistsRequest()
        exists_request.project_id = self._feature_set.project_id
        exists_request.feature_set_id = self._feature_set.id
        if wait_for_completion:
            while self._stub.FeatureSetExists(exists_request).exists:
                time.sleep(1)
                print(
                    "Waiting for feature set '{}' deletion".format(
                        self._feature_set.feature_set_name
                    )
                )

    def add_owners(self, user_emails):
        return self._add_permissions(user_emails, pb.PermissionType.Owner)

    def add_editors(self, user_emails):
        return self._add_permissions(user_emails, pb.PermissionType.Editor)

    def add_consumers(self, user_emails):
        return self._add_permissions(user_emails, pb.PermissionType.Consumer)

    def add_sensitive_consumers(self, user_emails):
        return self._add_permissions(user_emails, pb.PermissionType.SensitiveConsumer)

    def remove_owners(self, user_emails):
        return self._remove_permissions(user_emails, pb.PermissionType.Owner)

    def remove_editors(self, user_emails):
        return self._remove_permissions(user_emails, pb.PermissionType.Editor)

    def remove_consumers(self, user_emails):
        return self._remove_permissions(user_emails, pb.PermissionType.Consumer)

    def remove_sensitive_consumers(self, user_emails):
        return self._remove_permissions(
            user_emails, pb.PermissionType.SensitiveConsumer
        )

    def get_active_jobs(self, job_type=pb.JobType.Unknown):
        self._get_jobs(True, job_type)

    def _get_jobs(self, active, job_type=pb.JobType.Unknown):
        from ..collections.jobs import Jobs  # Lazy import to avoid circular reference

        request = pb.ListJobsRequest(active=active)
        request.feature_set.CopyFrom(self._feature_set)
        request.job_type = job_type
        resp = self._stub.ListJobs(request)
        return [Jobs._create_job(self._stub, job_proto) for job_proto in resp.jobs]

    def _add_permissions(self, user_emails, permission):
        request = pb.FeatureSetPermissionRequest()
        request.feature_set.CopyFrom(self._feature_set)
        request.user_emails.extend(user_emails)
        request.permission = permission
        self._stub.AddFeatureSetPermission(request)
        return self

    def _remove_permissions(self, user_emails, permission):
        request = pb.FeatureSetPermissionRequest()
        request.feature_set.CopyFrom(self._feature_set)
        request.user_emails.extend(user_emails)
        request.permission = permission
        self._stub.RemoveFeatureSetPermission(request)
        return self

    def ingest_async(
        self,
        source,
        start_date_time=None,
        end_date_time=None,
        credentials=None,
    ):
        from ..data_source_wrappers import get_raw_data_location

        if isinstance(source, SparkDataFrame):
            source._write_to_cache(self._stub)
            data_source = source._get_cache_location()
        else:
            data_source = get_raw_data_location(source)
        request = pb.StartIngestJobRequest()
        request.feature_set.CopyFrom(self._feature_set)
        request.data_source.CopyFrom(data_source)
        CredentialsHelper.set_credentials(request, data_source, credentials)
        if start_date_time is not None:
            request.start_date_time = start_date_time
        if end_date_time is not None:
            request.end_date_time = end_date_time
        job_id = self._stub.StartIngestJob(request)
        return IngestJob(self._stub, job_id)

    @interactive_console.record_stats
    def ingest(
        self,
        source,
        start_date_time=None,
        end_date_time=None,
        credentials=None,
    ):
        job = self.ingest_async(
            source,
            start_date_time,
            end_date_time,
            credentials,
        )
        while not job.is_done():
            job.show_progress()
            time.sleep(2)
        job.show_progress()  # there is possibility that some progress was pushed before finishing job
        result = job.get_result()
        self._feature_set = result._get_feature_set()
        self._feature_set_header.feature_set_version = self._feature_set.version
        return result

    def materialize_online_async(self):
        request = pb.StartMaterializationOnlineRequest()
        request.feature_set.CopyFrom(self._feature_set)
        job_id = self._stub.StartMaterializationOnlineJob(request)
        return MaterializationOnlineJob(self._stub, job_id)

    @interactive_console.record_stats
    def materialize_online(self):
        job = self.materialize_online_async()
        while not job.is_done():
            job.show_progress()
            time.sleep(2)

        job.show_progress()  # there is possibility that some progress was pushed before finishing job
        result = job.get_result()
        return result

    def ingest_online(self, rows):
        if isinstance(rows, list):
            row_list = rows
        else:
            row_list = [rows]
        request = OnlineApi.OnlineIngestRequest()
        request.header.CopyFrom(self._feature_set_header)
        request.rows.extend(row_list)
        self._stub.OnlineIngest(request)

    def retrieve_online(self, key) -> dict:
        request = OnlineApi.OnlineRetrieveRequest()
        request.header.CopyFrom(self._feature_set_header)
        request.key = str(key)
        json_row = self._stub.OnlineRetrieve(request).row
        return json.loads(json_row)

    def retrieve(self, start_date_time=None, end_date_time=None):
        return RetrieveHolder(
            self._stub, self._feature_set, start_date_time, end_date_time, ""
        )

    def list_versions(self):
        request = pb.ListFeatureSetsVersionRequest()
        request.feature_set.CopyFrom(self._feature_set)
        response = self._stub.ListFeatureSetVersions(request)
        return [VersionDescription(version) for version in response.versions]

    @property
    def schema(self):
        return FeatureSetSchema(self._stub, self)

    def ingest_history(self):
        return IngestHistory(self._stub, self._feature_set)

    def get_recommendations(self):
        request = pb.GetRecommendationRequest()
        request.feature_set.CopyFrom(self._feature_set)
        response = self._stub.GetRecommendations(request)
        return [Recommendation(self._stub, self, item) for item in response.matches]

    def __repr__(self):
        return Utils.pretty_print_proto(self._feature_set)


class VersionDescription:
    def __init__(self, version_description):
        self._version_description = version_description

    def __repr__(self):
        return Utils.pretty_print_proto(self._version_description)


class TimeToLive:
    def __init__(self, stub, feature_set):
        self._stub = stub
        self._fs = feature_set

    @property
    def ttl_offline(self):
        return self._fs._feature_set.time_to_live.ttl_offline

    @ttl_offline.setter
    def ttl_offline(self, value):
        update_request = pb.FeatureSetIntFieldUpdateRequest()
        update_request.new_value = value
        update_request.header.CopyFrom(self._fs._feature_set_header)
        self._stub.UpdateTimeToLiveOfflineInterval(update_request)
        self._fs.refresh()

    @property
    def ttl_offline_interval(self):
        return TimeToLiveApi.Offline.TimeToLiveInterval.Name(
            self._fs._feature_set.time_to_live.ttl_offline_interval
        )

    @ttl_offline_interval.setter
    def ttl_offline_interval(self, value):
        valid_units = TimeToLiveApi.Offline.TimeToLiveInterval.keys()
        if value.upper() in valid_units:
            update_request = pb.FeatureSetTimeToLiveOfflineIntervalUnitUpdateRequest()
            update_request.new_value = TimeToLiveApi.Offline.TimeToLiveInterval.Value(
                value.upper()
            )
            update_request.header.CopyFrom(self._fs._feature_set_header)
            self._stub.UpdateTimeToLiveOfflineIntervalUnit(update_request)
            self._fs.refresh()
        else:
            raise Exception(
                "Invalid offline time to live interval unit. Supported values are: "
                + ", ".join(map(str, valid_units))
            )

    @property
    def ttl_online(self):
        return self._fs._feature_set.time_to_live.ttl_online

    @ttl_online.setter
    def ttl_online(self, value):
        update_request = pb.FeatureSetIntFieldUpdateRequest()
        update_request.new_value = value
        update_request.header.CopyFrom(self._fs._feature_set_header)
        self._stub.UpdateTimeToLiveOnlineInterval(update_request)
        self._fs.refresh()

    @property
    def ttl_online_interval(self):
        return TimeToLiveApi.Online.TimeToLiveInterval.Name(
            self._fs._feature_set.time_to_live.ttl_online_interval
        )

    @ttl_online_interval.setter
    def ttl_online_interval(self, value):
        valid_units = TimeToLiveApi.Online.TimeToLiveInterval.keys()
        if value.upper() in valid_units:
            update_request = pb.FeatureSetTimeToLiveOnlineIntervalUnitUpdateRequest()
            update_request.new_value = TimeToLiveApi.Online.TimeToLiveInterval.Value(
                value.upper()
            )
            update_request.header.CopyFrom(self._fs._feature_set_header)
            self._stub.UpdateTimeToLiveOnlineIntervalUnit(update_request)
            self._fs.refresh()
        else:
            raise Exception(
                "Invalid online time to live interval unit. Supported values are: "
                + ", ".join(map(str, valid_units))
            )

    def __repr__(self):
        return Utils.pretty_print_proto(self._fs._feature_set.time_to_live)


class FeatureSetScope:
    def __init__(self, feature_set):
        self._feature_set = feature_set
        self._scope = self._feature_set.time_travel_scope

    @property
    def start_date_time(self):
        return Utils.timestamp_to_string(self._scope.start_date_time)

    @property
    def end_date_time(self):
        return Utils.timestamp_to_string(self._scope.end_date_time)

    def __repr__(self):
        return Utils.pretty_print_proto(self._scope)


class FeatureSetSpecialData:
    def __init__(self, stub, feature_set):
        self._stub = stub
        self._fs = feature_set

    @property
    def spi(self):
        return self._fs._feature_set.special_data.spi

    @property
    def pci(self):
        return self._fs._feature_set.special_data.pci

    @property
    def rpi(self):
        return self._fs._feature_set.special_data.rpi

    @property
    def demographic(self):
        return self._fs._feature_set.special_data.demographic

    @property
    def legal(self):
        return Legal(self._stub, self._fs)

    def __repr__(self):
        return Utils.pretty_print_proto(self._fs._feature_set.special_data)


class Statistics:
    def __init__(self, feature_set):
        self._feature_set = feature_set
        self._statistics = self._feature_set.statistics

    @property
    def data_latency(self):
        return self._statistics.data_latency

    def __repr__(self):
        return Utils.pretty_print_proto(self._statistics)


class Legal:
    def __init__(self, stub, feature_set):
        self._stub = stub
        self._fs = feature_set

    @property
    def approved(self):
        return self._fs._feature_set.special_data.legal.approved

    @approved.setter
    def approved(self, value):
        update_request = pb.FeatureSetBooleanFieldUpdateRequest()
        update_request.new_value = value
        update_request.header.CopyFrom(self._fs._feature_set_header)
        self._stub.UpdateFeatureSetLegalApproved(update_request)
        self._fs.refresh()

    @property
    def approved_date(self):
        return Utils.timestamp_to_string(
            self._fs._feature_set.special_data.legal.approved_date
        )

    @property
    def notes(self):
        return self._fs._feature_set.special_data.legal.notes

    @notes.setter
    def notes(self, value):
        update_request = pb.FeatureSetStringFieldUpdateRequest()
        update_request.new_value = value
        update_request.header.CopyFrom(self._fs._feature_set_header)
        self._stub.UpdateFeatureSetLegalApprovedNotes(update_request)
        self._fs.refresh()

    def __repr__(self):
        return Utils.pretty_print_proto(self._fs._feature_set.special_data.legal)


class Online:
    def __init__(self, feature_set):
        self._feature_set = feature_set
        self._online = self._feature_set.online

    @property
    def online_namespace(self):
        return self._online.online_namespace

    @property
    def connection_type(self):
        return self._online.connection_type

    @property
    def topic(self):
        return self._online.topic

    def __repr__(self):
        return Utils.pretty_print_proto(self._online)
