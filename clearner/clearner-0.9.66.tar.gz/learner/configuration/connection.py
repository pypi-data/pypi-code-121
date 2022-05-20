# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

import os
import sys
import getpass
import logging
import warnings

import pandas as pd
from sqlalchemy import create_engine

from learner.data_worker.data_loader import get_value
from learner.setup.setup import load_json
from learner.validator.input_validator import InputValidator, validate_subset_list
from learner.configuration.data import DataConfiguration


class ConnectionConfiguration:
    """Parse the fields in the connection section of the configuration file."""

    def __init__(self, json_config, data: DataConfiguration=None):
        self._json_config = json_config
        self._data = data

        self.credentials_schema_file = get_value(self._json_config,
                                                 os.path.join(os.path.dirname(__file__),
                                                              "..", "schema", "credentials_schema.json"),
                                                 "connection",
                                                 "credentials_schema")
        self.credentials_schema = load_json(self.credentials_schema_file)
        self.credentials_file = get_value(self._json_config, os.path.join(os.environ['HOME'], ".learner_credentials.json"),
                                          "connection",
                                          "credentials_file")
        self.credentials = self.get_credentials()
        # this is anti-pattern but looks like the best way to keep things clean
        if self._data is None:  # pragma: no cover
            return
        self.presto_activate = self.get_presto_activate()
        self.presto_protocol = self.get_presto_protocol()
        self.presto_username = self.get_presto_username()
        self.presto_password = self.get_presto_password()
        self.presto_host = self.get_presto_host()
        self.presto_port = get_value(self._json_config, 8080, "connection", "presto_params", "port")
        self.presto_dbname = self.get_presto_dbname()
        self.presto_client = self.get_presto_client()

        self.postgres_activate = self.get_postgres_activate()
        self.postgres_username = self.get_postgres_username()
        self.postgres_password = self.get_postgres_password()
        self.postgres_host = self.get_postgres_host()
        self.postgres_port = get_value(self._json_config, 5432, "connection", "postgres_params", "port")
        self.postgres_dbname = self.get_postgres_dbname()
        self.postgres_client = self.get_postgres_client()

        self.mysql_activate = self.get_mysql_activate()
        self.mysql_username = self.get_mysql_username()
        self.mysql_password = self.get_mysql_password()
        self.mysql_host = self.get_mysql_host()
        self.mysql_port = get_value(self._json_config, 3306, "connection", "mysql_params", "port")
        self.mysql_dbname = self.get_mysql_dbname()
        self.mysql_client = self.get_mysql_client()

        self.snowflake_activate = self.get_snowflake_activate()
        self.snowflake_username = self.get_snowflake_username()
        self.snowflake_password = self.get_snowflake_password()
        self.snowflake_account = self.get_snowflake_account()
        self.snowflake_warehouse = self.get_snowflake_warehouse()
        self.snowflake_role = self.get_snowflake_role()
        self.snowflake_region = self.get_snowflake_region()
        self.snowflake_database = self.get_snowflake_database()
        self.snowflake_schema = self.get_snowflake_schema()
        self.snowflake_client = self.get_snowflake_client()

    def get_credentials(self):
        if self.credentials_file and os.path.exists(self.credentials_file):
            self.credentials = load_json(self.credentials_file)
            logging.info("---Validating the credentials file---")
            InputValidator(self.credentials, self.credentials_schema)
            return self.credentials
        return None  # pragma: no cover

    def get_presto_activate(self):
        activate = False
        try:
            activate = self._json_config["connection"]["presto_params"]["activate"]
        except KeyError:
            activate = False
        finally:
            if not activate:
                if (self._data.train_query_activate and self._data.train_db_type == "presto") or\
                    (self._data.test_query_activate and self._data.test_db_type == "presto"):
                    logging.critical("Connection to a presto database is required based on the information in the "
                                     "data section but presto connection was not activated. Please update the "
                                     "configuration file and try again. Exiting...")
                    sys.exit(1)
            return activate

    def get_presto_protocol(self):
        if self.presto_activate:
            try:
                protocol = self._json_config["connection"]["presto_params"]["protocol"].lower()
                validate_subset_list(parent_list=["http", "https"], parent_name="accepted presto protocols",
                                     subset_list=[protocol], subset_name="provided protocol")
                return protocol
            except KeyError:
                return "http"

    def get_presto_username(self):
        if self.presto_activate and self.presto_protocol == "https":
            username = os.getenv("LEARNER_PRESTO_USERNAME")
            if not username:
                try:
                    username = self._json_config["connection"]["presto_params"]["username"]
                except KeyError:
                    try:
                        username = self.credentials["presto"]["username"]
                    except (KeyError, TypeError):  # pragma: no cover
                        username = input("Please enter your username for presto server: ")
            return username

    def get_presto_password(self):
        if self.presto_activate and self.presto_protocol == "https":
            password = os.getenv("LEARNER_PRESTO_PASSWORD")
            if not password:
                try:
                    password = self._json_config["connection"]["presto_params"]["password"]
                except KeyError:
                    try:
                        password = self.credentials["presto"]["password"]
                    except (KeyError, TypeError):  # pragma: no cover
                        password = getpass.getpass("Please enter your password for presto server: ")
            return password

    def get_presto_host(self):
        if self.presto_activate:
            try:
                return self._json_config["connection"]["presto_params"]["host"]
            except KeyError:
                logging.critical("Connection to a presto server was activated but host is not defined. Please update "
                                 "the configuration file and try again. Exiting...")
                sys.exit(1)

    def get_presto_dbname(self):
        if self.presto_activate:
            try:
                return self._json_config["connection"]["presto_params"]["dbname"]
            except KeyError:
                warnings.warn("Connection to a presto server was activated but dbname is not defined. Leraner will use "
                              "an empty string here", UserWarning)
                return ""

    def get_presto_client(self):
        if self.presto_activate:
            url = self._construct_presto_url()
            client = create_engine(url, connect_args={'protocol': self.presto_protocol})
            self.validate_presto_connection(client)
            return client

    def _construct_presto_url(self):
        if self.presto_protocol == "https":
            url = f"presto://{self.presto_username}:{self.presto_password}@{self.presto_host}:{self.presto_port}/{self.presto_dbname}"
        else:
            url = f"presto://{self.presto_host}:{self.presto_port}/{self.presto_dbname}"
        return url

    @staticmethod
    def validate_presto_connection(client):  # pragma: no cover
        try:
            with client.connect() as conn:
                logging.info("Validating the connection to presto server by running a simple query...")
                result = pd.read_sql("SELECT * FROM system.runtime.nodes LIMIT 1", con=conn)
            assert len(result) > 0, "No running nodes available"
        except Exception as e:
            logging.critical("Test connection to presto server failed. The error is {error}".format(error=str(e)))
            sys.exit(1)

    def get_postgres_activate(self):
        activate = False
        try:
            activate = self._json_config["connection"]["postgres_params"]["activate"]
        except KeyError:
            activate = False
        finally:
            if not activate:
                if (self._data.train_query_activate and self._data.train_db_type == "postgres") or\
                    (self._data.test_query_activate and self._data.test_db_type == "postgres"):
                    logging.critical("Connection to a postgres database is required based on the information in the "
                                     "data section but postgres connection was not activated. Please update the "
                                     "configuration file and try again. Exiting...")
                    sys.exit(1)
            return activate

    def get_postgres_username(self):
        if self.postgres_activate:
            username = os.getenv("LEARNER_POSTGRES_USERNAME")
            if not username:
                try:
                    username = self._json_config["connection"]["postgres_params"]["username"]
                except KeyError:
                    try:
                        username = self.credentials["postgres"]["username"]
                    except (KeyError, TypeError):  # pragma: no cover
                        username = input("Please enter your username for postgres server: ")
            return username

    def get_postgres_password(self):
        if self.postgres_activate:
            password = os.getenv("LEARNER_POSTGRES_PASSWORD")
            if not password:
                try:
                    password = self._json_config["connection"]["postgres_params"]["password"]
                except KeyError:
                    try:
                        password = self.credentials["postgres"]["password"]
                    except (KeyError, TypeError):  # pragma: no cover
                        password = getpass.getpass("Please enter your password for postgres server: ")
            return password

    def get_postgres_host(self):
        if self.postgres_activate:
            try:
                return self._json_config["connection"]["postgres_params"]["host"]
            except KeyError:
                logging.critical("Connection to a postgres server was activated but host is not defined. Please "
                                 "update the configuration file and try again. Exiting...")
                sys.exit(1)

    def get_postgres_dbname(self):
        if self.postgres_activate:
            try:
                return self._json_config["connection"]["postgres_params"]["dbname"]
            except KeyError:
                warnings.warn("Connection to a postgres server was activated but dbname is not defined. Leraner will "
                              "use an empty string here", UserWarning)
                return ""

    def get_postgres_client(self):
        if self.postgres_activate:
            url = self._construct_postgres_url()
            client = create_engine(url)
            self.validate_postgres_connection(client)
            return client

    def _construct_postgres_url(self):
        url = f"postgresql+psycopg2://{self.postgres_username}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_dbname}"
        return url

    @staticmethod
    def validate_postgres_connection(client):  # pragma: no cover
        try:
            with client.connect() as conn:
                logging.info("Validating the connection to postgres server by running a simple query...")
                pd.read_sql("SELECT version()", con=conn)
        except Exception as e:
            logging.critical("Test connection to postgres server failed. The error is {error}".format(error=str(e)))
            sys.exit(1)

    def get_mysql_activate(self):
        activate = False
        try:
            activate = self._json_config["connection"]["mysql_params"]["activate"]
        except KeyError:
            activate = False
        finally:
            if not activate:
                if (self._data.train_query_activate and self._data.train_db_type == "mysql") or \
                        (self._data.test_query_activate and self._data.test_db_type == "mysql"):
                    logging.critical("Connection to a mysql database is required based on the information in the data "
                                     "section but mysql connection was not activated. Please update the configuration "
                                     "file and try again. Exiting...")
                    sys.exit(1)
            return activate

    def get_mysql_username(self):
        if self.mysql_activate:
            username = os.getenv("LEARNER_MYSQL_USERNAME")
            if not username:
                try:
                    username = self._json_config["connection"]["mysql_params"]["username"]
                except KeyError:
                    try:
                        username = self.credentials["mysql"]["username"]
                    except (KeyError, TypeError):  # pragma: no cover
                        username = input("Please enter your username for mysql server: ")
            return username

    def get_mysql_password(self):
        if self.mysql_activate:
            password = os.getenv("LEARNER_MYSQL_PASSWORD")
            if not password:
                try:
                    password = self._json_config["connection"]["mysql_params"]["password"]
                except KeyError:
                    try:
                        password = self.credentials["mysql"]["password"]
                    except (KeyError, TypeError):  # pragma: no cover
                        password = getpass.getpass("Please enter your password for mysql server: ")
            return password

    def get_mysql_host(self):
        if self.mysql_activate:
            try:
                return self._json_config["connection"]["mysql_params"]["host"]
            except KeyError:
                logging.critical("Connection to a mysql server was activated but host is not defined. Please update "
                                 "the configuration file and try again. Exiting...")
                sys.exit(1)

    def get_mysql_dbname(self):
        if self.mysql_activate:
            try:
                return self._json_config["connection"]["mysql_params"]["dbname"]
            except KeyError:
                warnings.warn("Connection to a mysql server was activated but dbname is not defined. Leraner will "
                              "use an empty string here", UserWarning)
                return ""

    def get_mysql_client(self):
        if self.mysql_activate:
            url = self._construct_mysql_url()
            client = create_engine(url)
            self.validate_mysql_connection(client)
            return client

    def _construct_mysql_url(self):
        url = f"mysql+mysqlconnector://{self.mysql_username}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_dbname}"
        return url

    @staticmethod
    def validate_mysql_connection(client):  # pragma: no cover
        try:
            with client.connect() as conn:
                logging.info("Validating the connection to mysql server by running a simple query...")
                pd.read_sql("SELECT version()", con=conn)
        except Exception as e:
            logging.critical("Test connection to mysql server failed. The error is {error}".format(error=str(e)))
            sys.exit(1)

    def get_snowflake_activate(self):
        activate = False
        try:
            activate = self._json_config["connection"]["snowflake_params"]["activate"]
        except KeyError:
            activate = False
        finally:
            if not activate:
                if (self._data.train_query_activate and self._data.train_db_type == "snowflake") or \
                        (self._data.test_query_activate and self._data.test_db_type == "snowflake"):
                    logging.critical("Connection to a snowflake database is required based on the information in the "
                                     "data section but snowflake connection was not activated. Please update the "
                                     "configuration file and try again. Exiting...")
                    sys.exit(1)
            return activate

    def get_snowflake_username(self):
        if self.snowflake_activate:
            username = os.getenv("LEARNER_SNOWFLAKE_USERNAME")
            if not username:
                try:
                    username = self._json_config["connection"]["snowflake_params"]["username"]
                except KeyError:
                    try:
                        username = self.credentials["snowflake"]["username"]
                    except (KeyError, TypeError):  # pragma: no cover
                        username = input("Please enter your username for snowflake server: ")
            return username

    def get_snowflake_password(self):
        if self.snowflake_activate:
            password = os.getenv("LEARNER_SNOWFLAKE_PASSWORD")
            if not password:
                try:
                    password = self._json_config["connection"]["snowflake_params"]["password"]
                except KeyError:
                    try:
                        password = self.credentials["snowflake"]["password"]
                    except (KeyError, TypeError):  # pragma: no cover
                        password = getpass.getpass("Please enter your password for snowflake server: ")
            return password

    def get_snowflake_warehouse(self):
        if self.snowflake_activate:
            try:
                return self._json_config["connection"]["snowflake_params"]["warehouse"]
            except KeyError:
                return None

    def get_snowflake_role(self):
        if self.snowflake_activate:
            try:
                return self._json_config["connection"]["snowflake_params"]["role"]
            except KeyError:
                return None

    def get_snowflake_database(self):
        if self.snowflake_activate:
            try:
                return self._json_config["connection"]["snowflake_params"]["database"]
            except KeyError:
                return None

    def get_snowflake_schema(self):
        if self.snowflake_activate:
            try:
                return self._json_config["connection"]["snowflake_params"]["schema"]
            except KeyError:
                return None

    def get_snowflake_region(self):
        if self.snowflake_activate:
            try:
                return self._json_config["connection"]["snowflake_params"]["region"]
            except KeyError:
                return None

    def get_snowflake_account(self):
        if self.snowflake_activate:
            try:
                return self._json_config["connection"]["snowflake_params"]["account"]
            except KeyError:
                logging.critical("Connection to a snowflake server was activated but account is not defined. "
                                 "Please update the configuration file and try again. Exiting...")
                sys.exit(1)

    def get_snowflake_client(self):
        if self.snowflake_activate:
            url = self._construct_snowflake_url()
            client = create_engine(url)
            self.validate_snowflake_connection(client)
            return client

    def _construct_snowflake_url(self):
        from snowflake.sqlalchemy import URL
        params = {"account": self.snowflake_account,
                  "user": self.snowflake_username,
                  "password": self.snowflake_password}
        if self.snowflake_account:
            params["account"] = self.snowflake_account
        if self.snowflake_region:
            params["region"] = self.snowflake_region
        if self.snowflake_database:
            params["database"] = self.snowflake_database
        if self.snowflake_schema:
            if not self.snowflake_database:
                logging.critical("snowflake schema was defined but database was not. Please update your configuration "
                                 "file and try again. Exiting...")
                sys.exit(1)
            params["schema"] = self.snowflake_schema
        if self.snowflake_role:
            params["role"] = self.snowflake_role

        return URL(**params)

    @staticmethod
    def validate_snowflake_connection(client):  # pragma: no cover
        try:
            with client.connect() as conn:
                logging.info("Validating the connection to snowflake server by running a simple query...")
                pd.read_sql("SELECT current_version()", con=conn)
        except Exception as e:
            logging.critical("Test connection to snowflake server failed. The error is {error}".format(error=str(e)))
            sys.exit(1)
