# Default Python Libraries
from importlib import import_module
from multiprocessing.pool import ThreadPool
from typing import Dict
from uuid import uuid4

# AristaFlow REST Libraries
from aristaflow.configuration import Configuration


class RestPackage(object):
    """
    Represents an AristaFlow REST endpoint package, e.g. af_execution_manager.
    """

    package_name: str = None
    # cached configuration as this can be used across all instances
    __config: object = None
    af_conf: Configuration = None

    def __init__(self, package_name: str, af_conf: Configuration):
        """
        :param package_name str: The base package name, e.g. af_org_model_manager
        :param af_conf Configuration: The AristaFlow BPM configuration.
        """
        self.package_name = package_name
        self.af_conf = af_conf

    @property
    def config(self):
        """
        :return: The configuration of the REST package
        """
        if self.__config is None:
            config_module = import_module(self.package_name + ".configuration")
            config_class = config_module.__getattribute__("Configuration")
            config = config_class()
            config.host = self.af_conf.get_host(self.service_type_name)
            config.debug = self.af_conf.get_debug(self.service_type_name)
            config.verify_ssl = self.af_conf.verify_ssl
            self.__config = config

        return self.__config

    def build_api_client(self):
        """
        Create a new ApiClient instance for this REST package
        """
        ac_module = import_module(self.package_name + ".api_client")
        ac_class = ac_module.__getattribute__("ApiClient")
        api_client = ac_class(self.config)
        api_client.set_default_header("x-AF-Caller-URI", self.af_conf.caller_uri)
        # Runtime Service requires matching session IDs for its start/signal calls
        # since we can't set them on a per-request basis, set a random session
        # id for the lifetime of the service instance
        if self.package_name.startswith("af_runtime_service"):
            api_client.set_default_header("x-AF-Session-ID", str(uuid4()))
        return api_client

    @property
    def service_type_name(self):
        """
        The AristaFlow service type name for this package, e.g. ExecutionManager
        """
        if self.package_name == "af_execution_manager":
            return "ExecutionManager"
        elif self.package_name == "af_licence_manager":
            return "LicenceManager"
        elif self.package_name == "af_org_model_manager":
            return "OrgModelManager"
        elif self.package_name == "af_process_manager":
            return "ProcessManager"
        elif self.package_name == "af_runtime_service":
            return "RuntimeService"
        elif self.package_name == "af_worklist_manager":
            return "WorklistManager"
        elif self.package_name == "af_remote_html_runtime_manager":
            return "RuntimeManager"
        elif self.package_name == "af_simple_process_image_renderer":
            return "SimpleProcessImageRenderer"
        elif self.package_name == "af_res_model_manager":
            return "ResModelManager"
        elif self.package_name == "af_process_image_renderer":
            return "ProcessImageRenderer"
        else:
            raise Exception("Unknown package: " + self.package_name)

    @property
    def default_instance_name(self):
        """
        The AristaFlow default hierarchical instance name, e.g. /ExecutionManager/ExecutionManager
        """
        service_instance_name: str = (
            self.service_type_name
            if self.service_type_name != "RuntimeManager"
            else "RemoteHTMLRuntimeManager"
        )
        return "/" + self.service_type_name + "/" + service_instance_name


class RestPackageRegistry(object):
    __rest_packages: [str, RestPackage] = None
    af_conf: Configuration = None

    def __init__(self, af_conf: Configuration):
        self.__rest_packages = {}
        self.af_conf = af_conf

    def get_rest_package(self, service_type: type):
        """
        Returns the REST package for the given service type.
        :return RestPackage: The REST package object.
        """
        pn = self.get_package_name(service_type)
        if pn in self.__rest_packages:
            return self.__rest_packages[pn]
        pkg = RestPackage(pn, self.af_conf)
        self.__rest_packages[pn] = pkg
        return pkg

    def get_package_name(self, service_type: type):
        """
        Returns the rest package for the given service type.
        :return str: The package name for the given service type.
        """
        moduleName: str = service_type.__module__
        return moduleName.split(".")[0]


class RestPackageInstance(object):
    """
    A REST package instance, ie. a REST package with an ApiClient object to be used for
    all of its services
    """

    __rest_package: RestPackage = None
    __api_client: object = None

    def __init__(self, rest_package: RestPackage, async_thread_pool: ThreadPool):
        self.__rest_package = rest_package
        self.__async_thread_pool = async_thread_pool

    @property
    def api_client(self) -> object:
        if self.__api_client is None:
            self.__api_client = self.__rest_package.build_api_client()
            # replace the default thread pool with our own, shared one
            orig_pool = self.__api_client.pool
            self.__api_client.pool = self.__async_thread_pool
            orig_pool.close()  # no need to join(), work hadn't started yet
        return self.__api_client

    def deserialize(self, data, klass):
        """Deserialize data using the given class of the generated OpenAPI models."""
        ac = self.api_client
        # print(dir(ac))
        return ac._ApiClient__deserialize(data, klass)

    def serialize(self, obj) -> Dict:
        """Serialize REST model object"""
        ac = self.api_client
        return ac.sanitize_for_serialization(obj)
