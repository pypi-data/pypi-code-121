# encoding: utf-8
from __future__ import absolute_import
import enum
import time

from rapyuta_io.clients.provision_client import ProvisionClient
from rapyuta_io.utils import ObjDict, to_objdict, DeploymentNotRunningException, RetriesExhausted
from rapyuta_io.utils.settings import BIND_ID, DEFAULT_SLEEP_INTERVAL, \
    DEPLOYMENT_STATUS_RETRY_COUNT
from rapyuta_io.utils.partials import PartialMixin
import six
from six.moves import range


def _poll_till_ready(instance, retry_count, sleep_interval):
    # TODO: convert into DeploymentPollerMixin (pollers.py)
    """

    :param instance:  instance can be a deployment, volume, or a routed network instance with get_status method
    :param retry_count: Parameter to specify the retries.
    :param sleep_interval: Parameter to specify the interval between retries.

    """
    dep_status = None
    for _ in range(retry_count):
        dep_status = instance.get_status()

        if dep_status.phase == DeploymentPhaseConstants.SUCCEEDED.value:
            if dep_status.status in [DeploymentStatusConstants.RUNNING.value,
                                     DeploymentStatusConstants.AVAILABLE.value,
                                     DeploymentStatusConstants.RELEASED.value]:
                return dep_status
            time.sleep(sleep_interval)
            continue
        if dep_status.phase == DeploymentPhaseConstants.INPROGRESS.value:
            time.sleep(sleep_interval)
            continue
        if dep_status.phase == DeploymentPhaseConstants.PROVISIONING.value:
            errors = dep_status.errors or []
            if 'DEP_E153' not in errors:  # DEP_E153 (image-pull error) will persist across retries
                time.sleep(sleep_interval)
                continue

        msg = 'Deployment might not progress: phase={} status={} errors={}'.format(
            dep_status.phase, dep_status.status, dep_status.errors)
        raise DeploymentNotRunningException(msg, deployment_status=dep_status)

    msg = 'Retries exhausted: Tried {} times with {}s interval.'.format(retry_count,
                                                                        sleep_interval)
    if dep_status:
        msg += ' Deployment: phase={} status={} errors={}'.format(dep_status.phase, dep_status.status,
                                                                  dep_status.errors)
    raise RetriesExhausted(msg)


class DeploymentPhaseConstants(str, enum.Enum):
    """
    Enumeration variables for the deployment phase

    Deployment phase can be any of the following types \n
    DeploymentPhaseConstants.INPROGRESS \n
    DeploymentPhaseConstants.PROVISIONING \n
    DeploymentPhaseConstants.SUCCEEDED \n
    DeploymentPhaseConstants.FAILED_TO_START \n
    DeploymentPhaseConstants.PARTIALLY_DEPROVISIONED \n
    DeploymentPhaseConstants.DEPLOYMENT_STOPPED \n
    """

    def __str__(self):
        return str(self.value)

    INPROGRESS = 'In progress'
    PROVISIONING = 'Provisioning'
    SUCCEEDED = 'Succeeded'
    FAILED_TO_START = 'Failed to start'
    PARTIALLY_DEPROVISIONED = 'Partially deprovisioned'
    DEPLOYMENT_STOPPED = 'Deployment stopped'


class DeploymentStatusConstants(str, enum.Enum):
    """
    Enumeration variables for the deployment status

    Deployment status can be any of the following types \n
    DeploymentStatusConstants.RUNNING \n
    DeploymentStatusConstants.PENDING \n
    DeploymentStatusConstants.ERROR \n
    DeploymentStatusConstants.UNKNOWN \n
    DeploymentStatusConstants.STOPPED \n
    """

    def __str__(self):
        return str(self.value)

    RUNNING = 'Running'
    PENDING = 'Pending'
    ERROR = 'Error'
    UNKNOWN = 'Unknown'
    STOPPED = 'Stopped'

    # Disk statuses, not meant to be documented
    BOUND = 'Bound'
    RELEASED = 'Released'
    AVAILABLE= 'Available'
    FAILED = 'Failed'


class DeploymentStatus(ObjDict):
    """
    DeploymentStatus class

    :ivar deploymentId: Deployment Id.
    :ivar name: Deployment name.
    :ivar packageId: Package Id.
    :ivar status: Deployment status
    :ivar phase: Deployment phase
    :ivar errors: Deployment errors
    :ivar componentInfo: List containing the deployment components and their status.
    :ivar dependentDeploymentStatus: Dependent deployment status.
    :ivar packageDependencyStatus: Package dependency status.
    """

    def __init__(self, *args, **kwargs):
        super(ObjDict, self).__init__(*args, **kwargs)


class Deployment(PartialMixin, ObjDict):
    """
    Deployment class represents a running deployment. Member variables of the class represent the
    properties of the deployment. \n
    Variables marked as (full-only) are only available on a full object. Use `refresh()` to convert a
    partial object into a full one.

    :ivar deploymentId: Deployment Id.
    :ivar name: Deployment name.
    :ivar packageId: Package Id.
    :ivar packageName: Package Name.
    :ivar packageAPIVersion: Package API Version.
    :ivar planId: Plan Id.
    :ivar bindable: Deployment is bindable or not.
    :ivar labels: (full-only) Labels associated with the deployment.
    :ivar parameters: (full-only) Deployment parameters.
    :ivar componentInfo: (full-only) List of component details.
    :ivar componentInstanceIds: (full-only) List of component instance ids.
    :ivar dependentDeployments: (full-only) List of dependent deployments.
    :ivar dependentDeploymentStatus: (full-only) Dependent deployments status details.
    :ivar packageDependencyStatus: (full-only) Package dependency status details.
    :ivar coreNetworks: (full-only) Routed and Native network details.
    :ivar phase: Phase of the deployment.
    :vartype phase: :py:class:`~rapyuta_io.clients.deployment.DeploymentPhaseConstants`
    :ivar status: (full-only) Status of the deployment.
    :vartype status: :py:class:`~rapyuta_io.clients.deployment.DeploymentStatusConstants`
    :ivar provisionContext: (full-only) Context set during provisioning.
    :ivar currentGeneration: (full-only) Build generation number.
    :ivar errors: (full-only) List of errors.
    :ivar inUse: Deployment is in use or not.
    :ivar ownerProject: Owner project guid.
    :ivar creator: Creator user guid.
    :ivar CreatedAt: Date of creation.
    :ivar UpdatedAt: Date of updation.
    :ivar DeletedAt: Date of deletion.
    """

    def __init__(self, *args, **kwargs):
        super(ObjDict, self).__init__(*args, **kwargs)

    def _get_status(self, retry_limit=0):
        provision_client = ProvisionClient(self._host, self._auth_token, self._project)
        return provision_client.deployment_status(self.deploymentId, retry_limit)

    def refresh(self):
        full_deployment = self._get_status()
        for key, value in six.iteritems(full_deployment):
            setattr(self, key, to_objdict(value))
        self.is_partial = False

    def get_status(self, retry_limit=0):
        """
        Get the deployment status

        :param retry_limit: Optional parameter to specify the number of retry attempts to be
              carried out if any failures occurs during the API call.
        :type retry_limit: int
        :returns: instance of class :py:class:`DeploymentStatus`:
        :raises: :py:class:`APIError`: If the get deployment status api returns an error, the status
                code is anything other than 200/201

        Following example demonstrates how to get a deployment status

             >>> from rapyuta_io import Client
             >>> client = Client(auth_token='auth_token', project="project_guid")
             >>> deployment = client.get_deployment('test_deployment_id')
             >>> deployment.get_status()

        """
        return DeploymentStatus(to_objdict(self._get_status(retry_limit)))

    def deprovision(self, retry_limit=0):
        """
        Deprovision the deployment instance represented by the corresponding  :py:class:`~Deployment`: class.

        :param retry_limit:
        :return: True if de-provision is successful, False otherwise
        :raises: :py:class:`~rapyuta_io.utils.error.ParameterMissingException`: If the planId or
                 deploymentId is missing in the request.
        :raises: :py:class:`~rapyuta_io.utils.error.APIError`: If the deprovision-api returns an error, the status code
            is anything other than 200/201

        Following example demonstrates how to deprovision a deployment

             >>> from rapyuta_io import Client
             >>> client = Client(auth_token='auth_token', project="project_guid")
             >>> deployment = client.get_deployment('test_deployment_id')
             >>> deployment.deprovision()

        """
        provision_client = ProvisionClient(self._host, self._auth_token, self._project)
        return provision_client.deprovision(self.deploymentId, self.planId, self.packageId,
                                            retry_limit)

    def get_service_binding(self, binding_id=None, retry_limit=0):
        """
        Get the service bindings of the deployment. Service Bindings contain the credentials that
        can be used to communicate with the deployment.

        :param binding_id: Optional parameter Binding Id
        :type binding_id: string
        :param retry_limit: Optional parameter to specify the number of retry attempts to be
              carried out if any failures occurs during the API call.
        :type retry_limit: int
        :return: Service binding dictionary containing credentials.
        :raises: :py:class:`ServiceBindingError`: If the request failed to get the service binding.
        :raises: :py:class:`APIError`: If service binding api return an error, the status code is
            anything other than 200/201

        Following example demonstrates how to get the service binding

             >>> from rapyuta_io import Client
             >>> client = Client(auth_token='auth_token', project="project_guid")
             >>> deployment = client.get_deployment('test_deployment_id')
             >>> deployment.get_service_binding()

        """

        if binding_id is None:
            binding_id = BIND_ID
        provision_client = ProvisionClient(self._host, self._auth_token, self._project)
        credentials = provision_client.service_binding(self.deploymentId, self.planId,
                                                       self.packageId, binding_id, retry_limit)
        return credentials

    def poll_deployment_till_ready(self, retry_count=DEPLOYMENT_STATUS_RETRY_COUNT,
                                   sleep_interval=DEFAULT_SLEEP_INTERVAL):
        """

        Wait for the deployment to be ready

        :param retry_count: Optional parameter to specify the retries. Default value is 15
        :param sleep_interval: Optional parameter to specify the interval between retries.
                Default value is 6 Sec.
        :return: instance of class :py:class:`DeploymentStatus`:
        :raises: :py:class:`APIError`: If service binding api return an error, the status code is
            anything other than 200/201
        :raises: :py:class:`DeploymentNotRunningException`: If the deployment’s state might not 
            progress due to errors.
        :raises: :py:class:`RetriesExhausted`: If number of polling retries exhausted before the 
            deployment could succeed or fail.

        Following example demonstrates use of poll_deployment_till_ready, and in case of deployment
        failure uses error codes to check whether it was due to device being offline.
        Read more on error codes: https://userdocs.rapyuta.io/6_troubleshoot/611_deployment-error-codes/

            >>> from rapyuta_io import Client
            >>> from rapyuta_io.utils.error import (DeploymentNotRunningException,
            ...     RetriesExhausted)
            >>> client = Client(auth_token='auth_token', project="project_guid")
            >>> deployment = client.get_deployment('test_deployment_id')
            >>> try:
            ...     dep_status = deployment.poll_deployment_till_ready()
            ...     print dep_status
            ... except RetriesExhausted as e:
            ...     print e, 'Retry again?'
            ... except DeploymentNotRunningException as e:
            ...     print e
            ...     if 'DEP_E151' in e.deployment_status.errors:
            ...         print 'Device is either offline or not reachable'


        """
        return _poll_till_ready(self, retry_count, sleep_interval)

    def get_component_instance_id(self, component_name):
        for component_info in self.componentInfo:
            component_instance_id = component_info.get('componentInstanceID')
            if component_info.get('name') == component_name:
                return component_instance_id
        return None
