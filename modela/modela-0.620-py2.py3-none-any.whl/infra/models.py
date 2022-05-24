from dataclasses import field
import github.com.metaprov.modelaapi.pkg.apis.catalog.v1alpha1.generated_pb2 as catalog_pb
import github.com.metaprov.modelaapi.pkg.apis.infra.v1alpha1.generated_pb2 as infra_pb
import github.com.metaprov.modelaapi.pkg.apis.data.v1alpha1.generated_pb2 as data_pb
from modela.infra.common import *
from modela.Configuration import *
from modela.common import ObjectReference


@datamodel(proto=catalog_pb.NotificationSpec)
class NotificationSettings(Configuration):
    """ NotificationSpec specifies which Notifiers to forward Alert resources to """
    ErrorTTL: int = 3600
    """ Time-to-live for error messages, in seconds """
    SuccessTTL: int = 3600
    """ Time-to-live for success messages. In seconds """
    NotifierName: str = ''
    """ The name of the Notifier which exists in the same tenant as the resource specifying the NotificationSpec """


@datamodel(proto=catalog_pb.ResourceSpec)
class Workload(Configuration):
    """ ResourceSpec specifies the amount of resources that will be allocated to a workload """
    WorkloadName: str = ''
    """
    If this resource is based on the workload, this field contain the name of the workload.
    The name of a WorkloadClass. The system will use the resource requirements described by the WorkloadClass
    """
    CpuImage: ObjectReference = ObjectReference('modela-catalog', 'modela-cpu-trainer-latest')
    """ Reference to the managed CPU trainer image, used internally """
    GpuImage: ObjectReference = ObjectReference('modela-catalog', 'modela-gpu-trainer-latest')
    """ Reference to the managed GPU trainer image, used internally """


@datamodel(proto=catalog_pb.ContainerLog)
class ContainerLog(Configuration):
    """ ContainerLog describes the location of logs for a single Job """
    Job: str = ''
    """ The name of the Job """
    Container: str = ''
    """ The container name """
    Key: str = ''
    """ The path to the log in the bucket """


@datamodel(proto=catalog_pb.Logs)
class OutputLogs(Configuration):
    """ Logs describes the location of logs produced by workloads associated with a resource """
    BucketName: str = ''
    """ The name of the VirtualBucket resource where the logs are stored """
    Containers: List[ContainerLog] = field(default_factory=lambda : [])
    """ The collection of ContainerLog objects that describe the location of logs per container """


@datamodel(proto=data_pb.GitLocation)
class GitSettings(Configuration):
    """ GitLocation specifies the Git location where Modela will track resources as YAML """
    GitConnectionName: str = ''
    """ The Git Connection resource which exists in the same tenant as the parent DataProduct """
    Url: str = ''
    """ The URL to the destination Git repository """
    Branch: str = ''
    """ The branch inside the Git repository """
    Private: bool = False
    """ Indicates if the repository is private """


@datamodel(proto=data_pb.ImageLocation)
class ImageLocation(Configuration):
    """ ImageLocation specifies the destination for all model images produced under a DataProduct """
    Name: str = ''
    """ The canonical name of the image repository. If not set, it will default to docker/{dataproduct_name} """
    RegistryConnectionName: str = ''
    """
    The image repository Connection resource which exists in the same tenant as the parent DataProduct. If the field
    is not set, Modela will ignore the image location and not push images
    """


@datamodel(proto=infra_pb.RuleSpec)
class Rule(Configuration):
    """ RuleSpec defines the relation between a resource and the actions that can be performed on the resource """
    Resource: ResourceKind = None
    """ The kind of the resource """
    Verbs: List[Verb] = field(default_factory=lambda : [])
    """ List of allowed actions on the resource """


@datamodel(proto=infra_pb.UserRoleClassSpec)
class UserRoleClassSpec(Configuration):
    """ UserRoleClassSpec contains the permissions for a UserRoleClass """
    TenantRef: ObjectReference = None
    """ The owner of the user role class """
    Description: str = ''
    """ The description of the user role class. """
    Owner: str = ''
    """ The name of the Account which created the object, which exists in the same tenant as the object """
    Rules: List[Rule] = field(default_factory=lambda : [])
    """ The collection of rules, consisting of a resource and the actions that can be performed on the resource """
