# encoding: utf-8
from __future__ import absolute_import
import json
import re
import six
from time import mktime
from datetime import datetime
from dateutil.parser import parse

from rapyuta_io.utils import ObjDict, InvalidCommandException, InvalidParameterException
from rapyuta_io.utils.object_converter import ObjBase
from rapyuta_io.utils.settings import ENV_VAR_REGEX_PATTERN, SHARED_URL_PATH
from rapyuta_io.utils.utils import is_empty

DEFAULT_LOG_UPLOAD_BANDWIDTH = 1 * 1024 * 1024


class DeviceConfig(ObjDict):
    """
    DeviceConfig class represents configuration of a device. Member variables of the class
    represent the properties of device.

    :ivar id: Id of the configuration.
    :ivar key: Configuration key.
    :ivar value: Value of the configuration key.
    """
    DEFAULT_DEVICE_CONFIG_VARIABLES = ('runtime', 'ros_workspace', 'ros_distro',
                                       'rosbag_mount_path')

    def __init__(self, *args, **kwargs):
        super(ObjDict, self).__init__(*args, **kwargs)

    def is_deletable(self):
        if self.key in self.DEFAULT_DEVICE_CONFIG_VARIABLES:
            return False
        return True

    def is_updatable(self):
        if self.key == self.DEFAULT_DEVICE_CONFIG_VARIABLES[0]:
            return False
        return True


class Command(ObjDict):
    """
    Command class represent command that is executed on a device.

    :ivar shell: Represents the shell where it is going to execute
    :ivar env: List of environment variables.
    :ivar bg: Boolean value specifying whether the execution runs on the background or not
    :ivar runas: Run the command as a specific user
    :ivar cmd: Command to execute on the device
    :ivar pwd: Present working directory
    :ivar cwd: Current working directory

    :Note: **pwd** is deprecated. Although backward compatibility is supported, it is recommended to use **cwd** instead.

    """

    def __init__(self, cmd, shell=None, env=None, bg=False, runas=None, pwd=None, cwd=None):
        super(ObjDict, self).__init__()
        if env is None:
            env = dict()
        self.cmd = cmd
        self.shell = shell
        self.env = env
        self.bg = bg
        self.runas = runas
        self.cwd = pwd
        if cwd is not None:
            self.cwd = cwd
        self.validate()

    def validate(self):
        if is_empty(self.cmd) or not isinstance(self.cmd, six.string_types):
            raise InvalidCommandException("Invalid execution command")
        if self.shell is not None and not isinstance(self.shell, six.string_types):
            raise InvalidCommandException("Invalid shell")
        if self.bg is not None and not isinstance(self.bg, bool):
            raise InvalidCommandException("Invalid background option")
        if self.runas is not None and not isinstance(self.runas, six.string_types):
            raise InvalidCommandException("Invalid runas option")
        if self.cwd is not None and not isinstance(self.cwd, six.string_types):
            raise InvalidCommandException("Invalid cwd option")
        if self.env:
            if isinstance(self.env, dict):
                for env_var in self.env:
                    if not re.match(ENV_VAR_REGEX_PATTERN, env_var):
                        raise InvalidCommandException('Invalid environment variables')
                return
            raise InvalidCommandException('Invalid environment variables')

    def to_json(self):
        # TODO: we need to rewrite this function.
        js = json.loads(json.dumps(self))
        ret = {}
        for key, value in js.items():
            if value is not None and str(value) != '':
                ret[key] = value
        return ret


class TopicsStatus(ObjDict):
    """
    Topic class represents the status - subscribed and unsubscribed - for logs and metrics

    :ivar master_up: Boolean represents whether the master is running or not
    :ivar subscribed: List of subscribed topics
    :ivar unsubscribed: List of unsubscribed topics

     """

    def __init__(self, *args, **kwargs):
        super(ObjDict, self).__init__(*args, **kwargs)


class Label(ObjDict):
    """ Label class represents labels associated with a device.

         :ivar id: Integer represents the id of the label
         :ivar key: Key or label name
         :ivar value: Value of the label

         """

    def __init__(self, *args, **kwargs):
        super(ObjDict, self).__init__(*args, **kwargs)


class Metric(ObjDict):
    """
    Class represents current status of subscription of the metric

    :ivar name: Name of the metric
    :ivar kind: metric
    :ivar config: Metric collection configuration
    """

    def __init__(self, *args, **kwargs):
        super(ObjDict, self).__init__(*args, **kwargs)


class LogsUploadRequest(ObjDict):
    """
     Request class for log upload API

     :ivar device_path: absolute path of file on device
     :ivar file_name: Name of the file in cloud storage. If not provided, file name is derived from the device_path
     :ivar max_upload_rate: network bandwidth to be used for upload
     :ivar override: If true overrides the destination file
     :ivar purge_after: If true purges the log file after upload
     :ivar metadata: Key/value to be associated with log file
    """

    def __init__(self, device_path, file_name='', max_upload_rate=DEFAULT_LOG_UPLOAD_BANDWIDTH, override=False, purge_after=False,
                 metadata=None):
        super(ObjDict, self).__init__()
        self.device_path = device_path
        self.file_name = file_name
        self.max_upload_rate = max_upload_rate
        self.override = override
        self.purge_after = purge_after
        self.metadata = metadata if metadata else {}
        self._validate()

    def _validate(self):
        if is_empty(self.device_path) or not isinstance(self.device_path, six.string_types):
            raise InvalidParameterException('file must be valid')

    def to_json(self):
        js = self.to_dict()
        ret = {}
        for key, value in js.items():
            if value is not None and str(value) != '':
                ret[key] = value
        return ret


class LogUploadStatus(ObjDict):
    """
    This class instance represent current status of the upload request

    :ivar status: Represents the current file upload status
    :ivar error_message: Any error message during file upload
    :ivar creator: User guid who initiated the upload operation
    :ivar created_at: Timestamp at which logs upload initiated
    :ivar request_uuid: An uniquely identifier associated with current upload
    :ivar filename: Name of the file which is to be uploaded
    :ivar updated_at: Timestamp at which file is updated
    """

    def __init__(self, *args, **kwargs):
        super(ObjDict, self).__init__(*args, **kwargs)
        # The SharedURL class is based on the ObjBase but LogUploadStatus is not. This logic acts as the glue that
        # deserializes the shared_urls and puts it back in the ObjDict.
        if 'shared_urls' in self:
            url_list = []
            for shared_url in self['shared_urls']:
                url_list.append(SharedURL.deserialize(shared_url))
            self['shared_urls'] = url_list


class LogUploads(ObjDict):
    """
    This class represents the status and other attributes associated with upload files.

    :ivar status: Represents the current upload status
    :ivar content_length: Length in bytes
    :ivar creator: User guid who initiated the upload operation
    :ivar created_at: Timestamp at which logs upload initiated
    :ivar request_uuid: UUID associated with the request
    :ivar creation_time: Timestamp at which file upload is completed
    :ivar updated_at: Timestamp at which last file updated happened
    :ivar filename: Name of the file which is to be uploaded
    :ivar last_modified: represents the time at which last modification done to the file on cloud
    :ivar metadata: key/value pair associated with upload request
    """

    def __init__(self, *args, **kwargs):
        super(ObjDict, self).__init__(*args, **kwargs)


class SharedURL(ObjBase):
    """
    This class represents the Shared URL for Logs uploaded from the Device.

    :param request_uuid: Request GUID of the Log file
    :type request_uuid: str
    :param expiry_time: Datetime object for the time at which Shared URL is supposed to expire.
    :type expiry_time: :py:class:`datetime.datetime`
    :param creator: User GUID that created the Shared URL
    :type creator: str
    :param created_at: Timestamp at which Shared URL was created
    :type created_at: str
    """

    def __init__(self, request_uuid, expiry_time):
        self.validate(request_uuid, expiry_time)
        self.request_uuid = request_uuid
        self.expiry_time = expiry_time
        self.url_uuid = None
        self.creator = None
        self.created_at = None

    @property
    def url(self):
        """
        The generated public URL.

        :raises: :py:class:`~rapyuta_io.utils.errors.InvalidParameterException`: If the Shared URL is not created
        """
        if not hasattr(self, '_device_api_host'):
            raise InvalidParameterException('SharedURL must be created first')
        return '{}/{}/{}'.format(self._device_api_host, SHARED_URL_PATH, self.url_uuid)

    def serialize(self):
        return {
            'expiry_time': mktime(self.expiry_time.timetuple())
        }

    def get_serialize_map(self):
        pass

    def get_deserialize_map(self):
        return {
            'expiry_time': ('expiry_time', lambda data: parse(data) if data is not None else None),
            'created_at': 'created_at',
            'creator': 'creator',
            'url_uuid': 'url_uuid'
        }

    @staticmethod
    def validate(request_uuid, expiry_time):
        if not (isinstance(request_uuid, six.binary_type) or isinstance(request_uuid, six.string_types)) or request_uuid == '':
            raise InvalidParameterException('request_uuid must be a non-empty string')
        if not isinstance(expiry_time, datetime) or expiry_time is None:
            raise InvalidParameterException('expiry_time must be a datetime.datetime')
