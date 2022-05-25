import io
import os
from typing import List

import boto3
import pandas as pd

from aqueduct_executor.operators.connectors.tabular import common, config, connector, extract, load


class S3Connector(connector.TabularConnector):
    def __init__(self, config: config.S3Config):
        # TODO ENG-369: Remove this once service acct is implemented for local clusters
        if "AWS_ACCESS_KEY_ID" in os.environ:
            # This is a local cluster, which uses the root AWS credentials.
            # Root credentials cannot be used to assume another role.
            self.s3 = boto3.resource("s3")
        else:
            sts_client = boto3.client("sts")
            assumed_role = sts_client.assume_role(
                RoleArn=config.role_arn,
                RoleSessionName="AssumeRoleSession1",
                ExternalId=config.external_id,
            )
            credentials = assumed_role["Credentials"]

            self.s3 = boto3.resource(
                "s3",
                aws_access_key_id=credentials["AccessKeyId"],
                aws_secret_access_key=credentials["SecretAccessKey"],
                aws_session_token=credentials["SessionToken"],
            )

        self.bucket = config.bucket

    def authenticate(self) -> None:
        pass

    def discover(self) -> List[str]:
        raise Exception("Discover is not supported for S3.")

    def extract(self, params: extract.S3Params) -> pd.DataFrame:
        response = self.s3.Object(self.bucket, params.filepath).get()
        data = response["Body"].read()
        buf = io.BytesIO(data)

        if params.format == common.S3FileFormat.CSV:
            return pd.read_csv(buf)
        elif params.format == common.S3FileFormat.JSON:
            return pd.read_json(buf)
        elif params.format == common.S3FileFormat.PARQUET:
            return pd.read_parquet(buf)

        raise Exception("Unknown S3 file format %s" % format)

    def load(self, params: load.S3Params, df: pd.DataFrame) -> None:
        buf = io.BytesIO()

        if params.format == common.S3FileFormat.CSV:
            df.to_csv(buf, index=False)
        elif params.format == common.S3FileFormat.JSON:
            # Index cannot be False for `to.json` for default orient
            # See: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_json.html
            df.to_json(buf)
        elif params.format == common.S3FileFormat.PARQUET:
            df.to_parquet(buf, index=False)
        else:
            raise Exception("Unknown S3 file format %s" % format)

        self.s3.Object(self.bucket, params.filepath).put(Body=buf.getvalue())
