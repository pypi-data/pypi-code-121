"""
    Reader class for DWH

    Default connection is using sca service account's credentials
"""
import sys
import time
import os
import yaml
import pandas as pd
import jaydebeapi
from loguru import logger
from impala.dbapi import connect
from hellofresh_data.parameter_store import get_parameter_store_value

MAX_GET_CONNECTION_ATTEMPTS = 3


class ImpalaReader():

    def __init__(self, user=None, password=None, platform='CDH'):
        self.__user_var = user
        self.__password_var = password
        self.platform_vars = 'dwh' if platform == 'CDH' else 'dwh_cdp'
        self._logger = logger.bind(user='ImpalaReader')
        self.instantiate_config()
        self.instantiate_impala_creds()
        if platform == 'CDH':
            self.__get_connection()
        elif platform == 'CDP':
            self.__get_connection_cdp()
        else:
            self._logger.error('Invalid platform, only CDH/CDP allowed')
            sys.exit(1)

    def __del__(self):
        try:
            self.__impala_conn.close()
        except Exception:
            self.__impala_conn = None

    def instantiate_config(self):
        """
            Instantiate config to expose variables
        """
        self.__location__ = \
            os.path.realpath(
                os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.config = \
            yaml.safe_load(open(os.path.join(self.__location__, 'config.yml')))

    def instantiate_impala_creds(self):
        """
            Set DWH variables

            For self.__user and self.__password either use passed in variables
            or assign those of a sca service account
        """
        __user = self.config['impala_reader'][self.platform_vars]['user']
        __password = self.config['impala_reader'][self.platform_vars]['password']

        self.__user = self.__user_var or get_parameter_store_value(__user)
        self.__password = \
            self.__password_var or get_parameter_store_value(__password)

        self._logger.info(f'Using creds for user: {self.__user}')

        self.host = self.config['impala_reader'][self.platform_vars]['host']
        self.port = self.config['impala_reader'][self.platform_vars]['port']
        self.auth_mechanism = self.config['impala_reader'][self.platform_vars]['auth_mechanism']
        self.use_ssl = self.config['impala_reader'][self.platform_vars]['use_ssl']

    def __get_connection(self):
        """
            Try to establish connection to DWH using set variables
        """

        max_connect_attempts = MAX_GET_CONNECTION_ATTEMPTS
        while max_connect_attempts > 0:
            try:
                self._logger.info(f'Attempting to connect to DWH, '
                                  f'{max_connect_attempts} tries left')
                self.__impala_conn = connect(host=self.host,
                                             port=self.port,
                                             user=self.__user,
                                             password=self.__password,
                                             auth_mechanism=self.auth_mechanism,
                                             use_ssl=self.use_ssl)
                self._logger.info(f'Connected to DWH')
                break
            except Exception as err:
                max_connect_attempts -= 1
                self._logger.error('Failed to connect to DWH')
                self._logger.error(err)
                time.sleep(10)

    def __get_connection_cdp(self):
        """
            Try to establish connection to CDP using set variables
        """
        max_connect_attempts = MAX_GET_CONNECTION_ATTEMPTS
        while max_connect_attempts > 0:
            try:
                self._logger.info(f'Attempting to connect to CDP, '
                                  f'{max_connect_attempts} tries left')
                self.__impala_conn = jaydebeapi.connect(
                                    "com.cloudera.impala.jdbc.Driver",
                                    f"{self.host}",
                                    {'UID': f"{self.__user}",
                                    'PWD': f"{self.__password}"},
                                    'ImpalaJDBC42.jar')
                self._logger.info(f'Connected to CDP')
                break
            except Exception as err:
                max_connect_attempts -= 1
                self._logger.error('Failed to connect to DWH')
                self._logger.error(err)
                time.sleep(10)

    def validate_sql(self, sql):
        """
            Run basic checks on SQL.
            1. First command of SQL must be in the "allowed_command_ls" list
            2. Commands in forbidden_command_ls cannot exist in SQL
            3. Only one statement can be executed at a time

            This is more of a foolproof check vs. checking for an
            actual malicious behaviour. This "ensures" we only use this
            class for reading/refreshing data.
        """
        sql_parts = sql.strip().split(' ')
        delimiter_count = sql.strip().count(';')

        allowed_command_ls = \
            self.config['impala_reader']['sql_validate']['allowed_command']

        if sql_parts[0].lower() not in allowed_command_ls:
            self._logger.error(f'Can only run: {allowed_command_ls}')
            sys.exit(1)

        forbidden_command_ls = \
            self.config['impala_reader']['sql_validate']['forbidden_command']

        if any(ext in sql_parts for ext in forbidden_command_ls):
            self._logger.error(f'SQL cannot include: {forbidden_command_ls}')
            sys.exit(1)

        try:
            delimiter_count = int(delimiter_count)
        except Exception:
            delimiter_count = 0
            pass

        if int(delimiter_count) > 1:
            self._logger.error('Can only execute 1 sql command at a time')
            sys.exit(1)

    def execute_sql(self, sql):
        """
            Validate passed in query and then try to execute without return
            value. This function is meant to run "refresh"
            and "invalidate metadata" statements.
        """
        self.validate_sql(sql)

        cursor = self.__impala_conn.cursor()
        try:
            cursor.execute(sql)
            self._logger.info(f'SUCCESS: {sql}')
        except Exception as err:
            self._logger.warning(err)

    def get_result_of_sql_as_df(self, sql):
        """
            Validate passed in query and then try to execute and return as a
            pandas DataFrame. This function is meant to run "select"
            statements.
        """
        self.validate_sql(sql)

        try:
            df = pd.read_sql(sql, self.__impala_conn)
        except Exception as err:
            df = None
            self._logger.warning(err)

        return df
