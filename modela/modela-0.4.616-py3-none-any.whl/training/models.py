from dataclasses import field
from typing import List
from github.com.metaprov.modelaapi.pkg.apis.catalog.v1alpha1.generated_pb2 import Measurement
from github.com.metaprov.modelaapi.services.common.v1.common_pb2 import ModelProfile
from modela.Configuration import Configuration, ImmutableConfiguration, datamodel
from modela.common import PriorityLevel, Time, StatusError, ConditionStatus, ObjectReference, Freq, Plot
from modela.data.common import DataType
from modela.data.models import DataLocation, GovernanceSpec, CompilerSettings, Correlation, DataSourceSpec
from modela.inference.common import AccessType
from modela.infra.models import Workload, OutputLogs, NotificationSettings
from modela.training.common import *
import github.com.metaprov.modelaapi.pkg.apis.catalog.v1alpha1.generated_pb2 as catalog_pb
import github.com.metaprov.modelaapi.pkg.apis.training.v1alpha1.generated_pb2 as training_pb
import github.com.metaprov.modelaapi.services.common.v1.common_pb2 as common_pb


@datamodel(proto=training_pb.ModelValidation)
class ModelValidation(Configuration):
    """ ModelValidation defines a single validation to be run against a model """
    Type: ModelValidationType = None
    """ The type of model validation """
    PrevModel: str = ''
    """ PrevModel specifies a previous model to compare against """
    DatasetName: str = ''
    """ The name of a labeled dataset used to test the model, when measuring a performance metric """
    DriftFreq: Freq = None
    DriftInterval: int = 0
    Column: str = ''
    Metric: Metric = None
    Min: float = 0
    Max: float = 0
    MinPercent: float = 0
    MaxPercent: float = 0
    Agg: Aggregate = None
    """ Agg specifies the type of aggregate when measuring aggregate performance (e.g. median, average) """


@datamodel(proto=training_pb.ModelValidationResult)
class ModelValidationResult(Configuration):
    Type: str = ''
    DatasetName: str = ''
    """ DatasetName is the name of the dataset used to perform the validation """
    ModelName: str = ''
    """ ModelName is the name of the model under test """
    Column: str = ''
    """ Column is the name of the feature. """
    Error: str = ''
    """ Error is a string. """
    Metric: Metric = None
    """ Metric is the measurement """
    ActualValue: float = 0
    """ Actual value is the actual value """
    Passed: bool = False
    """ Passed indicate if the result passed. """
    At: Time = None
    """ At is the time the validation was performed. """
    DurationInSec: int = 0
    """ The amount of time it took to compute this result """


@datamodel(proto=catalog_pb.Measurement)
class Measurement(ImmutableConfiguration):
    """ Measurement is a value for a specific metric """
    Metric: Metric = Metric.Null
    """ The metric type name (e.g. F1 / Accuracy) """
    Value: float = 0
    """ The value of the metric """


@datamodel(proto=training_pb.SegmentSpec)
class Segment(Configuration):
    ColumnName: str = ''
    Op: Operation = Operation.EQ
    """ The segment operation """
    Value: str = ''
    """ The value operation """


@datamodel(proto=training_pb.HyperParameterValue)
class HyperParameterValue(ImmutableConfiguration):
    """ HyperParameterValue represent an individual hyper-parameter of a machine earning algorithm """
    Name: str = ''
    """ The name of the hyper-parameter """
    Value: str = ''
    """ The value of the hyper-parameter """


@datamodel(proto=training_pb.ClassicalEstimatorSpec)
class ClassicalEstimatorSpec(ImmutableConfiguration):
    """ ClassicalEstimatorSpec is the specification for an algorithm and the actual value fof the hyper parameters """
    AlgorithmName: str = ''
    """ AlgorithmName is a reference to the algorithm in the catalog """
    Parameters: List[HyperParameterValue] = field(default_factory=lambda : [])
    """ Parameters is a list of the algorithm hyper parameters """


@datamodel(proto=training_pb.ChatbotEstimatorSpec)
class ChatbotEstimatorSpec(ImmutableConfiguration):
    """ ChatbotEstimatorSpec specifies the configuration for a chatbot model """
    Base: str = ''
    """ The name of the base model """


@datamodel(proto=training_pb.NLPEstimatorSpec)
class NLPEstimatorSpec(ImmutableConfiguration):
    """ NLPEstimatorSpec specifies the configuration for an NLP model """
    Base: str = ''
    """ The name of the base model """


@datamodel(proto=training_pb.FeatureImportance)
class FeatureImportance(ImmutableConfiguration):
    """ FeatureImportance records the computed importance of a single feature """
    Feature: str = ''
    """ The name of the feature """
    Importance: float = 0
    """ The importance of the feature """


@datamodel(proto=training_pb.SuccessiveHalvingSpec)
class SuccessiveHalving(ImmutableConfiguration):
    """ SuccessiveHalvingSpec records the position of a single model in a successive halving search """
    Budget: int = 0
    """
    The budget to be used in a multi-fidelity search, for example the number of epochs
    or the percentage of data to train the model with
    """
    Bracket: int = 0
    """ The bracket of the model """
    Rung: int = 0
    """ The rung of the model """
    ConfID: int = 0
    """ The configuration ID allocated to the model """
    Modality: ModalityType = None
    """
    The type of modality, based on the type of model
    For classical models, it should be based on data percentage
    For deep models, it should be based on epochs
    """


@datamodel(proto=training_pb.DataSplitSpec)
class DataSplit(Configuration):
    """ DataSplitSpec specifies the configuration to split a dataset into training and testing datasets """
    Method: DataSplitMethod = DataSplitMethod.Auto
    """ The type of split method """
    Train: int = 80
    """ The number percentage (0 through 100) of rows that will be allocated to the training dataset """
    Validation: int = 0
    """
    The number percentage (0 through 100) of rows that will be allocated to the validation dataset.
    If Validation is set to 0 the model will default to use cross-validation
    """
    Test: int = 20
    """ The number percentage (0 through 100) of rows that will be allocated to the training dataset """
    SplitColumn: str = ''
    """
    The name of the column containing a binary value that indicates if the row should be split.
    The split type must use split-column in order for SplitColumn to have an effect
    """
    Segments: List[Segment] = field(default_factory=lambda : [])
    """ The collection of segments """
    TrainDataset: str = ''
    """ The name of the Dataset resource which will be used as the training dataset """
    TestDataset: str = ''
    """
    The name of the Dataset resource which will be used as the testing dataset, applicable
    if the split type uses test-dataset. If enabled, the training dataset will not be split and used as-is
    If empty, we will not use test dataset
    """


@datamodel(proto=training_pb.CheckpointSpec)
class CheckpointSpec(Configuration):
    """ CheckpointSpec specifies where to store model checkpoints """
    Enabled: bool = False
    """ Indicates if checkpointing is enabled. """
    CheckpointInterval: int = 10
    """
    The interval, in minutes, at which a snapshot of a partially trained model will be saved.
    Applicable to models with long training times for resiliency if training is suddenly stopped
    """
    Location: DataLocation = DataLocation()
    """ The location of the model checkpoint """


@datamodel(proto=training_pb.EarlyStopSpec)
class EarlyStopping(Configuration):
    """
    EarlyStopSpec specifies the configuration to automatically abort a model search
    if further improvements in model performance cannot be produced
    """
    Enabled: bool = False
    """ Indicates if early stopping is enabled """
    Initial: int = 10
    """ The number of models to train before model objective metrics will begin to be checked for early stopping """
    MinModelsWithNoProgress: int = 5
    """ The number of models with no improvement in score that are required to abort the model search """


@datamodel(proto=training_pb.TrainingSpec)
class Training(Configuration):
    """ TrainingSpec specifies the configuration of a model training workload """
    Priority: PriorityLevel = PriorityLevel.Medium
    """ The priority of the Kubernetes Job created by the Model (medium, by default) """
    Cvtype: CvType = CvType.CVTypeKFold
    """ The type of cross-validation to use, in the case that a validation dataset is not enabled """
    CV: bool = True
    """ Indicates if cross-validation should be used to score models """
    Folds: int = 5
    """ The number of folds to use during cross-validation """
    Split: DataSplit = DataSplit()
    """ Split specifies the configuration to generate training, testing, and validation datasets """
    EvalMetrics: List[Metric] = field(default_factory=lambda : [])
    """ EvalMetrics specifies the collection of metrics that will be evaluated after model training is complete """
    Sh: SuccessiveHalving = None
    """ SuccessiveHalving specifies the configuration for a Study to execute a model search using successive halving """
    Seed: float = 42
    """ The random state used for the model's estimator, if applicable (for example, in RandomForestClassifier) """
    Resources: Workload = Workload('general-large')
    """ Resources specifies the resource requirements allocated to the model training workload """
    Gpu: bool = False
    """ Indicates if a GPU will be allocated for model training """
    Distributed: bool = False
    """ Indicates if model training will be distributed across multiple nodes (currently unimplemented) """
    NodeCount: int = 1
    """ The number of nodes to use, in the case of distributed training """
    FeatureImportance: bool = True
    """
    Indicates if feature importance for the model will be computed as part of training. Some algorithms
    (e.g. Random Forest) have built in support for feature importance
    """
    Checkpoint: CheckpointSpec = CheckpointSpec()
    """ Checkpoint specifies the location to store model checkpoints """
    LogLevel: str = 'info'
    """ The maximum log level for logs produced by Jobs associated with the Model """
    SamplePct: int = 100
    """ The number percentage (0 through 100) of rows to be used during training """
    LabRef: ObjectReference = ObjectReference('default-tenant', 'default-lab')
    """ The reference to the Lab under which the model training Job will be created """
    TimeoutInSecs: int = 600
    """ The maximum time, in seconds, that Jobs associated with the Model can run for before being forcefully cancelled. """


@datamodel(proto=training_pb.ServingSpec)
class ServingSpec(ImmutableConfiguration):
    """ ServingSpec specifies the requirements to serve a model """
    Resources: Workload = None
    Format: ModelServingFormat = ModelServingFormat.CloudPickle


@datamodel(proto=training_pb.TextPipelineSpec)
class TextPipelineSpec(ImmutableConfiguration):
    """ TextPipelineSpec represents a single pipeline for transforming text data """
    Encoder: TextEncoding = TextEncoding.Auto
    """ The text encoder (e.g. TFIDF) """
    Tokenizer: str = ' '
    """ The text tokenizer character """
    Stopwords: bool = True
    """ Indicates if the pipeline will add stop word handling """
    Pos: bool = True
    """ Indicates if the pipeline will add part-of-speech handling """
    Lemma: bool = True
    """ Indicates if the pipeline will implement lemmatization """
    Stem: bool = True
    """ Indicates if the pipeline will implement word stemming """
    Embedding: str = ''
    """ Indicates if the pipeline will generate a word embedding """
    Svd: bool = True
    """ Indicates if the pipeline will add singular value decomposition """
    MaxSvdComponents: int = 0
    """ The maximum number of SVD components to use, if applicable """


@datamodel(proto=training_pb.ImagePipelineSpec)
class ImagePipelineSpec(ImmutableConfiguration):
    """ ImagePipelineSpec represents a single pipeline for preprocessing image data """
    Featurizer: str = None
    """ The date time imputer. """


@datamodel(proto=training_pb.VideoPipelineSpec)
class VideoPipelineSpec(ImmutableConfiguration):
    """ VideoPipelineSpec represents a single pipeline for preprocessing video data """
    Featurizer: str = None
    """ The date time imputer. """


@datamodel(proto=training_pb.AudioPipelineSpec)
class AudioPipelineSpec(ImmutableConfiguration):
    """ AudioPipelineSpec represents a single pipeline for preprocessing audio data """
    Featurizer: str = None
    """ The date time imputer. """


@datamodel(proto=training_pb.ResourceConsumption)
class ResourceConsumption(ImmutableConfiguration):
    """ ResourceConsumption represents the total resources consumed by a workload """
    Cpu: float = 0
    Mem: float = 0
    Gpu: float = 0


@datamodel(proto=training_pb.DataHashes)
class DataHashes(ImmutableConfiguration):
    """ DataHashes contains the hashes for datasets used during model training """
    TrainHash: str = ''
    TestingHash: str = ''
    ValidationHash: str = ''


@datamodel(proto=training_pb.GeneratedColumnSpec)
class GeneratedColumnSpec(ImmutableConfiguration):
    """ GeneratedColumnSpec describes a column to be generated and applied to a dataset """
    Name: str = ''
    """ The name of the generated column """
    Datatype: DataType = DataType.Text
    """ The resulting data type """
    First: str = ''
    """ The name of the first original column """
    Second: str = ''
    """ The name of the second original column, if the expression is binary operator """
    Original: str = ''
    """ The expression to apply in order to generate the new column """


@datamodel(proto=training_pb.FeatureSelectionSpec)
class FeatureSelection(Configuration):
    """ FeatureSelectionSpec specifies the configuration to run feature selection on a dataset """
    Enabled: bool = False
    """ Indicates if feature selection is enabled """
    SamplePct: int = 100
    """ The number percentage (0 through 100) of the dataset to sample """
    Embedding: bool = False
    """ Indicates if embedded methods will be tested as part of the candidate algorithms (e.g. tree-based selection) """
    Filter: bool = False
    """ Indicates if filter methods will be tested as part of the candidate algorithms (e.g. chi-square or anova tests) """
    Wrapper: bool = False
    """ Indicates if wrapper methods will be tested as part of the candidate algorithms """
    Pipeline: List[FeatureSelectionType] = field(default_factory=lambda : [])
    """ The collection of feature selection methods that will be applied in order to the dataset """
    VarianceThresholdPct: int = 5
    """ The threshold as a percentage to remove low variance features """
    CorrThreshold: int = 95
    """ The threshold to remove features with high correlations """
    TopN: int = 0
    """ The number of features that will be selected based on importance. If TopN is 0, all features will be selected """
    CumulativeImportancePercent: int = 95
    """ The cumulative importance threshold of features to be included """
    Reserved: List[str] = field(default_factory=lambda : [])
    """ List of features that are reserved and will always be included in the final feature selection """


@datamodel(proto=training_pb.FeaturePair)
class FeaturePair(ImmutableConfiguration):
    X: str = ''
    Y: str = ''


@datamodel(proto=training_pb.InterpretabilitySpec)
class Interpretability(Configuration):
    """ InterpretabilitySpec specifies the configuration to generate interpretability data and diagrams """
    Ice: bool = True
    """ Indicates if ICE (individual condition expectation) plots will be generated """
    Icepairs: List[FeaturePair] = field(default_factory=lambda : [])
    """ The collection of feature pairs to generate ICE scatter diagrams for each """
    Lime: bool = False
    """ Indicates if LIME (local interpretable model-agnostic explanations) diagrams will be generated """
    Shap: ShapType = ShapType.Auto
    """
    The type of SHAP values to be generated. Linear and tree values are the
    only recommended types due to the high compute times of other methods
    """
    Shappairs: List[FeaturePair] = field(default_factory=lambda : [])
    """ The collection of feature pairs to generate SHAP scatter diagrams for each """
    Counterfactual: bool = False
    """ Indicates if counter-factual diagrams will be generated """
    Anchor: bool = False
    """ Indicates if anchor explanation diagrams will be generated """


ImputationType = Imputation
DiscretisationType = Discretisation
OutlierHandlingType = OutlierHandling
VariableTransformationType = VariableTransformation
DatetimeTransformationType = DatetimeTransformation
ScalingType = Scaling


@datamodel(proto=training_pb.FeatureEngineeringPipeline)
class FeatureEngineeringPipeline(ImmutableConfiguration):
    """ FeatureEngineeringPipeline represent a single pipeline to transform a dataset """
    Name: str = ''
    """ The name of the pipeline """
    Datatype: DataType = DataType.Text
    """ The type of data which the pipeline applies to """
    Columns: List[str] = field(default_factory=lambda : [])
    """
    The collection of columns which the pipeline applies to. Each column in the dataset with the
    data type of the pipeline should be added to the collection of columns
    """
    Imputation: ImputationType = ImputationType.AutoImputer
    """ The imputation method to use, which fills in missing values within the columns """
    Encoding: CategoricalEncoding = CategoricalEncoding.NoneEncoding
    """ The encoding method to use for categorical data types """
    Scaling: ScalingType = ScalingType.NoScaling
    """ The scaling method to use for numerical data types """
    Discretisation: DiscretisationType = DiscretisationType.NoDiscretisation
    """ The discretisation method, which converts numerical data types to discrete variables """
    VariableTransformation: VariableTransformationType = VariableTransformationType.NoneTransform
    """ The transformation method to use for numerical data types """
    OutlierHandling: OutlierHandlingType = OutlierHandlingType.AutoOutlier
    """
    The method to use when handling outliers
    Apply only to numeric data types.
    """
    DatetimeTransformation: DatetimeTransformationType = DatetimeTransformationType.NoneDatetime
    """ The method to use when handling the date-time data type """
    Text: TextPipelineSpec = None
    """ Text specifies the pipeline to handle raw text """
    Image: ImagePipelineSpec = None
    """ Image specifies the pipeline to handle image data (currently unsupported) """
    Audio: AudioPipelineSpec = None
    """ Audio specifies the pipeline to handle audio data (currently unsupported) """
    Video: VideoPipelineSpec = None
    """ Video specifies the pipeline to handle video data (currently unsupported) """
    Generated: List[GeneratedColumnSpec] = field(default_factory=lambda : [])
    """ Generated specifies a collection of columns to be generated """
    Custom: List[GeneratedColumnSpec] = field(default_factory=lambda : [])
    """ Custom specifies a collection of columns to be generated. Custom columns are specified by end-users """
    Drop: bool = False
    """ Indicates if all of all the columns specified by the Columns field should be dropped """
    Passthrough: bool = False
    """ Indicates if the pipeline should not be applied and the columns should remain unchanged """


@datamodel(proto=training_pb.FeatureEngineeringSpec)
class FeatureEngineeringSpec(ImmutableConfiguration):
    """ FeatureEngineeringSpec specifies the feature engineering and preprocessing to be performed on a dataset """
    Pipelines: List[FeatureEngineeringPipeline] = field(default_factory=lambda : [])
    """
    Pipelines contains the collection of feature engineering pipelines that
    will be applied to a dataset prior to model training
    """
    Imbalance: ImbalanceHandling = ImbalanceHandling.ImbalanceAuto
    """ The method which will be used to handle an imbalanced dataset """
    Selection: FeatureSelection = FeatureSelection()
    """
    FeatureSelection specifies the configuration to perform
    feature selection on a dataset prior to model training
    """


@datamodel(proto=training_pb.EnsembleSpec)
class EnsembleSpec(ImmutableConfiguration):
    """ EnsembleSpec specifies the parameters of an ensemble model """
    Models: List[str] = field(default_factory=lambda : [])
    """ The collection of models (by their name) to be used as estimators in the ensemble """
    Estimators: List[ClassicalEstimatorSpec] = field(default_factory=lambda : [])
    """ The collection of estimators to be used in the ensemble, derived from Models """
    Final: ClassicalEstimatorSpec = None
    """ The base estimator """
    Type: EnsembleType = None
    """ The ensemble type method """


TrainingSpec = Training
InterpretabilitySpec = Interpretability


@datamodel(proto=training_pb.ModelSpec)
class ModelSpec(ImmutableConfiguration):
    """ ModelSpec defines the desired state of the Model resource """
    Owner: str = 'no-one'
    """ The Account which owns the the Study that created the Model """
    VersionName: str = 'v0.0.1'
    """
    The name of the DataProductVersion which describes the version of the resource
    that exists in the same DataProduct namespace as the resource, derived from the parent Study
    """
    ModelVersion: str = ''
    """ The user-assigned version of the Model, derived from the parent Study """
    StudyName: str = ''
    """ The name of the Study which created the Model. If empty, the Model will be trained as a stand-alone model """
    DatasetName: str = ''
    """ The name of the Dataset resource which the Model is being trained with """
    Task: TaskType = None
    """ The machine learning task type of the Model (i.e. regression, classification), derived from the parent Study """
    Objective: Metric = None
    """ The objective metric that will be used to evaluate the performance of the model """
    FeatureEngineering: FeatureEngineeringSpec = None
    """
    FeatureEngineering specifies the preprocessing pipelines that will be applied to the model prior to training.
    By default, feature engineering is generated automatically by sampling different pipelines in competition
    """
    Estimator: ClassicalEstimatorSpec = None
    """ Estimator specifies the machine learning algorithm and hyper-parameters of the Model """
    NlpEstimator: NLPEstimatorSpec = None
    """ NLPEstimator specifies the estimator for a deep NLP model (currently unimplemented) """
    Ensemble: EnsembleSpec = None
    """ Ensemble specifies the configuration to create an ensemble model """
    Training: TrainingSpec = None
    """ TrainingSpec specifies the configuration to prepare and train a model """
    Serving: ServingSpec = None
    """
    ServingSpec defines the resource requirements that will be applied to a Predictor
    that will be created if the model is set to be released
    """
    Tested: bool = False
    """
    Tested indicates if a workload will be instantiated to test the model. The Study resource controller
    will automatically set this field if the Model was found to be the highest-performing
    """
    Aborted: bool = False
    """ Aborted indicates if any workloads associated with the Model should stop execution """
    Packaged: bool = False
    """ Packaged indicates if the Model should be packaged into tarbell """
    Published: bool = False
    """ Published indicates that the Model should be baked into a Docker image """
    Pushed: bool = False
    """ Pushed indicates that the Model image should be pushed to a Docker image registry """
    Reported: bool = False
    """ Reported indicates that a Report will be generated for the Model """
    Paused: bool = False
    """ Paused indicates that the execution of new workloads associated with the Model should be paused """
    Profiled: bool = False
    """ Profiled indicates that the Model will be profiled """
    Archived: bool = False
    """ Archived indicates that the Model should be archived in long-term storage """
    Forecasted: bool = False
    """ Forecasted indicates that the Model should perform a forecast """
    Released: bool = False
    """ Released indicates that the Model will be deployed within Predictor """
    Explained: bool = False
    """ Explained indicates if a workload to compute SHAP values/diagrams should be executed """
    Baseline: bool = False
    """ Baseline indicates if the Model was produced by the baseline phase of a Study """
    Flagged: bool = False
    """ Indicates if the model is flagged """
    Location: DataLocation = None
    """ The data location where artifacts (metadata, reports, and estimators) generated by the Model will be stored """
    Compilation: CompilerSettings = None
    """ Compilation specifies the configuration to compile a model to a binary (currently unimplemented) """
    ActiveDeadlineSeconds: int = 600
    """ The deadline for any Jobs associated with the Model to be completed in seconds """
    EstimatorType: ModelType = ModelType.Classical
    """ ModelType is the type of model for this estimator """
    ModelClass: ModelClassType = None
    """ The model class, which is derived from the phase of the Study that the Model was created for """
    TrialID: int = 0
    """ The trial ID, which is incremented for each Model produced by the data plane """
    Governance: GovernanceSpec = None
    """ Governance specifies the model governance requirements (currently unimplemented) """
    Interpretability: InterpretabilitySpec = None
    """ Interpretability specifies the configuration to generate model interpretability visualizations """
    Fast: bool = False
    """ Fast indicates if the Model should skip profiling, explaining, and reporting """
    Ttl: int = 0
    """ The time-to-live of the Model, after which the Model will be archived """


@datamodel(proto=training_pb.InterpretabilityStatus)
class InterpretabilityStatus(ImmutableConfiguration):
    """ InterpretabilityStatus represents the state of the explanation phase of a Model """
    TrainingStartTime: Time = None
    """ StartTime represents the time when the model explanation phase started """
    TrainingEndTime: Time = None
    """ EndTime represents the time when the model explanation phase ended """
    ExplainerURI: str = ''
    """ The URI for the generated explanation data """
    TrainShapValuesURI: str = ''
    """ The URI for the train SHAP values """
    TestShapValuesURI: str = ''
    """ The URI for the test SHAP values """
    Importance: List[FeatureImportance] = field(default_factory=lambda : [])
    """ The collection of feature importances generated from the computed SHAP values """


@datamodel(proto=training_pb.ModelCondition)
class ModelCondition(ImmutableConfiguration):
    """ ModelCondition describes the state of a Model at a certain point """
    Type: ModelConditionType = ModelConditionType.ModelReady
    """ Type of Model condition """
    Status: ConditionStatus = ConditionStatus.ConditionUnknown
    """ Status of the condition, one of True, False, Unknown """
    LastTransitionTime: Time = None
    """ Last time the condition transitioned from one status to another """
    Reason: str = ''
    """ The reason for the condition's last transition """
    Message: str = ''
    """ A human-readable message indicating details about the transition """


@datamodel(proto=training_pb.ModelStatus)
class ModelStatus(ImmutableConfiguration):
    """ ModelStatus defines the observed state of a Model """
    StartTime: Time = None
    """ StartTime represents the time at which the execution of the Model started """
    TrainingStartTime: Time = None
    """ TrainStartTime represents the time at which the Model started training """
    TrainingEndTime: Time = None
    """ TrainCompletionTime represents the time at which the Model completed training """
    TestingStartTime: Time = None
    """ TestingStartTime represents the time at which the Model started testing """
    TestingEndTime: Time = None
    """ TestingEndTime represents the time at which the Model completed testing """
    EndTime: Time = None
    """ EndTime represents the time at which the Model was marked as ready, failed, or aborted """
    CvScore: float = 0
    """ The cross-validation score for the objective metric produced after training """
    TrainingScore: float = 0
    """ The score for the objective metric based on the training dataset """
    TestScore: float = 0
    """ The score for the objective metric based on the testing dataset """
    Cost: float = 0
    """ Cost is the cost of training the model in the case of a deep-learning model """
    Best: bool = False
    """ Best indicates if the Model was found to be the best model produced by a Study """
    Cv: List[Measurement] = field(default_factory=lambda : [])
    """
    CV contains the collection of measurements produced by cross-validation
    on the training dataset or validation on the validation dataset
    """
    Train: List[Measurement] = field(default_factory=lambda : [])
    """ Train contains the collection of measurements produced by validation on the training dataset """
    Test: List[Measurement] = field(default_factory=lambda : [])
    """ Train contains the collection of measurements produced by validation on the testing dataset """
    Phase: ModelPhase = ModelPhase.Pending
    """ The phase of the Model """
    ReportName: str = ''
    """ The name of the Report resource produced by the Model """
    ReportUri: str = ''
    """ The URI of the Report """
    ManifestUri: str = ''
    """ The URI of the Model manifest """
    WeightsUri: str = ''
    """ The URI of the model weights binary file """
    LabelEncoderUri: str = ''
    """ The URI of the label encoder binary file, if it exists """
    LogsUri: str = ''
    """ The URI of the logs file """
    ProfileUri: str = ''
    """ The URI of the model profile, which contains visualizations produced during the profiling phase """
    TarUri: str = ''
    """ The URI to the model tarbell file """
    AppUri: str = ''
    """ The URI to the model application file """
    ImageName: str = ''
    """ The name of the Docker image produced by the Model """
    Importance: List[FeatureImportance] = field(default_factory=lambda : [])
    """ The collection of features and their importance, sorted by the greatest importance first """
    ForecastUri: str = ''
    """ The URI of the model forecast """
    PythonVersion: str = ''
    """ The Python version of the data plane used during training """
    TrainDataset: DataLocation = None
    """ TrainDatasetLocation specifies the location of the training dataset """
    TestDataset: DataLocation = None
    """ TestDatasetLocation specifies the location of the testing dataset """
    ValidationDataset: DataLocation = None
    """ ValidationDataset specifies the location of the validation dataset """
    ObservedGeneration: int = 0
    """ ObservedGeneration is the last generation that was acted on """
    TrainingRows: int = 0
    """ The number of rows in the training dataset """
    TestingRows: int = 0
    """ The number of rows in the testing dataset """
    ValidationRows: int = 0
    """ The number of rows in the validation dataset, if applicable """
    FailureReason: StatusError = None
    """ In the case of failure, the Model resource controller will set this field with a failure reason """
    FailureMessage: str = ''
    """ In the case of failure, the Model resource controller will set this field with a failure message """
    Progress: int = 0
    """ The progress percentage of the Model, which is derived from the Model's current phase """
    SizeInBytes: int = 0
    """ The size of the model binary in bytes """
    Latency: float = 0
    """ The measured prediction latency """
    Url: str = ''
    """ The URL to the released model """
    PredictorName: str = ''
    """ The name of the Predictor in the case that the Model has been released and deployed """
    ReleasedAt: Time = None
    """ The time at which the Model was set to release """
    ImageHash: str = ''
    """ Sha256 of the model image """
    TrainingDataHash: DataHashes = None
    """ TrainingDataHash specifies the hashes for datasets used by the Model """
    TrainingResources: ResourceConsumption = None
    """ TrainingResources details the resources that were consumed by the training workload """
    TestingResources: ResourceConsumption = None
    """ TestingResources details the resources that were consumed by the testing workload """
    TrainedBy: str = ''
    """ The Account which trained the model, derived from the parent Study """
    Team: str = ''
    """ The team of the Account which trained the model, derived from the parent Study """
    Endpoint: str = ''
    """ The endpoint of the Model, which is set after it is deployed to a Predictor """
    Logs: OutputLogs = None
    """ Logs specifies the location of logs produced by workloads associated with the Model """
    CorrelationsWithTarget: List[Correlation] = field(default_factory=lambda : [])
    """ The collection of correlations of the features of the training dataset and the target feature """
    TopCorrelations: List[Correlation] = field(default_factory=lambda : [])
    """ The top correlations between features of the training dataset """
    LastUpdated: Time = None
    """ The last time the object was updated """
    Interpretability: InterpretabilityStatus = None
    """ Interpretability contains results produced during the explaining phase of the Model """
    Conditions: List[ModelCondition] = field(default_factory=lambda : [])


@datamodel(proto=common_pb.ModelProfile)
class ModelProfile(ImmutableConfiguration):
    Name: str = ''
    Importance: List[float] = field(default_factory=lambda : [])
    Plots: List[Plot] = field(default_factory=lambda : [])


@datamodel(proto=training_pb.AlgorithmSearchSpaceSpec)
class AlgorithmSearchSpace(Configuration):
    """ AlgorithmSearchSpaceSpec defines the algorithms available to models produced by a Study """
    Allowlist: List[ClassicEstimator] = field(default_factory=lambda : [])
    """
    AllowList contains the collection of algorithms available to the Study specifying the AlgorithmSearchSpaceSpec.
    If empty, all algorithms will be available for training
    """


@datamodel(proto=training_pb.SuccessiveHalvingOptions)
class SuccessiveHalvingOptions(Configuration):
    MinResources: int = 0
    ReductionFactor: int = 0
    """ A parameter for specifying reduction factor of promotable trials """
    MinEarlyStoppingRate: int = 0
    """ A parameter for specifying the minimum early-stopping rate """
    BootstrapCount: int = 0
    """ Minimum number of trials that need to complete a rung before any trial is considered for promotion into the next rung. """


@datamodel(proto=training_pb.PrunerSpec)
class PrunerSettings(Configuration):
    Type: Pruner = Pruner.MedianPruner


SamplerType = Sampler


@datamodel(proto=training_pb.SearchSpec)
class ModelSearch(Configuration):
    """ SearchSpec specifies the configuration for a distributed model search """
    Sampler: SamplerType = SamplerType.TPESearch
    """ The hyper-parameter optimization search method """
    Pruner: PrunerSettings = None
    """
    Pruner specifies the configuration to run a model search using a pruning algorithm. Using a pruning
    algorithm allows you to train a large number of candidate models with a subset of the dataset
    """
    MaxCost: int = 100
    """ The maximum cost that can be incurred before stopping the model search (applicable for deep learning models) """
    MaxTime: int = 30
    """ The maximum number of minutes, that the model search can run for """
    MaxModels: int = 10
    """ The maximum number of candidate models that will be sampled and trained """
    MinBestScore: float = 0
    """
    The minimum best score needed to finish the search. The system will finish the search when the minimum is reached.
    Note that this number can be negative for a regression.
    """
    Trainers: int = 1
    """
    The desired number of trainers that will train candidate models in parallel. The number
    of trainers is restricted based on the allowance provided by the active License
    """
    Test: int = 1
    """
    The number of top candidate models that will be moved to the testing phase once the model search is complete.
    By default, only the best model will be retained
    """
    RetainTop: int = 1
    """
    The number of top candidate models, sorted by their objective score, that will be retained in
    the case that garbage collection is enabled. All other models will be archived
    """
    RetainedFor: int = 60
    """
    The time, in minutes, for which candidate models (excluding the best model) will be
    retained, after which they will be archived
    """
    SearchSpace: AlgorithmSearchSpace = AlgorithmSearchSpace()
    """ SearchSpace specifies the algorithms available to candidate models """
    Objective: Metric = None
    """ The objective metric that will be measured against all models to evaluate their performance """
    Objective2: Metric = None
    """
    The second objective metric that will be measured and evaluated in tandem with the primary objective.
    The model search optimizer will attempt to optimize both metrics
    """
    EarlyStop: EarlyStopping = EarlyStopping()
    """
    The number of new models produced by the search which, if there is no improvement
    in score, the model search will conclude
    """


@datamodel(proto=training_pb.BaselineSpec)
class BaselineSettings(Configuration):
    """ BaselineSpec specifies the configuration to produce baseline models """
    Enabled: bool = False
    """
    Indicates if baseline models will be produced. Enabling baseline will create a model for each
    algorithm in the parent Study's search space with default hyper-parameters
    """
    Baselines: List[ClassicEstimator] = field(default_factory=lambda : [])
    """ Baselines contains the collection of algorithms that models will be created with """
    All: bool = False
    """ Indicates if models will be created for every algorithm """


@datamodel(proto=training_pb.FeatureEngineeringSearchSpec)
class FeatureEngineeringSearch(Configuration):
    """
    FeatureEngineeringSearchSpec specifies the configuration to produce
    the best-performing feature engineering pipeline for a given dataset
    """
    Enabled: bool = True
    """ Indicates if the feature engineering search will be performed """
    ImbalancedHandler: ImbalanceHandling = ImbalanceHandling.ImbalanceAuto
    """ The method to use when handling an imbalanced dataset """
    Estimator: ClassicEstimator = ClassicEstimator.DecisionTreeClassifier
    """ The algorithm to use when evaluating models with different feature engineering pipelines """
    MaxModels: int = 2
    """
    The number of models to sample, after which the feature engineering with the highest
    score will be used with Model resources produced by the primary model search of the parent Study
    """
    MaxTime: int = 3600
    """ The deadline, in seconds, for models produced by the search to be trained """
    MaxTrainers: int = 1
    """
    The desired number of trainers that will train candidate models in parallel. The number
    of trainers is restricted based on the allowance provided by the active License
    """
    SamplePct: int = 100
    """ The number percentage (0 through 100) of the dataset to train models with """
    AutoRemove: bool = True
    """
    Indicates if models produced by the feature engineering search should be
    automatically removed at the conclusion of the search
    """
    Reuse: bool = False
    """
    If true, if a feature engineering pipeline was previously produced for
    the same dataset it will be used as a starting point for the search
    """
    FeatureSelectionTemplate: FeatureSelection = FeatureSelection()
    """
    Specification for feature selection.
    successful study.
    """


@datamodel(proto=training_pb.StudyScheduleSpec)
class StudySchedule(Configuration):
    """ StudyScheduleSpec specifies the parameters for a Study to be executed at a certain time """
    Enabled: bool = False
    """ Indicates if the schedule is enabled """
    StartAt: Time = None
    """ The time at which the Study will begin execution """


@datamodel(proto=training_pb.ModelResult)
class ModelResult(Configuration):
    """ ModelResult contains the records of a single garbage-collected model """
    Name: str = ''
    """ The name of the model """
    Alg: str = ''
    """ The type of estimator of the model """
    Score: float = 0
    """ The objective score of the model """
    Error: bool = False
    """ Indicates if the model experience an error whilst training """
    TrialID: int = 0
    """ The optimizer trial ID of the model """


@datamodel(proto=training_pb.ImbalanceHandlingSpec)
class ImbalanceHandlingSpec(Configuration):
    """ ImbalanceHandlingSpec specifies the configuration to process an imbalanced dataset """
    Enabled: bool = False
    """ Indicates if imbalance handling is enabled """
    Imbalance: ImbalanceHandling = ImbalanceHandling.ImbalanceAuto
    """ The technique that will be used to handle the imbalanced dataset """


@datamodel(proto=training_pb.GarbageCollectionSpec)
class GarbageCollection(Configuration):
    """ GarbageCollectionSpec specifies the configuration to garbage-collect unused Model resources """
    CollectAtStudyEnd: bool = True
    """ Indicates if all models of the Study, excluding the highest-performing model, will be archived """
    KeepOnlyBestModelPerAlgorithm: bool = True
    """
    Indicates if multiple models with the same algorithm are produced by the Study, the
    model with the lowest score will be garbage-collected
    """
    KeepPrunedModels: bool = False
    """
    Indicates if we should keep pruned models
    model with the lowest score will be garbage-collected
    """


@datamodel(proto=training_pb.EnsemblesSpec)
class Ensemble(Configuration):
    """ EnsemblesSpec specifies the configuration to produce ensemble models """
    Enabled: bool = False
    """ Indicates if ensemble models will be created """
    VotingEnsemble: bool = False
    """ Indicates if a voting ensemble model will be created """
    StackingEnsemble: bool = True
    """ Indicates if a stacking ensemble model will be created """
    Top: int = 3
    """ The number of top candidate models to include in the ensemble """


@datamodel(proto=training_pb.StudySpec)
class StudySpec(Configuration):
    """ StudySpec defines the desired state of a Study and the parameters for a model search """
    VersionName: str = 'v0.0.1'
    """
    The name of the DataProductVersion which describes the version of the resource
    that exists in the same DataProduct namespace as the resource
    """
    Description: str = ''
    """ The user-provided description of the Study """
    LabRef: ObjectReference = ObjectReference('default-tenant', 'default-lab')
    """
    The reference to the Lab under which the Model resources created by the Study will be trained.
    If unspecified, the default Lab from the parent DataProduct will be used
    """
    DatasetName: str = ''
    """
    The name of the Dataset resource that will be used to train models with.
    The dataset will be split into individual training, testing, and validation datasets
    """
    Task: TaskType = TaskType.AutoDetectTask
    """ The machine learning task type (i.e. regression, classification) """
    FeSearch: FeatureEngineeringSearch = FeatureEngineeringSearch()
    """ FeatureEngineeringSearch specifies the parameters to perform a feature engineering search """
    Baseline: BaselineSettings = BaselineSettings()
    """ Baseline specifies the parameters to generate baseline (default hyper-parameters) models """
    Search: ModelSearch = ModelSearch()
    """ Search specifies the configuration to perform the model search for the best algorithm and hyper-parameters """
    Ensembles: Ensemble = Ensemble()
    """ Ensembles specifies to parameters to generate ensemble models """
    ServingTemplate: ServingSpec = None
    """
    ServingTemplate specifies the model format and resource requirements that will be applied to
    the Predictor created for the Model that will be selected by the Study
    """
    ImbalanceHandler: ImbalanceHandlingSpec = ImbalanceHandlingSpec()
    """ Set the imbalance dataset handling. """
    TrainingTemplate: Training = Training()
    """ TrainingTemplate specifies the configuration to train and evaluate models """
    Schedule: StudySchedule = StudySchedule()
    """ Schedule specifies the configuration to execute the Study at a later date """
    Interpretability: InterpretabilitySpec = InterpretabilitySpec()
    """ Interpretability specifies the parameters to create interpretability visualizations for the final model """
    Aborted: bool = False
    """ Aborted indicates that the execution of the Study and associated Models should be permanently stopped """
    Reported: bool = True
    """ Reported indicates that a report will be generated for the Study """
    Paused: bool = False
    """ Paused indicates that the execution of new workloads associated with the Study should be paused """
    Profiled: bool = True
    """ Profiled indicates that the Study will be profiled after the conclusion of it's model search """
    ModelPublished: bool = False
    """ ModelPublished indicates that a Docker image will be created containing the best model produced by the Study """
    ModelImagePushed: bool = False
    """ ModelImagePushed indicates that if a Docker image of the best model will be pushed to a Docker image registry """
    ModelExplained: bool = True
    """
    ModelExplained indicates if interpretability diagrams, as specified
    by the Interpretability field, will be produced for the final model
    """
    Fast: bool = False
    """ Fast indicates if Models associated with the Study should skip profiling, explaining, and reporting """
    Location: DataLocation = DataLocation(BucketName='default-minio-bucket')
    """ The data location where Study artifacts (metadata, reports, and model artifacts) generated by the Study will be stored """
    Owner: str = 'no-one'
    """ The name of the Account which created the object, which exists in the same tenant as the object """
    Compilation: CompilerSettings = None
    """ CompilerSpec specifies the configuration to compile the best-selected model to a binary (currently unimplemented) """
    Template: bool = False
    """ Indicates if the Study is a template, in which case it will not be executed """
    Flagged: bool = False
    """ Indicates if the Study is flagged """
    Notification: NotificationSettings = NotificationSettings()
    """ The notification specification that determines which notifiers will receive Alerts generated by the object """
    Gc: GarbageCollection = GarbageCollection()
    """ GarbageCollectionSpec specifies the configuration to automatically clean-up unused models """
    Ttl: int = 0
    """ The time-to-live, in seconds, for Model resources produced by the Study """
    ModelVersion: str = ''
    """ ModelVersion specifies the version assigned to all the Model resources produced by the Study """
    TimeoutInSecs: int = 14400
    """ The time, in seconds, after which the execution of the Study will be forcefully aborted (4 hours, by default) """


@datamodel(proto=training_pb.StudyCondition)
class StudyCondition(Configuration):
    """ StudyCondition describes the state of a Study at a certain point """
    Type: StudyConditionType = None
    """ Type of study condition """
    Status: ConditionStatus = None
    """ Status of the condition, one of True, False, Unknown """
    LastTransitionTime: Time = None
    """ Last time the condition transitioned from one status to another """
    Reason: str = ''
    """ The reason for the condition's last transition """
    Message: str = ''
    """ A human-readable message indicating details about the transition """


@datamodel(proto=training_pb.GarbageCollectionStatus)
class GarbageCollectionStatus(Configuration):
    """ GarbageCollectionStatus contains the records for garbage-collected models """
    Collected: int = 0
    """ The number of models that were collected, equal to len(Models) """
    Models: List[ModelResult] = field(default_factory=lambda : [])
    """ The collection of models that were archived """


@datamodel(proto=training_pb.StudyPhaseStatus)
class StudyPhaseStatus(Configuration):
    """ StudyPhaseStatus contains the statistics for a single phase of a Study """
    StartTime: Time = None
    """ The time at which the phase started """
    EndTime: Time = None
    """ The time at which the phase concluded """
    Waiting: int = 0
    """ The number of models pending training """
    Running: int = 0
    """ The number of models currently being trained """
    Failed: int = 0
    """ The number of models that experienced an error whilst training """
    Completed: int = 0
    """ The number of models that have been successfully trained """
    BestScore: float = 0
    """ Best score so far in this phase. The best score is the value of the objective. """
    ModelsWithNoProgress: int = 0
    """ Actual number of models where no progress was made. This used to decide on early stop. """


@datamodel(proto=training_pb.StudyStatus)
class StudyStatus(ImmutableConfiguration):
    """ StudyStatus defines the observed state of a Study """
    Models: int = 0
    """ Total models created for the study """
    StartTime: Time = None
    """ StartTime represents the time at which the execution of the Study started """
    EndTime: Time = None
    """ EndTime represents the time at which the Study was marked as completed, failed, or aborted """
    BestModel: str = ''
    """ The name of the Model resource which was determined to be the highest-performing """
    BestModelScore: float = 0
    """ The score of the Model resource which was determined to be the highest-performing """
    ProfileUri: str = ''
    """ The URI of the raw profile data produced by the Study """
    ReportName: str = ''
    """
    Reference to the report object that was generated for the dataset, which exists in the same Data Product namespace
    as the object
    """
    Phase: StudyPhase = StudyPhase.ModelPending
    """ The phase of the Study """
    ObservedGeneration: int = 0
    """ ObservedGeneration is the last generation that was acted on """
    TrainDataset: DataLocation = None
    """ TrainDatasetLocation specifies the location of the training dataset """
    TestDataset: DataLocation = None
    """ TestDatasetLocation specifies the location of the testing dataset """
    ValidationDataset: DataLocation = None
    """ ValidationDataset specifies the location of the validation dataset """
    LastModelID: int = 0
    """ The Kubernetes-internal ID of the last Model resource generated by the Study """
    FailureReason: StatusError = None
    """ In the case of failure, the Study resource controller will set this field with a failure reason """
    FailureMessage: str = ''
    """ In the case of failure, the Study resource controller will set this field with a failure message """
    TrainingRows: int = 0
    """ The number of rows in the training dataset """
    TestingRows: int = 0
    """ The number of rows in the testing dataset """
    ValidationRows: int = 0
    """ The number of rows in the validation dataset """
    Progress: int = 0
    """ The progress percentage of the Study, which is derived from the Study's current phase """
    TrainingDataHash: DataHashes = None
    """
    Sha 256 of the data sig
    TrainingDataHash specifies the hashes for datasets used by the Study
    """
    TriggeredBy: TriggerType = None
    """ The type of trigger which started the Study """
    Logs: OutputLogs = None
    """ Logs specifies the location of logs produced by workloads associated with the Study """
    FeatureEngineering: StudyPhaseStatus = None
    """ FeatureEngineeringStatus contains the status of the feature engineering phase """
    Baseline: StudyPhaseStatus = None
    """ BaselineStatus contains the status of the baseline phase """
    Search: StudyPhaseStatus = None
    """ SearchStatus contains the status of the model search phase """
    Ensemble: StudyPhaseStatus = None
    """ EnsembleStatus contains the status of the ensemble phase """
    Test: StudyPhaseStatus = None
    """ TestStatus contains the status of the testing phase """
    Explain: StudyPhaseStatus = None
    """ ExplainStatus contains the status of the explaining phase """
    LastUpdated: Time = None
    """ The last time the object was updated """
    BestFE: FeatureEngineeringSpec = None
    """ BestFE specifies the best feature engineering pipeline produced by the Study """
    Gc: GarbageCollectionStatus = None
    """ GC specifies the status of garbage collection relevant to the Study """
    Conditions: List[StudyCondition] = field(default_factory=lambda : [])


@datamodel(proto=training_pb.ReportCondition)
class ReportCondition(Configuration):
    """ ReportCondition describes the state of a Report at a certain point. """
    Type: ReportConditionType = None
    """ Type of Report condition """
    Status: ConditionStatus = None
    """ Status of the condition, one of True, False, Unknown """
    LastTransitionTime: Time = None
    """ Last time the condition transitioned from one status to another """
    Reason: str = ''
    """ The reason for the condition's last transition """
    Message: str = ''
    """ A human-readable message indicating details about the transition """


ReportType_ = ReportType


@datamodel(proto=training_pb.ReportSpec)
class ReportSpec(Configuration):
    """ ReportSpec specifies the desired state of a Report """
    VersionName: str = 'v0.0.1'
    """
    The name of the DataProductVersion which describes the version of the resource
    that exists in the same DataProduct namespace as the resource
    """
    EntityRef: ObjectReference = None
    """ EntityRef specifies the entity which the Report references. The supported entities consist of Dataset, Model, and Study resources """
    Location: DataLocation = DataLocation(BucketName='modela')
    """ The location of the flat-file containing the PDF report """
    ReportType: ReportType_ = None
    """ The type of report (e.g. classification model report, study report) """
    Format: ReportFormat = ReportFormat.Pdf
    """ The format of the Report. `pdf` is the only supported type as of the current release """
    NotifierName: str = ''
    """ The name of the Notifier resource which Alerts created by the Report will be forwarded to """
    Owner: str = 'no-one'
    """ The name of the Account which created the object, which exists in the same tenant as the object """
    Resources: Workload = Workload('memory-large')
    """ Resources specifies the resource requirements that will be allocated to the report generation workload """
    ActiveDeadlineSeconds: int = 600
    """ The deadline for any Jobs associated with the Report to be completed in seconds """


@datamodel(proto=training_pb.ReportStatus)
class ReportStatus(Configuration):
    """ ReportStatus defines the observed state of a Report """
    StartTime: Time = None
    """ StartTime represents the time at which the execution of the Report started """
    EndTime: Time = None
    """ EndTime represents the time at which the Report was marked as completed, failed, or aborted """
    Phase: ReportPhase = ReportPhase.Pending
    """ The phase of the Report """
    Uri: str = ''
    """ The URI to the flat-file report within the VirtualBucket specified by the Report """
    ObservedGeneration: int = 0
    """ ObservedGeneration is the last generation that was acted on """
    FailureReason: StatusError = None
    """ In the case of failure, the Report resource controller will set this field with a failure reason """
    FailureMessage: str = ''
    """ In the case of failure, the Report resource controller will set this field with a failure message """
    Logs: OutputLogs = None
    """ Logs specifies the location of logs produced by workloads associated with the Report """
    LastUpdated: Time = None
    """ The last time the object was updated """
    Conditions: List[ReportCondition] = field(default_factory=lambda : [])


@datamodel(proto=training_pb.ModelAutobuilderCondition)
class ModelAutobuilderCondition(Configuration):
    """ ModelAutobuilderCondition describes the state of a ModelAutobuilder at a certain point """
    Type: ModelAutobuilderConditionType = None
    """ Type of ModelAutobuilder condition """
    Status: ConditionStatus = None
    """ Status of the condition, one of True, False, Unknown """
    LastTransitionTime: Time = None
    """ Last time the condition transitioned from one status to another """
    Reason: str = ''
    """ The reason for the condition's last transition """
    Message: str = ''
    """ A human-readable message indicating details about the transition """


DataSourceTemplate = DataSourceSpec
DatasetType_ = DatasetType


@datamodel(proto=training_pb.ModelAutobuilderSpec)
class ModelAutobuilderSpec(Configuration):
    """ ModelAutobuilderSpec define the desired state of a ModelAutobuilder """
    DataProductName: str = ''
    """ The name of the DataProduct namespace that the resource exists under """
    DataProductVersionName: str = ''
    """
    The name of the DataProductVersion which describes the version of the resource
    that exists in the same DataProduct namespace as the resource
    """
    DatasourceName: str = ''
    """
    DataSourceName is the name of an existing DataSource resource which will be used as the schema for the ModelAutoBuilder's Dataset.
    If empty, a DataSource will be automatically created based on the data specified by the Location field
    """
    DatasetName: str = ''
    """
    The name of an existing Dataset resource, or the name of the Dataset resource that will be created
    based on the data specified by the Location field, which will be used to train models
    """
    Location: DataLocation = None
    """ The location for data that will be saved in a Dataset resource to train models with """
    Task: TaskType = None
    """ The machine learning task type relevant to the dataset (i.e. regression, classification) """
    Objective: Metric = None
    """ The objective metric that will be measured against trained models to evaluate their performance """
    TargetColumn: str = ''
    """ The name of the column within the dataset that contains the label(s) to be predicted """
    MaxTime: int = 600
    """ The deadline for models to complete training, in seconds """
    MaxModels: int = 10
    """ The number of candidate models that will be sampled and trained """
    Fast: bool = False
    """
    Fast indicates if Dataset and Study resources associated with the ModelAutobuilder should run in fast mode.
    Running in fast mode will skip unnecessary workloads such as profiling, reporting, explaining, etc.
    """
    AccessMethod: AccessType = AccessType.ClusterIP
    """
    The Kubernetes-native access method which specifies how the Predictor created by the ModelAutobuilder will be exposed.
    See https://modela.ai/docs/docs/serving/production/#access-method for a detailed description of each access type
    """
    AutoScale: bool = False
    """ Indicates if the Predictor created by the ModelAutobuilder will automatically scale to traffic """
    Dataapp: bool = False
    """ Indicates if the ModelAutobuilder will create a DataApp resource to serve the highest-performing model that was trained """
    DataSourceSpec: DataSourceSpec = None
    """
    DataSourceSpec specifies the full specification of the DataSource resource that will be created by the ModelAutobuilder.
    If empty, the ModelAutobuilder will attempt to infer the schema of the data specified by the Location field
    """
    Trainers: int = 1
    """
    The desired number of trainers that will train candidate models in parallel. The number
    of trainers is restricted based on the allowance provided by the active License
    """
    Sampler: SamplerType = SamplerType.TPESearch
    """ The hyper-parameter optimization search method """
    Aborted: bool = False
    """ Aborted indicates that the execution of the ModelAutobuilder and any associated workloads should be permanently stopped """
    Owner: str = 'no-one'
    """ The name of the Account which created the object, which exists in the same tenant as the object """
    Resources: Workload = None
    """ Resources specifies the resource requirements that will be allocated to dataset and model training Jobs """
    FeatureEngineering: bool = False
    """ Indicates if feature engineering will be performed prior to the primary model search """
    FeatureSelection: bool = False
    """ Indicates if feature selection will be performed prior to the primary model search """
    ServingSiteRef: ObjectReference = ObjectReference(Namespace='default-tenant', Name='default-serving-site')
    """
    The reference to the ServingSite where the Predictor created by the ModelAutobuilder will be hosted.
    If unspecified, the default ServingSite from the parent DataProduct will be used
    """
    LabRef: ObjectReference = ObjectReference(Namespace='default-tenant', Name='default-lab')
    """
    The reference to the Lab under which Dataset and Study resources created by the ModelAutobuilder will be trained.
    If unspecified, the default Lab from the parent DataProduct will be used
    """
    DatasetType: DatasetType_ = DatasetType_.Tabular
    """ The type of dataset which was uploaded. `tabular` is the only supported type as of the current release """


@datamodel(proto=training_pb.ModelAutobuilderStatus)
class ModelAutobuilderStatus(Configuration):
    """ ModelAutobuilderStatus define the observed state of a ModelAutobuilder """
    FlatFileName: str = ''
    """ The name of the flat-file generated for the associated Dataset """
    DataSourceName: str = ''
    """ The name of the DataSource associated with resource """
    DatasetName: str = ''
    """ The name of the Dataset associated with the resource """
    DataappName: str = ''
    """ The name of the DataApp associated with the resource """
    StudyName: str = ''
    """ The name of the Study associated with the resource """
    BestModelName: str = ''
    """ The name of the highest-performing Model resource produced as a result of the associated Study resource """
    PredictorName: str = ''
    """ The name of the Predictor associated with the resource """
    ImageRepoName: str = ''
    Phase: ModelAutobuilderPhase = ModelAutobuilderPhase.Pending
    """ The phase of the ModelAutobuilder """
    Rows: int = 0
    """ The number of rows observed in the Dataset associated with the resource """
    Cols: int = 0
    """ The number of columns observed in the Dataset associated with the resource """
    FileSize: int = 0
    """ The size of the raw data in the Dataset associated with the resource """
    Models: int = 0
    """ The number of total Model resources created by the associated Study resource """
    TrainedModels: int = 0
    """ The number of successfully trained Model resources created by the associated Study resource """
    BestModelScore: float = 0
    """ The highest score out of all Models created by the associated Study resource """
    Estimator: ClassicalEstimatorSpec = None
    """ The estimator specification for the highest-performing Model resource """
    StartTime: Time = None
    """ StartTime represents the time at which the execution of the ModelAutobuilder started """
    EndTime: Time = None
    """ EndTime represents the time at which the ModelAutobuilder was marked as completed, failed, or aborted """
    ObservedGeneration: int = 0
    """ ObservedGeneration is the last generation that was acted on """
    FailureReason: StatusError = None
    """ In the case of failure, the ModelAutobuilder resource controller will set this field with a failure reason """
    FailureMessage: str = ''
    """ In the case of failure, the ModelAutobuilder resource controller will set this field with a failure message """
    LastUpdated: Time = None
    """ The last time the object was updated """
    Conditions: List[ModelAutobuilderCondition] = field(default_factory=lambda : [])
