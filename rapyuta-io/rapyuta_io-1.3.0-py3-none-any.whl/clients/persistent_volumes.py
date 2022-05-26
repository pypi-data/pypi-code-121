# encoding: utf-8
from __future__ import absolute_import
import enum

from rapyuta_io.clients import ProvisionClient
from rapyuta_io.clients.deployment import DeploymentPhaseConstants, _poll_till_ready
from rapyuta_io.clients.package import ProvisionConfiguration, Runtime
from rapyuta_io.clients.plan import Plan
from rapyuta_io.utils import ObjDict, to_objdict, InvalidParameterException, DeploymentNotRunningException
from rapyuta_io.utils.settings import DEPLOYMENT_STATUS_RETRY_COUNT, DEFAULT_SLEEP_INTERVAL
from rapyuta_io.utils.partials import PartialMixin

import six

VOLUME_COMPONENT = 'volumeComponent'


class DiskType(str, enum.Enum):
    """
    Enumeration variables for the Volume Type. The type may be 'Default' or 'SSD' \n
    DiskType.DEFAULT \n
    DiskType.SSD
    """

    def __str__(self):
        return str(self.value)

    SSD = 'ssd'
    DEFAULT = 'ssd'


class DiskCapacity(int, enum.Enum):
    """
    Enumeration variables for disk capacity. The type may be one of the following \n
    DiskCapacity.GiB_4 \n
    DiskCapacity.GiB_8 \n
    DiskCapacity.GiB_16 \n
    DiskCapacity.GiB_32 \n
    DiskCapacity.GiB_64 \n
    DiskCapacity.GiB_128 \n
    DiskCapacity.GiB_256 \n
    DiskCapacity.GiB_512 \n
    """

    def __str__(self):
        return str(self.value)

    GiB_4 = 4
    GiB_8 = 8
    GiB_16 = 16
    GiB_32 = 32
    GiB_64 = 64
    GiB_128 = 128
    GiB_256 = 256
    GiB_512 = 512


class VolumeInstanceStatus(ObjDict):
    """
    VolumeInstanceStatus class

    :ivar deploymentId: Deployment Id.
    :ivar name: Volume instance name.
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


class PersistentVolumes(ObjDict):
    """
    PersistentVolumes class represents a a persistent volume package. It contains methods to create
    persistent volume instance and listing all the instances.

    :ivar packageId: Id of the package.
    :ivar packageName: Package name.
    :ivar packageVersion: Version of the package.
    :ivar apiVersion: Package API Version.
    :ivar bindable: Package is bindable or not.
    :ivar description: Description of the package.
    :ivar category: Package category.
    :ivar plans: List of plans associated with the package.
    :vartype plans: list(:py:class:`~rapyuta_io.clients.plan.Plan`)
    :ivar isPublic: Boolean denoting whether the package is public or not.
    :ivar status: Status of the package.
    :ivar tags: Tags associated with the package.
    :ivar buildGeneration: Build generation.
    :ivar ownerProject: Owner project guid.
    :ivar creator: Creator user guid.
    :ivar CreatedAt: Date of creation.
    :ivar UpdatedAt: Date of updation.
    :ivar DeletedAt: Date of deletion.

    """

    def __init__(self, *args, **kwargs):
        super(ObjDict, self).__init__(*args, **kwargs)
        plan = Plan(to_objdict(self.plans[0]))
        self.plans = [plan]

    def _update_auth_token(self, objects):
        for obj in objects:
            setattr(obj, '_host', self._host)
            setattr(obj, '_auth_token', self._auth_token)
            setattr(obj, '_project', self._project)
        return

    def create_volume_instance(self, name, capacity, disk_type=DiskType.DEFAULT, retry_limit=0):
        """
        Create a volume instance

        :param name: name of the volume instance
        :type name: str
        :param capacity: disk capacity of the volume instance
        :type capacity: enum :py:class:`~DiskCapacity`
        :param disk_type: Type of disk to be deployed. Allowed values are - default or ssd
        :type disk_type: enum :py:class:`~DiskType`
        :param retry_limit: Optional parameter to specify the number of retry attempts to be
               carried out if any failures occurs during the API call.
        :type retry_limit: int
        :returns: volume instance
        :raises: :py:class:`InvalidParameterException`: If the disk type and volume capacity
                 parameters are missing or invalid.
        :raises: :py:class:`APIError`: If the api return an error, the status code is
            anything other than 200/201

        Following example demonstrates how to create a volume instance

             >>> from rapyuta_io import Client
             >>> from rapyuta_io.clients.persistent_volumes import DiskType, DiskCapacity
             >>> client = Client(auth_token='auth_token', project='project_guid')
             >>> pv = client.get_persistent_volume()
             >>> pv.create_volume_instance(name='myVolume', capacity=DiskCapacity.GiB_32, disk_type=DiskType.SSD)

        """
        if disk_type not in list(DiskType.__members__.values()):
            raise InvalidParameterException('disk_type must be of rapyuta_io.clients.persistent_volumes.DiskType')
        # supporting integer values for backward compatibility
        if capacity not in list(DiskCapacity.__members__.values()) or not(isinstance(capacity, DiskCapacity)
                                                                          or isinstance(capacity, six.integer_types)):
            raise InvalidParameterException('capacity must be one of '
                                            'rapyuta_io.clients.persistent_volumes.DiskCapacity')
        disk_capacity = capacity if isinstance(capacity, six.integer_types) else capacity.value

        disk_payload = {'name': name, 'runtime': Runtime.CLOUD, 'capacity': disk_capacity, 'diskType': disk_type}
        provision_client = ProvisionClient(self._host, self._auth_token, self._project)
        response = provision_client.create_disk(disk_payload, retry_limit)
        disk = provision_client.get_disk(response['guid'], retry_limit)
        volume_instance = provision_client.deployment_status(disk['internalDeploymentGUID'], retry_limit)
        volume_instance = VolumeInstance(to_objdict(volume_instance))
        self._update_auth_token([volume_instance])
        volume_instance.is_partial = False
        return volume_instance

    def get_volume_instance(self, volume_instance_id, retry_limit=0):
        """
        Get a volume instance

        :param volume_instance_id: Volume instance Id
        :type volume_instance_id: string
        :param retry_limit: Optional parameter to specify the number of retry attempts to be
              carried out if any failures occurs during the API call.
        :type retry_limit: int
        :return: return instance of class :py:class:`VolumeInstance`:
        :raises: :py:class:`APIError`: If the api return an error, the status code is
            anything other than 200/201


        Following example demonstrates how to a volume instance

            >>> from rapyuta_io import Client
            >>> client = Client(auth_token='auth_token', project="project_guid")
            >>> persistent_volume = client.get_persistent_volume()
            >>> volume_instance = persistent_volume.get_volume_instance('instance_id')

        """
        provision_client = ProvisionClient(self._host, self._auth_token, self._project)
        instance = provision_client.deployment_status(volume_instance_id, retry_limit)
        volume_instance = VolumeInstance(to_objdict(instance))
        self._update_auth_token([volume_instance])
        volume_instance.is_partial = False
        return volume_instance

    def get_all_volume_instances(self, phases=None, retry_limit=0, deploymentGUIDs=None):
        """
        Get all persistent volume instances

        :param phases: optional parameter to filter out the deployments based on current deployment
        :type phases: list(DeploymentPhaseConstants)
        :param retry_limit: Optional parameter to specify the number of retry attempts to be
               carried out if any failures occurs during the API call.
        :type retry_limit: int
        :returns: List of volume instances
        :raises: :py:class:`APIError`: If the api return an error, the status code is
            anything other than 200/201

        Following example demonstrates how to create a volume instance

             >>> from rapyuta_io import Client, DeploymentPhaseConstants
             >>> client = Client(auth_token='auth_token', project="project_guid")
             >>> pv = client.get_persistent_volume()
             >>> pv.get_all_volume_instances()
             >>> volume_deployments_list_filtered_by_phase = pv.get_all_volume_instances(phases=
             >>>   [DeploymentPhaseConstants.SUCCEEDED, DeploymentPhaseConstants.PROVISIONING])

        """

        provision_client = ProvisionClient(self._host, self._auth_token, self._project)
        disks = provision_client.list_disk(deploymentGUIDs, retry_limit)
        volumes = list()
        for disk in disks:
            volume_instance = provision_client.deployment_status(disk['internalDeploymentGUID'], retry_limit)
            volume_instance = VolumeInstance(to_objdict(volume_instance))
            if phases is None or volume_instance.phase in phases:
                volumes.append(volume_instance)
        self._update_auth_token(volumes)
        return volumes


class VolumeInstance(PartialMixin, ObjDict):
    """
    VolumeInstance class represents a running Persistent Volume. \n
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

    def get_status(self, retry_limit=0):
        """
        Get the status of volume instance

        :param retry_limit: Optional parameter to specify the number of retry attempts to be
              carried out if any failures occurs during the API call.
        :type retry_limit: int
        :returns: instance of class :py:class:`DeploymentStatus`:
        :raises: :py:class:`APIError`: If the api return an error, the status code is
            anything other than 200/201

        Following example demonstrates how to get a deployment status

            >>> from rapyuta_io import Client
            >>> client = Client(auth_token='auth_token', project="project_guid")
            >>> persistent_volume = client.get_persistent_volume()
            >>> volume_instance = persistent_volume.get_volume_instance('instance_id')
            >>> volume_instance.get_status()

        """
        provision_client = ProvisionClient(self._host, self._auth_token, self._project)
        instance_status = provision_client.deployment_status(self.deploymentId, retry_limit)
        return VolumeInstanceStatus(to_objdict(instance_status))

    def refresh(self):
        provision_client = ProvisionClient(self._host, self._auth_token, self._project)
        full_volume_instance = provision_client.deployment_status(self.deploymentId, retry_limit=0)
        for key, value in six.iteritems(full_volume_instance):
            setattr(self, key, to_objdict(value))
        self.is_partial = False

    def poll_deployment_till_ready(self, retry_count=DEPLOYMENT_STATUS_RETRY_COUNT,
                                   sleep_interval=DEFAULT_SLEEP_INTERVAL):
        """

        Wait for the deployment to be ready

        :param retry_count: Optional parameter to specify the retries. Default value is 15
        :param sleep_interval: Optional parameter to specify the interval between retries.
              Default value is 6 Sec.
        :return: instance of class :py:class:`VolumeInstanceStatus`:
        :raises: :py:class:`APIError`: If service binding api return an error, the status code is
            anything other than 200/201
        :raises: :py:class:`DeploymentNotRunningException`: If the deployment's state might not
            progress due to errors
        :raises: :py:class:`RetriesExhausted`: If number of polling retries exhausted before the
            deployment could succeed or fail.

        Following example demonstrates use of poll_deployment_till_ready.

            >>> from rapyuta_io import Client
            >>> from rapyuta_io.utils.error import (DeploymentNotRunningException,
            ...     RetriesExhausted)
            >>> client = Client(auth_token='auth_token', project="project_guid")
            >>> persistent_volume = client.get_persistent_volume()
            >>> volume_instance = persistent_volume.get_volume_instance('instance_id')
            >>> try:
            ...     vol_status = volume_instance.poll_deployment_till_ready(sleep_interval=20)
            ...     print vol_status
            ... except RetriesExhausted as e:
            ...     print e, 'Retry again?'
            ... except DeploymentNotRunningException as e:
            ...     print e, e.deployment_status

        """
        return _poll_till_ready(self, retry_count, sleep_interval)

    def destroy_volume_instance(self, retry_limit=0):
        """
        Destroy a volume instance

        :param retry_limit: Optional parameter to specify the number of retry attempts to be
               carried out if any failures occurs during the API call.
        :type retry_limit: int
        :returns: True if volume is destroyed is successfully, False otherwise
        :raises: :py:class:`APIError`: If the api return an error, the status code is
            anything other than 200/201
        """
        provision_client = ProvisionClient(self._host, self._auth_token, self._project)
        disks = provision_client.list_disk([self.deploymentId], retry_limit)
        if len(disks):
            return provision_client.delete_disk(disks[0]['guid'], retry_limit)
