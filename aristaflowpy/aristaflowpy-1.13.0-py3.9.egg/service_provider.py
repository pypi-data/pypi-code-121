# -*- coding: utf-8 -*-
# Default Python Libraries
from concurrent.futures import ThreadPoolExecutor
from importlib import import_module
from typing import Dict, Generator, Tuple, Type, TypeVar

# Third Party Libraries
import sseclient

# AristaFlow REST Libraries
from af_org_model_manager.models.client_session_details import ClientSessionDetails

from .rest_helper import RestPackage, RestPackageInstance, RestPackageRegistry


T = TypeVar("T")


class ServiceProvider(object):
    """Per user session service provider caching service stubs and providing authentication data to them."""

    __rest_package_registry: RestPackageRegistry = None
    # package to package instance map
    __rest_packages: [RestPackage, RestPackageInstance] = None
    # cached service stubs
    __services: [type, object] = None
    # authentication
    __csd: ClientSessionDetails = None
    # thread pool for sse handling
    __thread_pool: ThreadPoolExecutor = None

    def __init__(
        self,
        rest_package_registry: RestPackageRegistry,
        thread_pool: ThreadPoolExecutor,
    ):
        self.__rest_package_registry = rest_package_registry
        self.__rest_packages = {}
        self.__services = {}
        self.__thread_pool = thread_pool

    def __get_package_instance(self, service_type: Type) -> RestPackageInstance:
        """Returns the (cached) ApiClient instance for the package of the given service_type.
        Note, that service_type may also be a model class.
        """
        # find the package description and package instance
        pkg = self.__rest_package_registry.get_rest_package(service_type)
        pkg_instance: RestPackageInstance = None
        if pkg in self.__rest_packages:
            pkg_instance = self.__rest_packages[pkg]
        else:
            pkg_instance = RestPackageInstance(pkg, self.__thread_pool)
            self.__rest_packages[pkg] = pkg_instance

        return pkg_instance

    def get_service(self, service_type: Type[T]) -> T:
        """
        Returns a service instance for the given service type, e.g.
        get_service(InstanceControlApi)
        @param service_type The class of the requested service.
        """
        # return a cached instance
        if service_type in self.__services:
            return self.__services[service_type]

        # get the ApiClient object of the package
        api_client = self.__get_package_instance(service_type).api_client

        # authentication data
        if self.__csd:
            self.__use_authentication(api_client)
        # instantiate the service
        service = service_type(api_client)
        # cache it
        self.__services[service_type] = service
        return service

    def __use_authentication(self, api_client: object):
        """Uses the client session details to set the default header"""
        api_client.set_default_header("x-AF-Security-Token", self.__csd.token)

    def authenticated(self, csd: ClientSessionDetails):
        """set the authentication for all ApiClient objects"""
        if self.__csd is not None:
            raise Exception("Already authenticated")

        self.__csd = csd
        for key in self.__rest_packages:
            inst = self.__rest_packages[key]
            self.__use_authentication(inst.api_client)

    def deserialize(self, data, klass):
        """Deserialize data using the given class of the generated OpenAPI models."""
        return self.__get_package_instance(klass).deserialize(data, klass)

    def serialize(self, obj) -> Dict:
        """Serialize REST model object"""
        klass = type(obj)
        return self.__get_package_instance(klass).serialize(obj)

    def get_arista_flow_service_api(self, klass: Type):
        """
        Returns the AristaFlowApi object for the endpoint the given klass belongs to.
        """
        package_name = self.__rest_package_registry.get_package_name(klass)
        package_name = package_name + ".api.arista_flow_service_api"
        afsapi_module = import_module(package_name)
        afsapi_class = afsapi_module.__getattribute__("AristaFlowServiceApi")
        return self.get_service(afsapi_class)

    @property
    def thread_pool(self) -> ThreadPoolExecutor:
        return self.__thread_pool

    def connect_sse(self, klass: Type) -> Tuple[str, sseclient.SSEClient]:
        """
        Creates a new SSE connection for the given endpoint
        """
        pkg = self.__rest_package_registry.get_rest_package(klass)
        service_type = pkg.service_type_name
        host = self.__rest_package_registry.af_conf.get_host(service_type)
        register_sse_endpoint = host + "/sse"
        kwargs = {}
        kwargs["headers"] = {}
        kwargs["headers"]["x-AF-Security-Token"] = self.__csd.token
        kwargs["verify"] = self.__rest_package_registry.af_conf.verify_ssl

        sse: sseclient.SSEClient = sseclient.SSEClient(register_sse_endpoint, **kwargs)
        initial = next(sse)
        return (initial.data, sse)

    @property
    def csd(self):
        """
        Returns the client session details
        """
        return self.__csd
