from enum import Enum


class HolidayCountry(Enum):
    UnitedState = "US"
    Brazil = "BR"
    Indonesia = "ID"
    India = "IN"
    Malaysia = "MY"
    Vietnam = "VN"
    Thailand = "TH"
    Philippines = "PH"
    Pakistan = "PK"
    Bangladesh = "BD"
    Egypt = "EG"
    China = "CN"
    Russian = "RU"
    Korea = "KR"
    Belarus = "BY"
    UnitedArabEmirates = "AE"
    NoneHoliday = "none"


class Frequency(Enum):
    Seconds = "second"
    Minutes = "minute"
    Hours = "hour"
    Days = "day"
    Weeks = "week"
    Months = "month"
    Qtrs = "quarter"
    Years = "year"


class TaskType(Enum):
    BinaryClassification = "binary-classification"
    MultiClassification = "multi-classification"
    MultiLabelClassification = "multi-label-classification"
    Forecasting = "forecasting"
    Regression = "regression"
    Clustering = "clustering"
    Recommendation = "recommendation"
    OutlierDetection = "outlier-detection"
    NoveltyDetection = "novelty-detection"
    TopicModeling = "topic-modeling"
    VideoActionRecognition = "video-action-recognition"
    VideoClassification = "video-classification"
    VideoObjectTracking = "video-object-tracking"
    ImageClassification = "image-classification"
    ImageMultiLabelClassification = "image-multi-classification"
    ImageObjectDetection = "image-object-detection"
    ImageSegmentation = "image-segmentation"
    AutoDetectTask = "auto"


class Metric(Enum):
    Accuracy = "accuracy"
    AveragePrecision = "average-precision"
    BalancedAccuracy = "balanced-accuracy"
    F1Binary = "f1"
    F1Micro = "f1-micro"
    F1Macro = "f1-macro"
    F1Weighted = "f1-weighted"
    F1Samples = "f1-samples"
    PrecisionBinary = "precision"
    PrecisionMicro = "precision-micro"
    PrecisionMacro = "precision-macro"
    PrecisionWeighted = "precision-weighted"
    PrecisionSamples = "precision-samples"
    RecallBinary = "recall"
    RecallMacro = "recall-macro"
    RecallMicro = "recall-micro"
    RecallWeighted = "recall-weighted"
    RecallSamples = "recall-samples"
    LogLoss = "log-loss"
    RocAuc = "auc"
    RocAucMicro = "auc-micro"
    RocAucMacro = "auc-macro"
    RocAucWeighted = "auc-weighted"
    PRRocAuc = "pr-auc"
    PRRocAucMicro = "pr-auc-micro"
    PRRocAucMacro = "pr-auc-macro"
    PRRocAucWeighted = "pr-auc-weighted"
    ZeroOne = "zero-one"
    HammingLoss = "hamming-loss"
    HingeLoss = "hinge-loss"
    JacquardScore = "jacquard-loss"
    MatthewsCorrCoef = "mcc"
    Fp = "fp"
    Fn = "fn"
    Tn = "tn"
    Tp = "tp"
    Tpr = "tpr"
    Fpr = "fpr"
    Tnr = "tnr"
    MCC = "matthews-corr-coef"
    ExplainedVariance = "explained-variance"
    MaxError = "max-error"
    MAE = "mae"
    MSE = "mse"
    MSLE = "msle"
    RMSE = "rmse"
    RMSLE = "rmsle"
    MedianAbsoluteError = "median-absolute-error"
    R2 = "r2"
    AdjR2 = "adj-r2"
    MeanPoissonDeviance = "mean_poisson_deviance"
    MeanGammaDeviance = "mean-gamma-deviance"
    MeanTweedieDeviance = "mean-tweedie-deviance"
    MAPE = "mape"
    MAZE = "maze"
    MDAPE = "mdape"
    SMAPE = "smape"
    AdjustedMutualInfoScore = "adjusted-mutual-info-score"
    AdjustedRandScore = "adjusted-rand-score"
    CompletenessScore = "completeness-score"
    FowlkesMallowsScore = "fowlkes-mallows-score"
    HomogeneityScore = "homogeneity-score"
    MutualInfoScore = "mutual-info-score"
    NormalizedMutualInfoScore = "normalized-mutual-info-score"
    VMeasureScore = "v-measure-score"
    P50Latency = "p50-latency"
    P95Latency = "p95-latency"
    P99Latency = "p99-latency"
    Cpu = "cpu"
    Gpu = "gpu"
    Mem = "mem"
    GpuMem = "gpu-mem"
    ReqSec = "req-per-sec"
    UncrainPredictionPercent = "uncertain-prediction-percent"
    Null = "none"


class Imputation(Enum):
    RemoveRowsWithMissingValues = "remove-rows-with-missing-values"
    ReplaceWithMean = "replace-with-mean"
    ReplaceWithMedian = "replace-with-median"
    ReplaceWithArbitraryValue = "replace-with-arbitrary-value"
    ReplaceWithEndOfTail = "replace-with-end-of-tail"
    ReplaceWithRandomSample = "replace-with-random-sample"
    FreqCategory = "freq-category-imputation"
    AddMissingValueIndicator = "add-missing-value-indicator"
    Knn = "knn"
    Iterative = "iterative"
    MICE = "mice"
    No = "no-imputation"
    AutoImputer = "auto"


class Scaling(Enum):
    Standard = "standard-scaling"
    MaxAbs = "max-abs-scaling"
    MinMax = "min-max-scaling"
    Normalization = "normalizion-scaling"
    Robust = "robust-scaling"
    ScaleToUnitNorm = "scale-to-unit-norm"
    NoScaling = "none"
    Auto = "auto"


class DatasetType(Enum):
    Tabular = "tabular"
    Image = "image"
    Text = "text"
    Video = "video"
    Audio = "audio"


class RelationshipArity(Enum):
    OneToOne = "one-to-one"
    OneToMany = "one-to-many"
    ManyToMany = "many-to-many"


class FeatureSelectionType(Enum):
    DropFeatures = "drop-features"
    DropConstantFeatures = "drop-constant-features"
    DropDuplicateFeatures = "drop-deplicated-features"
    DropCorrelatedFeatures = "drop-correlated-features"
    MutualInformation = "mutal-information"
    ChiSquare = "chisquare-fearture-selection"
    StepForward = "step-forward-feature-selection"
    StepBackward = "step-backward-feature-selection"
    LassoRegression = "lasso-regression-feature-selection"
    TreeImportance = "tree-importance-feature-selection"
    RecursiveFeatureElimination = "recursive-feature-elimination"
    RecursiveFeatureAddition = "recursive-feature-addition"
    SelectPercentile = "select-percentile"
    SelectKBest = "select-kbest"
    SelectFpr = "select-fpr"
    SelectFdr = "select-fdr"
    VarianceThreshold = "variance-threshold"
    Nothing = "none"
    Auto = "auto"


class ShapType(Enum):
    Permutation = "permutation"
    Partition = "partition"
    Tree = "tree"
    Kernel = "kernel"
    Sampling = "sampling"
    Linear = "linear"
    Deep = "deep"
    Gradient = "gradient"
    Auto = "auto"
    Unknown = "none"


class ModelClassType(Enum):
    FE = "feature-engineering"
    Baseine = "baseline"
    Search = "search"
    Ensemble = "ensemble"
    Test = "test"


class ModelType(Enum):
    Classical = "classical"
    DNN = "dnn"
    Transformer = "transformer"
    Chatbot = "chatbot"
    RL = "rl"


class CategoricalEncoding(Enum):
    OneHotEncoding = "one-hot-encoding"
    OneHotEncoderTop = "one-hot-encoding-top-categories"
    OrdinalEncoding = "ordinal-encoding"
    CountEncoding = "count-encoding"
    TargetEncoding = "target-encoding"
    WoERatioEncoding = "weight-of-evidence-encoding"
    BinaryEncoding = "binary-encoding"
    LabelEncoding = "label-encoding"
    HashEncoding = "hash-encoding"
    CatboostEncoding = "catboost-encoding"
    LeaveOneOutEncoding = "loo-encoding"
    NoEncoding = "no-encoding"
    AutoEncoding = "auto"
    NoneEncoding = "none"


class Discretisation(Enum):
    EqualWidth = "equal-width-discretisation-"
    EqualFreq = "equal-freq-discretisation"
    KBins = "kbin-discretisation"
    KernelCenterer = "kernel-centerer-discretisation"
    LabelBinarizer = "label-binarizer-discretisation"
    MultiLabelBinarizer = "multi-label-binarizer-discretisation"
    NoDiscretisation = "none"
    Auto = "auto"


class OutlierHandling(Enum):
    Trim = "trim-outliers"
    Winsorizer = "winsorizer-outliers"
    Cap = "cap-outliers"
    ZeroCode = "zero-code-outliers"
    NoneOutlier = "none"
    AutoOutlier = "auto"


class VariableTransformation(Enum):
    LogTransformation = "log-transformation"
    ReciprocalTransformation = "reciprocal-transformation"
    SqrtTransformation = "sqrt-transformation"
    PowerTransformation = "power-transformation"
    BoxCoxTransformation = "box-cox-transformation"
    YeoJohnsonTransformation = "yj-transformation"
    NoneTransform = "none"
    AutoTransform = "auto"


class DatetimeTransformation(Enum):
    ExtractDateTimeInformation = "extract-datetime-information"
    NoneDatetime = "none"
    AutoDatetime = "auto"


class TextEncoding(Enum):
    TfIdf = "tfidf"
    CountVectorizer = "count-vec"
    HashingVectorizer = "hashing-vec"
    NoEncoding = "none"
    Auto = "auto"


class CvType(Enum):
    Nothing = "none"
    GroupKFold = "group-kfold"
    GroupShuffleSplit = "group-shuffle-split"
    CVTypeKFold = "kfold"
    CVTypeLeaveOneGroupOut = "leave-one-group-out"
    LeavePGroupsOut = "leave-p-groups-out"
    LeaveOneOut = "leave-one-out"
    LeavePOut = "leave-p-out"
    PredefinedSplit = "predefined-split"
    RepeatedKFold = "repeated-kfold"
    RepeatedStratifiedKFold = "repeated-stratified-k-fold"
    ShuffleSplit = "shuffle-split"
    StratifiedKFold = "stratified-k-fold"
    StratifiedShuffleSplit = "stratified-shuffle-split"
    StratifiedGroupKFold = "stratified-group-k-fold"
    TimeSeriesSplit = "time-series-split"


class EnsembleType(Enum):
    Voting = "voting"
    Stack = "stacking"


class DataSplitMethod(Enum):
    RandomStratified = "random-stratified"
    Random = "random"
    SplitColumn = "split-column"
    Time = "time"
    Auto = "auto"
    TestDataset = "test-dataset"


class Operation(Enum):
    LT = "lt"
    EQ = "eq"
    GT = "gt"
    NE = "ne"
    LE = "le"
    GE = "ge"


class ImbalanceHandling(Enum):
    ADASYN = "adasyn"
    BorderlineSMOTE = "baseline-smote"
    KMeansSMOTE = "kmean-smote"
    RandomOverSampler = "random-over-sampler"
    SMOTE = "smote"
    SMOTENC = "smotenc"
    SVMSMOTE = "svmsmote"
    ClassWeights = "class-weights"
    ImbalanceNone = "none"
    ImbalanceAuto = "auto"


class ModalityType(Enum):
    Data = "data"
    Epochs = "epochs"


class ModelPhase(Enum):
    Failed = "Failed"
    Pending = "Pending"
    Training = "Training"
    Trained = "Trained"
    Testing = "Testing"
    Tested = "Tested"
    Reporting = "Reporting"
    Reported = "Reported"
    Completed = "Completed"
    Publishing = "Publishing"
    Published = "Published"
    Packaging = "Packaging"
    Packaged = "Packaged"
    Profiling = "Profiling"
    Profiled = "Profiled"
    Explaining = "Explaining"
    Explained = "Explained"
    Aborted = "Aborted"
    Forecasting = "Forecasting"
    Forecasted = "Forecasted"
    Uat = "UAT"
    Deployed = "Deployed"
    Releasing = "Releasing"
    Live = "Live"
    Maintenance = "Maintenance"
    Retired = "Retired"


class ModelConditionType(Enum):
    ModelInitialized = "Initialized"
    ModelTrained = "Trained"
    ModelTested = "Tested"
    ModelReported = "Reported"
    ModelPackaged = "Packaged"
    ModelPublished = "Published"
    ModelProfiled = "Profiled"
    ModelReady = "Ready"
    ModelSaved = "Saved"
    ModelArchived = "Archived"
    ModelExplained = "Explained"
    ModelReleased = "Released"
    ModelAborted = "Aborted"
    ModelPaused = "Paused"
    ModelForecasted = "Forecasted"
    ModelUat = "UAT"
    ModelLive = "Live"
    ModelStale = "Stale"
    ModelMaintenance = "Maintenance"
    ModelRetired = "Retired"


class ClassicEstimator(Enum):
    KNeighborsRegressor = "knn-regressor"
    RidgeRegressor = "ridge-regressor"
    LassoRegressor = "lasso-regressor"
    AdaBoostRegressor = "ada-boost-regressor"
    DecisionTreeRegressor = "decision-tree-regressor"
    ExtraTreeRegressor = "extra-tree-regressor"
    LinearSvr = "linear-svr"
    Svr = "svr"
    PassiveAggressiveRegressor = "passive-agressive-regressor"
    SGDRegressor = "sgd-regressor"
    GradientBoostingRegressor = "gradient-boosting-regressor"
    HistGradientBoostingRegressor = "hist-gradient-boosting-regressor"
    RandomForestRegressor = "random-forest-regressor"
    XGBRegressor = "xgb-regressor"
    CatBoostRegressor = "catboost-regressor"
    LightGbmRegressor = "lightgbm-regressor"
    ElasticNetRegressor = "elasticnet-regressor"
    DNNRegressor = "dnn-regressor"
    EllipticEnvelope = "elliptic-envelope"
    OneClassSVM = "one-class-svm"
    IsolationForest = "isolation-forest"
    LocalOutlierFactor = "local-outlier-factor"
    Prophet = "prophet"
    ARIMA = "arima"
    AutoARIMA = "auto-arima"
    VRIMA = "vrima"
    ExponentialSmoothing = "exponential-smoothing"
    FastFourierTransform = "fast-fourier-transform"
    NBeats = "nbeats"
    ThetaMethod = "theata-method"
    ALS = "als"
    BayesianPersonalizedRanking = "bayesian-personalized-ranking"
    KNeighborsClassifier = "knn-classifier"
    AdaBoostClassifier = "ada-boost-classifier"
    BernoulliNB = "bernoulli-nb"
    DecisionTreeClassifier = "decision-tree-classifier"
    ExtraTreeClassifier = "extra-tree-classifier"
    LinearSVC = "linear-svc"
    SVC = "svc"
    PassiveAggressiveClassifier = "passive-aggressive-classifier"
    SGDClassifier = "sgd-classifier"
    LogisticRegression = "logistic-regression"
    GradientBoostingClassifier = "gradient-boosting-classifier"
    HistGradientBoostingClassifier = "hist-gradient-boosting-classifier"
    RandomForestClassifier = "random-forest-classifier"
    XGBClassifier = "xgboost-classifier"
    RidgeClassifier = "ridge-classifier"
    QuadraticDiscriminant = "quadratic-discriminant"
    LinearDiscriminant = "linear-discriminant"
    LightGBMClassifier = "lightgbm-classifier"
    CatBoostClassifier = "catboost-classifier"
    StackingEnsemble = "stacking-ensemble"
    UnknownEstimatorName = "unknown"
    NoneEstimatorName = "none"
    SpectralClustering = "spectral"
    AgglomerativeClustering = "agglomerative"
    GaussianMixtureClustering = "gaussian-mixture"
    KMeanClustering = "kmean"
    DBSCANClustering = "dbscan"
    VotingClassifier = "voting-classifier"
    VotingRegressor = "voting-regressor"
    StackingClassifier = "stacking-classifier"
    StackingRegressor = "stacking-regressor"


class Sampler(Enum):
    RandomSearch = "random"
    GridSearch = "grid"
    BayesianSearch = "bayesian"
    TPESearch = "tpe"
    ManualSearch = "manual"
    AutoSearchMethod = "auto"


class Pruner(Enum):
    NonePruner = "none"
    PatientPruner = "patient"
    MedianPruner = "median"
    PercentilePruner = "percentile"
    SHPruner = "sh"
    HyperbandPruner = "hyperband"
    ThresholdPruner = "threshold"


class AlgorithmFilter(Enum):
    Quick = "quick"
    LinearOnly = "linear-only"
    TreeOnly = "tree"
    DefaultParameters = "default-hp"
    NoFilter = "none"


class StudyPhase(Enum):
    ModelPending = "Pending"
    Splitting = "Spliting"
    Splitted = "Splitted"
    EngineeringFeature = "EngineeringFeatures"
    FeatureEngineered = "FeaturesEngineered"
    Baseline = "Baselining"
    Baselined = "Baselined"
    Searching = "Searching"
    Searched = "Searched"
    CreatingEnsembles = "CreatingEnsembles"
    CreatedEnsembles = "CreatedEnsembles"
    Testing = "Testing"
    Tested = "Tested"
    Reported = "Reported"
    Reporting = "Reporting"
    Profiling = "Profiling"
    Profiled = "Profiled"
    Explaining = "Explaining"
    Explained = "Explained"
    Completed = "Completed"
    Failed = "Failed"
    Aborted = "Aborted"
    Paused = "Paused"


StudyPhaseToProgress = {
    StudyPhase.ModelPending: "Pending",
    StudyPhase.Splitting: "Splitting Dataset",
    StudyPhase.Splitted: "Split Complete",
    StudyPhase.EngineeringFeature: "Feature Engineering Search",
    StudyPhase.FeatureEngineered: "Feature Engineering Complete",
    StudyPhase.Baseline: "Creating Baseline Models",
    StudyPhase.Baselined: "Baseline Models Complete",
    StudyPhase.Searching: "Searching Models",
    StudyPhase.Searched: "Search Complete",
    StudyPhase.CreatingEnsembles: "Creating Ensembles",
    StudyPhase.CreatedEnsembles: "Ensembles Created",
    StudyPhase.Testing: "Testing",
    StudyPhase.Tested: "Tested",
    StudyPhase.Reported: "Reported",
    StudyPhase.Reporting: "Reporting",
    StudyPhase.Profiling: "Profiling",
    StudyPhase.Profiled: "Profiled",
    StudyPhase.Explaining: "Explaining",
    StudyPhase.Explained: "Explained",
    StudyPhase.Completed: "Completed",
    StudyPhase.Failed: "Failed",
    StudyPhase.Aborted: "Aborted",
    StudyPhase.Paused: "Paused"
}


class StudyConditionType(Enum):
    StudyInitialized = "Initialized"
    StudySplitted = "StudySplitted"
    StudyFeatureEngineered = "StudyFeaturesEngineered"
    StudyBaselined = "StudyBaselined"
    StudySearched = "StudySearched"
    StudyEnsembleCreated = "ModelsEnsembleCreated"
    StudyTested = "ModelTested"
    StudyReported = "Reported"
    StudyProfiled = "Profiled"
    StudyExplained = "Explained"
    StudyAborted = "Aborted"
    StudyPaused = "Paused"
    StudySaved = "Saved"
    StudyCompleted = "Completed"
    StudyPartitioned = "Partitioned"


class TriggerType(Enum):
    OnDemand = "on-demand"
    Schedule = "on-schedule"
    NewData = "on-new-data"
    GithubEvent = "on-github-event"
    ConceptDrift = "on-concept-drift"
    PrefDegradation = "on-perf-degradation"


class ReportConditionType(Enum):
    ReportReady = "Ready"
    ReportSent = "Sent"
    ReportSaved = "Saved"


class ReportPhase(Enum):
    Pending = "Pending"
    Running = "Running"
    Completed = "Completed"
    Failed = "IsFailed"


class ReportFormat(Enum):
    Pdf = "pdf"


class ReportType(Enum):
    BinaryClassificationModelReport = "binary-classification-model"
    ForecastModelReport = "forecast-model"
    RegressionModelReport = "regression-model"
    MultiClassificationModelReport = "multi-classification-model"
    TextClassificationModelReport = "text-classification-model"
    ClassificationDatasetReport = "classification-dataset"
    ForecastDatasetReport = "forecast-dataset"
    TextClassificationDatasetReport = "text-classification-dataset"
    RegressionDatasetReport = "regression-dataset"
    SummaryReport = "summary-report"
    CustomReport = "custom-report"
    StudyReport = "study-report"
    ForecastReport = "forecast-report"
    FeatureReport = "feature-report"
    InvalidReport = "invalid-report"


class ModelAutobuilderConditionType(Enum):
    Ready = "Ready"
    DataProductReady = "DataProductReady"
    DataProductVersionReady = "DataProductVersionReady"
    DataSourceReady = "DataSourceReady"
    DatasetCompleted = "DatasetCompleted"
    StudyCompleted = "StudyCompleted"
    PredictorReady = "PredictorReady"
    DataAppReady = "DataAppReady"
    Saved = "Saved"


class ModelAutobuilderPhase(Enum):
    Pending = "Pending"
    DataSourceRunning = "DataSourceRunning"
    DataSourceReady = "DataSourceReady"
    DatasetRunning = "DatasetRunning"
    DatasetCompleted = "DatasetCompleted"
    StudyRunning = "StudyRunning"
    StudyCompleted = "StudyCompleted"
    PredictorRunning = "PredictorRunning"
    PredictorCompleted = "PredictorCompleted"
    DataAppRunning = "DataAppRunning"
    DataAppCompleted = "DataAppCompleted"
    Completed = "Completed"
    Aborted = "Aborted"
    Failed = "Failed"


class ModelValidationType(Enum):
    ModelTest = "model-test"
    PredictionCountDrift = "prediction-count-drift"
    PredictionLatencyDrift = "prediction-latency-drift"
    PredictionLatencySkew = "prediction-latency-skew"
    ModelPrefSkew = "model-pref-skew"
    ModelPrefDrift = "model-pref-drift"
    CategoricalColumnSkew = "cat-column-skew"
    CategoricalColumnDrift = "cat-column-drift"
    NumericalColumnSkew = "numerical-column-skew"
    NumericalColumnDrift = "numerical-column-drift"
    MissingValueDrift = "missing-values-drift"
    MissingValueSkew = "missing-values-skew"
    ColumnStatSkew = "column-stat-skew"
    ColumnStatDrift = "column-stat-drift"


class Aggregate(Enum):
    Min = "min"
    Max = "max"
    Avg = "avg"
    Median = "median"
    Stddev = "stddev"
    Var = "var"


class ModelServingFormat(Enum):
    Protobuf = "protobuf"
    Pickle = "pickle"
    CloudPickle = "cloudpickle"
    MLLeap = "mlleap"
    MLModel = "mlmodel"
    H5 = "h5"
    Onyx = "onyx"
    Pmml = "pmml"
    TorchScript = "pt"
