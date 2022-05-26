# coding=utf-8
from __future__ import absolute_import

import rapyuta_io.clients.package  # to prevent cyclic import
from rapyuta_io.clients.deployment import _poll_till_ready
from rapyuta_io.clients.common_models import InternalDeploymentStatus
from rapyuta_io.utils import RestClient
from rapyuta_io.utils.error import InvalidParameterException, OperationNotAllowedError, ParameterMissingException
from rapyuta_io.utils.rest_client import HttpMethod
from rapyuta_io.utils.utils import create_auth_header, get_api_response_data
from rapyuta_io.utils.object_converter import ObjBase, enum_field, nested_field
from rapyuta_io.utils.partials import PartialMixin
import six


class NativeNetwork(PartialMixin, ObjBase):
    """
    NativeNetwork represents native network. \n
    Variables marked as (full-only) are only available on a full object. Use `refresh()` to convert a
    partial object into a full one.

    :ivar name: name of the native network
    :vartype name: str
    :ivar runtime: runtime of the native network
    :vartype runtime: :py:class:`~rapyuta_io.clients.package.Runtime`
    :ivar ros_distro: ROS distribution
    :vartype ros_distro: :py:class:`~rapyuta_io.clients.package.ROSDistro`
    :ivar parameters: parameters of the native network
    :vartype parameters: :py:class:`~rapyuta_io.clients.native_network.Parameters`
    :ivar created_at: creation time of the native network
    :vartype created_at: str
    :ivar updated_at: updating time of the native network
    :vartype updated_at: str
    :ivar guid: native network guid
    :vartype guid: str
    :ivar owner_project: project id
    :vartype owner_project: str
    :ivar creator: user id
    :vartype creator: str
    :ivar internal_deployment_guid: guid of the internal deployment
    :vartype internal_deployment_guid: str
    :ivar internal_deployment_status: internal deployment status of the native network
    :vartype internal_deployment_status: :py:class:`~rapyuta_io.clients.common_models.InternalDeploymentStatus`

    :param name: name of the native network
    :type name: str
    :param runtime: runtime of the native network
    :type runtime: :py:class:`~rapyuta_io.clients.package.Runtime`
    :param ros_distro: ROS distribution
    :type ros_distro: :py:class:`~rapyuta_io.clients.package.ROSDistro`
    :param parameters: parameters of the native network
    :type parameters: :py:class:`~rapyuta_io.clients.native_network.Parameters`
    """
    NATIVE_NETWORK_PATH = 'nativenetwork'

    def __init__(self, name, runtime, ros_distro, parameters=None):
        self.validate(name, runtime, ros_distro, parameters)
        self.name = name
        self.runtime = runtime
        self.ros_distro = ros_distro
        self.parameters = parameters
        self.created_at = None
        self.updated_at = None
        self.guid = None
        self.owner_project = None
        self.creator = None
        self.internal_deployment_guid = None
        self.internal_deployment_status = None

    @staticmethod
    def validate(name, runtime, ros_distro, parameters=None):
        if not name or not isinstance(name, six.string_types):
            raise InvalidParameterException('name must be a non-empty string')
        if ros_distro not in list(rapyuta_io.clients.package.ROSDistro.__members__.values()):
            raise InvalidParameterException('ros_distro must be one of rapyuta_io.clients.package.ROSDistro')
        if runtime not in list(rapyuta_io.clients.package.Runtime.__members__.values()):
            raise InvalidParameterException('runtime must be one of rapyuta_io.clients.package.Runtime')
        if ros_distro == rapyuta_io.clients.package.ROSDistro.NOETIC and \
                runtime == rapyuta_io.clients.package.Runtime.DEVICE:
            raise InvalidParameterException('device runtime does not support noetic ros_distro yet')
        if parameters is not None and not isinstance(parameters, Parameters):
            raise InvalidParameterException('parameters must be of type rapyuta_io.clients.native_network.Parameters')
        if runtime == rapyuta_io.clients.package.Runtime.DEVICE.value:
            if parameters is None:
                raise InvalidParameterException('parameters must be present for device runtime')
            if not parameters.device_id:
                raise InvalidParameterException('device_id field must be present in rapyuta_io.clients.'
                                                'native_network.Parameters object for device runtime')
            if not parameters.network_interface:
                raise InvalidParameterException('network_interface must be present in rapyuta_io.clients.'
                                                'native_network.Parameters object for device runtime')

    def get_deserialize_map(self):
        return {
            'name': 'name',
            'guid': 'guid',
            'owner_project': 'ownerProject',
            'creator': 'creator',
            'runtime': enum_field('runtime', rapyuta_io.clients.package.Runtime),
            'ros_distro': enum_field('rosDistro', rapyuta_io.clients.package.ROSDistro),
            'internal_deployment_guid': 'internalDeploymentGUID',
            'internal_deployment_status': nested_field('internalDeploymentStatus', InternalDeploymentStatus),
            'parameters': nested_field('parameters', Parameters),
            'created_at': 'CreatedAt',
            'updated_at': 'UpdatedAt'
        }

    def get_serialize_map(self):
        return {
            'name': 'name',
            'runtime': 'runtime',
            'rosDistro': 'ros_distro',
            'parameters': 'parameters'
        }

    def poll_native_network_till_ready(self, retry_count=120, sleep_interval=5):
        # TODO: implement and use DeploymentPollerMixin. see _poll_till_ready
        """

        Wait for the native network to be ready

        :param retry_count: Optional parameter to specify the retries. Default value is 120
        :param sleep_interval: Optional parameter to specify the interval between retries.
                Default value is 5 Sec.
        :return: instance of class :py:class:`~rapyuta_io.clients.common_models.InternalDeploymentStatus`:
        :raises: :py:class:`APIError`: If service binding api return an error, the status code is
            anything other than 200/201
        :raises: :py:class:`DeploymentNotRunningException`: If the deployment’s state might not
            progress due to errors.
        :raises: :py:class:`RetriesExhausted`: If number of polling retries exhausted before the
            deployment could succeed or fail.

        Following example demonstrates use of poll_native_network_till_ready:

            >>> from rapyuta_io import Client
            >>> from rapyuta_io.utils.error import (DeploymentNotRunningException,
            ...     RetriesExhausted)
            >>> client = Client(auth_token='auth_token', project="project_guid")
            >>> native_network = client.get_native_network('network-guid')
            >>> try:
            ...     network_status = native_network.poll_native_network_till_ready()
            ...     print network_status
            ... except RetriesExhausted as e:
            ...     print e, 'Retry again?'
            ... except DeploymentNotRunningException as e:
            ...     print e, e.deployment_status

        """
        _poll_till_ready(self, retry_count, sleep_interval)
        return self

    def get_status(self):
        if self.guid is None:
            raise OperationNotAllowedError('resource has not been created')
        native_network = NativeNetwork.deserialize(self._get_full_resource())
        internal_deployment_status = native_network.internal_deployment_status
        internal_deployment_status.errors = native_network.get_error_code()
        return internal_deployment_status

    def _get_full_resource(self):
        url = '{}/{}/{}'.format(self._host, self.NATIVE_NETWORK_PATH, self.guid)
        headers = create_auth_header(self._auth_token, self._project)
        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()
        return get_api_response_data(response, parse_full=True)

    def refresh(self):
        NativeNetwork.deserialize(self._get_full_resource(), obj=self)
        self.is_partial = False

    def delete(self):

        """
        Delete the native network using the native network object.

        Following example demonstrates how to delete a native network using native network object:

        >>> from rapyuta_io import Client
        >>> client = Client(auth_token='auth_token', project='project_guid')
        >>> native_network = client.get_native_network(network_guid='network_guid')
        >>> native_network.delete()

        """

        url = '{}/{}/{}'.format(self._host, self.NATIVE_NETWORK_PATH, self.guid)
        headers = create_auth_header(self._auth_token, self._project)
        response = RestClient(url).method(HttpMethod.DELETE).headers(headers).execute()
        get_api_response_data(response, parse_full=True)
        return True

    def get_error_code(self):
        getattr(self.internal_deployment_status, "error_code", [])


class Parameters(ObjBase):
    """
    Parameters represents Native Network Parameters

    :ivar limits: Values corresponding to limits of the parameters
    :vartype limits: :py:class:`~rapyuta_io.clients.native_network.NativeNetworkLimits`
    :ivar device_id: device_id of device on which the native network is deployed.
    :vartype device_id: str
    :ivar network_interface: network interface to which native network is binded.
    :vartype network_interface: str
    :ivar restart_policy: restart policy of native network.
    :vartype restart_policy: enum :py:class:`~rapyuta_io.clients.package.RestartPolicy`

    :param limits: Values corresponding to limits of the parameters
    :type limits: :py:class:`~rapyuta_io.clients.native_network.NativeNetworkLimits`
    :param device: device on which the native network is deployed.
    :type device: :py:class:`~rapyuta_io.clients.device.Device`
    :param network_interface: network interface to which native network is binded.
    :type network_interface: str
    :param restart_policy: restart policy of native network.
    :type restart_policy: enum :py:class:`~rapyuta_io.clients.package.RestartPolicy`
    """

    def __init__(self, limits=None, device=None, network_interface=None, restart_policy=None):
        self.validate(limits, device, network_interface, restart_policy)
        self.limits = limits
        self.device_id = device and device.uuid
        self.network_interface = network_interface
        self.restart_policy = restart_policy

    @staticmethod
    def validate(limits, device, network_interface, restart_policy):
        if device is None:
            if not isinstance(limits, _Limits):
                raise InvalidParameterException('limits must be one of '
                                                'rapyuta_io.clients.native_network.NativeNetworkLimits')
            return
        if not isinstance(device, rapyuta_io.clients.device.Device):
            raise InvalidParameterException('device must be of type rapyuta_io.clients.device.Device')
        if not device.get('uuid'):
            raise InvalidParameterException('uuid field must be present in rapyuta_io.clients.device.Device object')
        if not device.get('ip_interfaces'):
            raise InvalidParameterException(
                'ip_interfaces field must be present in rapyuta_io.clients.device.Device object')
        ip_interfaces = device.ip_interfaces or {}
        if network_interface not in list(ip_interfaces.keys()):
            raise InvalidParameterException('NETWORK_INTERFACE should be in {}'.format(list(ip_interfaces.keys())))
        if restart_policy is not None and (
                restart_policy not in list(rapyuta_io.clients.package.RestartPolicy.__members__.values())):
            raise InvalidParameterException('RestartPolicy must be one of rapyuta_io.clients.package.RestartPolicy')

    def get_deserialize_map(self):
        return {
            'limits': nested_field('limits', _Limits),
            'device_id': 'device_id',
            'network_interface': 'NETWORK_INTERFACE',
            'restart_policy': enum_field('restart_policy', rapyuta_io.clients.package.RestartPolicy),
        }

    def get_serialize_map(self):
        return {
            'limits': 'limits',
            'device_id': 'device_id',
            'NETWORK_INTERFACE': 'network_interface',
            'restart_policy': 'restart_policy'
        }


class _Limits(ObjBase):
    """
    Limits represents cpu, memory details of the parameter

    :ivar cpu: cpu
    :vartype cpu: Union [float, integer]
    :ivar memory: memory
    :vartype memory: integer

    :param cpu: cpu
    :type cpu: Union [float, integer]
    :param memory: memory
    :type memory: integer
    """

    def __init__(self, cpu, memory):
        self.validate(cpu, memory)
        self.cpu = cpu
        self.memory = memory

    @staticmethod
    def validate(cpu, memory):
        if (not isinstance(cpu, float) and not isinstance(cpu, six.integer_types)) or cpu <= 0:
            raise InvalidParameterException('cpu must be a positive float or integer')
        if not isinstance(memory, six.integer_types) or memory <= 0:
            raise InvalidParameterException('memory must be a positive integer')

    def get_deserialize_map(self):
        return {
            'cpu': 'cpu',
            'memory': 'memory'
        }

    def get_serialize_map(self):
        return {
            'cpu': 'cpu',
            'memory': 'memory'
        }


class NativeNetworkLimits(object):
    """
    NativeNetworkLimits may be one of: \n
    NativeNetworkLimits.X_SMALL (cpu: 0.5core, memory: 2GB) \n
    NativeNetworkLimits.SMALL (cpu: 1core, memory: 4GB) \n
    NativeNetworkLimits.MEDIUM (cpu: 2cores, memory: 8GB) \n
    NativeNetworkLimits.LARGE (cpu: 4cores, memory: 16GB) \n
    """

    X_SMALL = _Limits(0.5, 2048)
    SMALL = _Limits(1, 4096)
    MEDIUM = _Limits(2, 8192)
    LARGE = _Limits(4, 16384)
