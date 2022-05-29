from dataclasses import field
from typing import List
import github.com.metaprov.modelaapi.pkg.apis.catalog.v1alpha1.generated_pb2 as catalog_pb
import github.com.metaprov.modelaapi.pkg.apis.inference.v1alpha1.generated_pb2 as inference_pb
from github.com.metaprov.modelaapi.services.grpcinferenceservice.v1.grpcinferenceservice_pb2 import *
from modela.Configuration import datamodel
from modela.common import Configuration, ConditionStatus, Time, ObjectReference, StatusError, TriggerScheduleEventType
from modela.inference.common import PredictorConditionType, CanaryMetric, AccessType, PredictorType, ModelDeploymentPhase
from modela.infra.models import Workload
from modela.data.models import DataLocation
from modela.training.common import TaskType
from modela.training.models import ModelValidation, ModelValidationResult


@datamodel(proto=catalog_pb.RunSchedule)
class RunSchedule(Configuration):
    """ RunSchedule specifies the schedule for a Job to be executed """
    Enabled: bool = False
    """ Indicates if the schedule is enabled and the Jobs associated it will be created at the specified time """
    StartTime: Time = None
    """ The time of the day when the schedule will be executed """
    EndTime: Time = None
    """ The time of the day when the schedule is expected to conclude """
    Cron: str = ''
    """ The cron string of the schedule. See https://docs.oracle.com/cd/E12058_01/doc/doc.1014/e12030/cron_expressions.htm for more information """
    Type: TriggerScheduleEventType = None
    """ The type of schedule, which can be a frequency interval or a cron expression """


@datamodel(proto=inference_pb.ModelDeploymentStatus)
class ModelDeploymentStatus(Configuration):
    ImageName: str = ''
    DeploymentRef: ObjectReference = None
    """ The deployment name that serves this model """
    ServiceRef: ObjectReference = None
    """ The service name that serves this model """
    HpaName: str = ''
    """ the name of the horizonal pod autoscaler, if autoscaling is true """
    P50: float = 0
    """ P50 latency """
    P95: float = 0
    """ P95 latency """
    P99: float = 0
    """ P99 is the 99% latency of the model """
    LastPredictionTime: Time = None
    """ Last prediction time is the time of the last prediction """
    DailyPredictionAvg: int = 0
    LastFailure: str = ''
    """ LastFailure is the last failure that occur with the model """
    Phase: ModelDeploymentPhase = None
    """ Phase is the current phase of this model deployment """
    DeployedAt: Time = None
    """ DeployedAt is the last time that this model was deployed """
    ReleasedAt: Time = None
    """ ReleasedAt is the time that this model was released """
    DeploymentReady: bool = False
    """ If true, the deployment is ready """
    ServiceReady: bool = False
    """ If true, the service is ready """
    DataDrift: bool = False
    """ Indicates if a data drift has been detected based on incoming prediction data """
    ConceptDrift: bool = False
    """ Indicates if a concept drift has been detected based on incoming prediction data """
    LastDailyPredictions: List[int] = field(default_factory=lambda : [])
    """ The predictions from the last 7 days """


@datamodel(proto=inference_pb.ModelRecord)
class ModelRecord(Configuration):
    """ ModelRecord hold the state of a model that was in production """
    ModelName: str = ''
    """ Model Name is the name of the model """
    ModelVersion: str = ''
    """ Model version is the version of the model """
    LiveAt: Time = None
    """ Live at is the time that the model were placed in production """
    RetiredAt: Time = None
    """ Retried at is the time that the model was retired from production. """
    AvgDailyPrediction: int = 0
    """ Retried at is the time that the model was retired from production. """
    AvgLatency: float = 0
    """ Retried at is the time that the model was retired from production. """


@datamodel(proto=catalog_pb.ModelDeploymentSpec)
class ModelDeploymentSpec(Configuration):
    """
    ModelDeploymentSpec describes how a single model should be deployed with a Predictor, and
    how prediction traffic will be routed to the model
    """
    ModelName: str = ''
    """
    The name of a model, which is fully complete and packaged, that exists in the same DataProduct namespace
    as the resource which specifies the ModelDeploymentSpec
    """
    ModelVersion: str = ''
    """ The version of the model """
    MaxTraffic: int = 0
    """ The maximum percentage of traffic that will be served by the model """
    Traffic: int = 0
    """ The minimum percentage of traffic that will be served by the model """
    Canary: bool = False
    """ Canary denotes if this deployment is a staged release. A staged release will serve traffic in increments """
    Shadow: bool = False
    """
    Shadow denotes if the model is running in shadow mode. A shadow model face the production traffic, however, the predictions are not
    served back to the client
    """
    Released: bool = False
    """ A released model is a model that should serve production traffic """
    Deployed: bool = False
    """ A deployed model is a model whose containers are up, but does not serve production traffic """
    MountTar: bool = False
    """ MountTar means that we would mount the model tar file. Else we would use baked image. """
    TrafficSelector: str = ''
    """ TrafficSelector is a filter on the traffic to this model """
    CanaryMetrics: List[CanaryMetric] = field(default_factory=lambda : [])
    """
    If the deployment is canary, the metric define how to evaluate the canary.
    Default: none
    """
    ApprovedBy: str = ''
    """ The account name of the approver """
    ApprovedAt: Time = None
    """ The time of approval """


@datamodel(proto=inference_pb.PredictorCondition)
class PredictorCondition(Configuration):
    """ PredictorCondition describes the state of a Predictor at a certain point """
    Type: PredictorConditionType = None
    """ Type of Predictor condition """
    Status: ConditionStatus = None
    """ Status of the condition, one of True, False, Unknown """
    LastTransitionTime: Time = None
    """ Last time the condition transitioned from one status to another """
    Reason: str = ''
    """ The reason for the condition's last transition """
    Message: str = ''
    """ A human-readable message indicating details about the transition """


@datamodel(proto=inference_pb.ProgressiveSpec)
class ProgressiveSpec(Configuration):
    """ ProgressiveSpec defines the specification to progressively deploy a model to production """
    Warmup: int = 0
    """ The time, in seconds, for the warm-up period """
    TrafficIncrement: int = 0
    """ The percentage of traffic to increment """
    CanaryMetrics: List[CanaryMetric] = field(default_factory=lambda : [])
    """ What metric to use when comparing the candidate model to the current model """


@datamodel(proto=inference_pb.PredictionCacheSpec)
class PredictionCacheSpec(Configuration):
    """ PredictionCacheSpec specifies the connection information of a key-value cache to store predictions """
    Active: bool = False
    """ Active indicate if the cache is active """
    ServiceName: str = ''
    """ the name of the cache service """


@datamodel(proto=inference_pb.AutoScaling)
class AutoScaling(Configuration):
    """ AutoScaling defines the configuration for the automatic scaling of a service """
    Enabled: bool = False
    """ Indicates if automatic scaling is enabled """
    MinReplicas: int = 1
    """ The minimum number of replicas running the service """
    MaxReplicas: int = 1
    """ The maximum number of replicas running the service """
    CpuAvgUtilization: int = 80
    """
    The target average CPU utilization across all replicas. The HorizontalPodAutoscaler associated with the
    service will change the number of replicas to maintain this metric
    """
    MemAvgUtilization: int = 80
    """
    The target average memory utilization across all replicas. The HorizontalPodAutoscaler associated with the
    service will change the number of replicas to maintain this metric
    """


@datamodel(proto=inference_pb.PredictorStatus)
class PredictorStatus(Configuration):
    """ PredictorStatus contain the current state of the Predictor resource """
    ObservedGeneration: int = 0
    """ ObservedGeneration is the last generation that was acted on """
    History: List[ModelRecord] = field(default_factory=lambda : [])
    """ The collection of historical records of models deployed to the Predictor, used internally to roll-back models """
    LastUpdated: Time = None
    """ The last time the object was updated """
    EndPoint: str = ''
    """ The end-point URL of the Predictor """
    FailureReason: StatusError = None
    """ In the case of failure, the Predictor resource controller will set this field with a failure reason """
    FailureMessage: str = ''
    """ In the case of failure, the Predictor resource controller will set this field with a failure reason """
    Conditions: List[PredictorCondition] = field(default_factory=lambda : [])


@datamodel(proto=inference_pb.MonitorSpec)
class MonitorSpec(Configuration):
    """ MonitorSpec defines the specification to monitor a model in production """
    Enabled: bool = False
    """ If true monitoring is enabled. """
    SamplePercent: int = 0
    """ How many rows to sample from the live data for """
    Schedule: RunSchedule = None
    """ Schedule for running the monitor """
    NotifierName: str = ''
    """ NotifierName is the name of notifier to alert in case of """
    Validations: List[ModelValidation] = field(default_factory=lambda : [])
    """ List of model validation """
    LogRequests: bool = False
    """ Log requests (incoming traffic) """
    LogResponses: bool = False
    """ Log outgoing traffic """


@datamodel(proto=inference_pb.MonitorStatus)
class MonitorStatus(Configuration):
    MonitorLastAttemptAt: Time = None
    MonitorLastScore: float = 0
    """ The score from the last time model monitoring was computed """
    MonitorLastLatency: float = 0
    """ The model latency from the last time model monitoring was computed """


@datamodel(proto=inference_pb.PredictorAuthSpec)
class PredictorAuthSpec(Configuration):
    Enabled: bool = False


AccessType_ = AccessType
AutoScaling_ = AutoScaling


@datamodel(proto=inference_pb.PredictorSpec)
class PredictorSpec(Configuration):
    """ PredictorSpec defines the desired state of a Predictor """
    VersionName: str = ''
    """
    The name of the DataProductVersion which describes the version of the resource
    that exists in the same DataProduct namespace as the resource
    """
    Description: str = ''
    """ The user-provided description of the Predictor """
    ProductRef: ObjectReference = None
    """ The reference to the DataProduct that the resource exists under """
    ServingsiteRef: ObjectReference = ObjectReference('default-tenant', 'default-lab')
    """ The reference to the ServingSite resource that hosts the Predictor """
    Models: List[ModelDeploymentSpec] = field(default_factory=lambda : [])
    """
    The collection of model deployment specifications that define which Model resources will be deployed to the
    Predictor service and how they will be deployed. Each model should be trained with the same type of
    dataset and possess a unique version
    """
    Progressive: ProgressiveSpec = None
    """
    The specification to progressively deploy models. ModelDeploymentSpec specifications within Models that have the
    `Canary` field enabled will be progressively deployed according to the specification when they are applied to the Predictor
    """
    ArtifactsFolder: DataLocation = DataLocation()
    """ The data location where artifacts generated by the Predictor will be stored """
    Port: int = 8080
    """
    The port number that will be exposed on the Predictor's Pods to serve prediction traffic through the GRPCInferenceService API.
    The Kubernetes Service created by the Predictor will expose the port and forward GRPC traffic to the backend pods
    """
    NodePort: int = 30000
    """
    The port number that will be exposed on the external address of every node on the cluster, in the case of the
    Predictor's access type being NodePort. Traffic from the port will be forwarded to the Predictor's backend service
    """
    Path: str = ''
    """
    The auto-generated DNS path where the Predictor service can be accessed. If the access type is ClusterIP, it will
    be a cluster-internal DNS name (i.e. predictor.default-serving-site.svc.cluster.local). In the case of the Ingress
    access type, it will be determined by the FQDN of the host ServingSite (i.e. predictor.default-serving-site.modela.ai).
    """
    AccessType: AccessType_ = None
    """
    The Kubernetes-native access method which specifies how the Kubernetes Service created by the Predictor will be exposed.
    See https://modela.ai/docs/docs/serving/production/#access-method for a detailed description of each access type
    (defaults to cluster-ip)
    """
    Replicas: int = 1
    """
    The number of replicas for the Kubernetes Deployment associated with the Predictor, which will instantiate multiple
    copies of the service in the case that automatic scaling is disabled
    """
    AutoScaling: AutoScaling_ = None
    """ AutoScaling specifies the auto-scaling policy """
    Owner: str = 'no-one'
    """ The name of the Account which created the object, which exists in the same tenant as the object """
    Resources: Workload = Workload('general-nano')
    """ Resources specifies the resource requirements allocated to the prediction service """
    Cache: PredictionCacheSpec = None
    """ Cache is the specification of prediction cache (currently unimplemented) """
    ForwardCurtain: str = ''
    """ The forward curtain receives prediction requests before the prediction (currently unimplemented) """
    BackwardCurtain: str = ''
    """ The backward curtain receives prediction requests after the prediction (currently unimplemented) """
    TargetColumn: str = ''
    """ The target feature of the model that the Predictor serves """
    PositiveLabel: str = ''
    """ For binary classification, the name of the positive class of the target feature """
    NegativeLabel: str = ''
    """ For binary classification, the name of the negative class of the target feature """
    TrainingDatasetRef: ObjectReference = None
    """ The dataset where this model was trained on """
    REST: bool = True
    Type: PredictorType = PredictorType.Online
    """ The type of predictor (online, batch, or streaming). Online is the only supported type as of the current release """
    Task: TaskType = None
    """ The task type of the Predictor, which should match the task type of the models being served """
    PredictionThreshold: float = 0
    """ The prediction threshold """
    Monitor: MonitorSpec = None
    """ Monitor spec specify the monitor for this predictor. """
    Auth: PredictorAuthSpec = None
    """ The specification to authenticate requests to the prediction service """


@datamodel(proto=ProbabilityValue)
class ProbabilityValue(Configuration):
    Label: str = ''
    Probability: float = 0


@datamodel(proto=ShapValue)
class ShapValue(Configuration):
    Feature: str = ''
    Value: float = 0


@datamodel(proto=PredictResultLineItem)
class PredictionResult(Configuration):
    Success: bool = False
    Score: float = 0
    Label: str = ''
    Probabilities: List[ProbabilityValue] = field(default_factory=lambda : [])
    ShapValues: List[ShapValue] = field(default_factory=lambda : [])
    MissingColumns: List[str] = field(default_factory=lambda : [])
    OutOfBound: List[str] = field(default_factory=lambda : [])
    BaseShapValue: float = 0
