import json
from dataclasses import dataclass

from bigeye_sdk.log import get_logger

# create logger
from bigeye_aws.functions.aws import get_secret

log = get_logger(__file__)


@dataclass
class SnowflakeCredential:
    username: str
    password: str
    account_identifier: str

    def get_sqlalchemy_conn_str(self, database: str = None) -> str:
        url = f'snowflake://{self.username}:{self.password}@{self.account_identifier}/{database}'
        if database:
            url = f'{url}/{database}'
        return url

    @classmethod
    def load_snowflake_config_file(cls, snowflake_cred_file: str):
        log.info(f'Loading Snowflake Configuration: {snowflake_cred_file}')
        with open(snowflake_cred_file) as json_file:
            sc = SnowflakeCredential(**json.load(json_file))
            if sc is None:
                raise Exception('Could not load Snowflake Credential File.')
            return sc

    @classmethod
    def load_snowflake_config_secret(cls, region_name: str, secret_name: str):
        log.info(f'Loading Snowflake Credential Secret.')
        return SnowflakeCredential(**get_secret(region_name=region_name,
                                                secret_name=secret_name))
