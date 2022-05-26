"""Ascend SDK Client"""

import sys
import os
import configparser
import importlib.util
from importlib.machinery import ModuleSpec
from google.protobuf.message import Message
from google.protobuf.json_format import ParseDict, MessageToDict

# remove paths added by Bazel in a test environment
sys.path = [path for path in sys.path if not path.endswith("cli.runfiles") and not path.endswith("ascend/sdk")]

# protoc_gen_swagger is on `PYTHONPATH` when run under `bazel` but not
# when installed as a pip package. We move protoc_gen_swagger under our package
# when creating the pip artifacts and then manually add it to the path since references
# within the package still expect it to be a top-level package.

try:
  import protoc_gen_swagger  # noqa: F401
except Exception:
  import ascend.sdk.version
  path = os.path.normpath(os.path.join(os.path.dirname(ascend.sdk.version.__file__), "..", "external"))
  sys.path.insert(0, path)

import ascend.openapi.python_path  # noqa: E402

# We don't use the openapi-generated model classes, and hence remove them
# from our distribution. The generated code still wants to import the models package
# (even though it doesn't need any submodules or classes) so we synthesize it here.

models = importlib.util.module_from_spec(ModuleSpec("openapi_client.models", loader=None))
sys.modules["openapi_client.models"] = models

model = importlib.util.module_from_spec(ModuleSpec("openapi_client.model", loader=None))
sys.modules["openapi_client.model"] = model

import ascend.protos.api.api_pb2  # noqa: E402
from ascend.auth.session import Session  # noqa: E402

from openapi_client.api_client import ApiClient  # noqa: E402
from openapi_client.api.ascend_api import AscendApi  # noqa: E402
from openapi_client.configuration import Configuration  # noqa: E402
from openapi_client.exceptions import ApiException  # noqa:F401,E402
from openapi_client.exceptions import ApiKeyError  # noqa: F401,E402
from openapi_client.exceptions import ApiTypeError  # noqa: F401,E402
from openapi_client.exceptions import ApiValueError  # noqa: F401,E402
from openapi_client.exceptions import OpenApiException  # noqa: F401,E402

_HOSTNAME_SUFFIX = ".ascend.io"

# Monkey-patch to always use proto deserialization of JSON for api protos.


def __deserialize(self, data, klass):
  # We don't expect any generic objects to be deserialized
  if klass == "object":
    raise Exception(data)

  # We expect all class names to start with Api because they are
  # protos in the api package.
  if not klass.startswith("Api"):
    raise Exception(klass)

  class_name = klass[3:]
  cls = getattr(ascend.protos.api.api_pb2, class_name)
  return ParseDict(data, cls(), ignore_unknown_fields=True)


setattr(ApiClient, "_ApiClient__deserialize", __deserialize)

# Monkey-patch to serialize using standard protobuf serialization. In
# the openapi-generated stubs, this method is used to serialize
# generic objects as well as protos so we need to use the default
# mechanism if the parameter is not some type of message.  This would
# not do the right thing if the parameter was a POPO with messages as
# fields but this should never happen.

setattr(ApiClient, "orig_sanitize_for_serialization", getattr(ApiClient, "sanitize_for_serialization"))


def sanitize_for_serialization(self, obj):
  if isinstance(obj, Message):

    # The API server currently cannot always handle lowerCamelCase
    # field names so we always send snake_case.

    dict = MessageToDict(obj, preserving_proto_field_name=True)

    return dict
  else:
    return self.orig_sanitize_for_serialization(obj)


setattr(ApiClient, "sanitize_for_serialization", sanitize_for_serialization)

# Helper class to make setup/configuration easier.

_openapi_override_methods = []


def override_openapi(method):
  _openapi_override_methods.append(method.__name__)
  return method


class Client:
  """The SDK Client used to communicate with and access the Ascend service."""
  def __init__(self, hostname=None, access_key=None, secret_key=None, verify_ssl=True):
    """Get/create a new SDK client instance.

    If `access_key` and `secret_key` are not specified, the client looks for credentials
    in a file `~/.ascend/credentials` with the following example format -
    `[trial]
    ascend_access_key_id=<your_key_id_here>
    ascend_secret_access_key=<your_secret_key_here>`

    Parameters:
    - hostname: Ascend hostname
    - access_key (optional): Access key
    - secret_key (optional): Secret key
    - verify_ssl (optional): Enable verification of server's SSL certificate
    (`True` by default).
    Returns: a new SDK client instance.
    """
    if not hostname:
      raise ValueError("Must specify hostname")
    elif not hostname.endswith(_HOSTNAME_SUFFIX):
      raise ValueError(f"Invalid hostname {hostname}: " f"must follow format <SOMETHING>{_HOSTNAME_SUFFIX}")
    self.hostname = hostname

    if not access_key or not secret_key:
      access_key, secret_key, verify_ssl = _get_credentials(hostname, verify_ssl)

    self._session = Session(hostname, access_key, secret_key, verify_ssl)

    self._configuration = Configuration(
        host=f"https://{hostname}",
        api_key={"Authorization": None},
        api_key_prefix={"Authorization": "Bearer"},
    )

    self._configuration.verify_ssl = verify_ssl
    self._configuration.refresh_api_key_hook = self._session.refresh_api_key_hook
    self._configuration.debug = False

    self._api_client = ApiClient(self._configuration)

    # We set a header the API server uses to ensure standard-formatted
    # JSON. As of this writing, the API server sometime uses
    # non-standard JSON but we need to upgrade the FE at the same time
    # as making it standards compliant.

    self._api_client.set_default_header("Ascend-Json-Format", "protojson")

    # The "Ascend" in the name of this class is a result of using the
    # Ascend tag in the proto/openapi spec.

    self.openapi_client = AscendApi(self._api_client)
    for method in _openapi_override_methods:
      assert hasattr(self.openapi_client, method), f"openapi client does not have method {method}"

  def close(self):
    self._api_client.close()

  def __getattr__(self, name):
    return getattr(self.openapi_client, name)

  def __enter__(self):
    return self.openapi_client

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.close()

  @override_openapi
  def download_logs(self, *args, **kwargs):
    # openapi wants to decode everything as utf8, the raw response is good enough here
    return self.openapi_client.download_logs(*args, **{'_preload_content': False, **kwargs})


def _get_credentials(hostname: str, verify_ssl=True):
  if hostname.endswith(_HOSTNAME_SUFFIX):
    profile = hostname[:-len(_HOSTNAME_SUFFIX)]
  else:
    raise ValueError(f"Invalid hostname {hostname}: " f"must follow format <SOMETHING>{_HOSTNAME_SUFFIX}")

  config = configparser.ConfigParser()

  access_key = os.environ.get("ASCEND_ACCESS_KEY_ID")
  secret_key = os.environ.get("ASCEND_SECRET_ACCESS_KEY")

  if not access_key and not secret_key:
    config.read(os.path.expanduser("~/.ascend/credentials"))
    try:
      access_key = config.get(profile, "ascend_access_key_id")
      secret_key = config.get(profile, "ascend_secret_access_key")
      verify_ssl = config.getboolean(profile, "verify_ssl", fallback=verify_ssl)
    except Exception as e:
      raise ValueError('Unable to obtain credential from config') from e

  if not access_key or not secret_key:
    raise ValueError("Must have credentials to build client.")

  return access_key, secret_key, verify_ssl
