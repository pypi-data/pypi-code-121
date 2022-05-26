# coding=utf-8
from __future__ import absolute_import
import six

from rapyuta_io.clients.deployment import _poll_till_ready
from rapyuta_io.utils import ObjDict
from rapyuta_io.utils import RestClient
from rapyuta_io.utils import to_objdict
from rapyuta_io.utils.rest_client import HttpMethod
from rapyuta_io.utils.utils import create_auth_header, get_api_response_data
from rapyuta_io.utils.error import InvalidParameterException
from rapyuta_io.utils.partials import PartialMixin


class RoutedNetwork(PartialMixin, ObjDict):
    """
    RoutedNetwork represents Routed Network. \n
    Variables marked as (full-only) are only available on a full object. Use `refresh()` to convert a
    partial object into a full one.

    :ivar name: Name of RoutedNetwork.
    :vartype name: str
    :ivar guid: GUID
    :vartype guid: str
    :ivar runtime: Runtime of RoutedNetwork
    :vartype runtime: :py:class:`~rapyuta_io.clients.package.Runtime`
    :ivar rosDistro: ROSDistro of RoutedNetwork
    :vartype rosDistro: :py:class:`~rapyuta_io.clients.package.ROSDistro`
    :ivar shared: Whether the network can be shared.
    :vartype shared: bool
    :ivar parameters: parameters of the routed network
    :vartype parameters: :py:class:`~rapyuta_io.clients.routed_network.Parameters`
    :ivar phase: Deployment phase
    :vartype phase: :py:class:`~rapyuta_io.clients.deployment.DeploymentPhaseConstants`
    :ivar status: (full-only) Deployment status
    :vartype status: :py:class:`~rapyuta_io.clients.deployment.DeploymentStatusConstants`
    :ivar error_code: Deployment errors
    :ivar internalDeploymentGUID: guid of the internal deployment
    :vartype internalDeploymentGUID: str
    :ivar internalDeploymentStatus: Internal deployment status of the routed network. Has attributes: phase,
        status (full-only), and errors.
    :vartype internalDeploymentStatus: :py:class:`~rapyuta_io.clients.common_models.InternalDeploymentStatus`
    :ivar ownerProject: Owner project guid.
    :vartype ownerProject: str
    :ivar creator: Creator user guid.
    :vartype creator: str
    :ivar CreatedAt: Date of creation.
    :vartype CreatedAt: str
    :ivar UpdatedAt: Date of updation.
    :vartype UpdatedAt: str
    :ivar DeletedAt: Date of deletion.
    :vartype DeletedAt: str
    """

    ROUTED_NETWORK_PATH = 'routednetwork'

    def __init__(self, *args, **kwargs):
        super(ObjDict, self).__init__(*args, **kwargs)

    def poll_routed_network_till_ready(self, retry_count=120, sleep_interval=5):
        # TODO: implement and use DeploymentPollerMixin. see _poll_till_ready
        """

        Wait for the routed network to be ready

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

        Following example demonstrates use of poll_routed_network_till_ready:

            >>> from rapyuta_io import Client
            >>> from rapyuta_io.utils.error import (DeploymentNotRunningException,
            ...     RetriesExhausted)
            >>> client = Client(auth_token='auth_token', project="project_guid")
            >>> routed_network = client.get_routed_network('network-guid')
            >>> try:
            ...     network_status = routed_network.poll_routed_network_till_ready()
            ...     print network_status
            ... except RetriesExhausted as e:
            ...     print e, 'Retry again?'
            ... except DeploymentNotRunningException as e:
            ...     print e, e.deployment_status

        """
        _poll_till_ready(self, retry_count, sleep_interval)
        return self

    def get_status(self):
        routed_network = RoutedNetwork(to_objdict(self._get_full_resource()))
        internal_deployment_status = routed_network.internalDeploymentStatus
        internal_deployment_status.errors = routed_network.get_error_code()
        return internal_deployment_status

    def _get_full_resource(self):
        url = '{}/{}/{}'.format(self._host, self.ROUTED_NETWORK_PATH, self.guid)
        headers = create_auth_header(self._auth_token, self._project)
        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()
        return get_api_response_data(response, parse_full=True)

    def refresh(self):
        full_network = self._get_full_resource()
        for key, value in six.iteritems(full_network):
            setattr(self, key, to_objdict(value))
        self.is_partial = False

    def delete(self):

        """
        Delete the routed network using the routed network object.

        Following example demonstrates how to delete a routed network using routed network object:

        >>> from rapyuta_io import Client
        >>> client = Client(auth_token='auth_token', project='project_guid')
        >>> routed_network = client.get_routed_network(network_guid='network_guid')
        >>> routed_network.delete()

        """

        url = '{}/{}/{}'.format(self._host, self.ROUTED_NETWORK_PATH, self.guid)
        headers = create_auth_header(self._auth_token, self._project)
        response = RestClient(url).method(HttpMethod.DELETE).headers(headers).execute()
        get_api_response_data(response, parse_full=True)
        self.clear()
        return True

    def get_error_code(self):
        return self.internalDeploymentStatus.error_code if hasattr(self.internalDeploymentStatus, 'error_code') else []


class Parameters(ObjDict):
    """
    Parameters represents Routed Network Parameters

    :ivar limits: Values corresponding to limits of the parameters
    :vartype limits: :py:class:`~rapyuta_io.clients.routed_network.RoutedNetworkLimits`

    :param limits: Values corresponding to limits of the parameters
    :type limits: :py:class:`~rapyuta_io.clients.routed_network.RoutedNetworkLimits`
    """

    def __init__(self, limits):
        self.validate(limits)
        super(ObjDict, self).__init__(limits=limits)

    @staticmethod
    def validate(limits):
        if not isinstance(limits, _Limits):
            raise InvalidParameterException('limits must be one of '
                                            'rapyuta_io.clients.routed_network.RoutedNetworkLimits')


class _Limits(ObjDict):
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
        super(ObjDict, self).__init__(cpu=cpu, memory=memory)

    @staticmethod
    def validate(cpu, memory):
        if (not isinstance(cpu, float) and not isinstance(cpu, six.integer_types)) or cpu <= 0:
            raise InvalidParameterException('cpu must be a positive float or integer')
        if not isinstance(memory, six.integer_types) or memory <= 0:
            raise InvalidParameterException('memory must be a positive integer')


class RoutedNetworkLimits(object):
    """
    RoutedNetworkLimits may be one of: \n
    RoutedNetworkLimits.SMALL (cpu: 1core, memory: 4GB) \n
    RoutedNetworkLimits.MEDIUM (cpu: 2cores, memory: 8GB) \n
    RoutedNetworkLimits.LARGE (cpu: 4cores, memory: 16GB) \n
    """
    SMALL = _Limits(1, 4096)
    MEDIUM = _Limits(2, 8192)
    LARGE = _Limits(4, 16384)
