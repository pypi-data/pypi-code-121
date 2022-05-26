"""
    Gets Snowflake connection based on account type specified in the config,
    under `accounts`. To add new account, add credentials to the parameter
    store and then add path under `accounts`.

    Default account is read only, srv-us-ops-analytics-read-only.

    Usage:
        from snowflake_connect import SnowflakeConnect
        obj = SnowflakeConnect()
        # obj = SnowflakeConnect(account_type='service_account')

        conn = obj.get_snowflake_connection()
        cur = conn.cursor()
        cursor_execute = cur.execute('select * from delivery_list.odl_us limit 10;')

        cursor_result_ls = cursor_execute.fetchall()
        col_names_ls = [x[0] for x in cur.description]
"""
import os
import io
import sys
import yaml
import snowflake.connector
from loguru import logger
from typing import Optional, Any
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from hellofresh_data.parameter_store import get_parameter_store_value

CONFIG_FILE = 'config.yml'


class SnowflakeConnect(object):
    def __init__(self, account_type: Optional[str] = 'read_only'):

        logger.bind(user='SnowflakeConnect')
        self.account_type = account_type

        __location__ = os.path.realpath(os.path.join(os.path.dirname(__file__)))  # noqa
        try:
            with open(os.path.join(__location__, CONFIG_FILE), 'r') as f:
                self.config = yaml.load(f, Loader=yaml.FullLoader)
        except Exception as err:
            logger.error('Failed to load')
            logger.error(err)
            sys.exit(1)

        self.assert_account_type_is_allowed_type()
        self.set_connection_variables()
        logger.info(f'Connecting as {self.account_type} User')

        self.set_snowflake_sa_private_key()

    def assert_account_type_is_allowed_type(self):
        """
            Only accounts under `accounts` block in config can be passed in
            when instantiating an object. To use a new account, add it to the
            config.
        """
        allowed_type_ls = [k for k, v in self.config['snowflake']['accounts'].items()]  # noqa
        try:
            assert (self.account_type in allowed_type_ls) is True
        except AssertionError:
            logger.error(f'Account type, {self.account_type}, needs to be configured in config')  # noqa
            logger.error(f'Currently allowed accounts: {allowed_type_ls}')
            raise

    def set_connection_variables(self):
        snowflake_config = self.config['snowflake']
        self.account = get_parameter_store_value(snowflake_config['account'])
        self.warehouse = get_parameter_store_value(snowflake_config['warehouse'])  # noqa
        self.database = get_parameter_store_value(snowflake_config['database'])

        user_account_config = snowflake_config['accounts'][self.account_type]
        self.user = get_parameter_store_value(user_account_config['user'])
        self.role = get_parameter_store_value(user_account_config['role'])
        self.private_key_str = get_parameter_store_value(user_account_config['private_key'])  # noqa

    def set_snowflake_sa_private_key(self):
        """
            Sets private key as bytes object. This will be used to establish a
            connection to snowflake.
        """
        logger.info('Getting private key for Snowflake connection...')

        try:
            sa_private_key_io = io.StringIO(self.private_key_str)
            sa_private_str = sa_private_key_io.read()
            sa_private_byte = sa_private_str.encode()

            private_key_serialized = \
                serialization.load_pem_private_key(sa_private_byte,
                                                   password=None,
                                                   backend=default_backend()
                                                   )
            self.private_key_encrypted = private_key_serialized.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
                )
            logger.info('Retrieved private key successfully!')
        except Exception as err:
            logger.error('Failed to get private key')
            logger.error(err)
            sys.exit(1)

    def get_snowflake_connection(self) -> Any:
        logger.info('Getting connection for Snowflake...')
        try:
            conn = snowflake.connector.connect(
                user=self.user,
                account=self.account,
                private_key=self.private_key_encrypted,
                warehouse=self.warehouse,
                database=self.database,
                role=self.role
                )
            logger.info('Retrieved connection successfully!')
        except Exception as err:
            logger.error('Failed to build connection')
            logger.error(err)
            sys.exit(1)

        return conn

