from enum import Enum

from practicuscore.api_base import *  # DO NOT REMOVE


@dataclass_json
@dataclass
class CreateWorkerRequest(PRTRequest):
    pass


@dataclass_json
@dataclass
class CreateWorkerResponse(PRTResponse):
    worker_id: int = field(default=-1, metadata={
        "validators": (lambda x: int(x) > 0, "number must be an integer > 0")
    })


@dataclass_json
@dataclass
class StartExtSvcRequest(PRTRequest):
    svc_name: str = field(default="", metadata={
        "validators": (lambda x: len(x) > 0, "must provide svc_name")
    })
    port: Optional[int] = None
    dark_mode: bool = True
    auto_start_after_failure: bool = False
    singleton_service_per_node: bool = True
    additional_start_args: Optional[str] = None


@dataclass_json
@dataclass
class StartExtSvcResponse(PRTResponse):
    port: int = field(default=-1, metadata={
        "validators": (lambda x: x and 0 < int(x) < 65536, "invalid port ")
    })


@dataclass_json
@dataclass
class RestartNodeSvcRequest(PRTRequest):
    restart_reason_to_log: Optional[str] = None


@dataclass_json
@dataclass
class KillWorkerRequest(PRTRequest):
    worker_id: int = field(default=-1, metadata={
        "validators": (lambda x: int(x) > 0, "number must be an integer > 0")
    })


@dataclass_json
@dataclass
class KillWorkersRequest(PRTRequest):
    worker_id_list: Optional[List[int]] = None


@dataclass_json
@dataclass
class PingRequest(PRTRequest):
    pass


@dataclass_json
@dataclass
class CloneLogsRequest(PRTRequest):
    pass


@dataclass_json
@dataclass
class LoadRequest(PRTDataRequest):
    ws_uuid: Optional[str] = None  # ws_uuid of the app is synced with ws in Node, when possible.
    # response is csv, no class needed


@dataclass_json
@dataclass
class ExportDataRequest(PRTDataRequest):
    # conn_conf in base class is a mandatory field and is the destination of save
    source_conn_conf: Optional[Union[
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
        CustomDBConnConf,
    ]] = field(default=None, metadata={
        "validators": (lambda x: x is None or isinstance(x, dict) or isinstance(x, ConnConf),
                       "conn_conf dict or class not provided")
    })
    step_dict_list: Optional[List[dict]] = None
    # response is op_result


@dataclass_json
@dataclass
class GetDFRequest(PRTRequest):
    pass


class WSStateKeys:
    DF_FULL_TYPE_NAME = "DF_FULL_TYPE_NAME"
    DF_LOADED_ROWS_COUNT = "DF_LOADED_ROWS_COUNT"


@dataclass_json
@dataclass
class GetWSStateRequest(PRTRequest):
    wait_for_free_sec: float = 60
    generic_attributes_keys: Optional[List[str]] = None


@dataclass_json
@dataclass
class GetWSStateResponse(PRTResponse):
    busy: bool = False
    step_dict_list: List[dict] = field(default=None, metadata={
        "validators": (lambda x: x is not None, "No step list provided")
    })
    async_op_issues_json_list: Optional[List[str]] = None
    generic_attributes_dict: Optional[dict] = None


@dataclass_json
@dataclass
class RunStepsRequest(PRTRequest):
    # used to run for "Node only" steps. Using dict, since Step is not dataclass
    step_dict_list: List[dict] = field(default=None, metadata={
        "validators": (lambda x: x is not None, "No step list provided")
    })
    reset_steps: bool = False


@dataclass_json
@dataclass
class GetObjectStorageMetaRequest(PRTDataRequest):
    prefix: Optional[str] = None
    max_size: Optional[int] = None
    starting_token: Optional[str] = None
    element_uuid: Optional[str] = None


class StorageMetaChildrenLoadStatus(str, Enum):
    NOT_LOADED = "NOT_LOADED"
    LOADED = "LOADED"
    WONT_LOAD = "WONT_LOAD"


@dataclass_json
@dataclass
class ObjectStorageMeta:
    key: Optional[str] = None
    name: Optional[str] = None
    prefix: Optional[str] = None
    is_folder: Optional[bool] = None
    size: Optional[int] = None
    last_modified: Optional[datetime] = None
    level: int = 0
    children: Optional[List['ObjectStorageMeta']] = None
    children_loaded: StorageMetaChildrenLoadStatus = StorageMetaChildrenLoadStatus.NOT_LOADED


@dataclass_json
@dataclass
class GetObjectStorageMetaResponse(PRTResponse):
    meta_list: Optional[List[ObjectStorageMeta]] = None


@dataclass_json
@dataclass
class ConnSelectionStats:
    # statistics about a selected key or keys
    size_per_row: Optional[int] = None
    sample_size_in_bytes: Optional[int] = None
    sample_rows: Optional[int] = None
    total_size_in_bytes: Optional[int] = None
    total_rows: Optional[int] = None


@dataclass_json
@dataclass
class PreviewRequest(PRTDataRequest):
    pass


@dataclass_json
@dataclass
class PreviewResponse(PRTResponse):
    selection_stats: Optional[ConnSelectionStats] = None
    csv_str: Optional[str] = None


@dataclass_json
@dataclass
class TestRelationalConnRequest(PRTDataRequest):
    pass


@dataclass_json
@dataclass
class GetFileStatusRequest(PRTRequest):
    node_path_list: List[str] = field(default=None, metadata={
        "validators": (lambda x: x and len(x) > 0, "No path list provided")
    })
    recursive: bool = False


@dataclass_json
@dataclass
class FileStatus:
    file_path: str
    file_size: int
    file_epoch: float


@dataclass_json
@dataclass
class GetFileStatusResponse(PRTResponse):
    file_status_list: Optional[List[FileStatus]] = None


@dataclass_json
@dataclass
class UploadFilesRequest(PRTRequest):
    # opens a multi-part app to node communication channel. files/file parts are communicated chunk by chunk
    pass


@dataclass_json
@dataclass
class UploadFilesToCloudRequest(PRTRequest):
    conn_conf: Union[
        S3ConnConf
    ] = field(default=None, metadata={
        "validators": (lambda x: isinstance(x, ConnConf), "conn_conf class not provided")
    })


@dataclass_json
@dataclass
class UploadNodeFilesToCloudRequest(PRTRequest):
    conn_conf: Union[
        S3ConnConf
    ] = field(default=None, metadata={
        "validators": (lambda x: isinstance(x, ConnConf), "conn_conf class not provided")
    })
    source_path_list: List[str] = field(default=None, metadata={
        "validators": (lambda x: x and len(x) > 0, "No source_path_list provided")
    })
    target_dir_path: str = field(default=None, metadata={
        "validators": (lambda x: x and len(x) > 0, "No target_dir_path provided")
    })
    source_path_to_cut: Optional[str] = None


@dataclass_json
@dataclass
class DownloadFilesRequest(PRTRequest):
    node_path_list: List[str] = field(default=None, metadata={
        "validators": (lambda x: x and len(x) > 0, "No path list provided")
    })
    recursive: bool = False


@dataclass_json
@dataclass
class CopyFilesRequest(PRTRequest):
    source_path_list: List[str] = field(default=None, metadata={
        "validators": (lambda x: x and len(x) > 0, "No source_path_list provided")
    })
    target_dir_path: str = field(default=None, metadata={
        "validators": (lambda x: x and len(x) > 0, "No target_dir_path provided")
    })
    source_path_to_cut: Optional[str] = None


@dataclass_json
@dataclass
class ProfileWSRequest(PRTRequest):
    profile_uuid: str = field(default=None, metadata={
        "validators": (lambda x: x and len(x) > 0, "No profile_uuid provided")
    })
    title: Optional[str] = field(default=None, metadata={
        "validators": (lambda x: x and len(x) > 0, "No title provided")
    })
    compare_to_original: Optional[bool] = None


@dataclass_json
@dataclass
class ProfileWSResponse(PRTResponse):
    started_profiling: Optional[bool] = None


@dataclass_json
@dataclass
class ViewLogsRequest(PRTRequest):
    view_practicus_log: bool = True
    view_practicus_audit_log: bool = True
    log_size_mb: int = 10


@dataclass_json
@dataclass
class ViewLogsResponse(PRTResponse):
    practicus_log: Optional[str] = None
    practicus_audit_log: Optional[str] = None


@dataclass_json
@dataclass
class TestGenericRequest(PRTRequest):
    some_str: Optional[str] = None


@dataclass_json
@dataclass
class TestGenericResponse(PRTResponse):
    some_result: Optional[str] = None


@dataclass_json
@dataclass
class RunScriptRequest(PRTRequest):
    script_path: Optional[str] = None
    run_as_sudo: bool = False
    timeout_secs: int = 120
    wait_for_end: bool = True


@dataclass_json
@dataclass
class RunScriptResponse(PRTResponse):
    std_out: str = ""
    std_err: str = ""


@dataclass_json
@dataclass
class FlushLogsRequest(PRTRequest):
    pass


@dataclass_json
@dataclass
class XLImportRequest(PRTRequest):
    file_name: str = ""


@dataclass_json
@dataclass
class XLImportResponse(PRTResponse):
    dp_content: str = ""
    dp_err_warning: str = ""


@dataclass_json
@dataclass
class TestCodeRequest(PRTRequest):
    sampling_method: Optional[str] = field(
        default="ALL",
        metadata={
            "validators": (lambda x: x in ["ALL", "TOP", "RANDOM", "BOTTOM", None],
                           "Must be ALL, TOP, RANDOM, BOTTOM or None")
        })
    sample_size: Optional[int] = field(
        default=1000,
        metadata={
            "validators": (lambda x: x is None or int(x) > 0, "Must be None or > 0")
        })
    code_block_encoded: Optional[str] = field(
        default=None,
        metadata={
            "validators": (lambda x: x is not None and len(x) > 0, "No code provided")
        })


@dataclass_json
@dataclass
class TestCodeResponse(PRTResponse):
    test_result_csv_b: Optional[str] = None


@dataclass_json
@dataclass
class GenerateCodeRequest(PRTRequest):
    engine: Optional[str] = None
    template_list: Optional[List[str]] = None
    worksheet_name: Optional[str] = None
    user_name: Optional[str] = None
    params: Optional[dict] = None
    file_prefix: Optional[str] = None
    dag_id: Optional[str] = None


@dataclass_json
@dataclass
class GenerateCodeResponse(PRTResponse):
    generated_file_paths: Optional[List[str]] = None


@dataclass_json
@dataclass
class CreateFolderRequest(PRTDataRequest):
    full_path: Optional[str] = field(
        default=None,
        metadata={
            "validators": (lambda x: x is not None, "No path provided")
        })


@dataclass_json
@dataclass
class ModelConfig:
    state: Optional[str] = None
    model_name: Optional[str] = None
    model_desc: Optional[str] = None
    target: Optional[str] = None
    re_sample_size: Optional[int] = None
    model_dir: Optional[str] = None
    short_model_name: Optional[str] = None
    version_name: Optional[str] = None
    problem_type: Optional[str] = None
    limit_to_models: Optional[str] = None
    use_gpu: Optional[bool] = None
    user_name: Optional[str] = None
    node_name: Optional[str] = None
    node_instance_id: Optional[str] = None
    # Binary or Excel model
    build_full_fledged: Optional[bool] = None
    build_for_excel: Optional[bool] = None
    excel_rows_to_export: Optional[int] = None
    model_signature_json: Optional[str] = None
    # Experiment logging
    log_experiments: Optional[bool] = None
    log_exp_name: Optional[str] = None
    log_db_conn_str: Optional[str] = None
    log_artifacts_url: Optional[str] = None
    log_exp_id: Optional[str] = None
    log_exp_full_parent_run_id: Optional[str] = None
    log_exp_full_final_run_id: Optional[str] = None
    log_exp_excel_parent_run_id: Optional[str] = None
    log_exp_excel_final_run_id: Optional[str] = None
    final_model: Optional[str] = None
    score: Optional[float] = None
    errors: Optional[str] = None
    excel_final_model: Optional[str] = None
    excel_score: Optional[float] = None
    excel_errors: Optional[str] = None


@dataclass_json
@dataclass
class CreateModelRequest(PRTRequest):
    model_config: Optional[ModelConfig] = None
    status_check: bool = False


@dataclass_json
@dataclass
class CreateModelResponse(PRTResponse):
    model_config: Optional[ModelConfig] = None


@dataclass_json
@dataclass
class RegisterModelRequest(PRTRequest):
    model_dir: Optional[str] = None


@dataclass_json
@dataclass
class ModelSearchResult:
    model_name: Optional[str] = None
    latest_v: Optional[int] = None
    latest_v_timestamp: Optional[int] = None
    latest_staging_v: Optional[int] = None
    latest_staging_timestamp: Optional[int] = None
    latest_prod_v: Optional[int] = None
    latest_prod_timestamp: Optional[int] = None


@dataclass_json
@dataclass
class ModelSearchResults:
    results: Optional[List[ModelSearchResult]] = None


@dataclass_json
@dataclass
class SearchModelsRequest(PRTRequest):
    mlflow_tracking_uri: Optional[str] = None
    filter_string_b64: Optional[str] = None
    max_results: int = 100


@dataclass_json
@dataclass
class SearchModelsResponse(PRTResponse):
    model_search_results: Optional[ModelSearchResults] = None


@dataclass_json
@dataclass
class GetModelMetaRequest(PRTRequest):
    mlflow_tracking_uri: Optional[str] = None
    model_uri: Optional[str] = None


@dataclass_json
@dataclass
class GetModelMetaResponse(PRTResponse):
    model_config_json: Optional[str] = None
    prepare_ws_b64: Optional[str] = None


# todo: do we need the below xl model requests?

@dataclass_json
@dataclass
class XLModelRequest(PRTRequest):
    model_conf_path: str = ""
    xl_name: str = ""
    num_rows: int = 1_000


@dataclass_json
@dataclass
class XLModelResponse(PRTResponse):
    xl_path: str = ""


@dataclass_json
@dataclass
class GetMemoryStatRequest(PRTRequest):
    pass


@dataclass_json
@dataclass
class GetMemoryStatResponse(PRTResponse):
    memory_stat: Optional[dict] = None


@dataclass_json
@dataclass
class DeleteKeysRequest(PRTDataRequest):
    keys: Optional[List[str]] = field(
        default=None,
        metadata={
            "validators": (lambda x: x is not None, "No key provided")
        })
    delete_sub_keys: bool = False


@dataclass_json
@dataclass
class ListBucketsRequest(PRTDataRequest):
    pass


@dataclass_json
@dataclass
class ListBucketsResponse(PRTResponse):
    buckets: Optional[List[str]] = None
