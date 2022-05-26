from __future__ import absolute_import

import enum
import six

from rapyuta_io.clients.model import DEFAULT_LOG_UPLOAD_BANDWIDTH
from rapyuta_io.utils.error import InvalidParameterException, ROSBagBlobError
from rapyuta_io.utils.object_converter import ObjBase, enum_field, nested_field, list_field
from rapyuta_io.utils.partials import PartialMixin
from rapyuta_io.utils.pollers import RefreshPollerMixin
from rapyuta_io.utils.rest_client import HttpMethod, RestClient
from rapyuta_io.utils.utils import create_auth_header, get_api_response_data


class UploadOptions(ObjBase):
    """
    ROSBag Upload Options

    :ivar max_upload_rate: Upload Rate in Bytes for ROSBag Files
    :vartype max_upload_rate: int
    :ivar purge_after: Purge File after uploaded
    :vartype purge_after: bool

    :param max_upload_rate: Upload Rate in Bytes for ROSBag Files
    :type max_upload_rate: int
    :param purge_after: Purge File after uploaded
    :type purge_after: bool
    """

    def __init__(self, max_upload_rate=DEFAULT_LOG_UPLOAD_BANDWIDTH, purge_after=False):
        self.validate(max_upload_rate, purge_after)
        self.max_upload_rate = max_upload_rate
        self.purge_after = purge_after

    @staticmethod
    def validate(max_upload_rate, purge_after):
        if not isinstance(max_upload_rate, int) or max_upload_rate <= 0:
            raise InvalidParameterException('max_upload_rate must be a positive int')
        if not isinstance(purge_after, bool):
            raise InvalidParameterException('purge_after must be a bool')

    def get_deserialize_map(self):
        return {
            'max_upload_rate': 'maxUploadRate',
            'purge_after': 'purgeAfter'
        }

    def get_serialize_map(self):
        return {
            'maxUploadRate': 'max_upload_rate',
            'purgeAfter': 'purge_after'
        }


class ROSBagOptions(ObjBase):
    """
    ROSBag options

    :ivar all_topics: Record all topics
    :vartype all_topics: bool
    :ivar topics:  Record a bag file with the contents of the specified topics
    :vartype topics: list(str)
    :ivar topic_include_regex: Match topics using regular expressions
    :vartype topic_include_regex: list(str)
    :ivar topic_exclude_regex: Exclude topics matching the given regular expression
    :vartype topic_exclude_regex: str
    :ivar max_message_count: Only record NUM messages on each topic
    :vartype max_message_count: int
    :ivar node: Record all topics subscribed to by a specific node
    :vartype node: str
    :ivar compression: Compression can be LZ4 or BZ2
    :vartype compression: :py:class:`~rapyuta_io.clients.rosbag.ROSBagCompression`
    :ivar max_splits: Split bag at most MAX_SPLITS times
    :vartype max_splits: int
    :ivar max_split_size: Record a bag of maximum size
    :vartype max_split_size: int
    :ivar chunk_size: Record to chunks of size KB before writing to disk
    :vartype chunk_size: int

    :param all_topics: Record all topics
    :type all_topics: bool
    :param topics:  Record a bag file with the contents of the specified topics
    :type topics: list(str)
    :param topic_include_regex: Match topics using regular expressions
    :type topic_include_regex: list(str)
    :param topic_exclude_regex: Exclude topics matching the given regular expression
    :type topic_exclude_regex: str
    :param max_message_count: Only record NUM messages on each topic
    :type max_message_count: int
    :param node: Record all topics subscribed to by a specific node
    :type node: str
    :param compression: Compression can be LZ4 or BZ2
    :type compression: :py:class:`~rapyuta_io.clients.rosbag.ROSBagCompression`
    :param max_splits: Split bag at most MAX_SPLITS times
    :type max_splits: int
    :param max_split_size: Record a bag of maximum size
    :type max_split_size: int
    :param chunk_size: Record to chunks of size KB before writing to disk
    :type chunk_size: int
    """

    def __init__(self, all_topics=None, topics=None, topic_include_regex=None,
                 topic_exclude_regex=None, max_message_count=None, node=None, compression=None,
                 max_splits=None, max_split_size=None, chunk_size=None):
        self.validate(all_topics, topics, topic_include_regex, topic_exclude_regex, node,
                      compression, max_splits)
        self.all_topics = all_topics
        self.topics = topics
        self.topic_include_regex = topic_include_regex
        self.topic_exclude_regex = topic_exclude_regex
        self.max_message_count = max_message_count
        self.node = node
        self.compression = compression
        self.max_splits = max_splits
        self.max_split_size = max_split_size
        self.chunk_size = chunk_size

    @staticmethod
    def validate(all_topics, topics, topic_include_regex,
                 topic_exclude_regex, node, compression,
                 max_splits):
        if all_topics and not isinstance(all_topics, bool):
            raise InvalidParameterException('all_topics must be a bool')
        if topics and (not isinstance(topics, list) or [x for x in topics if not isinstance(x, six.string_types)]):
            raise InvalidParameterException('topics must be a list of string')
        if topic_include_regex and (not isinstance(topic_include_regex, list) or [x for x in topic_include_regex if
                                                                                  not isinstance(x, six.string_types)]):
            raise InvalidParameterException('topic_include_regex must be a list of string')
        if topic_exclude_regex and not isinstance(topic_exclude_regex, six.string_types):
            raise InvalidParameterException('topic_exclude_regex must be a non-empty string')
        if node and not isinstance(node, six.string_types):
            raise InvalidParameterException('node must be a non-empty string')
        if compression and compression not in list(ROSBagCompression.__members__.values()):
            raise InvalidParameterException('compression must be a LZ4 or BZ2')
        if max_splits and not isinstance(max_splits, int):
            raise InvalidParameterException('max_splits must be a int')
        if not all_topics and not topics and not topic_include_regex and not node:
            raise InvalidParameterException('One of all_topics, topics, topic_include_regex, and node must be provided')

    def get_deserialize_map(self):
        return {
            'all_topics': 'allTopics',
            'topics': 'topics',
            'topic_include_regex': 'topicIncludeRegex',
            'topic_exclude_regex': 'topicExcludeRegex',
            'max_message_count': 'maxMessageCount',
            'node': 'node',
            'compression': enum_field('compression', ROSBagCompression),
            'max_splits': 'maxSplits',
            'max_split_size': 'maxSplitSize',
            'chunk_size': 'chunkSize',
        }

    def get_serialize_map(self):
        return {
            'allTopics': 'all_topics',
            'topics': 'topics',
            'topicIncludeRegex': 'topic_include_regex',
            'topicExcludeRegex': 'topic_exclude_regex',
            'maxMessageCount': 'max_message_count',
            'node': 'node',
            'compression': 'compression',
            'maxSplits': 'max_splits',
            'maxSplitSize': 'max_split_size',
            'chunkSize': 'chunk_size',
        }


class ROSBagJob(ObjBase):
    """
    ROSBag Job

    :ivar guid: guid of the job
    :vartype guid: str
    :ivar deployment_id: deployment id
    :vartype deployment_id: str
    :ivar component_instance_id: component instance id
    :vartype component_instance_id: str
    :ivar name: name of the job
    :vartype name: str
    :ivar package_id: package id
    :vartype package_id: str
    :ivar status: status of the job
    :vartype status: :py:class:`~rapyuta_io.clients.rosbag.ROSBagJobStatus`
    :ivar component_id: component id
    :vartype component_id: str
    :ivar component_type: component type
    :vartype component_type: :py:class:`~rapyuta_io.clients.rosbag.ComponentType`
    :ivar device_id: device id
    :vartype device_id: str
    :ivar creator: user id
    :vartype creator: str
    :ivar project: id
    :vartype project: str
    :ivar rosbag_options: rosbag options
    :vartype rosbag_options: :py:class:`~rapyuta_io.clients.rosbag.ROSBagOptions`
    :ivar upload_options: Rosbag Upload Options, required in case of Device jobs
    :vartype upload_options: :py:class:`~rapyuta_io.clients.rosbag.UploadOptions`

    :param name: name of the job
    :type name: str
    :param rosbag_options: rosbag options
    :type rosbag_options: :py:class:`~rapyuta_io.clients.rosbag.ROSBagOptions`
    :param deployment_id: deployment id
    :type deployment_id: str
    :param component_instance_id: component instance id
    :type component_instance_id: str
    :param upload_options: Rosbag Upload Options, required in case of Device ROSBagJob
    :type upload_options: :py:class:`~rapyuta_io.clients.rosbag.UploadOptions`
    """

    def __init__(self, name, rosbag_options, deployment_id=None, component_instance_id=None,
                 upload_options=None):
        self.validate(name, rosbag_options)
        self.component_instance_id = component_instance_id
        self.deployment_id = deployment_id
        self.name = name
        self.rosbag_options = rosbag_options
        self.upload_options = upload_options
        self.package_id = None
        self.status = None
        self.component_id = None
        self.component_type = None
        self.device_id = None
        self.project = None

    @staticmethod
    def validate(name, rosbag_options):

        if not name or not isinstance(name, six.string_types):
            raise InvalidParameterException('name must be a non-empty string')

        if not rosbag_options or not isinstance(rosbag_options, ROSBagOptions):
            raise InvalidParameterException('rosbag_options must be a instance of ROSBagOptions')

    def get_deserialize_map(self):
        return {
            'guid': 'guid',
            'component_instance_id': 'componentInstanceID',
            'deployment_id': 'deploymentID',
            'component_id': 'componentID',
            'name': 'name',
            'node': 'node',
            'package_id': 'packageID',
            'status': enum_field('status', ROSBagJobStatus),
            'creator': 'creator',
            'project': 'project',
            'component_type': enum_field('componentType', ComponentType),
            'device_id': 'deviceID',
            'rosbag_options': nested_field('recordOptions', ROSBagOptions),
            'upload_options': nested_field('uploadOptions', UploadOptions)
        }

    def get_serialize_map(self):
        return {
            'componentInstanceID': 'component_instance_id',
            'deploymentID': 'deployment_id',
            'name': 'name',
            'recordOptions': 'rosbag_options',
            'uploadOptions': 'upload_options'
        }


class ROSBagCompression(str, enum.Enum):
    """
    Enumeration variables for the Supported ROSBag Compression. Compression may be 'LZ4', or 'BZ2' \n
    ROSBagCompression.LZ4 \n
    ROSBagCompression.BZ2 \n
    """

    def __str__(self):
        return str(self.value)

    LZ4 = 'LZ4'
    BZ2 = 'BZ2'


class ROSBagJobStatus(str, enum.Enum):
    """
    Enumeration variables for the Supported ROSBag Job Status. Job Status may be 'Starting', 'Running', 'Error',
    'Stopping', or 'Stopped' \n
    ROSBagJobStatus.STARTING \n
    ROSBagJobStatus.RUNNING \n
    ROSBagJobStatus.ERROR \n
    ROSBagJobStatus.STOPPING \n
    ROSBagJobStatus.STOPPED \n
    """

    def __str__(self):
        return str(self.value)

    STARTING = 'Starting'
    RUNNING = 'Running'
    ERROR = 'Error'
    STOPPING = 'Stopping'
    STOPPED = 'Stopped'


class ComponentType(str, enum.Enum):
    """
    Enumeration variables for the ComponentType for ROSBag Job. \n
    ComponentType.CLOUD \n
    ComponentType.DEVICE \n
    """

    def __str__(self):
        return str(self.value)

    CLOUD = 'Cloud'
    DEVICE = 'Device'


class ROSBagBlobStatus(str, enum.Enum):
    """
    Enumeration variables for the Supported ROSBag Blob Status. File Status may be 'Starting', 'Uploading', 'Uploaded',
    or 'Error' \n
    ROSBagBlobStatus.STARTING \n
    ROSBagBlobStatus.UPLOADING \n
    ROSBagBlobStatus.UPLOADED \n
    ROSBagBlobStatus.ERROR \n
    """

    def __str__(self):
        return str(self.value)

    STARTING = 'Starting'
    UPLOADING = 'Uploading'
    UPLOADED = 'Uploaded'
    ERROR = 'Error'


class ROSBagBlob(PartialMixin, RefreshPollerMixin, ObjBase):
    """
    ROSBag file class

    :ivar guid: bag id
    :vartype guid: str
    :ivar filename: filename of bag file
    :vartype filename: str
    :ivar job_id: job id
    :vartype job_id: str
    :ivar job: related job information
    :vartype job: :py:class:`~rapyuta_io.clients.rosbag.ROSBagJob`
    :ivar blob_ref_id: blob id
    :vartype blob_ref_id: int
    :ivar status: upload status of bag file
    :vartype status: :py:class:`~rapyuta_io.clients.rosbag.ROSBagBlobStatus`
    :ivar info: info about the bag file
    :vartype info: :py:class:`~rapyuta_io.clients.rosbag.ROSBagInfo`
    :ivar creator: user id
    :vartype creator: str
    :ivar project: project id
    :vartype project: str
    :ivar component_type: component type
    :vartype component_type: :py:class:`~rapyuta_io.clients.rosbag.ComponentType`
    :ivar device_id: device id
    :vartype device_id: str
    :ivar error_message: reason for upload failure
    :vartype error_message: str
    """

    ROSBAG_BLOBS_PATH = 'rosbag-blobs'

    def __init__(self):
        self.guid = None
        self.filename = None
        self.job_id = None
        self.job = None
        self.blob_ref_id = None
        self.status = None
        self.info = None
        self.creator = None
        self.project = None
        self.component_type = None
        self.device_id = None
        self.error_message = None

    def get_deserialize_map(self):
        return {
            'guid': 'guid',
            'filename': 'filename',
            'job_id': 'jobID',
            'job': nested_field('job', ROSBagJob),
            'blob_ref_id': 'blobRefID',
            'status': enum_field('status', ROSBagBlobStatus),
            'info': nested_field('info', ROSBagInfo),
            'error_message': 'errorMessage',
            'creator': 'creator',
            'project': 'project',
            'component_type': enum_field('componentType', ComponentType),
            'device_id': 'deviceID',
        }

    def get_serialize_map(self):
        return {}

    def delete(self):

        """
        Delete the rosbag blob using the rosbag blob object.

        Following example demonstrates how to delete a rosbag blob using rosbag blob object:

        >>> from rapyuta_io import Client
        >>> client = Client(auth_token='auth_token', project='project_guid')
        >>> rosbag_blobs = client.list_rosbag_blobs(deployment_ids=['dep-id'])
        >>> blob = rosbag_blobs[0]
        >>> blob.delete()

        """

        url = '{}/{}/{}'.format(self._host, self.ROSBAG_BLOBS_PATH, self.guid)
        headers = create_auth_header(self._auth_token, self._project)
        response = RestClient(url).method(HttpMethod.DELETE).headers(headers).execute()
        return response

    def retry_upload(self):
        """
        Retry upload for a Device ROSBagBlob with Error status.

        Following example demonstrates how to retry upload for a ROSBagBlob, and then wait for it to go to
        Uploaded/Error:

            >>> from rapyuta_io import Client
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> blobs = client.list_rosbag_blobs(statuses=[ROSBagBlobStatus.ERROR])
            >>> blobs[0].retry_upload()
            >>> blobs[0].poll_till_ready()

        """
        if self.component_type != ComponentType.DEVICE:
            raise InvalidParameterException('retry_upload not supported for Cloud ROSBagBlobs')
        if self.status != ROSBagBlobStatus.ERROR:
            raise InvalidParameterException('ROSBagBlob does not have Error status')
        url = '{}/{}/{}/retry'.format(self._host, self.ROSBAG_BLOBS_PATH, self.guid)
        headers = create_auth_header(self._auth_token, self._project)
        response = RestClient(url).method(HttpMethod.POST).headers(headers).execute()
        data = get_api_response_data(response, parse_full=True)
        self.status = data['status']

    def refresh(self):
        url = '{}/{}/{}'.format(self._host, self.ROSBAG_BLOBS_PATH, self.guid)
        headers = create_auth_header(self._auth_token, self._project)
        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()
        ROSBagBlob.deserialize(get_api_response_data(response, parse_full=True), obj=self)

    def poll_till_ready(self, retry_count=240, sleep_interval=5):
        """
        Polls the blob till its status changes from Starting/Uploading to Uploaded/Error.

        :param retry_count: Number of retries.
        :type retry_count: int
        :param sleep_interval: Sleep seconds between retries.
        :type sleep_interval: int
        :raises: :py:class:`ROSBagBlobError`: If status becomes Error.
        :raises: :py:class:`RetriesExhausted`: If the number of polling retries exhausted before the object was ready.

        Following example demonstrates how to poll a ROSBagBlob:

            >>> from rapyuta_io import Client
            >>> from rapyuta_io.utils.error import ROSBagBlobError, RetriesExhausted
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> blobs = client.list_rosbag_blobs(statuses=[ROSBagBlobStatus.STARTING, ROSBagBlobStatus.UPLOADING])
            >>> try:
            ...     blobs[0].poll_till_ready()
            ... except ROSBagBlobError as e:
            ...     print e
            ... except RetriesExhausted as e:
            ...     print e, 'Retry again ?'

        """
        super(ROSBagBlob, self).poll_till_ready(retry_count, sleep_interval)

    def is_ready(self):
        if self.status == ROSBagBlobStatus.ERROR:
            raise ROSBagBlobError(self.error_message if self.error_message else None)
        return self.status == ROSBagBlobStatus.UPLOADED


class ROSBagInfo(ObjBase):
    """
    ROSBag file related information

    :ivar bag_version: version of bag file
    :vartype bag_version: str
    :ivar duration: total record time
    :vartype duration: float
    :ivar start_time: record start time
    :vartype start_time: float
    :ivar end_time: record end time
    :vartype end_time: float
    :ivar size: size of bag file
    :vartype size: int
    :ivar message_count: number of messages
    :vartype message_count: int
    :ivar compression: compression used
    :vartype compression: str,
    :ivar uncompressed_size: size of bag file without compression
    :vartype uncompressed_size: int
    :ivar compressed_size: size of bag file with compression
    :vartype compressed_size: int
    :ivar message_types: instance of MessageType
    :vartype message_types: list(:py:class:`~rapyuta_io.clients.rosbag.MessageType`)
    :ivar topics: instance of TopicInfo
    :vartype topics: list(:py:class:`~rapyuta_io.clients.rosbag.TopicInfo`)
    """

    def get_deserialize_map(self):
        return {
            'bag_version': 'bagVersion',
            'duration': 'duration',
            'start_time': 'startTime',
            'end_time': 'endTime',
            'size': 'size',
            'message_count': 'messageCount',
            'compression': 'compression',
            'uncompressed_size': 'uncompressedSize',
            'compressed_size': 'compressedSize',
            'message_types': list_field('messageTypes', MessageType),
            'topics': list_field('topics', TopicInfo),
        }

    def get_serialize_map(self):
        return {}


class MessageType(ObjBase):
    """
    Message Type

    :ivar message_type: type of recorded message
    :vartype message_type: str
    :ivar md5: md5sum of messages
    :vartype md5: str
    """

    def get_deserialize_map(self):
        return {
            'message_type': 'type',
            'md5': 'md5',

        }

    def get_serialize_map(self):
        return {}


class TopicInfo(ObjBase):
    """
    Topic related information

    :ivar name: name of topics
    :vartype name: str
    :ivar message_type: type of topic
    :vartype message_type: str
    :ivar message_count: number of messages recorded
    :vartype message_count: int
    :ivar frequency: (Deprecated) frequency of topic
    :vartype frequency: float
    """

    def get_deserialize_map(self):
        return {
            'name': 'name',
            'message_type': 'messageType',
            'message_count': 'messageCount',
            'frequency': 'frequency',

        }

    def get_serialize_map(self):
        return {}
