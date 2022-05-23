import os


class ElboResources:
    #
    # Server endpoints
    #
    UPLOAD_URL_ENDPOINT = "upload_url"
    FILE_RECEIVER = "file_receiver"
    SCHEDULE_ENDPOINT = "schedule"
    PROVISION_ENDPOINT = "provision"
    CREATE_ENDPOINT = "create"
    LOGS_ENDPOINT = "logs"
    RESOURCE_ENDPOINT = "resource"
    DASHBOARD_ENDPOINT = "dashboard"
    SIGNUP_ENDPOINT = "signup"
    STATUS_ENDPOINT = "status"
    TASKS_ENDPOINT = "tasks"
    SHOW_ENDPOINT = "show"
    BALANCE_ENDPOINT = "balance"
    REMOVE_ENDPOINT = "rm"
    CANCEL_ENDPOINT = "cancel"
    EXCEPTION_REPORT_ENDPOINT = "exception_report"
    WANDB_DIRECTORY = "wandb"
    WORKSPACE_DIRECTORY = "workspace"
    OBJECT_INFO = "object_info"

    TASK_SUBMISSION_PREFIX = "submissions"

    # 100Mb
    LARGE_FILE_SIZE = 1024 * 1024 * 100
    # 4 Mb
    LARGE_FILE_UPLOAD_CHUNK_SIZE = 4 * 1024 * 1024

    ELBO_TOKEN_FILE = os.path.expanduser("~/.elbo/token")
    ELBO_CACHE_DIR = os.path.expanduser("~/.elbo/cache")
