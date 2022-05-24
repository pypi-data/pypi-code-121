import configparser
import os
from urllib.parse import urlparse

from . import CoreService_pb2 as pb
from .user_credentials import (
    AWSCredentials,
    AzureKeyCredentials,
    AzurePrincipalCredentials,
    AzureSasCredentials,
    DriverlessAICredentials,
    PostgresCredentials,
    SnowflakeCredentials,
    TeradataCredentials,
)
from .utils import Utils


class CredentialsHelper:
    @staticmethod
    def set_credentials(request, raw_data_location, credentials):
        source = getattr(raw_data_location, raw_data_location.WhichOneof("source"))
        if isinstance(source, pb.CSVFileSpec):
            url_path = raw_data_location.csv.path
            CredentialsHelper.get_credentials_based_on_cloud(
                request, url_path, credentials
            )
        elif isinstance(source, pb.CSVFolderSpec):
            url_path = raw_data_location.csv_folder.root_folder
            CredentialsHelper.get_credentials_based_on_cloud(
                request, url_path, credentials
            )
        elif isinstance(source, pb.JSONFolderSpec):
            url_path = raw_data_location.json_folder.root_folder
            CredentialsHelper.get_credentials_based_on_cloud(
                request, url_path, credentials
            )
        elif isinstance(source, pb.JSONFileSpec):
            url_path = raw_data_location.json.path
            CredentialsHelper.get_credentials_based_on_cloud(
                request, url_path, credentials
            )
        elif isinstance(source, pb.ParquetFileSpec):
            url_path = raw_data_location.parquet.path
            CredentialsHelper.get_credentials_based_on_cloud(
                request, url_path, credentials
            )
        elif isinstance(source, pb.ParquetFolderSpec):
            url_path = raw_data_location.parquet_folder.root_folder
            CredentialsHelper.get_credentials_based_on_cloud(
                request, url_path, credentials
            )
        elif isinstance(source, pb.DeltaTableSpec):
            url_path = raw_data_location.delta_table.path
            CredentialsHelper.get_credentials_based_on_cloud(
                request, url_path, credentials
            )
        elif isinstance(source, pb.SnowflakeTableSpec):
            CredentialsHelper.set_snowflake_credentials(request, credentials)
        elif isinstance(source, pb.JDBCTableSpec):
            CredentialsHelper.set_jdbc_credentials(
                request, source.connection_url, credentials
            )
        elif isinstance(source, pb.DriverlessAIMOJOSpec):
            CredentialsHelper.set_driverless_ai_license(request, credentials)
        elif isinstance(source, pb.SparkPipelineSpec):
            pass
        elif isinstance(source, pb.JoinedFeatureSetsSpec):
            pass
        elif isinstance(source, pb.TempParquetFileSpec):
            pass
        else:
            raise Exception("Unsupported external data spec!")

    @staticmethod
    def get_credentials_based_on_cloud(request, url_path, credentials):
        if url_path.lower().startswith("s3"):
            CredentialsHelper.set_aws_credentials(request, credentials)
        elif url_path.lower().startswith("wasb") or url_path.lower().startswith("abfs"):
            CredentialsHelper.set_azure_credentials(request, url_path, credentials)
        else:
            raise Exception("Unsupported external data spec!")

    @staticmethod
    def set_azure_credentials(request, url_path, credentials):
        sas_container = urlparse(url_path).netloc.split("@")[0]
        if credentials is None:
            account_name = Utils.read_env("AZURE_ACCOUNT_NAME", "Azure")
            account_key = os.getenv("AZURE_ACCOUNT_KEY")
            sas_token = os.getenv("AZURE_SAS_TOKEN")
            sp_client_id = os.getenv("AZURE_SP_CLIENT_ID")
            sp_tenant_id = os.getenv("AZURE_SP_TENANT_ID")
            sp_secret = os.getenv("AZURE_SP_SECRET")
            if account_key:
                credentials = AzureKeyCredentials(account_name, account_key)
            elif sas_token:
                credentials = AzureSasCredentials(account_name, sas_token)
            elif sp_client_id and sp_tenant_id and sp_secret:
                credentials = AzurePrincipalCredentials(
                    account_name, sp_client_id, sp_tenant_id, sp_secret
                )
            else:
                raise Exception(
                    "Either Azure Key, SAS token or Service Credentials environment variable must be specified to read from Azure data source!"
                )
        elif not isinstance(
            credentials,
            (AzureKeyCredentials, AzureSasCredentials, AzurePrincipalCredentials),
        ):
            raise Exception(
                "Credentials are not of type AzureKeyCredentials, AzureSasCredentials or AzurePrincipalCredentials!"
            )

        request.cred.azure.account_name = credentials.account_name
        if isinstance(credentials, AzureKeyCredentials):
            request.cred.azure.account_key = credentials.account_key
        if isinstance(credentials, AzureSasCredentials):
            request.cred.azure.sas_token = credentials.sas_token
            request.cred.azure.sas_container = sas_container
        if isinstance(credentials, AzurePrincipalCredentials):
            request.cred.azure.sp_client_id = credentials.client_id
            request.cred.azure.sp_tenant_id = credentials.tenant_id
            request.cred.azure.sp_secret = credentials.secret

    @staticmethod
    def set_aws_credentials(request, credentials):
        if credentials is None:
            if os.environ.get("AWS_ACCESS_KEY"):
                access_key = Utils.read_env("AWS_ACCESS_KEY", "S3")
            else:
                access_key = None
            if os.environ.get("AWS_SECRET_KEY"):
                secret_key = Utils.read_env("AWS_SECRET_KEY", "S3")
            else:
                secret_key = None
            if os.environ.get("AWS_REGION"):
                region = Utils.read_env("AWS_REGION", "S3")
            else:
                region = None
            if os.environ.get("AWS_ROLE_ARN"):
                role_arn = Utils.read_env("AWS_ROLE_ARN", "S3")
            else:
                role_arn = None

            if all(keys is not None for keys in [access_key, secret_key, region]):
                credentials = AWSCredentials(access_key, secret_key, region, role_arn)
            elif os.path.isfile(
                os.path.join(os.path.expanduser("~"), ".aws/credentials")
            ):
                config = configparser.RawConfigParser()
                config.read(os.path.join(os.path.expanduser("~"), ".aws/credentials"))
                try:
                    profile = Utils.read_env("AWS_PROFILE", "S3")
                except Exception:
                    profile = "default"
                    pass
                aws_key = config.get(profile, "aws_access_key_id")
                aws_secret = config.get(profile, "aws_secret_access_key")
                config.read(os.path.join(os.path.expanduser("~"), ".aws/config"))
                aws_region = config.get("default", "region")
                credentials = AWSCredentials(
                    access_key=aws_key, secret_key=aws_secret, region=aws_region
                )
            else:
                print(
                    "Credentials are not provided for AWS. Access only to public data."
                )
                request.cred.aws.access_token = "PUBLIC_ONLY"
                request.cred.aws.secret_token = "PUBLIC_ONLY"
                return
        if not isinstance(credentials, AWSCredentials):
            raise Exception("Credentials are not of type AWSCredentials!")
        request.cred.aws.access_token = credentials.access_token
        request.cred.aws.secret_token = credentials.secret_token
        request.cred.aws.region = credentials.region
        if credentials.role_arn:
            request.cred.aws.role_arn = credentials.role_arn

    @staticmethod
    def set_snowflake_credentials(request, credentials):
        if credentials is None:
            credentials = SnowflakeCredentials(
                user=Utils.read_env("SNOWFLAKE_USER", "Snowflake"),
                password=Utils.read_env("SNOWFLAKE_PASSWORD", "Snowflake"),
            )
        elif not isinstance(credentials, SnowflakeCredentials):
            raise Exception("Credentials are not of type snowflakeCredentials!")
        request.cred.snowflake.user = credentials.user
        request.cred.snowflake.password = credentials.password

    @staticmethod
    def set_jdbc_credentials(request, connection_url, credentials):
        database_type = connection_url.split(":")[1]
        if credentials is None:
            if database_type == "teradata":
                credentials = TeradataCredentials(
                    user=Utils.read_env("JDBC_TERADATA_USER", "JDBC Teradata"),
                    password=Utils.read_env("JDBC_TERADATA_PASSWORD", "JDBC Teradata"),
                )
            elif database_type == "postgres":
                credentials = PostgresCredentials(
                    user=Utils.read_env("JDBC_POSTGRES_USER", "JDBC Postgres"),
                    password=Utils.read_env("JDBC_TERADATA_PASSWORD", "JDBC Postgres"),
                )
            else:
                raise Exception(
                    "Invalid database type, supported types are: teradata, postgres"
                )
        elif not isinstance(credentials, (TeradataCredentials, PostgresCredentials)):
            raise Exception(
                "Credentials are not of type TeradataCredentials or PostgresCredentials!"
            )
        request.cred.jdbc_database.user = credentials.user
        request.cred.jdbc_database.password = credentials.password

    @staticmethod
    def set_driverless_ai_license(request, credentials):
        if credentials is None:
            credentials = DriverlessAICredentials(
                license_key=Utils.read_env(
                    "DRIVERLESS_AI_LICENSE_KEY", "Driverless AI MOJO"
                )
            )
        elif not isinstance(credentials, DriverlessAICredentials):
            raise Exception("Credentials are not of type DriverlessAICredentials!")
        request.cred.driverless_ai_license = credentials.license_key
