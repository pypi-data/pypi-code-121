"""
Data file model class file.

author: Matthew Casey

&copy; [Digital Content Analysis Technology Ltd](https://www.d-cat.co.uk)
"""

import i18n
from marshmallow import Schema, EXCLUDE

from fusion_platform.common.raise_thread import RaiseThread
from fusion_platform.common.utilities import dict_nested_get
from fusion_platform.models import fields
from fusion_platform.models.model import Model, ModelError


# Define the model schema classes. These are maintained from the API definitions.

class DataFileSelectorSchema(Schema):
    """
    Nested schema class for selector, category, data type, unit, format and statistics.
    """
    selector = fields.String(required=True)
    category = fields.String(allow_none=True)
    data_type = fields.String(allow_none=True)
    unit = fields.String(allow_none=True)
    validation = fields.String(allow_none=True)

    area = fields.Decimal(allow_none=True)

    initial_values = fields.List(fields.String(required=True), allow_none=True)
    minimum = fields.Decimal(allow_none=True)
    maximum = fields.Decimal(allow_none=True)
    mean = fields.Decimal(allow_none=True)
    sd = fields.Decimal(allow_none=True)

    histogram_minimum = fields.Decimal(allow_none=True)
    histogram_maximum = fields.Decimal(allow_none=True)
    histogram = fields.List(fields.Decimal(required=True), allow_none=True)

    class Meta:
        """
        When loading an object, make sure we exclude any unknown fields, rather than raising an exception, and put fields in their definition order.
        """
        unknown = EXCLUDE
        ordered = True


class DataFileSchema(Schema):
    """
    Schema class for data file model.

    Each data file model has the following fields (and nested fields):

    .. include::data_file.md
    """
    id = fields.UUID(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    created_at = fields.DateTime(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    updated_at = fields.DateTime(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    organisation_id = fields.UUID(allow_none=True, metadata={'read_only': True, 'title': i18n.t('models.data_file.organisation_id.title'), 'description': i18n.t(
        'models.data_file.organisation_id.description')})  # Added parameter so that it can be used.
    data_id = fields.UUID(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    file_id = fields.UUID(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    file_type = fields.String(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    file_name = fields.String(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    resolution = fields.Integer(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    crs = fields.String(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    bounds = fields.List(fields.Decimal(required=True), allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    area = fields.Decimal(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    mgrs_cells = fields.List(fields.String(required=True), allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    sinusoidal_cells = fields.List(fields.Tuple((fields.Integer, fields.Integer), required=True), allow_none=True,
                                   metadata={'read_only': True})  # Changed to prevent this being updated.

    size = fields.Integer(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    error = fields.Boolean(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    publishable = fields.Boolean(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    alternative = fields.UUID(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    source = fields.UUID(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    selectors = fields.List(fields.Nested(DataFileSelectorSchema()), allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    downloads = fields.Integer(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    title = fields.String(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    description = fields.String(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    class Meta:
        """
        When loading an object, make sure we exclude any unknown fields, rather than raising an exception, and put fields in their definition order.
        """
        unknown = EXCLUDE
        ordered = True


class DataFile(Model):
    """
    DataFile model class providing attributes and methods to manipulate data file details.
    """

    # Override the schema.
    _SCHEMA = DataFileSchema()

    # Override the base model class name.
    _BASE_MODEL_CLASS_NAME = 'Data'  # A string to prevent circular imports.

    # No standard model paths as data file objects cannot be retrieved directly from the API.

    # Add in the custom model paths.
    _PATH_DOWNLOAD_FILE = '/organisations/{organisation_id}/data/{data_id}/download_file/{file_id}'

    def __init__(self, session):
        """
        Initialises the object.

        Args:
            session: The linked session object for interfacing with the Fusion Platform<sup>&reg;</sup>.
        """
        super(DataFile, self).__init__(session)

        # Initialise the fields.
        self.__download_progress = None
        self.__download_thread = None

    def download(self, path, wait=False):
        """
        Downloads the file to the specified path. Optionally waits for the download to complete.

        Args:
            path: The local path to download the file to.
            wait: Optionally wait for the download to complete? Default False.

        Raises:
            RequestError: if the download fails.
        """
        # Make sure no download is currently in progress.
        if self.__download_thread is not None:
            raise ModelError(i18n.t('models.data_file.download_already_in_progress'))

        # Obtain the download URL.
        url = self.download_url()

        # Start the download in a separate thread.
        self.__download_progress = (url, path, 0)
        self.__download_thread = RaiseThread(target=self._session.download_file, args=(url, path, self.__download_callback))
        self.__download_thread.start()

        # Optionally wait for completion.
        self.download_complete(wait=wait)  # Ignore response.

    def __download_callback(self, url, destination, size):
        """
        Callback method used to receive progress from download. Updates the download progress.

        Args:
            url: The URL to download as a file.
            destination: The destination file path.
            size: The total size in bytes so far downloaded.
        """
        self.__download_progress = (url, destination, size)

    def download_complete(self, wait=False):
        """
        Checks whether the download has completed. If an error has occurred during the download, then this will raise a corresponding exception. Optionally waits
        for the download to complete.

        Args:
            wait: Optionally wait for the download to complete? Default False.

        Returns:
            True if the download is complete.

        Raises:
            RequestError: if any request fails.
            ModelError: if no download is in progress.
        """
        # Make sure a download is in progress.
        if self.__download_thread is None:
            raise ModelError(i18n.t('models.data_file.no_download'))

        # Check the download thread. This will raise an exception if an error has occurred.
        finished = False

        try:
            # Join will return immediately because of the timeout, but will raise an exception if something has gone wrong.
            self.__download_thread.join(timeout=None if wait else 0)

            # Check if the thread is still running after the join.
            finished = not self.__download_thread.is_alive()

        except:
            # Something went wrong. Make sure we mark the download as finished and re-raise the error.
            finished = True
            raise

        finally:
            # Make sure we clear the progress and thread if it has finished.
            if finished:
                self.__download_progress = None
                self.__download_thread = None

        return finished

    def download_progress(self):
        """
        Returns current download progress.

        Returns:
            A tuple of the URL, destination and total number of bytes downloaded so far.

        Raies:
            ModelError: if no download is in progress.
        """
        # Make sure a download is in progress.
        if self.__download_thread is None:
            raise ModelError(i18n.t('models.data_file.no_download'))

        return self.__download_progress

    def download_url(self):
        """
        Obtains a URL which can be used to download the file. This URL is only valid for up to 1 hour.

        Raies:
            RequestError: if the request fails.
        """
        response = self._session.request(path=self._get_path(self.__class__._PATH_DOWNLOAD_FILE, file_id=self.file_id, organisation_id=self.organisation_id))

        # Assume that the URL held within the expected key within the resulting dictionary.
        url = dict_nested_get(response, [self.__class__._RESPONSE_KEY_EXTRAS, self.__class__._RESPONSE_KEY_URL])

        if url is None:
            raise ModelError(i18n.t('models.data_file.failed_download_url'))

        return url
