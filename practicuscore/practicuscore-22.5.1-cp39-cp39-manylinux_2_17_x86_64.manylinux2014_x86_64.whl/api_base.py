import os.path
import sys
from abc import ABC
import platform
from dataclasses import dataclass, field, fields
from datetime import datetime
from typing import List, Optional, Union

from dataclasses_json import dataclass_json

from practicuscore.core_def import PRTEng, PRTConn, CoreDef, OPResult


@dataclass_json
@dataclass
class PRTDataClass(ABC):
    def validate(self, log_error=True):
        # Validate all fields, if they have "validators" metadata.
        # if log_error == False, returns a tuple (field_name, error_message)
        #    intended to be used in UI to gracefully check issues without breaking
        # "validators" can be a single tuple (lambda_func, "err message") OR a list of validation tuples
        #    i.e. use a single validator:
        #     some_field: int = field(
        #         metadata={
        #             "validators": (lambda x: x > 0, "Must be > 0")
        #         })
        #    OR multiple validators:
        #     some_field: int = field(
        #         metadata={
        #             "validators": [(lambda x: x > 0, "Must be > 0"),
        #                            (lambda x: x < 10, "Must be < 10")]
        #         })
        # This method will also call validate() for children. (If a field has the validate() method)
        #    Meaning, field is a PRTDataClass itself potentially containing simple fields with "validators"
        for fld in fields(self):
            field_val = getattr(self, fld.name)

            sub_validate_func = getattr(field_val, "validate", None)
            if callable(sub_validate_func):
                # field is a PRTDataClass and has validate() method.
                field_val.validate()

            if "validators" in fld.metadata:
                validator_or_validators = fld.metadata["validators"]

                if isinstance(validator_or_validators, tuple):
                    validators = [validator_or_validators]
                else:
                    validators = validator_or_validators
                for validator_tuple in validators:
                    assert isinstance(validator_tuple, tuple), \
                        "Validator must be a tuple in the form of (validator_lambda, 'error message')"
                    validator_func, validator_err_msg = validator_tuple
                    field_val = getattr(self, fld.name)
                    try:
                        failed = False
                        if not validator_func(field_val):
                            failed = True
                    except Exception as ex:
                        failed = True
                        validator_err_msg = f"Exception occurred while checking for '{validator_err_msg}', " \
                                            f"\nException: {ex}"

                    if failed:
                        if log_error:
                            from practicuscore.core_conf import log_manager_glbl
                            logger = log_manager_glbl.get_logger()
                            logger.error(f"Validation for {self.__class__.__name__}.{fld.name}={field_val} "
                                         f"failed. \nError: {validator_err_msg}")
                            # the below can cause a crash
                            # raise ValueError(f"Validation for {self.__class__.__name__}.{fld.name}={field_val} "
                            #                  f"failed. \nError: {validator_err_msg}")
                        else:
                            return fld.name, validator_err_msg  # return info about first encountered issue
        if log_error:
            pass  # no issue, nothing to raise
        else:
            return None, None  # no issue, nothing to return

    def __post_init__(self):
        self.validate()


@dataclass_json
@dataclass
class FlexValidateDataClass(PRTDataClass, ABC):
    # In some rare cases we create empty dataclasses which has fields to be filled later.
    # for these, we cannot validate right after init.
    # If we add this flexibility to the base class, all json files end up having an unnecessary field
    bypass_validation: bool = False

    def __post_init__(self):
        # Child classes validations metadata should work with default values, i.e. None
        # This will only work if values are passed part of init.
        # It is also possible fields are assigned value after init. In this case validate() should be called explicitly
        if not self.bypass_validation:
            self.validate()


@dataclass_json
@dataclass
class RequestMeta:
    meta_type: str = "Request"
    meta_name: str = ""
    req_time: Optional[datetime] = None
    req_core_v: str = CoreDef.CORE_VERSION
    req_os: str = platform.system()
    req_os_v: str = platform.release()
    req_py_minor_v: int = sys.version_info.minor


@dataclass_json
@dataclass
class PRTRequest(PRTDataClass, ABC):
    # Creating meta class here caused a nasty bug. meta became a shared object between child classes
    #   i.e. when __post_init() below updated meta_name for one type of Request class, al others got the new name
    # meta: RequestMeta = RequestMeta()
    meta: Optional[RequestMeta] = None

    @property
    def name(self) -> str:
        return self.meta.meta_name

    def __post_init__(self):
        self.meta = RequestMeta()
        self.meta.meta_name = self.__class__.__name__.rsplit("Request", 1)[0]
        # do not assign defaults in class definition. Gets assigned static one time
        self.meta.req_time = datetime.utcnow()
        super().__post_init__()


@dataclass_json
@dataclass
class ResponseMeta:
    meta_type: str = "Response"
    meta_name: str = ""
    resp_node_v: str = ""  # assigned later right before sending to client
    resp_py_minor_v: int = sys.version_info.minor


@dataclass_json
@dataclass
class PRTResponse(PRTDataClass, ABC):
    meta: Optional[ResponseMeta] = None
    op_result: Optional[OPResult] = None
    # meta: ResponseMeta = ResponseMeta()  Don't instantiate here. Read notes for PRTRequest

    @property
    def name(self) -> str:
        return self.meta.meta_name

    def __post_init__(self):
        self.meta = ResponseMeta()
        self.meta.meta_name = self.__class__.__name__.rsplit("Response", 1)[0]
        # do not assign defaults in class definition. Gets assigned static one time
        self.meta.req_time = datetime.utcnow()
        super().__post_init__()


@dataclass_json
@dataclass
class EmptyResponse(PRTResponse):
    # used when there's an error, no response can be created and we hae op_result send back
    pass


# Connection configuration classes

@dataclass
class UIMap:
    # Helps map an individual ConnConf field to a single GUI element.
    # i.e. MYSQL related field "db_host" should be visible as "Database Host Address", it is required, ...
    visible_name: Optional[str] = None
    auto_display: bool = True  # some fields are displayed manually and not automated
    tip: Optional[str] = None
    default_value: Optional[str] = None
    is_required: bool = True
    is_password: bool = False


@dataclass_json
@dataclass
class ConnConf(FlexValidateDataClass, ABC):
    sampling_method: Optional[str] = field(
        default="ALL",
        metadata={
            "validators": (lambda x: x is None or str(x).upper() in ["ALL", "TOP", "RANDOM", "BOTTOM"],
                           "Must be ALL, TOP, RANDOM, BOTTOM or None")
        })
    sample_size: Optional[int] = field(
        default=None,
        metadata={
            "validators": (lambda x: x is None or int(x) > 0, "Must be None or > 0")
        })
    sample_size_app: Optional[int] = field(
        default=None,
        metadata={
            "validators": (lambda x: x is None or int(x) > 0, "Must be None or > 0")
        })
    column_list: Optional[List[str]] = None
    filter: Optional[str] = None
    ws_uuid: Optional[str] = None
    file_type: Optional[str] = None

    @property
    def conn_type(self) -> PRTConn:
        return self._conn_type

    @property
    def friendly_desc(self) -> str:
        # override with children class for a better user friendly
        return f"Cloud {self._conn_type}"

    @property
    def friendly_long_desc(self) -> str:
        return self.friendly_desc

    @property
    def audit_desc(self) -> str:
        # override with children class for audit
        return self.friendly_desc


@dataclass_json
@dataclass
class InMemoryConnConf(ConnConf):
    _conn_type: PRTConn = PRTConn.IN_MEMORY
    df: Optional[object] = None

    @property
    def friendly_desc(self) -> str:
        return "In memory dataframe"


@dataclass_json
@dataclass
class LocalFileConnConf(ConnConf):
    _conn_type: PRTConn = PRTConn.LOCAL_FILE
    file_path: Optional[str] = field(default=None, metadata={
        "ui_map": UIMap(visible_name="File Path",
                        tip="Type path on local disk")
    })

    @property
    def friendly_desc(self) -> str:
        try:
            if self.file_path:
                return os.path.splitext(os.path.basename(self.file_path))[0]
        except:
            pass

        return self._conn_type.lower()


@dataclass_json
@dataclass
class NodeFileConnConf(ConnConf):
    # todo : Maybe we can inherit this class from LocalFileConnConf???
    _conn_type: PRTConn = PRTConn.NODE_FILE
    file_path: Optional[str] = field(default=None, metadata={
        "ui_map": UIMap(visible_name="File Path",
                        tip="Type path on node local disk. E.g. /home/ubuntu/data/file.csv")
    })

    @property
    def friendly_desc(self) -> str:
        try:
            if self.file_path:
                return os.path.splitext(os.path.basename(self.file_path))[0]
        except:
            pass

        return self._conn_type.lower()

    @property
    def friendly_long_desc(self) -> str:
        return self.file_path


@dataclass_json
@dataclass
class S3ConnConf(ConnConf):
    _conn_type: PRTConn = PRTConn.S3
    aws_region: Optional[str] = None
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    s3_bucket: Optional[str] = None
    # todo: this can be removed to ConnConf. Or we can create ObjectStorageConnConf and use it as keys.
    s3_keys: Optional[List[str]] = None

    @property
    def friendly_desc(self) -> str:
        try:
            if self.s3_keys:
                return os.path.splitext(os.path.basename(self.s3_keys[0]))[0]
        except:
            pass
        return self._conn_type.lower()

    @property
    def friendly_long_desc(self) -> str:
        if self.s3_keys:
            return self.s3_keys[0]
        return self.friendly_desc

    @property
    def audit_desc(self) -> str:
        if self.s3_bucket:
            s3_info = self.s3_bucket
            if self.s3_keys:
                for s3_key in self.s3_keys:
                    s3_info += " " + s3_key
            return s3_info
        return ""


@dataclass_json
@dataclass
class RelationalConnConf(ConnConf, ABC):
    sql_query: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="SQL Query",
                        auto_display=False),
        "validators": (lambda x: x and len(x) > 0, "No SQL query provided")
    })

    target_table_name: Optional[str] = None

    @property
    def friendly_desc(self) -> str:
        try:
            if self.sql_query:
                table_ind = self.sql_query.lower().find("from ") + len("from ")
                if table_ind > -1:
                    desc = self.sql_query[table_ind:].strip().lower()
                    desc = desc[:desc.find(" ")].strip()
                    if desc:
                        return desc
                return f"sqlite:{self.file_path}"
        except:
            pass
        return self._conn_type.lower()

    @property
    def audit_desc(self) -> str:
        audit_info = self.friendly_desc
        if self.sql_query:
            audit_info += "\nSQL: " + self.sql_query

        return audit_info


@dataclass_json
@dataclass
class SqLiteConnConf(RelationalConnConf):
    _conn_type: PRTConn = PRTConn.SQLITE
    file_path: str = field(default="None", metadata={
        "ui_map": UIMap(visible_name="File Path",
                        tip="Type path on node local disk. E.g. /home/ubuntu/data/database.db",
                        default_value="/home/ubuntu/samples/chinook.db"),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })


@dataclass_json
@dataclass
class MYSQLConnConf(RelationalConnConf):
    _conn_type: PRTConn = PRTConn.MYSQL
    db_host: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Database Server Address",
                        tip="E.g. test.abcde.us-east-1.rds.amazonaws.com or 192.168.0.1",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    db_name: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Database Name",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    db_port: int = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Port",
                        default_value="3306"),
        "validators": (lambda x: 1 <= int(x) <= 65_535, "Port must be between 1 and 65,535")
    })
    user: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="User Name",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    password: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Password",
                        is_password=True,
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })


    @property
    def audit_desc(self) -> str:
        audit_info = ""
        audit_info += f"MySQL Host:{self.db_host} DB:{self.db_name} User:{self.user}"
        if self.sql_query:
            audit_info += " SQL: " + self.sql_query

        return audit_info


@dataclass_json
@dataclass
class PostgreSQLConnConf(RelationalConnConf):
    _conn_type: PRTConn = PRTConn.POSTGRESQL
    db_host: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Database Server Address",
                        tip="E.g. test.abcde.us-east-1.rds.amazonaws.com or 192.168.0.1",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    db_name: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Database Name",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    db_port: int = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Port",
                        default_value="5432"),
        "validators": (lambda x: 1 <= int(x) <= 65_535, "Port must be between 1 and 65,535")
    })
    user: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="User Name",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    password: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Password",
                        is_password=True,
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })

    @property
    def audit_desc(self) -> str:
        audit_info = ""
        audit_info += f"PostgreSQL Host:{self.db_host} DB:{self.db_name} User:{self.user}"
        if self.sql_query:
            audit_info += " SQL: " + self.sql_query

        return audit_info


@dataclass_json
@dataclass
class RedshiftConnConf(RelationalConnConf):
    _conn_type: PRTConn = PRTConn.REDSHIFT
    # redshift_db_address: Optional[str] = None  # dummy
    db_host: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Database Server Address",
                        tip="E.g. test.abcde.us-east-1.rds.amazonaws.com or 192.168.0.1",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    db_name: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Database Name",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    db_port: int = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Port",
                        default_value="5439"),
        "validators": (lambda x: 1 <= int(x) <= 65_535, "Port must be between 1 and 65,535")
    })
    user: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="User Name",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    password: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Password",
                        is_password=True,
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })

    @property
    def audit_desc(self) -> str:
        audit_info = ""
        audit_info += f"Redshift Host:{self.db_host} DB:{self.db_name} User:{self.user}"
        if self.sql_query:
            audit_info += " SQL: " + self.sql_query

        return audit_info


@dataclass_json
@dataclass
class SnowflakeConnConf(RelationalConnConf):
    _conn_type: PRTConn = PRTConn.SNOWFLAKE
    # redshift_db_address: Optional[str] = None  # dummy

    db_name: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Database Name",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    schema: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Database Schema",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    warehouse_name: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Warehouse Name",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    user: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="User Name",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    role: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Role",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    account: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Account Name",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    password: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Password",
                        is_password=True,
                        ),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })

    @property
    def audit_desc(self) -> str:
        audit_info = ""
        audit_info += f"Snowflake Warehouse:{self.warehouse_name} DB:{self.db_name} Schema:{self.schema} " \
                      f"User:{self.user} Role:{self.role} Account:{self.account}"
        if self.sql_query:
            audit_info += " SQL: " + self.sql_query

        return audit_info


@dataclass_json
@dataclass
class MSSQLConnConf(RelationalConnConf):
    _conn_type: PRTConn = PRTConn.MSSQL
    # redshift_db_address: Optional[str] = None  # dummy
    db_host: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Database Server Address",
                        tip="E.g. test.abcde.us-east-1.rds.amazonaws.com or 192.168.0.1",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    db_name: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Database Name",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    # driver: str = field(default=None, metadata={
    #     "ui_map": UIMap(visible_name="Driver Name",
    #                     default_value="SQL Server Native Client 10.0"),
    #     "validators": (lambda x: x and len(x) > 0, "No value provided")
    # })
    db_port: int = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Port",
                        default_value="1433"),
        "validators": (lambda x: 1 <= int(x) <= 65_535, "Port must be between 1 and 65,535")
    })
    user: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="User Name",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    password: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Password",
                        is_password=True,
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })

    @property
    def audit_desc(self) -> str:
        audit_info = ""
        audit_info += f"MSSQL Host:{self.db_host} DB:{self.db_name} User:{self.user}"
        if self.sql_query:
            audit_info += " SQL: " + self.sql_query

        return audit_info


@dataclass_json
@dataclass
class OracleConnConf(RelationalConnConf):
    _conn_type: PRTConn = PRTConn.ORACLE
    # redshift_db_address: Optional[str] = None  # dummy
    db_host: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Database Server Address",
                        tip="E.g. test.abcde.us-east-1.rds.amazonaws.com or 192.168.0.1",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    db_name: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Database Name",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    # driver: str = field(default=None, metadata={
    #     "ui_map": UIMap(visible_name="Driver Name",
    #                     default_value="SQL Server Native Client 10.0"),
    #     "validators": (lambda x: x and len(x) > 0, "No value provided")
    # })
    db_port: int = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Port",
                        default_value="1521"),
        "validators": (lambda x: 1 <= int(x) <= 65_535, "Port must be between 1 and 65,535")
    })
    user: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="User Name",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    password: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Password",
                        is_password=True,
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })

    @property
    def audit_desc(self) -> str:
        audit_info = ""
        audit_info += f"Oracle Host:{self.db_host} DB:{self.db_name} User:{self.user}"
        if self.sql_query:
            audit_info += " SQL: " + self.sql_query

        return audit_info


@dataclass_json
@dataclass
class HiveHadoopConnConf(RelationalConnConf):
    _conn_type: PRTConn = PRTConn.HIVE_HADOOP
    db_host: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Database Server Address",
                        tip="E.g. test.abcde.us-east-1.rds.amazonaws.com or 192.168.0.1",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    db_name: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Database Name",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    db_port: int = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Port",
                        default_value=""),
        "validators": (lambda x: 1 <= int(x) <= 65_535, "Port must be between 1 and 65,535")
    })
    user: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="User Name",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    password: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Password",
                        is_password=True,
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })

    @property
    def audit_desc(self) -> str:
        audit_info = ""
        audit_info += f"Hive Host:{self.db_host} DB:{self.db_name}"
        if self.sql_query:
            audit_info += " SQL: " + self.sql_query

        return audit_info


@dataclass_json
@dataclass
class AthenaConnConf(RelationalConnConf):
    _conn_type: PRTConn = PRTConn.ATHENA
    db_host: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Database Server Address",
                        tip="E.g. test.abcde.us-east-1.rds.amazonaws.com or 192.168.0.1",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    db_name: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Database Name",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    s3_dir: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="S3 Location",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    db_port: int = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Port",
                        default_value="443"),
        "validators": (lambda x: 1 <= int(x) <= 65_535, "Port must be between 1 and 65,535")
    })
    access_key: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="AWS Access key ID",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    secret_key: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="AWS Secret access key",
                        is_password=True,
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })

    @property
    def audit_desc(self) -> str:
        audit_info = ""
        audit_info += f"Athena Host:{self.db_host} DB:{self.db_name}"
        if self.sql_query:
            audit_info += " SQL: " + self.sql_query

        return audit_info


@dataclass_json
@dataclass
class ElasticSearchConnConf(RelationalConnConf):
    _conn_type: PRTConn = PRTConn.ELASTIC_SEARCH
    db_host: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Database Server Address",
                        tip="E.g. test-2.latest-elasticsearch.abc-3.xyz.com or 192.168.0.1",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    db_port: int = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Port",
                        default_value=""),
        "validators": (lambda x: 1 <= int(x) <= 65_535, "Port must be between 1 and 65,535")
    })
    user: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="User Name",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    password: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Password",
                        is_password=True,
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })

    @property
    def audit_desc(self) -> str:
        audit_info = ""
        audit_info += f"Elastic :{self.db_host} DB:{self.db_port} User: {self.user}"
        if self.sql_query:
            audit_info += " SQL: " + self.sql_query

        return audit_info


@dataclass_json
@dataclass
class AWSElasticSearchConnConf(RelationalConnConf):
    _conn_type: PRTConn = PRTConn.AWS_ELASTIC_SEARCH
    db_host: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Database Server Address",
                        tip="E.g. search-test-abcde.us-east-1.es.amazonaws.com",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    db_port: int = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Port",
                        default_value="443"),
        "validators": (lambda x: 1 <= int(x) <= 65_535, "Port must be between 1 and 65,535")
    })
    user: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="User Name",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })
    password: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Password",
                        is_password=True,
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })

    @property
    def audit_desc(self) -> str:
        audit_info = ""
        audit_info += f"AWS OpenSearch :{self.db_host} DB:{self.db_port} User: {self.user}"
        if self.sql_query:
            audit_info += " SQL: " + self.sql_query

        return audit_info


@dataclass_json
@dataclass
class CustomDBConnConf(RelationalConnConf):
    _conn_type: PRTConn = PRTConn.CUSTOM_DB
    # redshift_db_address: Optional[str] = None  # dummy
    conn_string: str = field(default=None, metadata={
        "ui_map": UIMap(visible_name="Connection String",
                        tip="connection_string",
                        default_value=""),
        "validators": (lambda x: x and len(x) > 0, "No value provided")
    })

    @property
    def audit_desc(self) -> str:
        return f"Custom DB Connection with connection string (can include password)"


class ConnConfFactory:
    @staticmethod
    def create_or_get(conn_conf_json_dict_or_obj) -> ConnConf:
        # due to json serialization this method can get json, dict or actual class
        if isinstance(conn_conf_json_dict_or_obj, str):
            import json
            conn_conf_json_dict_or_obj = json.loads(conn_conf_json_dict_or_obj)

        if isinstance(conn_conf_json_dict_or_obj, dict):
            conn_type_str = conn_conf_json_dict_or_obj['_conn_type']
            if conn_type_str == PRTConn.LOCAL_FILE:
                return LocalFileConnConf.from_dict(conn_conf_json_dict_or_obj)
            if conn_type_str == PRTConn.NODE_FILE:
                return NodeFileConnConf.from_dict(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.S3:
                return S3ConnConf.from_dict(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.SQLITE:
                return SqLiteConnConf.from_dict(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.MYSQL:
                return MYSQLConnConf.from_dict(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.POSTGRESQL:
                return PostgreSQLConnConf.from_dict(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.REDSHIFT:
                return RedshiftConnConf.from_dict(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.SNOWFLAKE:
                return SnowflakeConnConf.from_dict(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.MSSQL:
                return MSSQLConnConf.from_dict(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.ORACLE:
                return OracleConnConf.from_dict(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.HIVE_HADOOP:
                return HiveHadoopConnConf.from_dict(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.ATHENA:
                return AthenaConnConf.from_dict(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.ELASTIC_SEARCH:
                return ElasticSearchConnConf.from_dict(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.AWS_ELASTIC_SEARCH:
                return AWSElasticSearchConnConf.from_dict(conn_conf_json_dict_or_obj)
            elif conn_type_str == PRTConn.CUSTOM_DB:
                return CustomDBConnConf.from_dict(conn_conf_json_dict_or_obj)
            else:
                raise AttributeError(f"Unknown connection type {conn_type_str}")
        elif issubclass(type(conn_conf_json_dict_or_obj), ConnConf):
            return conn_conf_json_dict_or_obj
        else:
            raise SystemError(f"Unknown conn_conf type {type(conn_conf_json_dict_or_obj)}")


# Engine Configuration Classes
@dataclass_json
@dataclass
class EngConf(PRTDataClass, ABC):
    @property
    def eng_type(self) -> PRTEng:
        return self._eng_type


@dataclass_json
@dataclass
class PandasEngConf(EngConf):
    _eng_type: PRTEng = PRTEng.PANDAS


@dataclass_json
@dataclass
class DaskEngConf(PandasEngConf):
    _eng_type: PRTEng = PRTEng.DASK
    worker_count: Optional[int] = None


@dataclass_json
@dataclass
class RapidsEngConf(PandasEngConf):
    _eng_type: PRTEng = PRTEng.RAPIDS


@dataclass_json
@dataclass
class RapidsMultiEngConf(DaskEngConf):
    _eng_type: PRTEng = PRTEng.RAPIDS_MULTI
    gpu_count: Optional[int] = None


@dataclass_json
@dataclass
class SparkEngConf(PandasEngConf):
    _eng_type: PRTEng = PRTEng.SPARK


class EngConfFactory:
    @staticmethod
    def create(eng_conf_json_dict_or_obj) -> EngConf:
        # due to json serialization this method can get json, dict or actual class
        if not eng_conf_json_dict_or_obj:
            return PandasEngConf()

        if isinstance(eng_conf_json_dict_or_obj, str):
            import json
            eng_conf_json_dict_or_obj = json.loads(eng_conf_json_dict_or_obj)

        if isinstance(eng_conf_json_dict_or_obj, dict):
            eng_type_str = eng_conf_json_dict_or_obj['_eng_type']
            if eng_type_str == PRTEng.PANDAS:
                return PandasEngConf.from_dict(eng_conf_json_dict_or_obj)
            elif eng_type_str == PRTEng.DASK:
                return DaskEngConf.from_dict(eng_conf_json_dict_or_obj)
            elif eng_type_str == PRTEng.RAPIDS:
                return RapidsEngConf.from_dict(eng_conf_json_dict_or_obj)
            elif eng_type_str == PRTEng.RAPIDS_MULTI:
                return RapidsMultiEngConf.from_dict(eng_conf_json_dict_or_obj)
            elif eng_type_str == PRTEng.SPARK:
                return SparkEngConf.from_dict(eng_conf_json_dict_or_obj)
            else:
                raise AttributeError(f"Unknown engine type {eng_type_str}")
        elif isinstance(eng_conf_json_dict_or_obj, EngConf):
            return eng_conf_json_dict_or_obj
        else:
            raise SystemError(f"Unknown eng_conf type {type(eng_conf_json_dict_or_obj)}")


@dataclass_json
@dataclass
class PRTDataRequest(PRTRequest):
    # ** We needed to add dict to this list since when dataclass_json cannot figure out type
    #    it returns dict instead of actual class. need to override or use as dict
    conn_conf: Union[
        dict,
        NodeFileConnConf,
        SqLiteConnConf,
        S3ConnConf,
        MYSQLConnConf,
        PostgreSQLConnConf,
        RedshiftConnConf,
        SnowflakeConnConf,
        MSSQLConnConf,
        OracleConnConf,
        HiveHadoopConnConf,
        AthenaConnConf,
        ElasticSearchConnConf,
        AWSElasticSearchConnConf,
        CustomDBConnConf,
    ] = field(default=None, metadata={
        "validators": (lambda x: isinstance(x, dict) or isinstance(x, ConnConf), "conn_conf dict or class not provided")
    })

    eng_conf: Optional[Union[
        dict,
        PandasEngConf,
        DaskEngConf,
        RapidsEngConf,
        RapidsMultiEngConf,
        SparkEngConf,
    ]] = field(default=None, metadata={
        "validators": (lambda x: x is None or isinstance(x, dict) or isinstance(x, EngConf),
                       "eng_conf must be None, a dict or subclass of EngConf")
    })

    # MySQLConnDef,
    # AuroraMySQLConnDef,


if __name__ == "__main__":
    pass
    # eng_conf = RapidsMultiEngConf()
    # eng_conf = EngConfFactory.create(eng_conf)
    # print(eng_conf)
