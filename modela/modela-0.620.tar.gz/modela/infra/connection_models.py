from dataclasses import dataclass, field
from typing import List

from modela.Configuration import Configuration
from modela.common import StatusError, Time, ConditionStatus, SecretReference, ObjectReference
from modela.infra.common import ProviderName, ConnectionConditionType, ConnectionCategory
dataclass()


@dataclass
class AmazonAthenaConnection(Configuration):
    HostName: str = ""
    Username: str = ""
    Password: str = ""
    Region: str = ""
    Url: str = ""


@dataclass
class GcpBigQueryConnection(Configuration):
    Host: str = ""
    Port: int = 9042
    Username: str = ""
    Password: str = ""
    ProjectID: str = ""
    OauthType: str = ""
    ServiceAccountKeyPath: str = ""
    Url: str = ""


@dataclass
class ApacheCassandraConnection(Configuration):
    Host: str = ""
    Port: int = 9042
    Keyspace: str = ""
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class ApacheDruidConnection(Configuration):
    Host: str = ""
    Port: int = 9042
    Keyspace: str = ""
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class ApacheDrillConnection(Configuration):
    Host: str = ""
    Port: int = 9042
    Keyspace: str = ""
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class AzureSQLDatabaseConnection(Configuration):
    Host: str = ""
    Port: int = 1433
    Username: str = ""
    Password: str = ""
    Database: str = ""
    Url: str = ""


@dataclass
class MongoDbConnection(Configuration):
    Host: str = ""
    Port: int = 27017
    Database: str = ""
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class MySqlConnection(Configuration):
    Host: str = ""
    Port: int = 3306
    Database: str = ""
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class OdbcConnection(Configuration):
    ConntectionString: str = ""


@dataclass
class OracleConnection(Configuration):
    Host: str = ""
    Port: int = 1521
    Sid: str = "XE"
    Driver: str = "thin"
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class PostgresSQLConnection(Configuration):
    Host: str = ""
    Port: int = 5432
    Database: str = ""
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class PrestoConnection(Configuration):
    Host: str = ""
    Port: int = 8080
    Catalog: str = ""
    Schema: str = ""
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class AmazonRedShiftConnection(Configuration):
    Host: str = ""
    Port: int = 5439
    Database: str = ""
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class ApacheHiveConnection(Configuration):
    Host: str = ""
    Port: int = 10000
    Schema: str = ""
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class SnowflakeConnection(Configuration):
    Host: str = ""
    Port: int = 443
    Username: str = ""
    Password: str = ""
    Database: str = ""
    Schema: str = ""
    Warehouse: str = ""
    Url: str = ""


@dataclass
class SybaseConnection(Configuration):
    Host: str = ""
    Port: int = 5000
    Database: str = ""
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class VerticaConnection(Configuration):
    Host: str = ""
    Port: int = 5433
    Database: str = ""
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class CockroachDBConnection(Configuration):
    Host: str = ""
    Port: int = 5432
    Database: str = ""
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class ElasticSearchConnection(Configuration):
    Host: str = ""
    Port: int = 5432
    Prefix: str = ""
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class InformixConnection(Configuration):
    Host: str = ""
    Port: int = 1526
    Database: str = ""
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class SAPHanaConnection(Configuration):
    Host: str = ""
    Port: int = 1526
    Database: str = ""
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class TeradataConnection(Configuration):
    Host: str = ""
    Port: int = 6666
    Database: str = ""
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class GcpSpannerConnection(Configuration):
    Project: str = ""
    Instance: str = ""
    Username: str = ""
    Password: str = ""
    Database: str = ""
    Url: str = ""


@dataclass
class ApacheSparkConnection(Configuration):
    Host: str = ""
    Port: int = 5433
    Schema: str = ""
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class MSSqlServerConnection(Configuration):
    Host: str = ""
    Port: int = 1433
    Database: str = ""
    Instance: str = ""
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class ClickHouseConnection(Configuration):
    Host: str = ""
    Port: int = 8123
    Database: str = ""
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class GreenPlumConnection(Configuration):
    Host: str = ""
    Port: int = 5432
    Database: str = ""
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class CouchbaseConnection(Configuration):
    Host: str = ""
    Port: int = 8123
    Database: str = ""
    Username: str = ""
    Password: str = ""
    DefaultBucket: str = ""
    Url: str = ""


@dataclass
class ExasolConnection(Configuration):
    Host: str = ""
    Port: int = 0
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class SingleStoreConnection(Configuration):
    Host: str = ""
    Port: int = 0
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class Neo4JConnection(Configuration):
    Host: str = ""
    Port: int = 0
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class KafkaConnection(Configuration):
    Host: str = ""
    Port: int = 0
    Channel: str = ""
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class SqliteConnection(Configuration):
    FileName: str = "general"


@dataclass
class AwsS3Connection(Configuration):
    DefaultRegion: str = ""
    AccessKey: str = ""
    SecretKey: str = ""


@dataclass
class AzureStorageConnection(Configuration):
    StorageAccount: str = ""
    AccessKey: str = ""


@dataclass
class GcpStorageConnection(Configuration):
    KeyFile: str = ""
    Project: str = ""


@dataclass
class DigitalOceanConnection(Configuration):
    Token: str = ""
    AccessKey: str = ""
    SecretKey: str = ""
    DefaultRegion: str = ""
    Host: str = ""


@dataclass
class MinioConnection(Configuration):
    AccessKey: str = ""
    SecretKey: str = ""
    Host: str = ""


@dataclass
class ImageRegistryConnection(Configuration):
    Host: str = ""
    Username: str = ""
    Password: str = ""


@dataclass
class SlackConnection(Configuration):
    WebhookUrl: str = ""
    Channel: str = ""
    UserName: str = ""
    Token: str = ""


@dataclass
class SmtpConnection(Configuration):
    Host: str = ""
    Port: int = 25
    UserName: str = ""
    Password: str = ""


@dataclass
class GithubConnection(Configuration):
    Token: str = ""
    UserName: str = ""
    Ssh: str = ""


@dataclass
class BitbucketConnection(Configuration):
    Token: str = ""
    UserName: str = ""
    Ssh: str = ""


@dataclass
class AliCloudConnection(Configuration):
    AccessKey: str = ""
    SecretKey: str = ""
    Region: str = ""
    Host: str = ""


@dataclass
class GitlabConnection(Configuration):
    Token: str = ""
    Ssh: str = ""


@dataclass
class HetznerConnection(Configuration):
    Token: str = ""
    Ssh: str = ""


@dataclass
class OpenstackConnection(Configuration):
    UserName: str = ""
    TenantName: str = ""
    Password: str = ""
    AuthUrl: str = ""
    Region: str = ""


@dataclass
class OvhConnection(Configuration):
    Endpoint: str = ""
    Application: str = ""
    Secret: str = ""
    Consumerkey: str = ""


@dataclass
class LinodeConnection(Configuration):
    Token: str = ""


@dataclass
class MSTeamConnection(Configuration):
    Webhook: str = ""


@dataclass
class MattermostConnection(Configuration):
    Url: str = ""
    Channel: str = ""
    Username: str = ""


@dataclass
class HipchatConnection(Configuration):
    Url: str = ""
    Token: str = ""
    Room: str = ""


@dataclass
class VictorOpConnection(Configuration):
    ApiID: str = ""
    ApiKey: str = ""
    Url: str = ""


@dataclass
class PagerDutyConnection(Configuration):
    ApiID: str = ""
    ApiKey: str = ""
    Url: str = ""


@dataclass
class PushoverConnection(Configuration):
    ApiID: str = ""
    ApiKey: str = ""
    Url: str = ""


@dataclass
class OpsgenieConnection(Configuration):
    ApiID: str = ""
    ApiKey: str = ""
    Url: str = ""


@dataclass
class WebhookConnection(Configuration):
    Url: str = ""


@dataclass
class GoogleSheetsConnection(Configuration):
    Scopes: str = ""
    Id: str = ""
    DataToPull: str = ""


@dataclass
class FTPConnection(Configuration):
    Host: str = ""
    Port: int = 9042
    Keyspace: str = ""
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class SFTPConnection(Configuration):
    Host: str = ""
    Port: int = 9042
    Keyspace: str = ""
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class DropboxConnection(Configuration):
    Token: str = ""


@dataclass
class BoxConnection(Configuration):
    Token: str = ""


@dataclass
class FacebookConnection(Configuration):
    Token: str = ""


@dataclass
class TwitterConnection(Configuration):
    Token: str = ""


@dataclass
class DB2Connection(Configuration):
    Host: str = ""
    Port: int = 9042
    Keyspace: str = ""
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class DremioConnection(Configuration):
    Host: str = ""
    Port: int = 9042
    Keyspace: str = ""
    Username: str = ""
    Password: str = ""
    Url: str = ""


@dataclass
class FtpConnection(Configuration):
    Host: str = ""
    Port: int = 21
    Username: str = ""
    Password: str = ""


@dataclass
class SFtpConnection(Configuration):
    Host: str = ""
    Port: int = 21
    Username: str = ""
    Password: str = ""


@dataclass
class RabbitMQConnection(Configuration):
    Host: str = ""
    Port: int = 21
    Username: str = ""
    Password: str = ""


@dataclass
class Connection(Configuration):
    TenantRef: ObjectReference = None
    Category: ConnectionCategory = ConnectionCategory.General
    Provider: ProviderName = ProviderName.UnknownProvider
    SecretRef: SecretReference = None
    Athena: AmazonAthenaConnection = None
    Drill: ApacheDrillConnection = None
    Druid: ApacheDruidConnection = None
    Hive: ApacheHiveConnection = None
    Redshift: AmazonRedShiftConnection = None
    Dermio: DremioConnection = None
    Db2: DB2Connection = None
    Bigquery: GcpBigQueryConnection = None
    Cassandra: ApacheCassandraConnection = None
    Azuresqldatabase: AzureSQLDatabaseConnection = None
    Mongodb: MongoDbConnection = None
    Mysql: MySqlConnection = None
    Odbc: OdbcConnection = None
    Oracle: OracleConnection = None
    Postgres: PostgresSQLConnection = None
    Presto: PrestoConnection = None
    Snowflake: SnowflakeConnection = None
    Sybase: SybaseConnection = None
    Vertica: VerticaConnection = None
    Cockroachdb: CockroachDBConnection = None
    Elasticsearch: ElasticSearchConnection = None
    Informix: InformixConnection = None
    Hana: SAPHanaConnection = None
    Teradata: TeradataConnection = None
    Spanner: GcpSpannerConnection = None
    Spark: ApacheSparkConnection = None
    Mssqlserver: MSSqlServerConnection = None
    Clickhouse: ClickHouseConnection = None
    Greenplum: GreenPlumConnection = None
    Couchbase: CouchbaseConnection = None
    Exasol: ExasolConnection = None
    Sqlite: SqliteConnection = None
    Singlestore: SingleStoreConnection = None
    Gsheets: GoogleSheetsConnection = None
    Azurestorage: AzureStorageConnection = None
    Alicloud: AliCloudConnection = None
    Digitalocean: DigitalOceanConnection = None
    Hetzner: HetznerConnection = None
    Gcpstorage: GcpStorageConnection = None
    Linode: LinodeConnection = None
    Minio: MinioConnection = None
    Openstack: OpenstackConnection = None
    Ovh: OvhConnection = None
    Aws: AwsS3Connection = None
    Smtp: SmtpConnection = None
    Ftp: FtpConnection = None
    Sftp: SFtpConnection = None
    Dropbox: DropboxConnection = None
    Box: BoxConnection = None
    ImageRegistry: ImageRegistryConnection = None
    Github: GithubConnection = None
    Gitlab: GitlabConnection = None
    Bitbucket: BitbucketConnection = None
    Slack: SlackConnection = None
    Msteam: MSTeamConnection = None
    MatterMost: MattermostConnection = None
    Hipchat: HipchatConnection = None
    Victorop: VictorOpConnection = None
    Pagerduty: PagerDutyConnection = None
    Pushover: PushoverConnection = None
    Opsgenie: OpsgenieConnection = None
    Webhook: WebhookConnection = None
    Facebook: FacebookConnection = None
    Twitter: TwitterConnection = None
    Rabbitmq: RabbitMQConnection = None
    Kafka: KafkaConnection = None
    Neo4j: Neo4JConnection = None
    Owner: str = "no-one"

@dataclass
class ConnectionCondition(Configuration):
    Type: ConnectionConditionType = ConnectionConditionType.ConnectionReady
    Status: ConditionStatus = ConditionStatus.ConditionUnknown
    LastTransitionTime: Time = None
    Reason: str = ""
    Message: str = ""


@dataclass
class ConnectionStatus(Configuration):
    ObservedGeneration: int = 0
    LastUpdated: Time = None
    FailureReason: StatusError = None
    FailureMessage: str = ""
    Conditions: List[ConnectionCondition] = field(default_factory=lambda: [])

