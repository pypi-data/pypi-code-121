import time

from google.protobuf.message import Message
from k8s.io.apimachinery.pkg.apis.meta.v1.generated_pb2 import ObjectMeta

from modela.common import ObjectReference
from modela.ModelaException import ResourceNotFoundException, ResourceExistsException, GrpcErrorException


class Resource:
    """
    Base class for all classes representing Modela custom resources
    """
    DefaultVersion = 'v0.0.1'

    def __init__(self, resource: Message, client=None, name="", namespace="", version='v0.0.1'):
        self._object: Message = resource

        if client is not None:
            self._client = client

        if name != "" and namespace != "":
            if hasattr(self._client, "get"):
                try:
                    self._object = self._client.get(namespace, name).raw_message
                except ResourceNotFoundException:
                    self._object.metadata.CopyFrom(ObjectMeta())
                    self._object.metadata.name = name
                    self._object.metadata.namespace = namespace
                    self.default()
                    if hasattr(self._object.spec, 'versionName'):
                        self._object.spec.versionName = version

            else:
                print("Unable to lookup resource: object has no client repository")

    @property
    def spec(self):
        return self._object.spec

    @property
    def metadata(self) -> ObjectMeta:
        return self._object.metadata

    @property
    def name(self) -> str:
        return self.metadata.name

    @property
    def namespace(self) -> str:
        return self.metadata.namespace

    def has_label(self, label: str) -> bool:
        return label in self.metadata.labels

    def set_label(self, label: str, value: str):
        self.metadata.labels[label] = value

    def label(self, label: str) -> str:
        return self.metadata.labels[label]

    @property
    def raw_message(self) -> Message:
        return self._object

    @property
    def reference(self) -> ObjectReference:
        return ObjectReference(Namespace=self.namespace, Name=self.name)

    def submit(self, replace=False, **kwargs):
        """
        Submit resource to the cluster

        :param replace: Replace the resource if it already exists on the cluster.
        """
        self.ensure_client_repository()
        if replace:
            self._client.delete(self.namespace, self.name)
            name, namespace = self.name, self.namespace
            self._object.metadata.Clear()
            self._object.metadata.CopyFrom(ObjectMeta())
            self._object.metadata.name = name
            self._object.metadata.namespace = namespace

        try:
            self._client.create(self, **kwargs)
        except GrpcErrorException as ex:
            if not replace:
                raise ex

            time.sleep(0.5)  # Avoid race condition
            self._client.create(self, **kwargs)


    def update(self):
        """ Update the resource on the cluster with the latest data from the SDK """
        self.ensure_client_repository()
        self._client.update(self)

    def delete(self):
        """ Delete the resource on the cluster """
        self.ensure_client_repository()
        self._client.delete(self.namespace, self.name)
        name, namespace = self.name, self.namespace
        self._object.metadata.Clear()
        self._object.metadata.CopyFrom(ObjectMeta())
        self._object.metadata.name = name
        self._object.metadata.namespace = namespace

    def sync(self):
        """ Update the resource with the latest information from the cluster """
        self.ensure_client_repository()
        self._object = self._client.get(self.namespace, self.name).raw_message

    def ensure_client_repository(self):
        """ Assert that the client repository exists """
        assert hasattr(self, "_client")

    def default(self):
        print("Resource {0} is missing a default constructor; you may encounter errors upon creation.\n"
              "Please file an issue at https://github.com/metaprov/modela-python-sdk/issues".format(
            self.__class__.__name__))

    def __repr__(self):
        return "<{0} Resource at {1}/{2}>".format(self.__class__.__name__, self.namespace, self.name)

    @staticmethod
    def set_default_version(version):
        Resource.DefaultVersion = version
