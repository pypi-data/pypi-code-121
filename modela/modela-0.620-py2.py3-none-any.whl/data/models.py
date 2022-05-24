from abc import ABC
import modela.data.common as data_common
from modela.data.common import *
from modela.infra.Account import Account
from modela.infra.UserRoleClass import UserRoleClass
from modela.infra.models import Workload, NotificationSettings, OutputLogs, GitSettings, ImageLocation
from modela.training.common import *
from modela.common import *
from modela.Configuration import *
from dataclasses import field
from typing import List, Union, Dict
from github.com.metaprov.modelaapi.pkg.apis.catalog.v1alpha1.generated_pb2 import CompilerSpec, Stakeholder, PermissionsSpec
import github.com.metaprov.modelaapi.pkg.apis.catalog.v1alpha1.generated_pb2 as catalog_pb
import github.com.metaprov.modelaapi.pkg.apis.data.v1alpha1.generated_pb2 as data_pb
import github.com.metaprov.modelaapi.services.common.v1.common_pb2 as common_pb
from modela.common import Plot
from modela.util import TrackedList


@datamodel(proto=data_pb.DataLocation)
class DataLocation(Configuration):
    """
    DataLocation describes the external location of data that will be accessed by Modela, and additional
    information on how to query the data if the location is a non flat-file source.
    """
    Type: DataLocationType = DataLocationType.ObjectStorage
    """
    The type of location where the data resides, which can either be an object inside an object storage system (i.e. Minio), a SQL location
    like a table or a view, a data stream (i.e. Kafka, currently unsupported), or a web location (currently unsupported)
    """
    ConnectionName: str = ''
    """
    In the case of the type of location being a database, ConnectionName specifies the name of the Connection resource
    that exists in the same tenant as the resource specifying the DataLocation. Modela will attempt to connect
    to the database using the credentials specified in the Connection, and will execute the query specified by the SQL field
    """
    BucketName: str = ''
    """
    In the case of the location type being an object storage system, BucketName is the name of the VirtualBucket resource
    that exists in the same tenant as the resource specifying the DataLocation. Modela will connect to the external
    object storage system, and will access the file from the path specified by the Path field
    """
    Path: str = ''
    """
    The path to a flat-file inside an object storage system. When using the Modela API to upload files (through the
    FileService API), Modela will upload the data to a predetermined path based on the Tenant, DataProduct,
    DataProductVersion, and resource type of the resource in relation to the file being uploaded.
    The path does not need to adhere to this format; you can still pass the path of a file inside a bucket not managed by Modela
    """
    Table: str = ''
    """ The name of a table inside a database, if applicable """
    Database: str = ''
    """ The name of a database inside the database system specified by the ConnectionName field """
    Sql: str = ''
    """ The SQL statement which will be executed to query data from the table specified by Table """
    Topic: str = ''
    """ The name of the streaming topic (currently unsupported) """


@datamodel(proto=data_pb.SampleSpec)
class SampleSettings(Configuration):
    """ SampleSpec specifies how the contents of a dataset should be sampled """
    Enabled: bool = False
    """ Indicates if sampling is enabled """
    Type: SamplingType = SamplingType.Random
    """ The type of sampling (random sampling, by default) """
    Rows: int = 500
    """ The number of rows to sample (by default, 500) """
    Percent: int = 100
    """ The percentage of rows to sample """
    Filter: str = ''
    """ The filter formula, valid only if the sample type is a filter """
    Column: str = ''
    """ The name of the column to be used for stratified sampling """


@datamodel(proto=data_pb.GovernanceSpec)
class GovernanceSpec(Configuration):
    """ GovernanceSpec describes the governance requirements for models produced under a DataProduct """
    Enabled: bool = False
    """ Indicates if governance is enabled """
    Country: str = ''
    """ The country whose regulations are under consideration """
    ItReviewer: str = ''
    """ The account name of the IT reviewer """
    ComplianceReviewer: str = ''
    """ The account name of the compliance reviewer """
    BusinessReviewer: str = ''
    """ The account name of the business reviewer """


@datamodel(proto=catalog_pb.CompilerSpec)
class CompilerSettings(Configuration):
    """ Compiler spec is used when there is a specification for model compilation """
    Enable: bool = False
    """ Enable set the enable to """
    Compiler: CompilerType = CompilerType.Nothing
    """
    Set one or more targets
    Enable set the enable to
    """
    Targets: List[HardwareTarget] = field(default_factory=lambda : [])
    """ Set one or more targets for the compiler """


ColorType = Color
ImageLocationType = ImageLocation
DataLocationType = DataLocation


@datamodel(proto=catalog_pb.Stakeholder)
class Stakeholder(Configuration):
    """ Stakeholder specifies the User Role Classes of an individual Account """
    Account: str = ''
    """ The name of an Account """
    Roles: List[ObjectReference] = field(default_factory=lambda : [])
    """ The object references to UserRoleClass resources which describe the actions the Account may perform """


@datamodel(proto=catalog_pb.PermissionsSpec)
class Permissions(Configuration):
    """
    PermissionsSpec specifies the Accounts that have access to a DataProduct or Tenant namespace and what permissions
    they possess for resources under the namespace
    """
    Stakeholders: List[Stakeholder] = field(default_factory=lambda : [])

    @classmethod
    def create(cls, accounts: Dict[Union[Account, str], Union[UserRoleClass, str, List[UserRoleClass], List[str]]], tenant='default-tenant') ->PermissionsSpec:
        """
        Generate a permission specification based on a dictionary of Accounts and their User Role Classes
        :param accounts: The dictionary of accounts to generate a permission specification from
        :param tenant: The name of the tenant which the accounts are based under. This parameter is not required if
          any User Role Class or Account resource is passed as an object (and not as a string)
        """
        stakeholders = []
        for account, roles in accounts.items():
            roleList, outList = roles if type(roles) == list else [roles], []
            for role in roleList:
                if type(account) == Account:
                    tenant = account.namespace
                    account = account.name
                if type(role) == UserRoleClass:
                    tenant = role.namespace
                    role = role.name
                outList.append(ObjectReference(Namespace=tenant, Name=role))
            stakeholders.append(Stakeholder(Account=account, Roles=outList))
        for stakeholder in stakeholders:
            for role in stakeholder.Roles:
                role.Namespace = tenant
        return cls(Stakeholders=stakeholders)


DataProductPermissions = Permissions


@datamodel(proto=data_pb.DataProductSpec)
class DataProductSpec(Configuration):
    """ DataProductSpec defines the desired state of the DataProduct """
    Owner: str = 'no-one'
    """ The name of the Account which created the object, which exists in the same tenant as the object """
    TenantRef: ObjectReference = ObjectReference(Namespace='modela-system', Name='default-tenant')
    """ The reference to the Tenant which owns the DataProduct. Defaults to `default-tenant` """
    GitLocation: GitSettings = GitSettings()
    """ GitLocation is the default Git location where all child resources will be tracked as YAML """
    ImageLocation: ImageLocationType = ImageLocation()
    """ ImageLocation is the default Docker image repository where model images produced under the DataProduct will be stored """
    LabName: str = 'default-lab'
    """ The name of the Lab that will be used by default with all compute-requiring child resources """
    ServingSiteName: str = 'default-serving-site'
    """ The name of the Serving Site which will be used by default with all Predictor resources """
    Task: TaskType = TaskType.BinaryClassification
    """ Task denote the machine learning task of the product (classification/regression,etc.) """
    Description: str = ''
    """ User-provided description of the object """
    DataLocation: DataLocationType = DataLocationType()
    """
    The default location for all artifacts created under the DataProduct. All data-producing resources will
    use the VirtualBucket specified by the DataLocation by default
    """
    Notification: NotificationSettings = NotificationSettings()
    """ The default notification specification for all resources under the DataProduct """
    TrainingResources: Workload = Workload('general-large')
    """ The default resource allocation for model training and data workloads that takes place under the DataProduct """
    ServingResources: Workload = Workload('general-large')
    """ The default resource allocation for model serving workloads that takes place under the DataProduct """
    RetriesOnFailure: int = 3
    """ Specifies how many times Jobs created under the DataProduct namespace will retry after failure """
    OnCallAccountName: str = ''
    """ The name of the Account which should be responsible for events that occur under the DataProduct """
    Compilation: CompilerSettings = CompilerSettings()
    """ The default compilation specification for Study resources created under the DataProduct """
    ClearanceLevel: SecurityClearanceLevel = SecurityClearanceLevel.Unclassified
    """
    The clearance level required to access the DataProduct. Accounts which do not have a clearance level
    greater than or equal to ClearanceLevel will be denied access to the DataProduct namespace
    """
    Priority: PriorityLevel = PriorityLevel.Medium
    """ The default priority level assigned to Jobs created under the DataProduct namespace """
    Color: ColorType = ColorType.NoColor
    """ The color assigned to the product, for visual purposes only """
    Governance: GovernanceSpec = GovernanceSpec()
    """ The Governance requirements (not functional as of the current release) """
    Public: bool = False
    """ Indicates if the DataProduct is public and can be accessed without permissions """
    Permissions: DataProductPermissions = DataProductPermissions()
    """
    Permissions denotes the specification that determines which Accounts
    can access the DataProduct and what actions they can perform
    """


@datamodel(proto=data_pb.DataProductVersionSpec)
class DataProductVersionSpec(Configuration):
    """ DataProductVersionSpec defines the desired state of a DataProductVersion """
    ProductRef: ObjectReference = ObjectReference(Namespace='default-tenant', Name='iris-product')
    """
    ProductRef contains the object reference to the DataProduct
    resource which the DataProductVersion describes the version of
    """
    Description: str = ''
    """ User-provided description of the object """
    PrevVersionName: str = ''
    """ The name of the version which preceded the current version """
    Baseline: bool = False
    """ Indicates if the version is a baseline, and if so will cause Modela to garbage collect the resources from previous versions """
    Owner: str = 'no-one'
    """ The name of the Account which created the object, which exists in the same tenant as the object """


@datamodel(proto=data_pb.CsvFileSpec)
class CsvFileFormat(Configuration):
    """ CsvFileSpec specifies the format of a CSV (comma-separated values) file """
    ColumnDelimiter: Delimiter = Delimiter.Comma
    """ The character used to separate fields (by default, a comma) """
    RowDelimiter: Delimiter = Delimiter.CRLF
    """ The character used to signal the end of a row (by default, a newline \\n) """
    EscapeChar: EscapeCharacter = EscapeCharacter.DoubleQuote
    """ The character used to escape the delimiter """
    Quote: QuoteCharacter = QuoteCharacter.DoubleQuote
    """ The charcter used for quotes (by default, a double quote ") """
    CommentChars: str = '#'
    """ The comment character used to split comments off the end of lines (by default, a hashtag #) """
    Header: bool = True
    """ Indicates if a header is present in the file """
    SkipRows: int = 0
    """ The number of rows to skip from the top of the file """
    NullValues: str = ''
    """ NullValues is a sequence of values to replace with NA. """
    Encoding: FileEncoding = FileEncoding.Utf8
    """ The unicode encoding of the file (e.g. 'utf-8' for UTF-8 encoded text) """
    MaxRows: int = 0
    """ The maximum number of rows to read """
    Strict: bool = True
    """ Indicates if the read of the CSV file should fail if there are any errors """
    Compression: CompressionType = CompressionType.Uncompressed
    """ The compression type, if the file is compressed """
    HasIndexColumn: bool = False
    """ Indicates if the file contains an index column """
    IndexColumn: int = 0
    """ The position of the index column """


@datamodel(proto=data_pb.ExcelSheetArea)
class ExcelSheetArea(Configuration):
    """ ExcelSheetArea specifies the bounds of the data within an excel sheet """
    EntireSheet: bool = True
    """
    Indicates if the excel reader should read the entire sheet; if false, it will read only within the bounds
    specified by the `To` and `From` fields of the ExcelSheetArea
    """
    FromColumn: int = 1
    """ If reading part of the excel sheet, start with the column in this position """
    ToColumn: int = 1
    """ If reading part of the excel sheet, end with the column in this position """
    FromRow: int = 1
    """ If reading part of the excel sheet, start with the row in this position """
    ToRow: int = 1
    """ If reading part of the excel sheet, end with the row in this position """


@datamodel(proto=data_pb.ExcelNotebookSpec)
class ExcelNotebookFormat(Configuration):
    """ ExcelNotebookSpec specifies the format of an excel file """
    FirstSheetWithData: bool = False
    """ Indicates if the excel reader should use the first sheet that contains data """
    SheetName: str = ''
    """ The name of the sheet that exists in the excel file to read data from """
    SheetIndex: int = 0
    """ The index of the sheet in the excel file to read data from """
    ColumnNameRow: int = 1
    """ The position of the row that contains the column names (i.e. the header) """
    Data: ExcelSheetArea = ExcelSheetArea()
    """ The specification for the bounds of the data """


@datamodel(proto=data_pb.Column)
class Column(Configuration):
    """
    Column specifies the attribute of a single column in a dataset. The fields of the Column align with the
    JSON schema standard; you can view detailed documentation at https://json-schema.org/draft/2020-12/json-schema-validation.html
    """
    Name: str = ''
    """ The name of the column """
    Datatype: DataType = DataType.Categorical
    """ The data type of the feature (e.g. number, string, boolean, etc.) """
    Format: DataDomain = DataDomain.Unknown
    """ The data domain of the feature, which constrains the contents of the feature to a specific set of values """
    DisplayName: str = ''
    """ The display name of the column, which is used in reports and other visual elements. If omitted, it will use the raw name """
    Description: str = ''
    """ The user-specified description of the feature """
    Ignore: bool = False
    """ Indicates if the feature should be ignored when building models """
    Target: bool = False
    """ Indicates if the feature is the target feature of the model, and the feature which predictions will be made on """
    Nullable: bool = False
    """ Indicates if the column can contain null values """
    Pk: bool = False
    """ Denotes if the column specifies a primary key of a database table (i.e. a users ID) """
    Fk: bool = False
    """ Denotes if the column specifies a foreign key of another database table """
    MultipleOf: int = 0
    """ The integer value which the values of the column should be a multiple of """
    Maximum: int = 0
    """ The maximum value of values all values in the column """
    ExclusiveMinimum: bool = False
    """ The exclusive lower limit of all values in the column, which does not include the minimum value """
    ExclusiveMaximum: bool = False
    """ The exclusive upper limit of all values in the column, which does not include the maximum value """
    Minimum: int = 0
    """ The minimum value of values all values in the column """
    MaxLength: int = 0
    """ The maximum length of values in the column, if the column data type is a string """
    MinLength: int = 0
    """ The minimum length of values in the column, if the column data type is a string """
    Pattern: str = ''
    """ The regex pattern which values in the column must adhere to """
    Required: bool = False
    """ Required """
    Example: str = ''
    """ A user-specified example value """
    ExternalDocs: str = ''
    """ A link to user-specified external documentation """
    Enum: List[str] = field(default_factory=lambda : [])
    """ The collection of unique values for categorical features """
    Ordinal: bool = False
    """ Indicates if the feature is ordinal, in the case of categorical features """
    MaxItems: int = 0
    """ The maximum number of items if the column is a list of values """
    MinItems: int = 0
    """ The minimum number of items if the column is a list of values """
    UniqueItems: bool = False
    """ Enforce that all the items in the list are unique """
    TimeColumn: bool = False
    """
    Indicates if the column is used as the time axis in time series forecasting
    Default is false.
    """
    Pii: bool = False
    """ Indicates if the column contains personally identifiable information """
    Phi: bool = False
    """ Indicates if the column contains personal health information """
    PersonalData: bool = False
    """ Indicates if the column contains any personal data """
    Protected: bool = False
    """ Protected means that this feature is important for ethical AI / Fairness """
    DefaultValueNum: float = 0
    """ The default value for number types; used internally for synthetic data and validation """
    Log: bool = False
    """ Indicates if values from this column will be sampled on a logarithmic scale """
    Mu: float = 0
    """ Mu is the mean of the normal distribution """
    Sigma: float = 0
    """ Sigma is the standard deviation of the distribution """
    SkewThreshold: float = None
    """ The threshold skew for skew detection """
    DriftThreshold: float = None
    """ The threshold drift value for model drift detection. """
    Index: bool = True
    """ Indicates if the column is an index column """
    Fold: bool = False
    """ Indicates if the column holds fold values """
    Weight: bool = False
    """ If True than this is a weight column """
    Reserved: bool = False
    """ Indicates that the feature should always be used in training """
    Imputation: Imputation = Imputation.AutoImputer
    """ The recommended imputation method for the column """
    Scaling: Scaling = Scaling.Auto
    """ The recommended scaling method for the column """
    Generated: bool = False
    """ Indicates if the feature was automatically generated """
    Formula: str = ''
    """ The formula used to generate the column """
    Id: bool = False
    """ Indicates if the column is an ID column """
    Step: float = 1
    """ The step value if the column values are a sequence of numbers """


@datamodel(proto=data_pb.TimeSeriesSchema)
class TimeSeriesSchema(Configuration):
    Freq: Frequency = None
    Country: HolidayCountry = None
    """ The holiday which should be taken into account """


@datamodel(proto=data_pb.RecommendationSchema)
class RecommendationSchema(Configuration):
    UserIDColumn: str = 'user_id'
    ItemIDColumn: str = 'item_id'
    """ The name of the column that specifies item IDs """
    RatingColumn: str = 'rating'
    """ The name of the column that specifies ratings """


@datamodel(proto=data_pb.MultiDatasetValidation)
class MultiDatasetValidation(Configuration):
    """ MultiDatasetValidation specifies a validation rule between multiple datasets """
    Type: MultiDatasetValidationRule = None
    """ The type of validation rule """
    Datasets: List[str] = field(default_factory=lambda : [])
    """ The list of datasets that will be checked """
    Generated: bool = False
    """ Indicates if this validation rule was automatically generated by the system """


@datamodel(proto=data_pb.DatasetValidation)
class DatasetValidation(Configuration):
    """ DatasetValidation specifies a validation rule for the contents of an entire dataset """
    Type: DatasetValidationRule = None
    """ The type of validation rule """
    Value: float = 0
    Min: float = 0
    Max: float = 0
    ValueSet: List[str] = field(default_factory=lambda : [])
    StrictMin: bool = False
    StrictMax: bool = False
    Generated: bool = False
    """ Indicates if this validation rule was automatically generated by the system """


@datamodel(proto=data_pb.MultiColumnValidation)
class MultiColumnValidation(Configuration):
    """ MultiColumnValidation specifies a validation rule that encompasses multiple columns """
    Type: MultiColumnValidationRule = None
    """ The type of validation rule """
    Columns: List[str] = field(default_factory=lambda : [])
    """ The list of columns that will be checked """
    Value: float = 0
    Min: float = 0
    Max: float = 0
    ValueSet: List[str] = field(default_factory=lambda : [])
    StrictMin: bool = False
    StrictMax: bool = False
    Generated: bool = False
    """ Indicates if this validation rule was automatically generated by the system """


@datamodel(proto=data_pb.ColumnValidation)
class ColumnValidation(Configuration):
    """ ColumnValidation specifies a validation rule for a single column """
    Type: ColumnValidationRule = None
    """ The type of validation rule """
    Column: str = ''
    """ The name of the column to be validated """
    Value: float = 0
    Min: float = 0
    Max: float = 0
    ValueSet: List[str] = field(default_factory=lambda : [])
    StrictMin: bool = False
    StrictMax: bool = False
    Generated: bool = False
    """ Indicates if this validation rule was automatically generated by the system """


@datamodel(proto=data_pb.FileValidation)
class FileValidation(Configuration):
    Type: FileValidationRule = None
    BucketName: str = ''
    Column: str = ''
    Value: float = 0
    """ For validation that need a single value """
    Min: float = 0
    Max: float = 0
    ValueSet: List[str] = field(default_factory=lambda : [])
    StrictMin: bool = False
    StrictMax: bool = False
    Generated: bool = False
    """ Generated indicate weather this validation rule was automatically generated """


@datamodel(proto=data_pb.ValidationSpec)
class ValidationRules(Configuration):
    MultiDatasetValidations: List[MultiDatasetValidation] = field(default_factory=lambda : [])
    DatasetValidations: List[DatasetValidation] = field(default_factory=lambda : [])
    """ DatasetValidations contains validations for the whole dataset """
    MultiColumnValidations: List[MultiColumnValidation] = field(default_factory=lambda : [])
    """ MultiColumnValidations defines validations for multiple columns from the dataset """
    ColumnValidations: List[ColumnValidation] = field(default_factory=lambda : [])
    """ ColumnValidations defines assertions for columns from the dataset """
    FileValidations: List[FileValidation] = field(default_factory=lambda : [])
    """ FileValidations defines assertions for the contents of the data file """


MDTimeSeriesSchema = TimeSeriesSchema
MDRecommendationSchema = RecommendationSchema


@datamodel(proto=data_pb.Schema)
class Schema(Configuration):
    """ Schema defines the column-level format and validation rules for data associated with a DataSource """
    Columns: List[Column] = field(default_factory=lambda : [])
    """ The collection of columns and their attributes """
    TimeSeriesSchema: MDTimeSeriesSchema = None
    """ The time-series schema, which sets time-series specific parameters """
    RecommendationSchema: MDRecommendationSchema = None
    """ The recommendation schema, which is used for the recommendation ML task """
    Validation: ValidationRules = ValidationRules()
    """ The specification for validation rules which will be performed on new Datasets """


@datamodel(proto=data_pb.RelationshipSpec)
class ColumnRelationship(Configuration):
    """ RelationSpec defines a relationship between two DataSource objects """
    Type: str = None
    """ The name of the relationship """
    Column: str = None
    """ The name of the columns that holds the foreign key """
    Arity: RelationshipArity = None
    """ The relationship arity """
    RelatesTo: str = None
    """ The name of the other DataSource object """


@datamodel(proto=data_pb.CorrelationSpec)
class CorrelationSetting(Configuration):
    """ CorrelationSpec specifies how the correlations between features in a Dataset should be computed """
    Cutoff: float = 50
    """ The minimum value of a computed correlation to be stored as a result """
    Method: str = 'pearson'
    """ The method to be used when computing correlations """
    Top: int = 10
    """ The number of top correlations to be included in the correlation results """


DataSourceSchema = Schema


@datamodel(proto=data_pb.DataSourceSpec)
class DataSourceSpec(Configuration):
    """ DataSourceSpec defines the desired state of the DataSource """
    Schema: DataSourceSchema = DataSourceSchema()
    """ The schema which will be used during the ingestion process of any Dataset resources which specify the DataSource """
    Sample: SampleSettings = SampleSettings()
    """
    The specification for how incoming data should be sampled (i.e. how many rows should be used). Applicable
    primarily for very large datasets
    """
    Relationships: List[ColumnRelationship] = field(default_factory=lambda : [])
    """ List of relationships to other data sources """
    Owner: str = 'no-one'
    """ The name of the Account which created the object, which exists in the same tenant as the object """
    VersionName: str = 'v0.0.1'
    """
    The name of the DataProductVersion which describes the version of the resource
    that exists in the same DataProduct namespace as the resource
    """
    Description: str = ''
    """ User-provided description of the object """
    FileType: FlatFileType = FlatFileType.Csv
    """ The file type of incoming data which uses the DataSource (by default, a CSV file) """
    Task: TaskType = TaskType.BinaryClassification
    """
    The default task for Dataset resources created from the DataSource. If null, this will be determined from
    the default task of the DataProduct which owns the DataSource
    """
    Csvfile: CsvFileFormat = CsvFileFormat()
    """ The file format for CSV files, if applicable """
    ExcelNotebook: ExcelNotebookFormat = None
    """ The file format of excel files, if applicable """
    DatasetType: DatasetType = DatasetType.Tabular
    """ The type of dataset; currently, the only supported type is `tabular` """


@datamodel(proto=data_pb.DatasetSpec)
class DatasetSpec(Configuration):
    """ DatasetSpec defines the desired state of the Dataset """
    Origin: DataLocation = DataLocation()
    """
    Origin is the location of the data file or database query which holds the raw data of the Dataset. When the Dataset is
    created, the resource controller will retrieve the data from the location, validate it against its Data Source
    if applicable, and store it inside the `live` section of the Virtual Bucket resource specified by the location
    """
    LabRef: ObjectReference = ObjectReference('default-tenant', 'default-lab')
    """ The reference to the Lab under which Jobs created by the Dataset will be executed """
    Location: DataLocation = DataLocation()
    """
    Location is the final location of the data which was copied from the `Origin` location during the ingestion phase.
    This field is set by the Dataset resource controller and should not be changed by any end-users
    """
    Owner: str = 'no-one'
    """ The name of the Account which created the object, which exists in the same tenant as the object """
    VersionName: str = 'v0.0.1'
    """
    The name of the DataProductVersion which describes the version of the resource
    that exists in the same DataProduct namespace as the resource
    """
    DatasourceName: str = ''
    """
    The reference to the Data Source resource which exists in the same Data Product namespace as the object.
    The Data Source must represent the columns and the task type of the Dataset. The validation rules associated with
    the Data Source will be validated against the raw data of the Dataset once it is created
    """
    Description: str = ''
    """ User-provided description of the object """
    DisplayName: str = ''
    """ User-provided display name of the object """
    Reported: bool = True
    """ Indicates if a PDF report containing the Dataset's profile should be generated """
    Snapshotted: bool = False
    """
    Indicates if the resource controller has created a snapshot of the data in the case that it is being read
    directly from a database, and must be converted to a flat-file type such as a CSV as a result
    """
    Validate: bool = True
    """ Indicates if the Dataset should be checked against the validation rules of its Data Source """
    Labeled: bool = True
    """ Indicates if the data is labeled or not """
    Synthetic: bool = False
    """ Indicates if synthetic data should be generated (currently unimplemented) """
    SyntheticRows: int = 0
    """ If `Synthetic` is set to true, SyntheticRows indicates how many rows of synthetic data should be generated """
    Resources: Workload = None
    """ Resources specifies the resource requirements which the Dataset will request when creating Jobs to analyze the data """
    ActiveDeadlineSeconds: int = 600
    """ The deadline in seconds for all Jobs created by the Dataset """
    Type: DatasetType = DatasetType.Tabular
    """ The type of dataset which was uploaded. `tabular` is the only supported type as of the current release """
    Sample: SampleSettings = None
    """
    The specification for how the data should be sampled, if applicable. Sampling may improve dataset and model creation
    time in the case of very large datasets that are being rapidly prototyped and iterated on
    """
    Task: TaskType = None
    """ The machine learning task relevant to the Dataset. This field *must* be the same as the Data Source of the object """
    Notification: NotificationSettings = None
    """ The notification specification that determines which notifiers will receive Alerts generated by the object """
    Correlation: CorrelationSetting = None
    """
    The specification for how to find the correlations of the Dataset's features during the profiling phase.
    Based on the specification, the data plane will compute the correlation between each feature and will store the highest-scoring
    """
    Fast: bool = False
    """
    Indicates if the Dataset should be quickly processed.
    If enabled, the validation, profiling, and reporting phases will be skipped.
    """


@datamodel(proto=data_pb.ColumnStatistics)
class ColumnStatistics(Configuration):
    """ ColumnStatistics contains statistical parameters for a single feature from a dataset """
    Name: str = ''
    """ The name of the column """
    Datatype: DataType = None
    """ The data type of the column """
    Count: float = 0
    """ Amount of rows which contain a value for the feature """
    Distinct: int = 0
    """ Amount of unique values present in the column """
    Missing: int = 0
    """ Amount of missing values present in the column """
    PercentMissing: float = 0
    """ Percentage of missing values in the column """
    Mean: float = 0
    """ The mean of all values in the column, if the column data type is a number """
    Stddev: float = 0
    """ The standard deviation of the columns values """
    Variance: float = 0
    """ The variability of the columns values from the columns mean """
    Min: float = 0
    """ The minimum value of all values in the column """
    Max: float = 0
    """ The maximum value of all values in the column """
    Kurtosis: float = 0
    """ The computed kurtosis, which measures the peakedness of the distribution of values in the column """
    Skewness: float = 0
    """ The computed skewness, which measures the asymmetry of the distribution of values in the column """
    Sum: float = 0
    """ Skewness is the standard deviation value of the attribute """
    Mad: float = 0
    """ The sum of all values in the column """
    P25: float = 0
    """ The 25% point of all the values of the column in order """
    P50: float = 0
    """ The 50% point of all the values of the column in order, also known as the median """
    P75: float = 0
    """ The 75% point of all the values of the column in order """
    Iqr: float = 0
    """ The interquartile range of the columns values """
    Mode: str = ''
    """ The mode value of the column, also known as the most frequent value """
    Zeros: float = 0
    """ The number of zero values in the column """
    Invalid: int = 0
    """ The number of invalid values in the column """
    Importance: float = 0
    """ The feature importance of the column """
    Target: bool = False
    """ Indicates if the feature is the target attribute for a Study, as specified by the Dataset's DataSource """
    Ignore: bool = False
    """ Indicates if the column should be ignored, as specified by the Dataset's DataSource """
    Nullable: bool = False
    """ Indicates if the column may contain null values, as specified by the Dataset's DataSource """
    HighCardinality: bool = False
    """ Indicates if the column has high cardinality and should use the high cardinality encoder during feature engineering """
    HighCorrWithOtherFeatures: bool = False
    """ Indicates if the column has high correlation with another feature, and that it should be dropped """
    LowCorrWithTarget: bool = False
    """ Indicate that the feature has low correlation with the target feature, and that it should be dropped """
    HighMissingPct: bool = False
    """ Indicates if the column has a high percentage of missing values, and that it should be dropped """
    Skewed: bool = False
    """
    Marks that the column is skewed and would require a power transform.
    
    If skewness is less than -1 or greater than 1, the distribution is highly skewed.
    If skewness is between -1 and -0.5 or between 0.5 and 1, the distribution is moderately skewed.
    If skewness is between -0.5 and 0.5, the distribution is approximately symmetric
    """
    Id: bool = False
    """ Indicates if the column is an ID column, such as a primary key """
    Constant: bool = False
    Duplicate: bool = False
    """ Indicates if the column is a duplicate of another column """
    Reserved: bool = False
    """ Indicates if the column is reserved and must be a feature included in model training """
    Outliers: int = 0
    """ The amount of outliers detected in the columns values """
    Completeness: float = 0
    """ The ratio between non-null and null values in the column """
    DistinctValueCount: float = 0
    """ The ratio between unique values and non-unique values in the column """
    MostFreqValuesRatio: float = 0
    """ The ratio between most the most frequent value to the number of total values in the column """
    IndexOfPeculiarity: float = 0
    """ Used for text attributes """
    CorrToTarget: float = 0
    """ Correlation to the target feature """


@datamodel(proto=common_pb.ColumnProfile)
class ColumnProfile(Configuration):
    Name: str = ''
    Count: int = 0
    Type: str = 0
    Missing: int = 0
    PercentMissing: float = 0
    Distinct: int = 0
    Mean: float = 0
    Mode: str = ''
    Stddev: float = 0
    Variance: float = 0
    Min: float = 0
    Max: float = 0
    Kurtosis: float = 0
    Skewness: float = 0
    Sum: float = 0
    Mad: float = 0
    Zeros: float = 0
    P25: float = 0
    P50: float = 0
    P75: float = 0
    P100: float = 0
    Iqr: float = 0
    Cv: float = 0
    Top: int = 0
    Freq: int = 0
    Ignore: bool = False
    Target: bool = False
    Invalid: int = 0
    Importance: float = 0
    Nullable: bool = False
    HighCardinality: bool = False
    HighCorrWithOtherFeatures: bool = False
    LowCorrWithTarget: bool = False
    HighMissingPct: bool = False
    Skewed: bool = False
    Id: bool = False
    Constant: bool = False
    Duplicate: bool = False
    Reserved: bool = False
    Outliers: int = 0
    Completeness: float = 0
    DistinctValueCount: float = 0
    MostFreqValuesRatio: float = 0
    IndexOfPeculiarity: float = 0
    Values: List[str] = field(default_factory=lambda : [])
    CorrToTarget: float = 0


@datamodel(proto=common_pb.DatasetProfile)
class DatasetProfile(Configuration):
    Cols: int = 0
    Rows: int = 0
    Filesize: int = 0
    Imbalance: bool = False
    Plots: List[Plot] = field(default_factory=lambda : [])
    Columns: List[ColumnProfile] = field(default_factory=lambda : [])
    Hash: str = ''


@datamodel(proto=data_pb.Correlation)
class Correlation(Configuration):
    """ Correlation records the correlation between two features in a Dataset """
    Feature1: str = ''
    """ The first feature name """
    Feature2: str = ''
    """ The second feature name """
    Value: float = 0
    """ The correlation value """
    Method: str = ''
    """ How the value was calculated """


@datamodel(proto=data_pb.DatasetStatistics)
class DatasetStatistics(Configuration):
    """
    DatasetStatistics contains statistics about the Dataset's overall data, as well as every feature of the data. The
    data structure is populated with information during the `Profiling` phase of the parent Dataset.
    """
    Columns: List[ColumnStatistics] = field(default_factory=lambda : [])
    """ Columns contains the collection of statistics for each feature """
    Rows: int = 0
    """ Number of rows observed from the data """
    Cols: int = 0
    """ Number of columns observed from the data """
    FileSize: int = 0
    """ The file size of the data in bytes """
    CorrelationsWithTarget: List[Correlation] = field(default_factory=lambda : [])
    """ The top correlations between all features and the target feature """
    TopCorrelations: List[Correlation] = field(default_factory=lambda : [])
    """ The top correlations between features, computed per the CorrelationSpec of the parent Dataset """

    def column(self, name) ->ColumnStatistics:
        """ Get the column with the specified name from the statistics """
        search = [col for col in self.Columns if col.Name == name]
        if len(search) == 0:
            raise ValueError('Column statistics does not have a column named {0}'.format(name))
        return search[0]


@datamodel(proto=data_pb.DatasetCondition)
class DatasetCondition(Configuration):
    """ DatasetCondition describes the state of a dataset at a certain point """
    Type: data_common.DatasetCondition = data_common.DatasetCondition.Ready
    Status: ConditionStatus = ConditionStatus.ConditionUnknown
    """ Status of the condition, one of True, False, Unknown """
    LastTransitionTime: Time = None
    """ Last time the condition transitioned from one status to another. """
    Reason: str = ''
    """ The reason for the condition's last transition. """
    Message: str = ''
    """ A human readable message indicating details about the transition. """


@datamodel(proto=data_pb.DataValidationResult)
class DataValidationResult(Configuration):
    Type: str = ''
    Column: str = ''
    Error: str = ''
    Passed: bool = False


@datamodel(proto=data_pb.DatasetStatus)
class DatasetStatus(ImmutableConfiguration):
    """ DatasetStatus defines the observed state of a Dataset object """
    Statistics: DatasetStatistics = None
    """ Statistics for each column of the Dataset, which are generated during the profiling phase. """
    Phase: DatasetPhase = DatasetPhase.Pending
    """ The current phase of the Dataset progress """
    ReportName: str = ''
    """
    Reference to the report object that was generated for the dataset, which exists in the same Data Product namespace
    as the object
    """
    ReportUri: str = ''
    """ The location of report generated during the reporting phase. This field is intended for internal use """
    ProfileUri: str = ''
    """ The location of raw profile data. This field is intended for internal use """
    Imbalanced: bool = False
    """ Whether or not the data was detected as imbalanced """
    ObservedGeneration: int = 0
    """ ObservedGeneration is the last generation that was acted on """
    ValidationResults: List[DataValidationResult] = field(default_factory=lambda : [])
    """ List of validation results which are generated for every validation rule associated with the Dataset's Data Source """
    LastStudyTime: Time = None
    """ Last time the Dataset was used with a Study """
    FailureReason: StatusError = None
    """ In the case of failure, the Dataset resource controller will set this field with a failure reason """
    FailureMessage: str = ''
    """ In the case of failure, the Dataset resource controller will set this field with a failure message """
    Progress: int = 0
    """ The current progress of the Dataset, with a maximum of 100, that is associated with the current phase """
    Hash: str = ''
    """ Sha256 signature of the raw data. Intended for internal use """
    Logs: OutputLogs = OutputLogs()
    """ The log file specification that determines the location of all logs produced by the object """
    DerivedFromDataset: str = ''
    """ If the dataset is derived, the name of the Dataset that the object is derived from """
    LastUpdated: Time = None
    """ The last time the object was updated """
    StartTime: Time = None
    """ The time that the system started processing the Dataset, usually after the creation of the object """
    EndTime: Time = None
    """ The time that the Dataset finished processing, either due to completion or failure """
    Conditions: List[DatasetCondition] = field(default_factory=lambda : [])
