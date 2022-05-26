# encoding: utf-8
from __future__ import absolute_import

from collections import defaultdict

import enum
import six

import rapyuta_io
from rapyuta_io.clients import ProvisionClient
from rapyuta_io.clients.deployment import Deployment
from rapyuta_io.clients.deployment import DeploymentPhaseConstants
from rapyuta_io.clients.native_network import NativeNetwork
from rapyuta_io.clients.device import SPACE_GUID, VOLUME_PACKAGE_ID, INSTANCE_ID, Device
from rapyuta_io.clients.plan import Plan
from rapyuta_io.clients.rosbag import ROSBagJob, ROSBagOptions, UploadOptions
from rapyuta_io.clients.routed_network import RoutedNetwork
from rapyuta_io.clients.static_route import StaticRoute
from rapyuta_io.utils import ObjDict, to_objdict, OperationNotAllowedError, PlanNotFound, \
    InvalidParameterException, RestClient, APIError, ParameterMissingException, \
    AliasNotProvidedException, DuplicateAliasException
from rapyuta_io.utils.constants import DEVICE, DEVICE_ID, LABELS
from rapyuta_io.utils.rest_client import HttpMethod
from rapyuta_io.utils.settings import ORGANIZATION_GUID, CATALOG_API_PATH
from rapyuta_io.utils.utils import is_empty, \
    get_api_response_data, \
    create_auth_header
from rapyuta_io.utils.partials import PartialMixin

CURRENT_PKG_VERSION = '2.0.0'


class Package(PartialMixin, ObjDict):
    """
    Package class represents a service package. It contains method to provision
    an instance of the package on cloud or on device. Additionally, it provides other utility
    method. \n
    Variables marked as (full-only) are only available on a full object. Use `refresh()` to convert a
    partial object into a full one.

    :ivar packageId: Id of the package.
    :ivar packageName: Package name.
    :ivar packageVersion: Version of the package.
    :ivar apiVersion: (full-only) Package API Version.
    :ivar bindable: Package is bindable or not.
    :ivar description: Description of the package.
    :ivar category: (full-only) Package category.
    :ivar plans: (full-only) List of plans associated with the package.
    :vartype plans: list(:py:class:`~rapyuta_io.clients.plan.Plan`)
    :ivar isPublic: (full-only) Boolean denoting whether the package is public or not.
    :ivar status: (full-only) Status of the package.
    :ivar tags: (full-only) Tags associated with the package.
    :ivar buildGeneration: (full-only) Build generation.
    :ivar ownerProject: (full-only) Owner project guid.
    :ivar creator: (full-only) Creator user guid.
    :ivar CreatedAt: (full-only) Date of creation.
    :ivar UpdatedAt: (full-only) Date of updation.
    :ivar DeletedAt: (full-only) Date of deletion.

    """

    def __init__(self, *args, **kwargs):
        super(ObjDict, self).__init__(*args, **kwargs)

        # Normalize object across responses from /serviceclass/status and /v2/catalog
        if 'guid' in self:  # /serviceclass/status
            self.packageId = self.guid
        else:  # /v2/catalog
            self.packageId = self.id
            self.packageName = self.name
            self.packageVersion = self.metadata['packageVersion']

        self._post_init()

    def refresh(self):
        self._refresh()

    def _refresh(self):
        url = self._host + CATALOG_API_PATH + "?package_uid=%s" % self.packageId
        headers = create_auth_header(self._auth_token, self._project)
        response = RestClient(url).method(HttpMethod.GET).headers(headers).execute()
        package = get_api_response_data(response, True)
        try:
            package = package['packageInfo']
        except Exception:
            raise APIError("packageInfo not present in the package")
        # PARTIAL_ATTR set before initializing Package: Package._post_init() depends on is_partial
        package[PartialMixin.PARTIAL_ATTR] = False
        pkg = Package(to_objdict(package))
        for attr in pkg.keys():
            self.__setattr__(attr, pkg.__getattr__(attr))

    def delete(self):

        """
        Delete the package using the package object.

        Following example demonstrates how to delete a package using package object:

        >>> from rapyuta_io import Client
        >>> client = Client(auth_token='auth_token', project='project_guid')
        >>> package = client.get_package(package_id='package_id')
        >>> package.delete()

        """

        url = self._host + '/serviceclass/delete?package_uid={}'.format(self.packageId)
        headers = create_auth_header(self._auth_token, self._project)
        response = RestClient(url).method(HttpMethod.DELETE).headers(headers).execute()
        get_api_response_data(response, parse_full=True)

    def _post_init(self):
        if self.plans and not self.is_partial:
            plans = list()
            for plan in self.plans:
                plans.append(Plan(to_objdict(plan)))
            self.plans = plans
        return

    def _update_auth_token(self, objects):
        for obj in objects:
            setattr(obj, '_host', self._host)
            setattr(obj, '_auth_token', self._auth_token)
            setattr(obj, '_project', self._project)
        return

    def get_plan_by_id(self, plan_id):
        for plan in self.plans:
            if plan.planId == plan_id:
                return plan
        raise PlanNotFound(plan_id)

    def provision(self, deployment_name, provision_configuration, retry_limit=0):
        """
        Provision the package (represented by the package class). Package can be deployed on device
        or cloud. If the required runtime of the package is device, then specify the device in the
        package config. \n
        If the Package object is not complete, as indicated by `self.is_partial`, then `self.refresh()` is called to
        update the object.

        :param deployment_name: Deployment Name
        :type  deployment_name: string
        :param provision_configuration: Provision payload
        :type provision_configuration: :py:class:`ProvisionConfiguration`:
        :param retry_limit: Optional parameter to specify the number of retry attempts to be
               carried out if any failures occurs during the API call.
        :type retry_limit: int
        :return: Instance of class :py:class:`Deployment`:
        :raises: :py:class:`APIError`: If the API returns an error, a status code of
            anything other than 200/201 is returned.
        :raises: :py:class:`OperationNotAllowedError`: If the provision request is invalid

        """
        if not deployment_name or not isinstance(deployment_name, six.string_types):
            raise InvalidParameterException("deployment_name must be a non-empty string")
        if not isinstance(provision_configuration, ProvisionConfiguration):
            raise InvalidParameterException('provision_configuration must be of type ProvisionConfiguration')
        if provision_configuration._is_provisioned:
            raise InvalidParameterException('cannot reuse this ProvisionConfiguration for provisioning')
        if self.is_partial:
            self.refresh()
        provision_configuration.validate()
        provision_configuration.context['name'] = deployment_name
        delattr(provision_configuration, 'plan')
        delattr(provision_configuration, '_dependency_seen_aliases')
        provision_configuration._is_provisioned = True

        provision_client = ProvisionClient(self._host, self._auth_token, self._project)
        response = provision_client.provision(provision_configuration, retry_limit)
        deployment_status = provision_client.deployment_status(response['operation'], retry_limit)
        deployment = Deployment(to_objdict(deployment_status))
        deployment.is_partial = False
        self._update_auth_token([deployment])
        return deployment

    def deployments(self,  phases=None, retry_limit=0):

        """
        Get all the deployments of the package

        :param phases: optional parameter to filter out the deployments based on current deployment
        :type phases: list(DeploymentPhaseConstants)
        :param retry_limit: Optional parameter to specify the number of retry attempts to be
              carried out if any failures occurs during the API call.
        :type retry_limit: int
        :return: list of instance of class :py:class:`Deployment`:
        :raises: :py:class:`APIError`: If deployment info api return an error, the status code is
            anything other than 200/201

        Following example demonstrates how to the deployment list

             >>> from rapyuta_io import Client, DeploymentPhaseConstants
             >>> client = Client(auth_token='auth_token', project='project')
             >>> package = client.get_package('test_package_id')
             >>> package.deployments()
             >>> deployments_list_filtered_by_phase = package.deployments(phases=
             >>>   [DeploymentPhaseConstants.SUCCEEDED, DeploymentPhaseConstants.PROVISIONING])

        """

        deployment_list = ProvisionClient(self._host, self._auth_token, self._project) \
            .deployments(self.packageId,  phases, retry_limit)
        deployments = list()
        if deployment_list:
            for deployment in deployment_list:
                deployments.append(Deployment(to_objdict(deployment)))
            self._update_auth_token(deployments)

        return deployments

    def get_provision_configuration(self, plan_id=None):
        """
        Get provision configuration payload for package provision request. \n
        If the Package object is not complete, as indicated by `self.is_partial`, then `self.refresh()` is called to
        update the object.

        :param plan_id: Plan Id
        :type plan_id: string
        :return: return instance of class :py:class:`ProvisionConfiguration`:

        """
        if self.is_partial:
            self.refresh()

        if plan_id:
            plan = self.get_plan_by_id(plan_id)
        else:
            try:
                plan = self.plans[0]
            except IndexError:
                raise PlanNotFound()

        provision_request = ProvisionConfiguration(self.packageId, plan)
        return provision_request


class ProvisionConfiguration(ObjDict):
    """
    ProvisionConfiguration class that contains the component configuration for a package
    deployment.

    """

    def __init__(self, package_id, plan, *args, **kwargs):
        super(ObjDict, self).__init__(*args, **kwargs)
        self.service_id = package_id
        self.plan = plan
        self.plan_id = plan.planId
        self.api_version = kwargs.get('api_version', '1.0.0')
        self._init_parameters()
        self._dependency_seen_aliases = set()
        self._is_provisioned = False
        self._devices = dict()

    def _init_parameters(self):
        self.context = dict()
        self.context['component_context'] = defaultdict(lambda: defaultdict(dict))
        self.instance_id = INSTANCE_ID
        self.organization_guid = ORGANIZATION_GUID
        self.space_guid = SPACE_GUID
        self.accepts_incomplete = True
        self.parameters = {'global': dict()}
        self.context.setdefault('labels', list())
        self.context.setdefault('dependentDeployments', list())
        self.context.setdefault('diskMountInfo', list())
        self.context.setdefault('routedNetworks', list())
        self.context.setdefault('nativeNetworks', list())
        for component in self.plan.components.components:
            component_id = self.plan.get_component_id(component.name)
            com_dict = dict(component_id=component_id)
            for params in component.parameters:
                if not params.get('default'):
                    com_dict[params.name] = None
                else:
                    com_dict[params.name] = params.default
            self.parameters[component_id] = com_dict
            self.set_component_alias(component.name)
            job_defs = getattr(component, 'rosBagJobDefs', [])
            for job_def in job_defs:
                rosbag_opts = ROSBagOptions.deserialize(job_def.recordOptions)
                upload_opts = UploadOptions.deserialize(job_def.uploadOptions) if hasattr(job_def, 'uploadOptions')\
                              else None
                job = ROSBagJob(job_def.name, rosbag_options=rosbag_opts, upload_options=upload_opts)
                self.add_rosbag_job(component.name, job)

    def _validate_device_id(self, component_id):
        value = self.parameters[component_id].get(DEVICE_ID, None)
        if is_empty(value):
            msg = 'component is not mapped with the device'
            raise OperationNotAllowedError(msg)
        return True

    def _get_component_by_name(self, component_name):
        for component in self.plan.components.components:
            if component.name == component_name:
                return component
        raise AttributeError

    def validate_component_executables(self, component_name, device_runtime):
        component = self.plan.get_component_by_name(component_name)
        if not component:
            raise OperationNotAllowedError('Component named %s is not found on the plan' %
                                           component_name)
        for executable in component.executables:
            is_docker_executable = executable.get('buildGUID') or \
                                   executable.get('gitExecutable') or executable.get('docker')
            if is_docker_executable and device_runtime == Device.PRE_INSTALLED:
                raise OperationNotAllowedError('Device must be a {} device'.format(Device.DOCKER_COMPOSE))
            if not is_docker_executable and device_runtime == Device.DOCKER_COMPOSE:
                raise OperationNotAllowedError('Device must be a {} device'.format(Device.PRE_INSTALLED))

    def add_restart_policy(self, component_name, restart_policy):
        """
        Add RestartPolicy for the component

        :param component_name: Component name
        :type component_name: string
        :param restart_policy: one of RestartPolicy enums
        :type restart_policy: enum :py:class:`~RestartPolicy`
        :return: Updated instance of class :py:class:`ProvisionConfiguration`
        :raises: :py:class:`InvalidParameterException`: If restart policy is not invalid
        """
        if restart_policy not in list(RestartPolicy.__members__.values()):
            raise InvalidParameterException('Restart policy must be one of rapyuta_io.clients.package.RestartPolicy')
        component_id = self.plan.get_component_id(component_name)
        self.context['component_context'][component_id]['component_override']['restart_policy'] = restart_policy.value
        return self

    def add_rosbag_job(self, component_name, rosbag_job):
        """
        Add rosbag for a component

        :param component_name: Component name
        :type component_name: string
        :param rosbag_job: instance of ROSBagJob
        :type rosbag_job: :py:class:`~rapyuta_io.clients.rosbag.ROSBagJob`
        :return: Updated instance of class :py:class:`ProvisionConfiguration`
        :raises: :py:class:`InvalidParameterException`: If rosbag_job is not instance of ROSBagJob
        :raises: :py:class:`OperationNotAllowedError`: If component is non ros or is a device component
        """
        component_id = self.plan.get_component_id(component_name)
        if not isinstance(rosbag_job, ROSBagJob):
            raise InvalidParameterException('rosbag_job needs to a ROSBagJob object')
        component = self.plan.get_component_by_name(component_name)
        if not component.ros.isROS:
            raise OperationNotAllowedError('rosbag job is only supported for ros components')
        component_context = self.context['component_context'][component_id]
        component_context['ros_bag_job_defs'] = component_context.get('ros_bag_job_defs', [])
        for job in component_context['ros_bag_job_defs']:
            if job['name'] == rosbag_job.name:
                raise OperationNotAllowedError('rosbag job with same name already exists')
        rosbag_jobs = {'name': rosbag_job.name,
                       'recordOptions': rosbag_job.rosbag_options.serialize()}
        if rosbag_job.upload_options:
            rosbag_jobs['uploadOptions'] = rosbag_job.upload_options.serialize()
        component_context['ros_bag_job_defs'].append(rosbag_jobs)

    def remove_rosbag_job(self, component_name, job_name):
        """
        Remove rosbag job by its name

        :param component_name: Component name
        :type component_name: string
        :param job_name: name of ROSBagJob
        :type job_name: string
        """
        component_id = self.plan.get_component_id(component_name)
        component_context = self.context['component_context'][component_id]
        component_context['ros_bag_job_defs'] =\
            [job for job in component_context['ros_bag_job_defs'] if job['name'] != job_name]

    def add_routed_network(self, routed_network, network_interface=None):
        """
        Add Routed Network

        :param routed_network: RoutedNetwork
        :type routed_network: instance of :py:class:`~rapyuta_io.clients.routed_network.RoutedNetwork`
        :param network_interface: interface to which current deployment to bind
        :type network_interface: string
        :return: Updated instance of class :py:class:`ProvisionConfiguration`
        :raises: :py:class:`InvalidParameterException`: If routed network is not valid
        :raises: :py:class:`OperationNotAllowedError`: If network interface given for cloud runtime
        """

        if not isinstance(routed_network, RoutedNetwork):
            raise InvalidParameterException('routed networks must be of type RoutedNetwork')

        if routed_network.runtime == Runtime.CLOUD and network_interface:
            raise OperationNotAllowedError('cloud routed network does not bind to network interface')

        routed_network_config = dict()
        routed_network_config_exists = False
        for routed_net in self.context['routedNetworks']:
            if routed_net['guid'] == routed_network['guid']:
                routed_network_config_exists = True
                routed_network_config = routed_net
                break

        if network_interface:
            routed_network_config['bindParameters'] = {'NETWORK_INTERFACE': network_interface}

        if not routed_network_config_exists:
            routed_network_config['guid'] = routed_network.guid
            self.context['routedNetworks'].append(routed_network_config)

        return self

    def add_routed_networks(self, routed_networks):
        """

        :param routed_networks: list of routed network :py:class:`~rapyuta_io.clients.routed_network.RoutedNetwork`
        :type routed_networks: list
        :return: Updated instance of class :py:class:`ProvisionConfiguration`

             >>> from rapyuta_io import Client
             >>> from rapyuta_io.clients.package import ROSDistro
             >>> client = Client(auth_token='auth_token', project='project')
             >>> routed_network = client.create_cloud_routed_network('network_name',
                                  ROSDistro.KINETIC, True)
             >>> routed_network.poll_routed_network_till_ready()
             >>> package = client.get_package('test_package_id')
             >>> package_provision_config = package.get_provision_configuration('test_plan_id')
             >>> package_provision_config.add_routed_networks([routed_network])
             >>> package.provision(deployment_name, package_provision_config)
        """

        for routed_network in routed_networks:
            self.add_routed_network(routed_network)
        return self

    def add_native_network(self, native_network, network_interface=None):
        """
        Add Native Network

        :param native_network: NativeNetwork
        :type native_network: instance of :py:class:`~rapyuta_io.clients.native_network.NativeNetwork`
        :param network_interface: interface to which current deployment to bind, only required for device native network
        :type network_interface: string

        :return: Updated instance of class :py:class:`ProvisionConfiguration`
        :raises: :py:class:`InvalidParameterException`: If native network is not valid
        :raises: :py:class:`OperationNotAllowedError`: If native network is not of cloud runtime

             >>> from rapyuta_io import Client
             >>> from rapyuta_io.clients.package import ROSDistro, Runtime
             >>> from rapyuta_io.clients.native_network import NativeNetwork
             >>> client = Client(auth_token='auth_token', project='project')
             >>> native_network = NativeNetwork("native_network_name", Runtime.CLOUD,
             ...                                ROSDistro.KINETIC)
             >>> native_network = client.create_native_network(native_network)
             >>> native_network.poll_native_network_till_ready()
             >>> package = client.get_package('test_package_id')
             >>> package_provision_config = package.get_provision_configuration('test_plan_id')
             >>> package_provision_config.add_native_network(native_network)
             >>> package.provision('deployment_name', package_provision_config)
        """
        if not isinstance(native_network, NativeNetwork):
            raise InvalidParameterException('native network must be of type NativeNetwork')

        if native_network.runtime == Runtime.CLOUD and network_interface:
            raise OperationNotAllowedError('cloud native network does not bind to network interface')

        native_network_config = dict()
        native_network_config_exists = False
        for native_net in self.context['nativeNetworks']:
            if native_net['guid'] == native_network.guid:
                native_network_config_exists = True
                native_network_config = native_net
                break

        if network_interface:
            native_network_config['bindParameters'] = {'NETWORK_INTERFACE': network_interface}

        if not native_network_config_exists:
            native_network_config['guid'] = native_network.guid
            self.context['nativeNetworks'].append(native_network_config)

        return self

    def add_native_networks(self, native_networks):
        """
        Add Native Networks

        :param native_networks: list of native network :py:class:`~rapyuta_io.clients.native_network.NativeNetwork`
        :type native_networks: list
        :return: Updated instance of class :py:class:`ProvisionConfiguration`

             >>> from rapyuta_io import Client
             >>> from rapyuta_io.clients.package import ROSDistro, Runtime
             >>> from rapyuta_io.clients.native_network import NativeNetwork
             >>> client = Client(auth_token='auth_token', project='project')
             >>> native_network = NativeNetwork("native_network_name", Runtime.CLOUD,
                                                ROSDistro.KINETIC)
             >>> native_network = client.create_native_network(native_network)
             >>> native_network.poll_native_network_till_ready()
             >>> package = client.get_package('test_package_id')
             >>> package_provision_config = package.get_provision_configuration('test_plan_id')
             >>> package_provision_config.add_native_networks([native_network])
             >>> package.provision('deployment_name', package_provision_config)
        """
        for native_network in native_networks:
            self.add_native_network(native_network)
        return self

    def add_device(self, component_name, device, ignore_device_config=None, set_component_alias=True):
        """
        Map component configuration with a device. ie, Setting the component is going to deploy on the given device.
        By Default, the component alias name is set to the device name, if this has to be ignored please use
        'set_component_alias=False' as one of the method parameters.

        :param component_name: Component name
        :type component_name: string
        :param device: Device
        :type device: instance of class :py:class:`Device`:
        :param ignore_device_config: Optional parameter to ignore the device config variables
        :type ignore_device_config: list
        :param set_component_alias: Optional parameter to set the alias name of the component same as device name.
                                    Defaults to True
        :type set_component_alias: bool
        :return: Updated instance of class :py:class:`ProvisionConfiguration`:
        :raises: :py:class:`OperationNotAllowedError`: If the device is not online

             >>> from rapyuta_io import Client
             >>> client = Client(auth_token='auth_token', project='project')
             >>> package = client.get_package('test_package_id')
             >>> device = client.get_device('test_device_id')
             >>> package_provision_config = package.get_provision_configuration('test_plan_id')
             >>> # ros_workspace will be ignored while adding device to provision configuration
             >>> package_provision_config.add_device('test_component_name', 'test_device_id',
             >>>                                     ignore_device_config=['ros_workspace'], set_component_alias=False)
             >>> package.provision('deployment_name', package_provision_config)

        """
        ignore_device_config = ignore_device_config or []
        if not device.is_online():
            raise OperationNotAllowedError('Device should be online')

        device_runtime = device.get_runtime()
        self.validate_component_executables(component_name, device_runtime)

        component_id = self.plan.get_component_id(component_name)
        component_params = self.parameters.get(component_id)
        component_params[DEVICE_ID] = device.deviceId
        if set_component_alias:
            self.set_component_alias(component_name, device.name)
        if device_runtime == device.DOCKER_COMPOSE and 'ros_workspace' not in ignore_device_config:
            ignore_device_config.append('ros_workspace')
        if device_runtime == device.PRE_INSTALLED and \
                'rosbag_mount_path' not in ignore_device_config:
            ignore_device_config.append('rosbag_mount_path')
        for config_var in device.get_config_variables():
            if config_var.key in ignore_device_config:
                continue
            component_params[config_var.key] = config_var.value

        if device_runtime == device.PRE_INSTALLED:
            if 'ros_workspace' not in ignore_device_config and not self._validate_ros_workspace(
                    component_id):
                raise InvalidParameterException('ros_workspace is not set')

        component = self._get_component_by_name(component_name)
        if not component.ros.isROS:
            self.parameters[component_id].pop('ros_distro', None)
        if device_runtime == device.PRE_INSTALLED and \
                not self._validate_ros_distro(component.ros.isROS, component_id):
            raise InvalidParameterException('ros_distro is not set')
        global_config = self.parameters.get('global')
        if 'device_ids' not in global_config:
            global_config['device_ids'] = list()
        global_config['device_ids'].append(device.deviceId)
        self._devices[device.deviceId] = device
        return self

    def add_parameter(self, component_name, key, value):
        """
        Add component parameters

        :param component_name: Component name
        :type component_name: string
        :param key: Parameter key
        :type key: string
        :param value: Parameter value
        :type value: string
        :return: Updated instance of class :py:class:`ProvisionConfiguration`:
        """
        if not component_name or not isinstance(component_name, six.string_types):
            raise InvalidParameterException("component_name must be a non-empty string")
        if not key or not isinstance(key, six.string_types):
            raise InvalidParameterException("key must be a non-empty string")
        if not value or not isinstance(value, six.string_types):
            raise InvalidParameterException("value must be a non-empty string")
        component_id = self.plan.get_component_id(component_name)
        self.parameters[component_id][key] = value
        return self

    def set_component_alias(self, component_name, alias="", set_ros_namespace=False):
        """
        Set an alias and ROS_NAMESPACE environment variable flag for the selected component.
        This is used in scoping and targeting. alias defaults to the component name.
        set_ros_namespace defaults to false

        *Note:* In typical scenarios in the case of a cloud deployment, alias is set to the component name
        (or some derivation thereof) and on the device it is set to the device name. But it is left to the user.
        All set aliases in a deployment and its dependent deployments are required to be unique.

        :param component_name: Component name
        :type component_name: string
        :param alias: alias for component
        :type alias: string
        :param set_ros_namespace: flag to set alias as ROS_NAMESPACE environment variable in the deployment.
                                  It should be used only for deployments using native networks.
        :type set_ros_namespace: bool
        :return: Updated instance of class :py:class:`ProvisionConfiguration`:
        """
        if not component_name or not isinstance(component_name, six.string_types):
            raise InvalidParameterException("component_name must be a non-empty string")
        if not isinstance(alias, six.string_types):
            raise InvalidParameterException("alias must be a string")
        if not isinstance(set_ros_namespace, bool):
            raise InvalidParameterException("set_ros_namespace must be a boolean")
        component_id = self.plan.get_component_id(component_name)
        alias = component_name if alias == "" else alias
        self.parameters[component_id]["bridge_params"] = {"alias": alias, "setROSNamespace": set_ros_namespace}

    def _add_dependency(self, deployment_id, component_id=None, mount_path=None, network_interface=None,
                        executable_mounts=None):
        dep_info = dict()
        dep_info['dependentDeploymentId'] = deployment_id
        if component_id:
            dep_info['applicableComponentId'] = component_id
        else:
            dep_info['applicableComponentId'] = ''

        dep_info['config'] = dict()
        if mount_path:
            dep_info['config']['mountPath'] = mount_path
        if executable_mounts:
            d = {}
            for mount in executable_mounts:
                d[mount.exec_name] = {}
                d[mount.exec_name]['mountPath'] = mount.mount_path
                if mount.sub_path:
                    d[mount.exec_name]['subPath'] = mount.sub_path
            dep_info['config']['mountPaths'] = d
        if network_interface:
            dep_info['config']['NETWORK_INTERFACE'] = network_interface
        self.context['dependentDeployments'].append(dep_info)

    def _add_disk_mount_info(self, resource_id, component_id, executable_mounts):
        dep_info = dict()
        dep_info['diskResourceId'] = resource_id
        dep_info['applicableComponentId'] = component_id
        dep_info['config'] = dict()
        mountPaths = {}
        for mount in executable_mounts:
            mountPaths[mount.exec_name] = {}
            mountPaths[mount.exec_name]['mountPath'] = mount.mount_path
            if mount.sub_path:
                mountPaths[mount.exec_name]['subPath'] = mount.sub_path
            else:
                mountPaths[mount.exec_name]['subPath'] = '/'

        dep_info['config']['mountPaths'] = mountPaths
        self.context['diskMountInfo'].append(dep_info)

    def mount_volume(self, component_name, volume=None, device=None, mount_path=None, executable_mounts=None):
        """
        To mount a volume instance.

        :param component_name: Component name
        :type component_name: string
        :param volume: VolumeInstance class
        :type volume: instance of class :py:class:`VolumeInstance`:
        :param device: Device class
        :type device: instance of class :py:class:`Device`:
        :param mount_path: Mount path
        :type mount_path: string
        :param executable_mounts: list of executable mounts. mandatory parameter for device volumes
        :type executable_mounts: list(:py:class:`ExecutableMount`)
        :return: Updated instance of class :py:class:`ProvisionConfiguration`:
        """
        if volume == None and device == None:
            raise InvalidParameterException('either a volume or device parameter must be present')
        if volume != None and device != None:
            raise InvalidParameterException('both volume and device parameter cannot be present')
        component_id = self.plan.get_component_id(component_name)
        if device != None:
            if not isinstance(device, Device):
                raise InvalidParameterException('device must be of type Device')
            if not isinstance(executable_mounts, list) or not all(
                    isinstance(mount, ExecutableMount) for mount in executable_mounts):
                raise InvalidParameterException(
                    'executable_mounts must be a list of rapyuta_io.clients.package.ExecutableMount')
            if not device.is_online():
                raise OperationNotAllowedError('Device should be online')
            if device.get_runtime() != Device.DOCKER_COMPOSE:
                raise OperationNotAllowedError('Device must be a {} device'.format(Device.DOCKER_COMPOSE))
            component_params = self.parameters.get(component_id)
            if component_params.get(DEVICE_ID) != device.deviceId:
                raise OperationNotAllowedError('Device must be added to the component')
            self._add_disk_mount_info(device.deviceId, component_id, executable_mounts)
        else:
            if not isinstance(volume, rapyuta_io.clients.persistent_volumes.VolumeInstance):
                raise InvalidParameterException(
                    'volume must be of type rapyuta_io.clients.persistent_volumes.VolumeInstance')
            if not volume.packageId == VOLUME_PACKAGE_ID:
                raise InvalidParameterException('Invalid volume instance')
            if volume.get_status().phase != DeploymentPhaseConstants.SUCCEEDED.value:
                raise OperationNotAllowedError('Dependent deployment is not running')
            if (mount_path is None and executable_mounts is None) or (
                        mount_path is not None and executable_mounts is not None):
                raise InvalidParameterException('One of mount_path or executable_mounts should be present')
            if executable_mounts is not None and ((not isinstance(executable_mounts, list)) or not all(
                        isinstance(mount, ExecutableMount) for mount in executable_mounts)):
                raise InvalidParameterException(
                    'executable_mounts must be a list of rapyuta_io.clients.package.ExecutableMount')
            self._add_dependency(volume.deploymentId, component_id, mount_path, executable_mounts=executable_mounts)
        return self

    def add_dependent_deployment(self, deployment):
        """
        Add dependent deployments. \n
        `deployment.refresh()` is called to get the latest deployment status.

        :param deployment: Deployment
        :type deployment:  class :py:class:`Deployment`:
        :return: Updated instance of class :py:class:`ProvisionConfiguration`:
        """
        deployment.refresh()
        if deployment.phase != DeploymentPhaseConstants.SUCCEEDED.value:
            raise OperationNotAllowedError('Dependent deployment is not running')
        self._update_dependency_seen_aliases_set(deployment)
        self._add_dependency(deployment_id=deployment.deploymentId)

        return self

    def add_static_route(self, component_name, endpoint_name, static_route):
        """
        Add static route to a component in a package

        :param component_name: Name of the component to add static route to
        :param endpoint_name: Name of the endpoint (Should be exposed externally)
        :param static_route: class :py:class:`StaticRoute`:
        :return: Updated instance of class :py:class:`ProvisionConfiguration`:
        """
        if not isinstance(static_route, StaticRoute):
            raise TypeError("{} is not of type Static Route".format(static_route))
        component_id = self.plan.get_component_id(component_name)
        self.context['component_context'][component_id]['static_route_config'][endpoint_name] = static_route.guid
        return self

    def _update_dependency_seen_aliases_set(self, deployment):
        for params in deployment.parameters.values():
            try:
                self._dependency_seen_aliases.add(params.bridge_params.alias)
                self.plan._needs_alias = True
            except AttributeError:
                pass

    def add_label(self, key, value):
        """
        Add labels

        :param key: Key
        :type key: string
        :param value: Value
        :type value: string
        :return: Updated instance of class :py:class:`ProvisionConfiguration`:
        """
        if not key or not value:
            raise ParameterMissingException(str.format("key or value of parameter is missing"))

        label = {'key': key, 'value': value}
        self.context[LABELS].append(label)
        return self

    def _validate_ros_workspace(self, component_id):
        if not self.parameters[component_id].get('ros_workspace'):
            return False
        return True

    def _validate_ros_distro(self, isRos, component_id):
        if isRos and not self.parameters[component_id].get('ros_distro'):
            return False
        return True

    def validate(self):
        for component in self.plan.components.components:
            component_id = self.plan.get_component_id(component.name)
            if component.requiredRuntime == DEVICE:
                self._validate_device_id(component_id)
                self._validate_rosbag_devices(component_id)
            component_params = component.parameters
            for param in component_params:
                name = param.name
                if is_empty(self.parameters[component_id][name]):
                    raise InvalidParameterException('Provide the value for the parameter {} in '
                                                    'component {}'.format(param.name, component.name))

        self._validate_aliases()
        return True

    def _validate_rosbag_devices(self, component_id):
        if not self.context['component_context'][component_id].get('ros_bag_job_defs'):
            return
        device_id = self.parameters[component_id].get(DEVICE_ID, None)
        if not device_id:
            return
        device = self._devices.get(device_id)
        if device.get_runtime() == device.PRE_INSTALLED:
            raise InvalidParameterException('ROSBag on Device does not support Preinstalled '
                                            'devices')
        required_config = [x for x in device.config_variables if x.key == 'rosbag_mount_path'
                           and x.value != '']
        if not required_config:
            raise InvalidParameterException('This device does not have ROSBag components installed.' 
                                            ' Please re-onboard the device to use ROSBag features')

    def _validate_aliases(self):
        aliases_needed = self.plan.needs_aliases()
        if not aliases_needed:
            for params in self.parameters.values():
                if "bridge_params" in params:
                    params.pop("bridge_params")
            return
        seen_aliases = set()
        for component_id, params in self.parameters.items():
            if component_id == "global":
                continue
            try:
                alias = params["bridge_params"]["alias"]
                if alias in seen_aliases:
                    raise DuplicateAliasException(
                        "Aliases must be unique. Alias %s provided for %s component isn't" % (alias, component_id))
                if alias in self._dependency_seen_aliases:
                    raise DuplicateAliasException(
                        "Aliase %s for %s component conflicts with dependant deployment" % (alias, component_id))
                seen_aliases.add(alias)
            except KeyError:
                raise AliasNotProvidedException(
                    "Aliases are required but not provided for %s component" % component_id)


class ExecutableMount(object):
    """
    ExecutableMount defines the mount details specific to an executable.

    :ivar exec_name: Name of the executable.
    :vartype exec_name: str
    :ivar mount_path: Mountpath of the executable
    :vartype mount_path: str
    :ivar sub_path: Subpath of the executable
    :vartype sub_path: str

    :param exec_name: Name of the executable.
    :type exec_name: str
    :param mount_path: Mountpath of the executable
    :type mount_path: str
    :param sub_path: Subpath of the executable
    :type sub_path: str
    """

    def __init__(self, exec_name, mount_path, sub_path=None):
        self.validate(exec_name, mount_path, sub_path)
        self.exec_name = exec_name
        self.mount_path = mount_path
        self.sub_path = sub_path

    @staticmethod
    def validate(exec_name, mount_path, sub_path=None):
        if not isinstance(exec_name, six.string_types):
            raise InvalidParameterException('exec_name must be a non-empty string')
        if not isinstance(mount_path, six.string_types):
            raise InvalidParameterException('mount_path must be a non-empty string')
        if sub_path is not None and not isinstance(sub_path, six.string_types):
            raise InvalidParameterException('sub_path must be a non-empty string')


class RestartPolicy(str, enum.Enum):
    """
    Enumeration variables for the Restart Policy. Restart Policy may be 'Always', 'Never' or 'OnFailure' \n
    RestartPolicy.Always \n
    RestartPolicy.Never \n
    RestartPolicy.OnFailure \n
    """

    def __str__(self):
        return str(self.value)

    Always = "always"
    Never = "no"
    OnFailure = "on-failure"


class ROSDistro(str, enum.Enum):
    """
    Enumeration variables for the Supported ROS Distros. ROS Distro may be one of: \n
    ROSDistro.KINETIC ('kinetic') \n
    ROSDistro.MELODIC ('melodic') \n
    ROSDistro.NOETIC ('noetic') \n
    """

    def __str__(self):
        return str(self.value)

    KINETIC = 'kinetic'
    MELODIC = 'melodic'
    NOETIC = 'noetic'


class Runtime(str, enum.Enum):
    """
    Enumeration variables for the Supported Runtimes. Runtime may be 'cloud', or 'device' \n
    Runtime.CLOUD \n
    Runtime.DEVICE \n
    """

    def __str__(self):
        return str(self.value)

    CLOUD = 'cloud'
    DEVICE = 'device'
