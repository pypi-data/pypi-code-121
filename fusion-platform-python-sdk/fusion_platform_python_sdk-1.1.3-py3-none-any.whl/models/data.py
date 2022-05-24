"""
Data model class file.

author: Matthew Casey

&copy; [Digital Content Analysis Technology Ltd](https://www.d-cat.co.uk)
"""

import i18n
from marshmallow import Schema, EXCLUDE
import os
from time import sleep

from fusion_platform.common.raise_thread import RaiseThread
from fusion_platform.common.utilities import dict_nested_get
from fusion_platform.models import fields
from fusion_platform.models.data_file import DataFile
from fusion_platform.models.model import Model, ModelError
from fusion_platform.session import Session


# Define the model schema classes. These are maintained from the API definitions.

class DataIngesterSchema(Schema):
    """
    Nested schema class for ingesters.
    """
    ingester_id = fields.UUID(required=True)
    dates = fields.List(fields.DateTime(required=True), required=True)

    class Meta:
        """
        When loading an object, make sure we exclude any unknown fields, rather than raising an exception, and put fields in their definition order.
        """
        unknown = EXCLUDE
        ordered = True


class DataSchema(Schema):
    """
    Schema class for data model.

    Each data has the following fields (and nested fields):

    .. include::data.md
    """
    id = fields.UUID(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    created_at = fields.DateTime(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    updated_at = fields.DateTime(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    organisation_id = fields.UUID(required=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    name = fields.String(required=True)

    # Removed lock.
    unlinked = fields.String(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    ingester_availability = fields.List(fields.Nested(DataIngesterSchema()), allow_none=True,
                                        metadata={'read_only': True})  # Changed to prevent this being updated.

    # Removed link_id.
    # Removed link_model.
    # Removed link_hash.

    uploaded_organisation_id = fields.UUID(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.
    deletable = fields.String(allow_none=True, metadata={'read_only': True})  # Changed to prevent this being updated.

    # Removed creator.

    class Meta:
        """
        When loading an object, make sure we exclude any unknown fields, rather than raising an exception, and put fields in their definition order.
        """
        unknown = EXCLUDE
        ordered = True


class Data(Model):
    """
    Data model class providing attributes and methods to manipulate data item details.
    """

    # Override the schema.
    _SCHEMA = DataSchema()

    # Override the base model class name.
    _BASE_MODEL_CLASS_NAME = 'Organisation'  # A string to prevent circular imports.

    # Base path.
    _PATH_ROOT = '/organisations/{organisation_id}/data'
    _PATH_BASE = f"{_PATH_ROOT}/{{data_id}}"

    # Override the standard model paths.
    _PATH_CREATE = _PATH_ROOT
    _PATH_DELETE = _PATH_BASE
    _PATH_GET = _PATH_BASE
    _PATH_NEW = f"{_PATH_ROOT}/new"
    _PATH_PATCH = _PATH_BASE

    # Add in the custom model paths.
    _PATH_ADD_FILE = f"{_PATH_BASE}/add_file"
    _PATH_FILES = f"{_PATH_BASE}/files"

    # Response keys.
    _RESPONSE_KEY_FILE = 'file'

    def __init__(self, session):
        """
        Initialises the object.

        Args:
            session: The linked session object for interfacing with the Fusion Platform<sup>&reg;</sup>.
        """
        super(Data, self).__init__(session)

        # Initialise the fields.
        self.__upload_threads = {}

    def __add_file(self, file_type, file):
        """
        Attempts to add a file to the data object and then starts its upload. The file is uploaded using a thread.

        Args:
            file_type: The type of file to add.
            file: The path to the file to add.

        Raises:
            RequestError: if the add fails.
        """
        # Make sure the file exists.
        if not os.path.exists(file):
            raise ModelError(i18n.t('models.data.failed_add_missing_file', file=file))

        # Add the file to the data model.
        body = {self.__class__.__name__: {'name': os.path.basename(file), 'file_type': file_type}}
        response = self._session.request(path=self._get_path(self.__class__._PATH_ADD_FILE), method=Session.METHOD_POST, body=body)

        # Assume that the file id is held within the expected key within the resulting dictionary.
        file_id = dict_nested_get(response, [self.__class__._RESPONSE_KEY_EXTRAS, self.__class__._RESPONSE_KEY_FILE])

        if file_id is None:
            raise ModelError(i18n.t('models.data.failed_add_file_id'))

        # Assume that the URL held within the expected key within the resulting dictionary.
        url = dict_nested_get(response, [self.__class__._RESPONSE_KEY_EXTRAS, self.__class__._RESPONSE_KEY_URL])

        if url is None:
            raise ModelError(i18n.t('models.data.failed_add_file_url'))

        # Make sure the file is unique so that we can keep track of it.
        if file_id in self.__upload_threads:
            raise ModelError(i18n.t('models.data.failed_add_file_not_unique'))

        # Create and start a thread for the upload.
        thread = None

        try:
            thread = RaiseThread(target=self._session.upload_file, args=(url, file))
            thread.start()

        finally:
            # Make sure we record the thread so we can monitor it, even if it fails.
            self.__upload_threads[file_id] = thread

    def check_analysis_complete(self, wait=False):
        """
        Checks that the analysis of all files associated with this data object is complete. Optionally waits for the analysis to complete.

        Args:
            wait: Optionally wait for the analysis to complete? Default False.

        Returns:
            True if the analysis is complete for all files.

        Raises:
            RequestError: if any get fails.
            ModelError: if a model could not be loaded or validated from the Fusion Platform<sup>&reg;</sup>.
        """
        while True:
            complete = True

            # Load in each of the file models and check that every file has been uploaded, and has a publishable or error field to indicate that the analysis is
            # complete.
            for file in self.files:
                self._logger.debug('file %s: %s', file.file_name, file.attributes)

                has_fields = hasattr(file, self.__class__._FIELD_SIZE) and (
                        hasattr(file, self.__class__._FIELD_PUBLISHABLE) or hasattr(file, self.__class__._FIELD_ERROR))

                if not has_fields:
                    self._logger.debug('file %s not yet analysed', file.file_name)
                    complete = False
                    break

            # Break the loop if we are not waiting or are complete.
            if (not wait) or complete:
                break

            # We are waiting, so block for a short while.
            sleep(self.__class__._API_UPDATE_WAIT_PERIOD)

        return complete

    def _create(self, name, file_type, files, wait=False):
        """
        Attempts to create the model object with the given values. This assumes the model template has been loaded first using the _new method, and that the model
        is then created using a POST RESTful request. This assumes that the post body contains key names which include the name of the model class.

        This method is overridden to also upload the corresponding files and optionally wait for the upload and analysis to complete.

        Args:
        name: The name of the data object.
        file_type: The type of files that the data object will hold.
        files: The list of file paths to be uploaded.
        wait: Optionally wait for the upload and analysis to complete? Default False.

        Returns:
            The created data object.

        Raises:
            RequestError: if the create fails.
            ModelError: if the model could not be created and validated by the Fusion Platform<sup>&reg;</sup>.
        """
        # Use the super method to create the data item with the correct attributes. This will raise an exception if anything fails.
        super(Data, self)._create(name=name)

        # Add each of the files, assuming that each is of the same file type, and start its upload in a thread.
        try:
            for file in files:
                self.__add_file(file_type, file)

        finally:
            # Optionally wait for completion. We must complete this even if an exception has occurred because there may be multiple files. However, we only do this
            # if any threads were started.
            if len(self.__upload_threads) > 0:
                self.create_complete(wait=wait)  # Ignore response.

    def create_complete(self, wait=False):
        """
        Checks whether the data object file(s) upload and analysis have completed. If an error has occurred during the upload and analysis, then this will raise
        a corresponding exception. Optionally waits for the upload and analysis to complete.

        Note, a failure of one file upload will not stop the upload of other files. Therefore, if an exception is raised, further calls to this method are required
        until all upload and analysis (or errored) has completed and this method returns True.

        Args:
            wait: Optionally wait for the upload and analysis to complete? Default False.

        Returns:
            True if the upload and analysis are complete for all files.

        Raises:
            RequestError: if any request fails.
            ModelError: if the upload or analysis failed.
        """
        # Make sure a create is in progress.
        if len(self.__upload_threads) <= 0:
            raise ModelError(i18n.t('models.data.no_create'))

        # Check the upload threads. This will raise an exception if an error has occurred.
        first_error = None

        for file_id, thread in self.__upload_threads.items():
            if thread is not None:
                thread_finished = False

                try:
                    # Join will return immediately because of the timeout, but will raise an exception if something has gone wrong.
                    thread.join(timeout=None if wait else 0)

                    # Check if the thread is still running after the join.
                    thread_finished = not thread.is_alive()

                except Exception as e:
                    # Something went wrong. Make sure we mark the upload as finished.
                    thread_finished = True

                    # If we are waiting for everything to complete, then we must not re-raise the error here so that everything else can be completed first.
                    # Instead, we save the error off and raise it later.
                    if wait:
                        first_error = e if first_error is None else first_error
                    else:
                        raise

                finally:
                    # Make sure we clear the thread if it has finished.
                    if thread_finished:
                        self.__upload_threads[file_id] = None

        # Have all the uploads finished?
        uploads_finished = all([value is None for value in self.__upload_threads.values()])

        # Now check whether the analysis has completed. We do this in a loop so that we can wait until completion, but break out if we are not waiting. If an
        # error occurs, then we assume that the analysis is complete to prevent indefinitely waiting.
        complete = False

        try:
            if uploads_finished:
                complete = self.check_analysis_complete(wait=wait)

        except Exception as e:
            # An error occurred, make sure we treat this as complete to prevent an indefinite loop.
            complete = True

            # If we already have an error to raise, make sure we do not overwrite it.
            first_error = e if first_error is None else first_error

        finally:
            if complete:
                # Tidy up any finished threads. This will allow us to indicate that everything is complete.
                self.__upload_threads = {file_id: thread for file_id, thread in self.__upload_threads.items() if thread is not None}

        # If we encountered an error, make sure we raise it.
        if first_error is not None:
            raise first_error

        return len(self.__upload_threads) <= 0

    @property
    def files(self):
        """
        Provides an iterator through the data object's files.

        Returns:
            An iterator through the data object's files.

        Raises:
            RequestError: if any get fails.
            ModelError: if a model could not be loaded or validated from the Fusion Platform<sup>&reg;</sup>.
        """
        return DataFile._models_from_api_path(self._session, self._get_path(self.__class__._PATH_FILES), organisation_id=self.organisation_id)
