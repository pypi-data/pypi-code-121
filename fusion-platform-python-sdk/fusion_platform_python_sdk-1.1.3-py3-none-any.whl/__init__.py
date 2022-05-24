"""
This package contains the Python SDK used to interact with the Fusion Platform<sup>&reg;</sup>. The Fusion Platform<sup>&reg;</sup> provides enhanced remote monitoring services. By ingesting
remotely sensed Earth Observation (EO) data, and data from other sources, the platform uses and fuses this data to execute algorithms which provide actionable
knowledge to customers.

The Python SDK is designed to enable interaction with the Fusion Platform<sup>&reg;</sup> via its API. As such, the SDK therefore allows software to login, upload
files, create and execute processes, monitor their execution and then download the corresponding results. Additional functionality is available directly via the
API, and this is defined within the corresponding OpenAPI 3.0 specification, which can be obtained via a support request.

&copy; [Digital Content Analysis Technology Ltd](https://www.d-cat.co.uk)
"""

# Do not modify the following two lines as they are maintained by the version.sh script.
__version__ = '1.1.3'
__version_date__ = '2022-05-24T06:21:42Z'

# Exclude certain sub-modules from documentation.
# @formatter:off
__pdoc__ = {
    'base': False,
    'command': False,
    'common': False,
    'documentation': False,
    'localisations': False,
    'localise': False,
    'translations': False,
    'models.credit.CreditSchema.Meta': False,
    'models.credit.CreditSchema.opts': False,
    'models.credit.CreditSsdsSchema': False,
    'models.data.DataSchema.Meta': False,
    'models.data.DataSchema.opts': False,
    'models.data.DataIngesterSchema': False,
    'models.data_file.DataFileSchema.Meta': False,
    'models.data_file.DataFileSchema.opts': False,
    'models.data_file.DataFileSelectorSchema': False,
    'models.fields': False,
    'models.organisation.OrganisationSchema.Meta': False,
    'models.organisation.OrganisationSchema.opts': False,
    'models.organisation.OrganisationUserSchema': False,
    'models.process.ProcessSchema.Meta': False,
    'models.process.ProcessSchema.opts': False,
    'models.process.OptionDataTypeSchema': False,
    'models.process.ProcessChainOptionSchema': False,
    'models.process.ProcessChainSchema': False,
    'models.process.ProcessInputSchema': False,
    'models.process.ProcessOptionSchema': False,
    'models.process.ProcessSelectorSchema': False,
    'models.process_execution.ProcessExecutionSchema.Meta': False,
    'models.process_execution.ProcessExecutionSchema.opts': False,
    'models.process_execution.ProcessExecutionChainOptionSchema': False,
    'models.process_execution.ProcessExecutionChainSchema': False,
    'models.process_execution.ProcessExecutionOptionSchema': False,
    'models.process_service_execution.ProcessServiceExecutionSchema.Meta': False,
    'models.process_service_execution.ProcessServiceExecutionSchema.opts': False,
    'models.process_service_execution.ProcessServiceExecutionActionSchema': False,
    'models.process_service_execution.ProcessServiceExecutionActionValueSchema': False,
    'models.process_service_execution.ProcessServiceExecutionActionsSchema': False,
    'models.process_service_execution.ProcessServiceExecutionMetricSchema': False,
    'models.process_service_execution.ProcessServiceExecutionOptionSchema': False,
    'models.process_service_execution_log.ProcessServiceExecutionLogSchema.Meta': False,
    'models.process_service_execution_log.ProcessServiceExecutionLogSchema.opts': False,
    'models.service.ServiceSchema.Meta': False,
    'models.service.ServiceSchema.opts': False,
    'models.service.ServiceActionSchema': False,
    'models.service.ServiceActionValueSchema': False,
    'models.service.ServiceDefinitionLinkageSchema': False,
    'models.service.ServiceDefinitionSchema': False,
    'models.service.ServiceInputExpressionSchema': False,
    'models.service.ServiceOptionExpressionSchema': False,
    'models.service.ServiceValidationSchema': False,
    'models.user.UserSchema.Meta': False,
    'models.user.UserSchema.opts': False,
    'models.user.UserOrganisationSchema': False,
}
# @formatter:on

# Logging constant.
FUSION_PLATFORM_LOGGER = 'fusion_platform'

# Option data types.
DATA_TYPE_NUMERIC = 'numeric'
DATA_TYPE_CURRENCY = 'currency'
DATA_TYPE_BOOLEAN = 'boolean'
DATA_TYPE_DATETIME = 'datetime'
DATA_TYPE_STRING = 'string'
DATA_TYPE_CONSTRAINED = 'constrained'

# File types.
FILE_TYPE_GEOTIFF = 'GeoTIFF'
FILE_TYPE_JPEG2000 = 'JPEG2000'
FILE_TYPE_DEM = 'DEM'
FILE_TYPE_GEOJSON = 'GeoJSON'
FILE_TYPE_KML = 'KML'
FILE_TYPE_KMZ = 'KMZ'
FILE_TYPE_CSV = 'CSV'
FILE_TYPE_ESRI_SHAPEFILE = 'ESRI Shapefile'
FILE_TYPE_JPEG = 'JPEG'
FILE_TYPE_PNG = 'PNG'
FILE_TYPE_OTHER = 'Other'

# Run types.
RUN_TYPE_RUN_ONCE = 'run_once'
RUN_TYPE_RUN_SCHEDULE = 'run_schedule'

# Imports.
import logging
import os

from .session import Session
from .models.user import User

# Find the package root directory.
PACKAGE_DIR = os.path.dirname(__file__)

# Example files.
# Lake district boundary provided from data.gov.uk. Contains public sector information licensed under the Open Government Licence v3.0:
# https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
EXAMPLE_GLASGOW_FILE = os.path.join(PACKAGE_DIR, 'glasgow.geojson')
EXAMPLE_LAKE_DISTRICT_FILE = os.path.join(PACKAGE_DIR, 'lake_district.geojson')


# Module-level methods.
def get_log_level():
    """
    Gets the logging level for the SDK.

    Returns:
        The current log level, as specified by the logging package.
    """
    logger = logging.getLogger(FUSION_PLATFORM_LOGGER)

    return logger.level


def login(email=None, user_id=None, password=None, api_url=None):
    """
    Attempts to log into the Fusion Platform<sup>&reg;</sup> to return a user model for the active session.

    Args:
        email: The user account email address. Either an email address or a user id must be provided.
        user_id: The user account user id. Either an email address or a user id must be provided.
        password: The password for the user account.
        api_url: The optional custom API URL to use. Defaults to the production Fusion Platform<sup>&reg;</sup>.

    Returns:
        The corresponding user model for the account on successful login.

    Raises:
        ValueError: on incorrect parameters.
        RequestError: on login failure.
    """
    # Create the session and attempt to login.
    session = Session()
    session.login(email, user_id, password, api_url)

    # Now load the corresponding user model using the user id obtained from the session.
    return User._model_from_api_id(session, id=session.user_id)


def set_log_level(level):
    """
    Sets the logging level for the SDK.

    Args:
        level: The required log level, as specified by the logging package. For example,
    """
    logger = logging.getLogger(FUSION_PLATFORM_LOGGER)
    logger.setLevel(level)
