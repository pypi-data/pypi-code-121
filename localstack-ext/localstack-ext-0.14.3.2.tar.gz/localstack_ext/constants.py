from localstack_ext import __version__

# version of localstack-ext
# TODO deprecated - use localstack-ext.__version__ instead
VERSION = __version__

# default expiry seconds for Cognito access tokens
TOKEN_EXPIRY_SECONDS = 24 * 60 * 60

# name of Docker registry for Lambda images
DEFAULT_LAMBDA_DOCKER_REGISTRY = "localstack/lambda"

# request path for local pod management API
API_PATH_PODS = "/_pods"

# name of S3 bucket containing assets that are lazily downloaded - TODO: unify assets bucket layout/naming
ASSETS_S3_BUCKET = "localstack-web-assets"

# default Spark version
DEFAULT_SPARK_VERSION = "2.4.3"
# folder to persist static fields in RegionBackend and moto backend classes
STATIC_DETAILS_FOLDER_NAME = "static"
# folder to persist miscellaneous global fields used in different API implementations
EXTENDED_DETAILS_FOLDER_NAME = "extended"
REGION_STATE_FILE = "region_state"
SHARED_STATE_FILE = "shared_state"
MOTO_BACKEND_STATE_FILE = "backend_state"
UPDATE_HTTP_METHODS = ["POST", "PUT", "DELETE", "PATCH"]
