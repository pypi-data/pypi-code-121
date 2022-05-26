# encoding: utf-8
from __future__ import absolute_import
import json
import os

from rapyuta_io.clients import DeviceManagerClient, _ParamserverClient
from rapyuta_io.clients.catalog_client import CatalogClient
from rapyuta_io.clients.core_api_client import CoreAPIClient
from rapyuta_io.clients.deployment import Deployment
from rapyuta_io.clients.device import Device
from rapyuta_io.clients.native_network import NativeNetwork
from rapyuta_io.clients.organization import Organization
from rapyuta_io.clients.package import Package
from rapyuta_io.clients.project import Project
from rapyuta_io.clients.secret import Secret
from rapyuta_io.clients.persistent_volumes import VolumeInstance
from rapyuta_io.clients.rip_client import RIPClient
from rapyuta_io.clients.routed_network import RoutedNetwork, Parameters
from rapyuta_io.clients.build import Build, BuildStatus
from rapyuta_io.clients.rosbag import ROSBagJob, ROSBagJobStatus, ROSBagBlob, ROSBagBlobStatus
from rapyuta_io.clients.metrics import QueryMetricsRequest, StepInterval, SortOrder, \
    MetricOperation, MetricFunction, QueryMetricsResponse, ListMetricsRequest, ListTagKeysRequest, \
    Metric, Tags, ListTagValuesRequest
from rapyuta_io.utils import to_objdict
from rapyuta_io.utils.settings import VOLUME_PACKAGE_ID, default_host_config
from rapyuta_io.utils import InvalidAuthTokenException, InvalidParameterException
from rapyuta_io.clients.package import Runtime, ROSDistro, RestartPolicy
from rapyuta_io.utils.utils import get_api_response_data, valid_list_elements
from rapyuta_io.utils.partials import PartialMixin
import six


class Client(object):
    """
    Client class provides access to device, package, volume and deployment classes.

    """

    def __init__(self, auth_token, project=None):
        """
        Get new client object

        :param auth_token: Authentication token
        :type auth_token: string

        :param project: project_guid of the user
        :type project: string
        """

        super(Client, self).__init__()
        self._validate_auth_token(auth_token)
        self._catalog_client = CatalogClient(auth_token, project,
                                             catalog_api_host=self._get_api_endpoints('catalog_host'))
        self._core_api_client = CoreAPIClient(auth_token, project,
                                              core_api_host=self._get_api_endpoints('core_api_host'))
        self._dmClient = DeviceManagerClient(auth_token, project,
                                             device_api_host=self._get_api_endpoints('core_api_host'))
        self._paramserver_client = _ParamserverClient(auth_token, project, self._get_api_endpoints('core_api_host'))

    @staticmethod
    def _validate_auth_token(auth_token):
        if not auth_token:
            raise InvalidAuthTokenException("Authentication token is missing")

    @staticmethod
    def _get_api_endpoints(host_type):
        try:
            config_file = os.environ["RIO_CONFIG"]
            with open(config_file, 'r') as f:
                configuration = json.load(f)
            return configuration[host_type]
        except Exception:
            return default_host_config[host_type]

    def _add_auth_token(self, obj):
        setattr(obj, '_host', self._catalog_client._catalog_api_host)
        setattr(obj, '_auth_token', self._catalog_client._auth_token)
        setattr(obj, '_project', self._catalog_client._project)

    @staticmethod
    def get_auth_token(email, password):
        """
        Generate and fetch a new API Authentication Token.

        :param email: Email of the user account.
        :type email: str
        :param password: User password for the account.
        :type password: str
        :return: str

        Following example demonstrates how to get auth token

            >>> from rapyuta_io import Client
            >>> auth_token = Client.get_auth_token('email@example.com', 'password')
            >>> client = Client(auth_token, 'project-id')
        """
        rip_client = RIPClient(rip_host=Client._get_api_endpoints('rip_host'))
        return rip_client.get_auth_token(email, password)

    def set_project(self, project_guid):
        """
        Sets the current Project for the Client.

        :param project_guid: GUID of the Project

        Following example demonstrates how to set the Project for the Client.

            >>> from rapyuta_io import Client
            >>> from rapyuta_io.clients.project import Project
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> project = client.create_project(Project('secret-guid'))
            >>> client.set_project(project.guid)
            >>> persistent_volume = client.get_persistent_volume()

        """
        self._catalog_client.set_project(project_guid)
        self._core_api_client.set_project(project_guid)
        self._dmClient.set_project(project_guid)
        self._paramserver_client.set_project(project_guid)

    def get_persistent_volume(self, retry_limit=0):
        """
        Get persistent volume class

        :param retry_limit: Number of retry attempts to be carried out if any failures occurs during the API call.
        :type retry_limit: int
        :return: :py:class:`PersistentVolumes` class.
        :raises: :py:class:`APIError`: If the API returns an error, a status code
            of anything other than 200/201 is returned.

        Following example demonstrates how to get a persistent volume

            >>> from rapyuta_io import Client
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> persistent_volume = client.get_persistent_volume()

        """
        volume = self._catalog_client.get_package(VOLUME_PACKAGE_ID, retry_limit)
        self._add_auth_token(volume)
        return volume

    def get_package(self, package_id, retry_limit=0):

        """
        Get package class

        :param package_id: Package ID
        :type package_id: string
        :param retry_limit: Number of retry attempts to be carried out if any failures occurs \
                during the API call.
        :type retry_limit: int
        :return: an instance of :py:class:`~clients.catalog.Package` class.
        :raises: :py:class:`PackageNotFound`: If the given package id is not found.
        :raises: :py:class:`ComponentNotFoundException`: If the plan inside the package does
                  not have components.
        :raises: :py:class:`APIError`: If the API returns an error, a status code
            of anything other than 200/201 is returned.


        Following example demonstrates how to get the packages

            >>> from rapyuta_io import Client
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> package = client.get_package('test_package_id')

        """

        pkg = self._catalog_client.get_package(package_id, retry_limit)
        self._add_auth_token(pkg)
        return pkg

    def get_all_packages(self, retry_limit=0, name=None, version=None):

        """
        Get list of all packages created by the user.

        :param retry_limit: Number of retry attempts to be carried out if any failures occurs \
                during the API call.
        :type retry_limit: int
        :param name: Optional parameter to filter the packages based on substring of the package name.
        :type name: str
        :param version: Optional parameter to filter the packages based on the version of the package.
        :type version: str
        :return: List of all packages. Each package is an instance of
                 :py:class:`~clients.catalog.Package` class.
        :raises: :py:class:`APIError`: If the API returns an error, a status code
            of anything other than 200/201 is returned.


        Following example demonstrates how to get the packages

            >>> from rapyuta_io import Client
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> package_list = client.get_all_packages()
            >>> pacakge_list_filter_by_name = client.get_all_packages(name='test-name')
            >>> pacakge_list_filter_by_version = client.get_all_packages(version='v0.0.0')

        """

        if name and not isinstance(name, six.string_types):
            raise InvalidParameterException('name must be a string')
        if version and not isinstance(version, six.string_types):
            raise InvalidParameterException('version must be a string')
        package_list = self._catalog_client.get_all_packages(retry_limit)
        packages = list()
        for package in package_list['services']:
            if package['id'] == VOLUME_PACKAGE_ID:
                continue
            package = Package(to_objdict(package))
            self._add_auth_token(package)
            packages.append(package)
        if name:
            packages = [p for p in packages if p.packageName.find(name) != -1]
        if version:
            packages = [p for p in packages if p.packageVersion == version]
        return packages

    def delete_package(self, package_id):

        """
        Delete a package.

        :param package_id: ID of the package to be deleted.
        :type  package_id:  str

        Following example demonstrates how to delete a package.

        >>> from rapyuta_io import Client
        >>> client = Client(auth_token='auth_token', project='project_guid')
        >>> client.delete_package('package_id')

        """

        if not (isinstance(package_id, str) or isinstance(package_id, six.string_types)) or package_id == '':
            raise InvalidParameterException("package_id must be a non-empty string")
        response = self._catalog_client.delete_package(package_id)
        get_api_response_data(response, parse_full=True)

    def get_deployment(self, deployment_id, retry_limit=0):
        """
        Get a deployment

        :param deployment_id: Deployment ID
        :type deployment_id: string
        :param retry_limit: Optional parameter to specify the number of retry attempts to be
              carried out if any failures occurs during the API call.
        :type retry_limit: int
        :return: instance of class :py:class:`Deployment`:
        :raises: :py:class:`APIError`:  If the API returns an error, a status code of
            anything other than 200/201 is returned.



        Following example demonstrates how to get all the deployments.

            >>> from rapyuta_io import Client
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> deployment = client.get_deployment('deployment_id')

        """
        deployment = self._catalog_client.get_deployment(deployment_id, retry_limit)
        deployment = Deployment(to_objdict(deployment))
        self._add_auth_token(deployment)
        deployment.is_partial = False
        return deployment

    def get_volume_instance(self, instance_id, retry_limit=0):
        """
        Get a volume instance

        :param instance_id: Volume instance Id
        :type instance_id: string
        :param retry_limit: Optional parameter to specify the number of retry attempts to be
              carried out if any failures occurs during the API call.
        :type retry_limit: int
        :return: instance of class :py:class:`VolumeInstance`:
        :raises: :py:class:`APIError`: If the API returns an error, a status code
            of anything other than 200/201 is returned.

        Following example demonstrates how to get a volume instance.

            >>> from rapyuta_io import Client
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> deployments = client.get_volume_instance('instance_id')

        """
        volume_instance = self._catalog_client.get_deployment(instance_id, retry_limit)
        volume_instance = VolumeInstance(to_objdict(volume_instance))
        self._add_auth_token(volume_instance)
        volume_instance.is_partial = False
        return volume_instance

    def get_all_deployments(self, phases=None, device_id='', retry_limit=0):
        """
        Get all deployments created by the user.

        :param phases: optional parameter to filter out the deployments based on current deployment
        :type phases: list(DeploymentPhaseConstants)
        :param device_id: optional parameter to filter out the deployments based on uid of the corresponding device
        :type device_id: str
        :param retry_limit: Optional parameter to specify the number of retry attempts to be
              carried out if any failures occurs during the API call.
        :type retry_limit: int
        :return: list of instances of class :py:class:`Deployment`:
        :raises: :py:class:`APIError`: If the API returns an error, a status code
            of anything other than 200/201 is returned.

        Following example demonstrates how to get all the deployments.

            >>> from rapyuta_io import Client, DeploymentPhaseConstants
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> deployments = client.get_all_deployments()
            >>> deployments_list_filtered_by_phase = client.get_all_deployments(phases=
            >>>    [DeploymentPhaseConstants.SUCCEEDED, DeploymentPhaseConstants.PROVISIONING])
            >>> deployments_list_filtered_by_device_id = client.get_all_deployments(
            >>>    device_id='<device_id>')

        """
        if not isinstance(device_id, six.string_types):
            raise InvalidParameterException('invalid deviceID')

        deployment_list = self._catalog_client.deployment_list(phases, device_id, retry_limit)
        deployments = list()
        for deployment in deployment_list:
            if deployment['packageId'] == VOLUME_PACKAGE_ID:
                continue
            deployment_object = Deployment(to_objdict(deployment))
            # todo: remove volume instances
            self._add_auth_token(deployment_object)
            deployments.append(deployment_object)
        return deployments

    def get_authenticated_user(self):
        """
        Get details for authenticated User.

        :rtype: :py:class:`~rapyuta_io.clients.project.User`

        Following example demonstrates how to get authenticated user details.

        >>> from rapyuta_io import Client
        >>> client = Client(auth_token='auth_token', project='project_guid')
        >>> user = client.get_authenticated_user()

        """
        return self._core_api_client.get_user()

    def get_user_organizations(self):
        """
        Get list of organizations that a user is part of.

        :rtype: list(:py:class:`~rapyuta_io.clients.organization.Organization`)

        Following example demonstrates how to get the list of organizations that a user is part of.

        >>> from rapyuta_io import Client
        >>> client = Client(auth_token='auth_token', project='project_guid')
        >>> organizations = client.get_user_organizations()

        """
        return self._core_api_client.get_user_organizations()

    def get_all_devices(self, online_device=False, arch_list=None, retry_limit=0):
        """
        Get all the devices

        :param online_device: The value True returns only those devices that are online,
            while the value False returns all devices
        :type online_device: bool
        :param arch_list: If set, another call is made to filter devices by architecture.
            Valid architectures can be found in :py:class:`~.DeviceArch` class. Note: Only online devices
            can be filtered by architecture. Therefore if `arch_list` is set, non-online
            devices are not included in the result irrespective of the value of `online_device`.
        :type arch_list: list
        :param retry_limit: No of retry attempts to be carried out if any failures occurs\
                during the API call.
        :type retry_limit: int
        :return: List of instances of :py:class:`~Device` class
        :raises: :py:class:`APIError`: If the API returns an error, a status code
            of anything other than 200/201 is returned

        Following example demonstrates how to get the device list

            >>> from rapyuta_io import Client
            >>> from rapyuta_io.clients import DeviceArch
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> devices = client.get_all_devices()
            >>> filtered_by_arch_devices = client.get_all_devices(arch_list=[
            >>>     DeviceArch.ARM32V7, DeviceArch.ARM64V8, DeviceArch.AMD64])

        """
        return self._dmClient.device_list(online_device, arch_list, retry_limit)

    def get_device(self, device_id, retry_limit=0):
        """
        Get information of a device.

        :param device_id: Device Id
        :type device_id: string
        :param retry_limit: No of retry attempts to be carried out if any failures occurs\
         during the API call.
        :type retry_limit: int
        :return: Instances of :py:class:`~Device` class.
        :raises: :py:class:`~utils.error.ResourceNotFoundError`: If the device with given device id is not present.
        :raises: :py:class:`APIError`: If the API returns an error, a status code of
            anything other than 200/201 is returned.

        Following example demonstrates how to select a device information.

            >>> from rapyuta_io import Client
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> device = client.get_device(device_id="device_id")

        """
        return self._dmClient.get_device(device_id, retry_limit)

    def create_device(self, device):
        """
        Create a device on rapyuta.io platform.

        :param device: device object
        :type device: :py:class:`~rapyuta_io.clients.device.Device`
        :rtype: :py:class:`~rapyuta_io.clients.device.Device`

        Following example demonstrates how to create a device.

            >>> from rapyuta_io import Client, ROSDistro
            >>> from rapyuta_io.clients.device import Device, DeviceRuntime, DevicePythonVersion
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> device = Device(name='test-device', runtime=DeviceRuntime.DOCKER, ros_distro=ROSDistro.MELODIC,
            ...                 rosbag_mount_path='/opt/rapyuta/volumes/rosbag', python_version=DevicePythonVersion.PYTHON3)
            >>> device = client.create_device(device)
        """
        if not isinstance(device, Device):
            raise InvalidParameterException("device must be non-empty and of type "
                                            "rapyuta_io.clients.device.Device")

        device_response = self._dmClient.create_device(device)
        device_id = device_response['response']['device_id']
        return self.get_device(device_id)

    def delete_device(self, device_id):
        """
        Delete a device based on its device id.

        :param device_id: Device Id
        :type device_id: str

        Following example demonstrates how to delete a device.

        >>> from rapyuta_io import Client, ROSDistro
        >>> client = Client(auth_token='auth_token', project='project_guid')
        >>> client.delete_device('device-id')
        """
        if not device_id or not isinstance(device_id, six.string_types):
            raise InvalidParameterException('device_id needs to be a non empty string')
        return self._dmClient.delete_device(device_id)

    def create_package_from_manifest(self, manifest_filepath, retry_limit=0):
        """
        Create package from a manifest file

        :param manifest_filepath: File path of the manifest
        :type manifest_filepath: string
        :param retry_limit: No of retry attempts to be carried out if any failures occurs\
         during the API call.
        :type retry_limit: int
        :raises: :py:class:`~utils.error.ConflictError`: Package already exists.
        :raises: :py:class:`~utils.error.BadRequestError`: Invalid package details.
        :return: dict containing package details

        **Copy the below json to listener.json file** \n
        Following example demonstrates how to use create_package_from_manifest.

            .. code-block:: JSON

               { "packageVersion": "v1.0.0", "plans": [{"singleton": false,
               "name": "default", "inboundROSInterfaces": {"services": [], "topics": [],
               "actions": []}, "dependentDeployments": [], "components": [{"executables": [{"cmd":
               ["roslaunch listener listener.launch"], "name": "listenerExec"}],
               "name": "default", "parameters": [], "architecture": "arm32v7", "requiredRuntime":
                "device", "ros": {"services": [], "topics": [], "isROS": true, "actions": []},
                 "description": ""}], "exposedParameters": [], "metadata": {}}], "name": "listener",
                 "apiVersion": "v1.0.0", "description": "listener arm32v7 sdk test package" }

        >>> from rapyuta_io import Client
        >>> client = Client(auth_token='auth_token', project='project_guid')
        >>> package_details = client.create_package_from_manifest('listener.json')

        """
        manifest = self._get_manifest_from_file(manifest_filepath)
        return self._catalog_client.create_package(manifest, retry_limit)

    @staticmethod
    def _get_manifest_from_file(manifest_filepath):
        with open(manifest_filepath, 'r') as f:
            return json.load(f)

    def create_package(self, manifest, retry_limit=0):
        """
        Create package from manifest dict.

        :param manifest: dict containing package details
        :type manifest: dict
        :param retry_limit: No of retry attempts to be carried out if any failures occurs\
         during the API call.
        :type retry_limit: int
        :raises: :py:class:`~utils.error.ConflictError`: Package already exists.
        :raises: :py:class:`~utils.error.BadRequestError`: Invalid package details.
        :return: dict containing package details

        Following example demonstrates how to use create_package.

            >>> manifest = {'packageVersion': 'v1.0.0',
                 'plans': ['singleton': False,
                 'name': 'default',
                 'inboundROSInterfaces': {'services': [], 'topics': [], 'actions': []},
                 'dependentDeployments': [],
                 'components': [{'executables': [{'cmd': ['roslaunch listener listener.launch'],
                     'name': 'listenerExec'}],
                     'name': 'default',
                     'parameters': [],
                     'architecture': 'arm32v7',
                     'requiredRuntime': 'device',
                     'ros': {'services': [], 'topics': [], 'isROS': True, 'actions': []},
                     'description': ''}],
                     'exposedParameters': [],
                     'metadata': {}}],
                 'name': 'listener',
                 'apiVersion': 'v1.0.0',
                 'description': 'listener arm32v7 sdk test package'}
            >>> from rapyuta_io import Client
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> package_details = client.create_package(manifest)

        """
        return self._catalog_client.create_package(manifest, retry_limit)

    def upload_configurations(self, rootdir, tree_names=None, delete_existing_trees=False):
        """
        Traverses rootdir and uploads configurations following the same directory structure.

        :param rootdir: Path to directory containing configurations
        :type rootdir: str
        :param tree_names: List of specific configuration trees to upload. If None, all trees under rootdir are uploaded
        :type tree_names: list[str], optional
        :param delete_existing_trees: For each tree to upload, delete existing tree at the server. Defaults to False
        :type delete_existing_trees: bool, optional

        Following example demonstrates how to use upload_configurations and handle errors.

            >>> from rapyuta_io import Client
            >>> from rapyuta_io.utils.error import BadRequestError, InternalServerError
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> try:
            ...     client.upload_configurations('path/to/configs/source_dir',
            ...                                  tree_names=['config_tree1', 'config_tree2'],
            ...                                  delete_existing_trees=True)
            ... except (BadRequestError, InternalServerError) as e:
            ...     print 'failed API request', e.tree_path, e
            ... except (IOError, OSError) as e:
            ...     print 'failed file/directory read', e

        """
        return self._paramserver_client.upload_configurations(rootdir, tree_names, delete_existing_trees)

    def download_configurations(self, rootdir, tree_names=None, delete_existing_trees=False):
        """
        Download all configurations to rootdir following the same directory structure. If rootdir does not exist, it is
        created.

        :param rootdir: Path to directory to store downloaded configurations
        :type rootdir: str
        :param tree_names: List of specific configuration trees to download. If None, all trees are downloaded
        :type tree_names: list[str], optional
        :param delete_existing_trees: For each tree to download, delete existing tree on the filesystem. Defaults to
            False
        :type delete_existing_trees: bool, optional

        Following example demonstrates how to use download_configurations and handle errors.

            >>> from rapyuta_io import Client
            >>> from rapyuta_io.utils.error import APIError, InternalServerError
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> try:
            ...     client.download_configurations('path/to/destination_dir',
            ...                                    tree_names=['config_tree1', 'config_tree2'],
            ...                                    delete_existing_trees=True)
            ... except (APIError, InternalServerError) as e:
            ...     print 'failed API request', e.tree_path, e
            ... except (IOError, OSError) as e:
            ...     print 'failed file/directory creation', e

        """
        return self._paramserver_client.download_configurations(rootdir, tree_names, delete_existing_trees)

    def apply_parameters(self, device_list, tree_names=None, retry_limit=0):
        """
        Applies configuration parameters for the given device_list. If tree_names is given, only these trees are
        applied.

        :param device_list: List of device IDs
        :type device_list: list[str]
        :param tree_names: List of configuration tree names
        :type tree_names: list[str]
        :param retry_limit: Optional parameter to specify the number of retry attempts to be
              carried out if any failures occurs during the API call.
        :type retry_limit: int
        :return: List of dictionaries - each with device_id, bool success status, and an error message if the success
            status is False for that device_id
        :rtype: list[dict]

        Following example demonstrates how to use apply_parameters and handle errors.

            >>> from rapyuta_io import Client
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> devices = client.get_all_devices()
            >>> response = client.apply_parameters([device.deviceId for device in devices])
            >>> for device in response:
            ...     if not device['success']:
            ...         print device['device_id'], device['error']

        """
        return self._dmClient.apply_parameters(device_list, tree_names, retry_limit)

    def get_all_static_routes(self):
        """
        List all static routes in a project.

        :return: Instances of :py:class:`~StaticRoute` class.

        Following example demonstrates how to list all static routes

            >>> from rapyuta_io import Client
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> static_routes = client.get_all_static_routes()
        """
        return self._core_api_client.get_all_static_routes()

    def get_static_route(self, route_guid):
        """
        Get static routes by its guid

        :param route_guid: GUID string of a :py:class:`~StaticRoute` class.
        :type route_guid: str
        :return: Instance of :py:class:`~StaticRoute` class.

        Following example demonstrates how to get a static route

            >>> from rapyuta_io import Client
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> static_route_guid = client.get_all_static_routes()[0]['guid']
            >>> static_route = client.get_static_route(static_route_guid)
        """
        return self._core_api_client.get_static_route(route_guid)

    def get_static_route_by_name(self, name):
        """
        Get static routes by its name

        :param name: Name (urlPrefix) of the :py:class:`~StaticRoute` instance.
        :type name: str
        :return: Instance of :py:class:`~StaticRoute` class or None if it doesn't exist

        Following example demonstrates how to get a static route by its name/url prefix

            >>> from rapyuta_io import Client
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> static_route = client.get_static_route_by_name('example-route')
        """
        return self._core_api_client.get_static_route_by_name(name)

    def create_static_route(self, name):
        """
        Create static route of a certain name

        :param name: Name of the static route. It should follow ^[a-z][a-z0-9-]*$ and should not contain black listed keyword and be of length between 4 and 64
        :type name: str
        :return: Instance of :py:class:`~StaticRoute` class.

        Following example demonstrates how to create a static route.

            >>> from rapyuta_io import Client
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> static_route = client.create_static_route('example-route')
        """
        return self._core_api_client.create_static_route(name)

    def delete_static_route(self, route_guid):
        """
        Delete static route by its guid

        :param route_guid: GUID string of a :py:class:`~StaticRoute` class.
        :type route_guid: str

        Following example demonstrates how to delete a static route

            >>> from rapyuta_io import Client
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> static_route_guid = client.get_all_static_routes()[0]['guid']
            >>> client.delete_static_route(static_route_guid)
        """
        return self._core_api_client.delete_static_route(route_guid)

    def get_routed_network(self, network_guid):
        """
        Get routed network for the guid

        :param network_guid: guid of routed network
        :type  network_guid: str
        :return: Instance of :py:class:`~rapyuta_io.clients.routed_network.RoutedNetwork` class.

            >>> from rapyuta_io import Client
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> routed_network = client.get_routed_network(network_guid)

        """
        routed_network = self._catalog_client.get_routed_network(network_guid)
        routed_network = RoutedNetwork(to_objdict(routed_network))
        routed_network.phase = routed_network.internalDeploymentStatus.phase
        routed_network.status = routed_network.internalDeploymentStatus.status
        routed_network.error_code = routed_network.get_error_code()
        self._add_auth_token(routed_network)
        routed_network.is_partial = False
        return routed_network

    def get_all_routed_networks(self):
        """
        List routed network

        :return: List instance of :py:class:`~rapyuta_io.clients.routed_network.RoutedNetwork` class.
        """

        routed_networks = []
        networks = self._catalog_client.list_routed_network()
        for routed_network in networks:
            routed_network = RoutedNetwork(to_objdict(routed_network))
            internal_deployment_status = routed_network.internalDeploymentStatus
            routed_network.phase = internal_deployment_status.phase
            routed_network.error_code = routed_network.get_error_code()
            self._add_auth_token(routed_network)
            routed_networks.append(routed_network)
        return routed_networks

    def delete_routed_network(self, network_guid):

        """
        Delete a routed network using its network_guid

        :param network_guid: Routed Network GUID
        :type network_guid: str

        Following example demonstrates how to delete a routed network under a project
            >>> from rapyuta_io import Client
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> client.delete_routed_network('network_guid')

        """
        if not network_guid or not isinstance(network_guid, six.string_types):
            raise InvalidParameterException('guid needs to be a non empty string')
        self._catalog_client.delete_routed_network(network_guid)

    def create_cloud_routed_network(self, name, ros_distro, shared, parameters=None):

        """
        Create a routed network

        :param name: Name of the routed network.
        :type name: str
        :param ros_distro: ros ditro of the runtime.
        :type ros_distro: enum :py:class:`~rapyuta_io.clients.package.ROSDistro`
        :param shared: Whether the network should be shared.
        :type shared: bool
        :param parameters: parameters of the routed network
        :type parameters: :py:class:`~rapyuta_io.clients.routed_network.Parameters`
        :return: Instance of :py:class:`~rapyuta_io.clients.routed_network.RoutedNetwork` class.

        Following example demonstrates how to create a routed network.

            >>> from rapyuta_io import Client
            >>> from rapyuta_io.clients.package import ROSDistro
            >>> from rapyuta_io.clients.routed_network import Parameters, RoutedNetworkLimits
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> parameters = Parameters(RoutedNetworkLimits.SMALL)
            >>> routed_network = client.create_cloud_routed_network('network_name', ROSDistro.KINETIC, True,
            ...                                                        parameters=parameters)
        """
        if ros_distro not in list(ROSDistro.__members__.values()):
            raise InvalidParameterException('ROSDistro must be one of rapyuta_io.clients.package.ROSDistro')

        if parameters and not isinstance(parameters, Parameters):
            raise InvalidParameterException('parameters must be of type rapyuta_io.clients.routed_network.Parameters')

        parameters = parameters.to_dict() if parameters else {}

        routed_network = self._catalog_client.create_routed_network(name=name, runtime=Runtime.CLOUD,
                                                                    rosDistro=ros_distro,
                                                                    shared=shared, parameters=parameters)
        routed_network = RoutedNetwork(to_objdict(routed_network))
        return self.get_routed_network(routed_network.guid)

    def create_device_routed_network(self, name, ros_distro, shared,
                                     device, network_interface, restart_policy=RestartPolicy.Always):

        """
        Create a routed network

        :param name: Name of the routed network.
        :type name: str
        :param ros_distro: ros ditro of the runtime.
        :type ros_distro: enum :py:class:`~rapyuta_io.clients.package.ROSDistro`
        :param shared: Whether the network should be shared.
        :type shared: bool
        :param device: device on which the routed network is deployed.
        :type device: Instance of :py:class:`~Device` class.
        :param network_interface: network interface to which routed network is binded.
        :type network_interface: str
        :param restart_policy: restart policy of routed network.
        :type restart_policy: enum :py:class:`~rapyuta_io.clients.package.RestartPolicy`
        :return: Instance of :py:class:`~rapyuta_io.clients.routed_network.RoutedNetwork` class.

        Following example demonstrates how to create a routed network.

            >>> from rapyuta_io import Client
            >>> from rapyuta_io.clients.package import ROSDistro
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> routed_network = client.create_device_routed_network('network_name',
            >>>                                                      ROSDistro.KINETIC, True)
        """

        parameters = {}
        if ros_distro not in list(ROSDistro.__members__.values()):
            raise InvalidParameterException('ROSDistro must be one of rapyuta_io.clients.package.ROSDistro')

        if not isinstance(device, Device):
            raise InvalidParameterException('device must be of type rapyuta_io.clients.device.Device')

        ip_interfaces = device.ip_interfaces or {}
        if network_interface not in list(ip_interfaces.keys()):
            raise InvalidParameterException('NETWORK_INTERFACE should be in {}'.format(list(ip_interfaces.keys())))

        if restart_policy not in list(RestartPolicy.__members__.values()):
            raise InvalidParameterException('RestartPolicy must be one of rapyuta_io.clients.package.RestartPolicy')

        parameters['device_id'] = device.uuid
        parameters['NETWORK_INTERFACE'] = network_interface
        parameters['restart_policy'] = restart_policy

        routed_network = self._catalog_client.create_routed_network(name=name, runtime=Runtime.DEVICE,
                                                                    rosDistro=ros_distro,
                                                                    shared=shared, parameters=parameters)
        routed_network = RoutedNetwork(to_objdict(routed_network))
        return self.get_routed_network(routed_network.guid)

    def create_build(self, build, refresh=True):

        """
        Create a new build

        :param build: Info about the build to be created
        :type build: :py:class:`~rapyuta_io.clients.build.Build`
        :param refresh: Whether the build needs to be refreshed
        :type refresh: bool
        :return: Instance of :py:class:`~rapyuta_io.clients.build.Build` class.

        Following example demonstrates how to create a build.

            >>> from rapyuta_io import Client, ROSDistro, SimulationOptions, BuildOptions, CatkinOption, GithubWebhook
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> simulationOptions = SimulationOptions(False)
            >>> buildOptions = BuildOptions(catkinOptions=[CatkinOption(rosPkgs='talker')])
            >>> webhooks = [GithubWebhook(workflowName='test.yaml', accessToken='github_access_token')]
            >>> build = Build(buildName='test-build',
            ...               strategyType='Source',
            ...               repository='https://github.com/rapyuta-robotics/io_tutorials.git',
            ...               architecture='amd64',
            ...               rosDistro='melodic',
            ...               isRos=True,
            ...               contextDir='talk/talker',
            ...               simulationOptions=simulationOptions,
            ...               buildOptions=buildOptions,
            ...               buildWebhooks=webhooks)
            >>> build = client.create_build(build)
            >>> build.poll_build_till_ready()

        """
        if not isinstance(build, Build):
            raise InvalidParameterException("build must be non-empty and of type "
                                            "rapyuta_io.clients.build.Build")
        response = self._catalog_client.create_build(build)
        build['guid'] = response.get('guid')
        self._add_auth_token(build)
        if refresh:
            build.refresh()
        return build

    def get_build(self, guid, include_build_requests=False):

        """
        Get a build based on the guid.

        :param guid: GUID of the build
        :type  guid: str
        :param include_build_requests: Whether to include build request in the response
        :type  include_build_requests: bool
        :return: Instance of :py:class:`~rapyuta_io.clients.build.Build` class.

        Following example demonstrates how to get a build.

        1. Get build without including build requests.

            >>> from rapyuta_io import Client
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> build = client.get_build('build-guid')

        2. Get build including the build requests.

            >>> from rapyuta_io import Client
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> build = client.get_build('build-guid', include_build_requests=True)

        """
        if not isinstance(include_build_requests, bool):
            raise InvalidParameterException('include_build_requests must be of bool type')
        build = self._catalog_client.get_build(guid, include_build_requests)
        build = Build._deserialize(build)
        self._add_auth_token(build)
        build.is_partial = False
        return build

    def list_builds(self, statuses=None):

        """
        List builds based on the passed query params

        :param statuses: statuses based on which the list build response will be filtered.
        :type  statuses: list(:py:class:`~rapyuta_io.clients.build.BuildStatus`)
        :return: list(:py:class:`~rapyuta_io.clients.build.Build`)

        Following example demonstrates how to list builds.

            1. List all builds present in the project.

                >>> from rapyuta_io import Client
                >>> client = Client(auth_token='auth_token', project='project_guid')
                >>> build = client.list_builds()

            2. List builds based on their statuses.

                >>> from rapyuta_io import Client, BuildStatus
                >>> client = Client(auth_token='auth_token', project='project_guid')
                >>> builds = client.list_builds(statuses=[BuildStatus.COMPLETE, BuildStatus.BUILD_FAILED,
                ...                                       BuildStatus.BUILD_IN_PROGRESS])
        """
        if statuses is not None:
            BuildStatus.validate(statuses)
        builds = self._catalog_client.list_builds(statuses)
        build_list = []
        for build in builds:
            build = Build._deserialize(build)
            self._add_auth_token(build)
            build_list.append(build)
        return build_list

    def delete_build(self, guid):

        """
        Delete a build.

        :param guid: GUID of the build to be deleted
        :type  guid:  str

        Following example demonstrates how to delete a build.

                >>> from rapyuta_io import Client
                >>> client = Client(auth_token='auth_token', project='project_guid')
                >>> client.delete_build('build-guid')
        """
        response = self._catalog_client.delete_build(guid=guid)
        get_api_response_data(response, parse_full=True)

    def trigger_build(self, buildOperation):

        """
        Trigger a new build request for a particular build

        :param buildOperation: Info of the operation to be performed on the build.
        :type  buildOperation: :py:class:`~rapyuta_io.clients.buildoperation.BuildOperation`

        Following example demonstrates how to trigger a new build request for a build:

            >>> from rapyuta_io import Client, BuildOperationInfo, BuildOperation
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> request = BuildOperation([BuildOperationInfo('build-guid', triggerName='trigger-name')])
            >>> response = client.trigger_build(request)
            >>> for resp in response['buildOperationResponse']:
            ...     if not resp['success']:
            ...         print resp['buildGUID'], resp['error']
            ...     else:
            ...         print resp['buildGUID'], resp['buildGenerationNumber']

        """
        return self._catalog_client.trigger_build(buildOperation=buildOperation)

    def rollback_build(self, buildOperation):

        """
        Rollback the build to a previously created build request

        :param buildOperation: Info of the operation to be performed on the build.
        :type  buildOperation: :py:class:`~rapyuta_io.clients.buildoperation.BuildOperation`

        Following example demonstrates how to rollback a build:

            >>> from rapyuta_io import Client, BuildOperationInfo, BuildOperation
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> request = BuildOperation([BuildOperationInfo('build-guid', 1)])
            >>> response = client.rollback_build(request)
            >>> for resp in response['buildOperationResponse']:
            ...     if not resp['success']:
            ...         print resp['buildGUID'], resp['error']
            ...     else:
            ...         print resp['buildGUID'], resp['buildGenerationNumber']

        """
        return self._catalog_client.rollback_build(buildOperation=buildOperation)

    def create_rosbag_job(self, rosbag_job):
        """
        Create a ROSBag Job

        :param rosbag_job: ROSBag object
        :type rosbag_job: :py:class:`~rapyuta_io.clients.rosbag.ROSBagJob`
        :raises: :py:class:`~utils.error.BadRequestError`: Rosbag Upload Options are required in case of Device jobs
        :return: Instance of :py:class:`~rapyuta_io.clients.rosbag.ROSBagJob` class

        Following example demonstrates how to create a ROSBag Job.

            >>> from rapyuta_io import Client
            >>> from rapyuta_io.clients.rosbag import ROSBagJob, ROSBagOptions
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> deployment = client.get_deployment('deployment_id')
            >>> component_instance_id = deployment.get_component_instance_id('comp-name')
            >>> rosbag_options = ROSBagOptions(all_topics=True)
            >>> rosbag_job = ROSBagJob(deployment_id=deployment.deploymentId,
            ...              component_instance_id=component_instance_id,
            ...              rosbag_options=rosbag_options, name='name')
            >>> rosbag_job = client.create_rosbag_job(rosbag_job)

        """
        if not isinstance(rosbag_job, ROSBagJob):
            raise InvalidParameterException("rosbag job must be non-empty and of type "
                                            "rapyuta_io.clients.rosbag.ROSBagJob")
        if not rosbag_job.deployment_id or not isinstance(rosbag_job.deployment_id, six.string_types):
            raise InvalidParameterException('deployment id must be non empty string')
        if not rosbag_job.component_instance_id or not isinstance(rosbag_job.component_instance_id, six.string_types):
            raise InvalidParameterException('component instance id must be non empty string')

        response = self._catalog_client.create_rosbag_job(rosbag_job)
        rosbag_job = ROSBagJob.deserialize(response)
        self._add_auth_token(rosbag_job)
        return rosbag_job

    def list_rosbag_jobs(self, deployment_id, component_instance_ids=None, guids=None, statuses=None):
        """
        Get rosbag jobs based on the passed query params

        :param deployment_id: deployment guid
        :type  deployment_id: str
        :param component_instance_ids: list of component instance id
        :type  component_instance_ids: list(str)
        :param guids: list of job guid
        :type  guids: list(str)
        :param statuses: list of rosbag status
        :type  statuses: list(:py:class:`~rapyuta_io.clients.rosbag.ROSBagJobStatus`)
        :return: list(:py:class:`~rapyuta_io.clients.rosbag.ROSBagJob`)

        Following example demonstrates how to get ROSBag Jobs
            1. List all ROSBagJobs of a deployment
                >>> from rapyuta_io import Client
                >>> client = Client(auth_token='auth_token', project='project_guid')
                >>> rosbag_jobs = client.list_rosbag_jobs(deployment_id)

            2. List ROSBagJobs of a deployment’s component instance
                >>> from rapyuta_io import Client
                >>> client = Client(auth_token='auth_token', project='project_guid')
                >>> rosbag_jobs = client.list_rosbag_jobs(deployment_id,
                ...                                       component_instance_ids=['comp-inst-id'])

            3. List specific ROSBagJobs of a deployment
                >>> from rapyuta_io import Client
                >>> client = Client(auth_token='auth_token', project='project_guid')
                >>> rosbag_jobs = client.list_rosbag_jobs(deployment_id, guids=['job-id'])

            4. List ROSBagJobs with statuses of a deployment
                >>> from rapyuta_io import Client
                >>> from rapyuta_io.clients.rosbag import ROSBagJobStatus
                >>> client = Client(auth_token='auth_token', project='project_guid')
                >>> rosbag_jobs = client.list_rosbag_jobs(deployment_id,
                ...                                       statuses=[ROSBagJobStatus.RUNNING])

        """
        if not deployment_id or not isinstance(deployment_id, six.string_types):
            raise InvalidParameterException('deployment id be non empty string')

        if component_instance_ids is not None and not valid_list_elements(component_instance_ids, six.string_types):
            raise InvalidParameterException('component_instance_ids needs to be a list of string')
        if guids is not None and not valid_list_elements(guids, six.string_types):
            raise InvalidParameterException('guids needs to be a list of string')
        if statuses is not None and not valid_list_elements(statuses, ROSBagJobStatus):
            raise InvalidParameterException('status needs to be a list of ROSBagJobStatus')
        if guids is not None and component_instance_ids:
            raise InvalidParameterException('only guid or component_instance_id should be present')

        response = self._catalog_client.list_rosbag_jobs(deployment_id, component_instance_ids=component_instance_ids,
                                                         guids=guids, statuses=statuses)
        rosbag_jobs = [ROSBagJob.deserialize(resp) for resp in response]
        for rosbag_job in rosbag_jobs:
            self._add_auth_token(rosbag_job)
        return rosbag_jobs

    def list_rosbag_jobs_in_project(self, device_ids):
        """
        Lists rosbag jobs based on device ids

        :param device_ids: list of device id
        :type  device_ids: list(str)

        Following example demonstrates how to list rosbag jobs in a project based on device ids:
            1. List all ROSBagJobs based on device ids
                >>> from rapyuta_io import Client
                >>> client = Client(auth_token='auth_token', project='project_guid')
                >>> rosbag_jobs = client.list_rosbag_jobs_in_project(['device-id'])
        """
        if device_ids is None or (not valid_list_elements(device_ids, six.string_types)) or len(device_ids) == 0:
            raise InvalidParameterException('device_ids need to be a non-empty list of string')

        response = self._catalog_client.list_rosbag_jobs_in_project(device_ids=device_ids)
        rosbag_jobs = [ROSBagJob.deserialize(resp) for resp in response]
        for rosbag_job in rosbag_jobs:
            self._add_auth_token(rosbag_job)
        return rosbag_jobs

    def stop_rosbag_jobs(self, deployment_id, component_instance_ids=None, guids=None):
        """
        Stop ROSBag Job based on the passed query params

        :param deployment_id: deployment guid
        :type deployment_id: str
        :param component_instance_ids: list of component instance id
        :type component_instance_ids: list(str)
        :param guids: list of job guid
        :type  guids: list(str)

        Following example demonstrates how to stop ROSBag Jobs
            1. Stop all ROSBagJobs of a deployment
                >>> from rapyuta_io import Client
                >>> client = Client(auth_token='auth_token', project='project_guid')
                >>> client.stop_rosbag_jobs(deployment_id)

            2. Stop ROSBagJobs of a deployment’s component instance
                >>> from rapyuta_io import Client
                >>> client = Client(auth_token='auth_token', project='project_guid')
                >>> client.stop_rosbag_jobs(deployment_id, component_instance_ids=['comp-inst-id'])

            3. Stop specific ROSBagJobs of a deployment
                >>> from rapyuta_io import Client
                >>> client = Client(auth_token='auth_token', project='project_guid')
                >>> client.stop_rosbag_jobs(deployment_id, guids=['job-id'])

        """
        if component_instance_ids is not None and not valid_list_elements(component_instance_ids, six.string_types):
            raise InvalidParameterException('component_instance_ids needs to be a list of string')
        if guids is not None and not valid_list_elements(guids, six.string_types):
            raise InvalidParameterException('guids needs to list of string')
        if guids and component_instance_ids:
            raise InvalidParameterException('only guid or component_instance_id should be present')

        self._catalog_client.stop_rosbag_jobs(deployment_id, component_instance_ids=component_instance_ids, guids=guids)

    def list_rosbag_blobs(self, guids=None, deployment_ids=None, component_instance_ids=None,
                          job_ids=None, statuses=None, device_ids=None):
        """
        Get rosbag blobs based on the passed query params


        :param guids: list of blob guid
        :type guids: list(str)
        :param deployment_ids: list of deployment id
        :type deployment_ids: list(str)
        :param component_instance_ids: list of component instance id
        :type component_instance_ids: list(str)
        :param job_ids: list of job guid
        :type job_ids: list(str)
        :param statuses: list of
        :type statuses: list(:py:class:`~rapyuta_io.clients.rosbag.ROSBagBlobStatus`)
        :param device_ids: list of device id
        :type  device_ids: list(str)
        :return: list(:py:class:`~rapyuta_io.clients.rosbag.ROSBagBlob`)

        Following example demonstrates how to stop ROSBag Blobs
            1. List specific ROSBagBlobs
                >>> from rapyuta_io import Client
                >>> client = Client(auth_token='auth_token', project='project_guid')
                >>> rosbag_blobs = client.list_rosbag_blobs(guids=['blob-id'])

            2. List all ROSBagBlobs of a deployment
                >>> from rapyuta_io import Client
                >>> client = Client(auth_token='auth_token', project='project_guid')
                >>> rosbag_blobs = client.list_rosbag_blobs(deployment_ids=['dep-id'])

            3. List ROSBagBlobs of a deployment’s component instance
                >>> from rapyuta_io import Client
                >>> client = Client(auth_token='auth_token', project='project_guid')
                >>> rosbag_blobs = client.list_rosbag_blobs(component_instance_ids=['dep-id'])

            4. List all ROSBagBlobs of a job
                >>> from rapyuta_io import Client
                >>> client = Client(auth_token='auth_token', project='project_guid')
                >>> rosbag_blobs = client.list_rosbag_blobs(job_ids=['job-id'])

            5. List ROSBagBlobs with statuses
                >>> from rapyuta_io import Client
                >>> from rapyuta_io.clients.rosbag import ROSBagBlobStatus
                >>> client = Client(auth_token='auth_token', project='project_guid')
                >>> rosbag_blobs = client.list_rosbag_blobs(statuses=[ROSBagBlobStatus.UPLOADED])

            6. List ROSBagBlobs of a device
                >>> from rapyuta_io import Client
                >>> from rapyuta_io.clients.rosbag import ROSBagBlobStatus
                >>> client = Client(auth_token='auth_token', project='project_guid')
                >>> rosbag_blobs = client.list_rosbag_blobs(device_ids=['device-id'])

        """
        if component_instance_ids is not None and not valid_list_elements(component_instance_ids, six.string_types):
            raise InvalidParameterException('component_instance_ids needs to be a list of string')
        if guids is not None and not valid_list_elements(guids, six.string_types):
            raise InvalidParameterException('guids needs to be a list of string')
        if deployment_ids is not None and not valid_list_elements(deployment_ids, six.string_types):
            raise InvalidParameterException('deployment_ids needs to be a list of string')
        if job_ids is not None and not valid_list_elements(job_ids, six.string_types):
            raise InvalidParameterException('job_ids needs to be a list of string')
        if statuses is not None and not valid_list_elements(statuses, ROSBagBlobStatus):
            raise InvalidParameterException('status needs to be a list of ROSBagBlobStatus')
        if device_ids is not None and not valid_list_elements(device_ids, six.string_types):
            raise InvalidParameterException('device_ids need to be a list of string')

        query_param_count = 0
        if deployment_ids:
            query_param_count += 1
        if component_instance_ids:
            query_param_count += 1
        if guids:
            query_param_count += 1
        if job_ids:
            query_param_count += 1

        if query_param_count > 1:
            raise InvalidParameterException('only one of deployment_ids, component_instance_ids, '
                                            'guids or job_ids should be present')

        response = self._catalog_client.list_rosbag_blobs(guids=guids, deployment_ids=deployment_ids,
                                                          component_instance_ids=component_instance_ids,
                                                          job_ids=job_ids, statuses=statuses, device_ids=device_ids)

        rosbag_blobs = [ROSBagBlob.deserialize(resp) for resp in response]
        for rosbag_blob in rosbag_blobs:
            self._add_auth_token(rosbag_blob)
        return rosbag_blobs

    def download_rosbag_blob(self, guid, filename=None, download_dir=None):
        """
        Download rosbag bag file

        :param guid: blob guid
        :type guid: str
        :param download_dir: filename
        :type download_dir: str

        :param filename: filename
        :type filename: str

        Following example demonstrates how to download ROSBag Blob

        >>> from rapyuta_io import Client
        >>> client = Client(auth_token='auth_token', project='project_guid')
        >>> client.download_rosbag_blob('blob-id', 'filename.bag')

        """
        if not guid or not isinstance(guid, six.string_types):
            raise InvalidParameterException('guid needs to non empty string')
        response = self._catalog_client.get_blob_download_url(guid)
        signed_url = response['url']
        self._catalog_client.download_blob(signed_url, filename, download_dir)

    def delete_rosbag_blob(self, guid):
        """
        Delete the rosbag bag file

        :param guid: blob guid
        :type guid: str

        Following example demonstrates how to delete ROSBag Blob

        >>> from rapyuta_io import Client
        >>> client = Client(auth_token='auth_token', project='project_guid')
        >>> client.delete_rosbag_blob('blob-id')

        """
        if not guid or not isinstance(guid, six.string_types):
            raise InvalidParameterException('guid needs to non empty string')
        self._catalog_client.delete_rosbag_blob(guid)

    def create_project(self, project):
        """
        Create a new Project

        :param project: Project object
        :type project: :py:class:`~rapyuta_io.clients.project.Project`
        :rtype: :py:class:`~rapyuta_io.clients.project.Project`

        Following example demonstrates the use of this method for creating a new Project.

            >>> from rapyuta_io.clients.project import Project
            >>> client = Client(auth_token='auth_token')
            >>> proj = Project('project-name')
            >>> client.create_project(proj)

        Following example demonstrates the use of this method for creating a new Project in a different organization.
        Please do note that the user should be a part of the organization where the project is to be created.

            >>> from rapyuta_io.clients.project import Project
            >>> client = Client(auth_token='auth_token')
            >>> proj = Project('project-name', 'org-guid')
            >>> client.create_project(proj)

        """
        if not isinstance(project, Project):
            raise InvalidParameterException("project must be non-empty and of type "
                                            "rapyuta_io.clients.project.Project")
        return self._core_api_client.create_project(project)

    def get_project(self, guid):
        """
        Get a Project from its GUID.

        :param guid: Project's GUID
        :type guid: str
        :rtype: :py:class:`~rapyuta_io.clients.project.Project`

        Following example demonstrates how a Project can be fetched using this method.

            >>> client = Client(auth_token='auth_token')
            >>> client.get_project('project-guid')

        """
        return self._core_api_client.get_project(guid)

    def list_projects(self):
        """
        Get a list of all the Projects.

        :return: A list of all available Projects for the user.
        :rtype: list(:py:class:`~rapyuta_io.clients.project.Project`)

        Following example demonstrates how to fetch the list of all Projects.

            >>> client = Client(auth_token='auth_token')
            >>> client.list_projects()

        """
        return self._core_api_client.list_projects()

    def delete_project(self, guid):
        """
        Delete a Project from the platform.

        :param guid: Project's GUID
        :type guid: str

        Following example demonstrates how to delete a Project using this method.

            >>> client = Client(auth_token='auth_token')
            >>> client.delete_project('project-guid')

        """
        return self._core_api_client.delete_project(guid)

    def add_user_to_project(self, project_guid, user_guid):

        """
        Creator of a Project can add a User belonging to the same Organization into the Project.

        :param project_guid: Project's GUID
        :type project_guid: str
        :param user_guid: User's GUID
        :type user_guid: str

        Following example demonstrates how to add a User to a Project using this method.

            >>> client = Client(auth_token='auth_token')
            >>> client.add_user_to_project(project_guid='project_guid', user_guid='user_guid')

        """
        return self._core_api_client.add_user_to_project(project_guid=project_guid, user_guid=user_guid)

    def remove_user_from_project(self, project_guid, user_guid):

        """
        Creator of a Project can remove a User from the Project.

        :param project_guid: Project's GUID
        :type project_guid: str
        :param user_guid: User's GUID
        :type user_guid: str

        Following example demonstrates how to remove a User from a Project using this method.

            >>> client = Client(auth_token='auth_token')
            >>> client.remove_user_from_project(project_guid='project_guid', user_guid='user_guid')

        """
        return self._core_api_client.remove_user_from_project(project_guid=project_guid, user_guid=user_guid)

    def create_secret(self, secret):
        """
        Create a new Secret on the Platform under the project.

        :param secret: Secret object
        :type secret: :py:class:`~rapyuta_io.clients.secret.Secret`
        :rtype: :py:class:`~rapyuta_io.clients.secret.Secret`

        Following example demonstrates the use of this method for creating a new Secret.

            >>> from rapyuta_io.clients.secret import Secret, SecretConfigSourceBasicAuth
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> secret_config = SecretConfigSourceBasicAuth('user', 'password')
            >>> secret = Secret('secret-name', secret_config)
            >>> client.create_secret(secret)

        """
        if not isinstance(secret, Secret):
            raise InvalidParameterException("secret must be non-empty and of type "
                                            "rapyuta_io.clients.secret.Secret")
        return self._core_api_client.create_secret(secret)

    def list_secrets(self):
        """
        List all the Secrets under the Project on the Platform.

        :return: A list of all available Secrets under the selected Project.
        :rtype: list(:py:class:`~rapyuta_io.clients.secret.Secret`)

        Following example demonstrates how to fetch the list of all Secrets.

            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> client.list_secrets()

        """
        return self._core_api_client.list_secrets()

    def get_secret(self, guid):
        """
        Get a Secret using its GUID.

        :param guid: Secret's GUID
        :type guid: str
        :rtype: :py:class:`~rapyuta_io.clients.secret.Secret`

        Following example demonstrates how a Secret can be fetched using this method.

            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> client.get_secret('secret-guid')

        """
        return self._core_api_client.get_secret(guid)

    def update_secret(self, guid, secret):
        """
        Update an existing Secret on the Platform under the project.

        :param guid: Secret's GUID
        :type guid: str
        :param secret: Secret object
        :type secret: :py:class:`~rapyuta_io.clients.secret.Secret`
        :rtype: :py:class:`~rapyuta_io.clients.secret.Secret`

        Following example demonstrates the use of this method for creating a new Secret.

            >>> from rapyuta_io.clients.secret import Secret, SecretConfigSourceBasicAuth
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> secret_config = SecretConfigSourceBasicAuth('user', 'new_password')
            >>> secret = Secret('secret-name', secret_config)
            >>> client.update_secret('secret-guid', secret)

        """
        if not isinstance(secret, Secret):
            raise InvalidParameterException("secret must be non-empty and of type "
                                            "rapyuta_io.clients.secret.Secret")
        return self._core_api_client.update_secret(guid, secret)

    def delete_secret(self, guid):
        """
        Delete a secret using its GUID.

        :param guid: Project's GUID
        :type guid: str

        Following example demonstrates how to delete a Secret using this method.

            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> client.delete_secret('secret-guid')

        """
        return self._core_api_client.delete_secret(guid)

    def get_native_network(self, network_guid):
        """
        Get a native network using its network_guid

        :param network_guid: native network GUID
        :type network_guid: str
        :rtype: :py:class:`~rapyuta_io.clients.native_network.NativeNetwork`

        Following example demonstrates how a native network can be fetched using this method

            >>> from rapyuta_io import Client
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> native_network = client.get_native_network('network_guid')
        """
        if not network_guid or not isinstance(network_guid, six.string_types):
            raise InvalidParameterException('guid needs to be a non empty string')

        native_network = self._catalog_client.get_native_network(network_guid)
        native_network = NativeNetwork.deserialize(native_network)
        self._add_auth_token(native_network)
        native_network.is_partial = False
        return native_network

    def list_native_networks(self):
        """
        Lists all the native networks under a project

        :return: A list of all available native networks under the Project.
        :rtype: List(:py:class:`~rapyuta_io.clients.native_network.NativeNetwork`)

        Following example demonstartes how to list all the native networks under a project

            >>> from rapyuta_io import Client
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> native_networks = client.list_native_networks()
        """
        native_networks = []
        networks = self._catalog_client.list_native_network()
        for native_network in networks:
            native_network = NativeNetwork.deserialize(native_network)
            self._add_auth_token(native_network)
            native_networks.append(native_network)
        return native_networks

    def create_native_network(self, native_network):
        """
        Creates a new native network

        :param  native_network: Native Network object
        :type native_network: :py:class:`~rapyuta_io.clients.native_network.NativeNetwork`
        :rtype: :py:class:`~rapyuta_io.clients.native_network.NativeNetwork`

        Following example demonstrates how to create a native network under a project
            >>> from rapyuta_io import Client
            >>> from rapyuta_io.clients.native_network import NativeNetwork,Parameters,NativeNetworkLimits
            >>> from rapyuta_io.clients.package import Runtime, ROSDistro
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> parameters = Parameters(NativeNetworkLimits.SMALL)
            >>> native_network = NativeNetwork('native_network_name', Runtime.CLOUD, ROSDistro.KINETIC,
            ...                                  parameters=parameters)
            >>> native_network = client.create_native_network(native_network)
        """
        if not isinstance(native_network, NativeNetwork):
            raise InvalidParameterException("native_network must be non-empty and of type "
                                            "rapyuta_io.clients.native_network.NativeNetwork")

        native_network_response = self._catalog_client.create_native_network(native_network)
        return self.get_native_network(native_network_response['guid'])

    def delete_native_network(self, network_guid):

        """
        Delete a native network using its network_guid

        :param network_guid: Native Network GUID
        :type network_guid: str

        Following example demonstrates how to delete a native network under a project
            >>> from rapyuta_io import Client
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> client.delete_native_network('network_guid')

        """
        if not network_guid or not isinstance(network_guid, six.string_types):
            raise InvalidParameterException('guid needs to be a non empty string')
        self._catalog_client.delete_native_network(network_guid)

    def query_metrics(self, query_metrics_request):
        """
        Query and fetch metrics

        :param query_metrics_request: QueryMetricsRequest instance
        :type query_metrics_request: :py:class:`~rapyuta_io.clients.metrics.QueryMetricsRequest`
        :rtype: :py:class:`~rapyuta_io.clients.metrics.QueryMetricsResponse`

        Following example demonstrates how to query metrics

            >>> from rapyuta_io import Client
            >>> from rapyuta_io.clients.metrics import QueryMetricsRequest, StepInterval, SortOrder,
            >>> MetricOperation, MetricFunction
            >>> from datetime import datetime, timedelta
            >>> client = Client(auth_token='auth_token', project='project_guid')
            >>> now = datetime.utcnow()
            >>> metrics = [MetricOperation(MetricFunction.AVG, 'mem.total'),
            >>>            MetricOperation(MetricFunction.AVG, 'mem.used')]
            >>> request = QueryMetricsRequest(from_datetime=now-timedelta(days=10), to_datetime=now,
            >>>                               step_interval=StepInterval.FIFTEEN_MINUTES, metrics=metrics)
            >>> response = client.query_metrics(request)
            >>> print([str(col) for col in response.columns])
            >>>
            >>> import pandas as pd  # pip install pandas
            >>> rows, columns = response.to_row_column_format()
            >>> df = pd.DataFrame(data=rows, columns=columns)
            >>> df['timestamp'] = pd.to_datetime(df['timestamp'])
            >>> print(df.head())

        """
        if not isinstance(query_metrics_request, QueryMetricsRequest):
            raise InvalidParameterException('metrics_query_request must be '
                                            'of type rapyuta_io.clients.metrics.MetricsQueryRequest')

        default_tags = {}
        if not query_metrics_request.tags.get(query_metrics_request.PROJECT_ID_TAG):
            project = self._core_api_client._project
            if not project:
                raise InvalidParameterException('Either set project on client using client.set_project(), or '
                                                'set {} in tags'.format(query_metrics_request.PROJECT_ID_TAG))
            default_tags[query_metrics_request.PROJECT_ID_TAG] = project

        if not query_metrics_request.tags.get(query_metrics_request.ORGANIZATION_ID_TAG):
            user = self._core_api_client.get_user()
            organization_guid = user.organization.guid
            default_tags[query_metrics_request.ORGANIZATION_ID_TAG] = organization_guid

        query_metrics_request.tags.update(default_tags)

        response = self._core_api_client.query_metrics(query_metrics_request)
        return QueryMetricsResponse.deserialize(response)

    def list_metrics(self, list_metrics_request):
        """
        List metrics for a particular entity

        :param list_metrics_request: ListMetricsRequest instance
        :type list_metrics_request: :py:class:`~rapyuta_io.clients.metrics.ListMetricsRequest`
        :rtype: list(:py:class:`~rapyuta_io.clients.metrics.Metric`)

        Following example demonstrates how to list metrics

            >>> from rapyuta_io import Client
            >>> from rapyuta_io.clients.metrics import ListMetricsRequest, Entity
            >>> from datetime import datetime, timedelta
            >>> project_guid = 'project_guid'
            >>> client = Client(auth_token='auth_token', project=project_guid)
            >>> now = datetime.utcnow()
            >>> request = ListMetricsRequest(Entity.PROJECT, project_guid,
            ...                              start_date=now-timedelta(days=30), end_date=now)
            >>> for metric in client.list_metrics(request):
            ...    print(metric.metric_group, metric.metric_names)

        """
        if not isinstance(list_metrics_request, ListMetricsRequest):
            raise InvalidParameterException('metrics_query_request must be of type '
                                            'rapyuta_io.clients.metrics.ListMetricsRequest')

        response = self._core_api_client.list_metrics(list_metrics_request)
        return [Metric.deserialize(resp) for resp in response.get('metrics', [])]

    def list_tag_keys(self, list_tag_keys_request):
        """
        List Tag Keys for a particular entity

        :param list_tag_keys_request: ListTagKeysRequest
        :type list_tag_keys_request: :py:class:`~rapyuta_io.clients.metrics.ListTagKeysRequest`
        :rtype: list(:py:class:`~rapyuta_io.clients.metrics.Tags`)

        Following example demonstrates how to list tag keys

            >>> from rapyuta_io import Client
            >>> from rapyuta_io.clients.metrics import ListTagKeysRequest, Entity
            >>> from datetime import datetime, timedelta
            >>> project_guid = 'project_guid'
            >>> client = Client(auth_token='auth_token', project=project_guid)
            >>> now = datetime.utcnow()
            >>> request = ListTagKeysRequest(Entity.PROJECT, project_guid,
            ...                              start_date=now-timedelta(days=30), end_date=now)
            >>> for tag in client.list_tag_keys(request):
            ...     print(tag.metric_group, tag.tags)

        """
        if not isinstance(list_tag_keys_request, ListTagKeysRequest):
            raise InvalidParameterException('metrics_query_request must be of '
                                            'type rapyuta_io.clients.metrics.ListTagKeysRequest')

        response = self._core_api_client.list_tag_keys(list_tag_keys_request)
        return [Tags.deserialize(resp) for resp in response.get('tag_keys', [])]

    def list_tag_values(self, list_tag_values_request):
        """
        List Tag Values for a particular entity

        :param list_tag_values_request: ListTagValuesRequest
        :type list_tag_values_request: :py:class:`~rapyuta_io.clients.metrics.ListTagValuesRequest`
        :rtype: list(str)

        Following example demonstrates how to list tag values

            >>> from rapyuta_io import Client
            >>> from rapyuta_io.clients.metrics import ListTagValuesRequest, Entity
            >>> from datetime import datetime, timedelta
            >>> project_guid = 'project_guid'
            >>> client = Client(auth_token='auth_token', project=project_guid)
            >>> now = datetime.utcnow()
            >>> request = ListTagValuesRequest(Entity.PROJECT, project_guid, 'cpu',
            ...                                start_date=now-timedelta(days=30), end_date=now)
            >>> for tag_value in client.list_tag_values(request):
            ...     print(tag_value)

        """
        if not isinstance(list_tag_values_request, ListTagValuesRequest):
            raise InvalidParameterException('metrics_query_request must be of '
                                            'type rapyuta_io.clients.metrics.ListTagValuesRequest')

        response = self._core_api_client.list_tag_values(list_tag_values_request)
        return response.get('tags_values', [])
