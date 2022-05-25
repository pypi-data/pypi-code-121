# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

""" A series of integration tests """

from pathlib import Path
import json
import logging
import os
import ast
import pydicom
from unittest import TestCase
import requests

from dicom_client import (
    DicomClient,
    TokenCache,
    make_get_token_func,
)

base_url = "https://tonydicom.azurewebsites.net"


class TestsIntegration(TestCase):
    """Testing some basic methods"""

    # -----------------------------------------
    # Set up some defaults for the tests
    # Specify input and output folders for DCM files
    # Specify the URL for the DICOM server
    def setUp(self):
        """ Set up the folder with DCM files """

        self._auth = ast.literal_eval(os.environ["AUTH_CONNECTION_INFO"])
        self._base_url = base_url
        self._output_folder = "./tests/sample_media/output"
        self._input_folder = "./tests/sample_media/input"
        self._input_filename = self._input_folder + "/" + "361_143_100_652.dcm"
        file_metadata = pydicom.filereader.dcmread(self._input_filename)
        study_id = file_metadata.StudyInstanceUID
        self._study_id_for_input_filename = study_id

    # -----------------------------------------
    # Test the ability to delete, upload, and download dcm files
    # Validates by checking a successfully downloaded dcm file
    def test_delete_upload_download_file(self):

        # Testing the upload capability means verfying that files are there and
        # have been uploaded correctly.

        # You can only do that be deleting the test data and then re-inserting it.
        # After re-insert, then download to make sure they are REALLY there.

        # After upload, verify you can download.

        # Get credentials
        token_cache = TokenCache(make_get_token_func(self._auth))
        dicom_client = DicomClient(self._base_url, token_cache)

        # Start with an emtpy output folder
        self.clean_output_folder()

        # Do an upload
        try:
            self.test_delete_study_ids()
            dicom_client.upload_dicom_file(self._input_filename)
        except requests.exceptions.HTTPError as errh:
            logging.error("Http Error: %s", errh)
            raise errh from None
        except requests.exceptions.ConnectionError as errc:
            logging.error("Error Connecting: %s", errc)
            raise errc from None
        except requests.exceptions.Timeout as errt:
            logging.error("Timeout Error: %s", errt)
            raise errt from None
        except requests.exceptions.RequestException as err:
            logging.error("Unknown error type: %s", err)
            raise err from None
        except Exception as err:
            logging.error("Unknown error type: %s", err)
            raise err from None

        # Verify a download is there and available.
        # This code should succeed because we just uploaded a file
        try:
            dicom_client.download_dicom(self._output_folder, self._study_id_for_input_filename)
        except requests.exceptions.HTTPError as errh:
            logging.error("Http Error: %s", errh)
            raise errh from None
        except requests.exceptions.ConnectionError as errc:
            logging.error("Error Connecting: %s", errc)
            raise errc from None
        except requests.exceptions.Timeout as errt:
            logging.error("Timeout Error: %s", errt)
            raise errt from None
        except requests.exceptions.RequestException as err:
            logging.error("Unknown error type: %s", err)
            raise err from None

        # Verify we have only one file
        files = list(Path(self._output_folder).rglob("*.dcm"))
        number_files = len(files)
        # It really is the final number that matters for everything to work!
        assert number_files == 1

    # -----------------------------------------
    # Validate that we can get an oauth_token
    # Assert token is not empty
    def test_oauth_token(self):
        token_cache = TokenCache(make_get_token_func(self._auth))
        oauth_token = token_cache.get_token()
        assert not oauth_token is None

    # -----------------------------------------
    # Validate that we can instantiate DicomClient
    def test_dicom_client(self):
        token_cache = TokenCache(make_get_token_func(self._auth))
        dicom_client = DicomClient(self._base_url, token_cache)
        assert not dicom_client is None

    # -----------------------------------------
    #  Validates that we can delete, upload, and retrieve
    #  DCM files using a study ID
    def test_query_by_patient_id(self):

        token_cache = TokenCache(make_get_token_func(self._auth))
        dicom_client = DicomClient(self._base_url, token_cache)

        self.clean_output_folder()

        self.test_delete_study_ids()

        # Do an upload now
        dicom_client.upload_dicom_folder(self._input_folder)

        # /studies?PatientID=11235813
        study_ids = dicom_client.get_patient_study_ids("ID00042637202184406822975")
        assert "2.25.263916267626722293569390930007441210" == study_ids[0]

    # -----------------------------------------
    # Validates correct response to incorrectly formatted DCM file
    # Demonstrates the use of finding failure "reasons"
    def test_upload_bad_file(self):

        token_cache = TokenCache(make_get_token_func(self._auth))
        dicom_client = DicomClient(self._base_url, token_cache)

        self.clean_output_folder()

        self.test_delete_study_ids()

        # Intentionally try to add a improperly formatted dcm file
        try:
            dicom_client.upload_dicom_file("./tests/sample_media/input/bad_dcm_file/temp.dcm")
        except requests.exceptions.HTTPError as errh:
            # There are more detailed errror codes embedded as JSON in response.text
            # See http://dicom.nema.org/medical/dicom/current/output/chtml/part18/sect_I.2.2.html
            logging.error("Http Error: %s", errh)
            assert errh.response.status_code == 409
            assert (
                json.loads(errh.response.text)["00081198"]["Value"][0]["00081197"]["Value"][0]
                == 43264
            )
        except requests.exceptions.ConnectionError as errc:
            logging.error("Error Connecting: %s", errc)
            raise errc from None
        except requests.exceptions.Timeout as errt:
            logging.error("Timeout Error: %s", errt)
            raise errt from None
        except requests.exceptions.RequestException as err:
            logging.error("Unknown error type: %s", err)
            raise err from None
        except Exception as err:
            logging.error("Unknown error type: %s", err)
            raise err from None

    # -----------------------------------------
    # A test designed to illustrate how to delete cdm files from Dicom Server
    # Intentionally try to download deleted file to demonstrate HTTP response 404
    def test_delete_file(self):

        # Setup so we have one file uploaded. Let's make sure we can delete it using study_id
        token_cache = TokenCache(make_get_token_func(self._auth))
        dicom_client = DicomClient(self._base_url, token_cache)

        try:
            self.test_delete_study_ids()
            dicom_client.upload_dicom_file(self._input_filename)
        except requests.exceptions.HTTPError as errh:
            logging.error("Http Error: %s", errh)
            raise errh from None
        except requests.exceptions.ConnectionError as errc:
            logging.error("Error Connecting: %s", errc)
            raise errc from None
        except requests.exceptions.Timeout as errt:
            logging.error("Timeout Error: %s", errt)
            raise errt from None
        except requests.exceptions.RequestException as err:
            logging.error("Unknown error type: %s", err)
            raise err from None
        except Exception as err:
            logging.error("Unknown error type: %s", err)
            raise err from None

        self.clean_output_folder()

        token_cache = TokenCache(make_get_token_func(self._auth))
        dicom_client = DicomClient(self._base_url, token_cache)
        try:
            dicom_client.delete_dicom(self._study_id_for_input_filename)
        except requests.exceptions.HTTPError as errh:
            logging.error("Http Error: %s", errh)
            raise errh from None
        except requests.exceptions.ConnectionError as errc:
            logging.error("Error Connecting: %s", errc)
            raise errc from None
        except requests.exceptions.Timeout as errt:
            logging.error("Timeout Error: %s", errt)
            raise errt from None
        except requests.exceptions.RequestException as err:
            logging.error("Unknown error type: %s", err)
            raise err from None

        # This attempted download should fail, resulting in a 404
        try:
            dicom_client.download_dicom(self._output_folder, self._study_id_for_input_filename)
        except requests.exceptions.HTTPError as errh:
            logging.error("Http Error: %s", errh)
            # We better fail at the download because we deleted the dcm file
            assert errh.response.status_code == 404
        except requests.exceptions.ConnectionError as errc:
            logging.error("Error Connecting: %s", errc)
            raise errc from None
        except requests.exceptions.Timeout as errt:
            logging.error("Timeout Error: %s", errt)
            raise errt from None
        except requests.exceptions.RequestException as err:
            logging.error("Unknown error type: %s", err)
            raise err from None

        # We have deleted the output folder. We should still have 0
        # as the download should fail.
        files = list(Path(self._output_folder).rglob("*.dcm"))
        number_files = len(files)
        # It really is the final number that matters for everything to work!
        assert number_files == 0

    # -----------------------------------------
    # Demonstrates how you can download multiple dcm files
    # bypassing in a single study ID
    def test_delete_upload_download(self):

        # Get some credentials
        token_cache = TokenCache(make_get_token_func(self._auth))
        dicom_client = DicomClient(self._base_url, token_cache)

        self.clean_output_folder()

        self.test_delete_study_ids()

        # Do an upload now
        dicom_client.upload_dicom_folder(self._input_folder)

        # Verify a download is there.
        # No try/except needed because we know these study ids are in the DICOM server
        dicom_client.download_dicom(
            self._output_folder, "2.25.263916267626722293569390930007441210"
        )
        dicom_client.download_dicom(
            self._output_folder, "2.25.185320577304339382525212889304442143"
        )
        files = list(Path(self._output_folder).rglob("*.dcm"))
        number_files = len(files)
        # It really is the final number that matters for everything to work!
        assert number_files == 9

    # =============================================
    # Helper Methods
    # =============================================

    # -----------------------------------------
    # A test to demonstrate unexpected delete failures
    # This code demonstrates how to implement a delete functionality and deal with http 404s
    def test_delete_study_ids(self):
        """ Hard Coded Test that we can delete matching DCM files from DICOM server """
        token_cache = TokenCache(make_get_token_func(self._auth))
        dicom_client = DicomClient(self._base_url, token_cache)

        try:
            dicom_client.delete_dicom(
                "1.3.6.1.4.1.14519.5.2.1.6834.5010.465205689126985052184293614571"
            )
        except requests.exceptions.HTTPError as errh:
            logging.error("Http Error: %s", errh)
            # For error 404, don't re-raise.
            # No expectation that dcm being deleted is there already.
            if errh.response.status_code != 404:
                raise errh from None
        except requests.exceptions.ConnectionError as errc:
            logging.error("Error Connecting: %s", errc)
            raise errc from None
        except requests.exceptions.Timeout as errt:
            logging.error("Timeout Error: %s", errt)
            raise errt from None
        except requests.exceptions.RequestException as err:
            logging.error("Unknown error type: %s", err)
            raise err from None

        try:
            dicom_client.delete_dicom("2.25.263916267626722293569390930007441210")
        except requests.exceptions.HTTPError as errh:
            logging.error("Http Error: %s", errh)
            # For error 404, don't re-raise.
            # No expectation that dcm being deleted is there already.
            if errh.response.status_code != 404:
                raise errh from None
        except requests.exceptions.ConnectionError as errc:
            logging.error("Error Connecting: %s", errc)
            raise errc from None
        except requests.exceptions.Timeout as errt:
            logging.error("Timeout Error: %s", errt)
            raise errt from None
        except requests.exceptions.RequestException as err:
            logging.error("Unknown error type: %s", err)
            raise err from None

        try:
            dicom_client.delete_dicom("2.25.185320577304339382525212889304442143")
        except requests.exceptions.HTTPError as errh:
            logging.error("Http Error: %s", errh)
            # For error 404, don't re-raise.
            # No expectation that dcm being deleted is there already.
            if errh.response.status_code != 404:
                raise errh from None
        except requests.exceptions.ConnectionError as errc:
            logging.error("Error Connecting: %s", errc)
            raise errc from None
        except requests.exceptions.Timeout as errt:
            logging.error("Timeout Error: %s", errt)
            raise errt from None
        except requests.exceptions.RequestException as err:
            logging.error("Unknown error type: %s", err)
            raise err from None

        try:
            dicom_client.delete_dicom("1.2.276.0.50.192168001092.11517584.14547392.4")
        except requests.exceptions.HTTPError as errh:
            logging.error("Http Error: %s", errh)
            # For error 404, don't re-raise.
            # No expectation that dcm being deleted is there already.
            if errh.response.status_code != 404:
                raise errh from None
        except requests.exceptions.ConnectionError as errc:
            logging.error("Error Connecting: %s", errc)
            raise errc from None
        except requests.exceptions.Timeout as errt:
            logging.error("Timeout Error: %s", errt)
            raise errt from None
        except requests.exceptions.RequestException as err:
            logging.error("Unknown error type: %s", err)
            raise err from None
        return True

    # -----------------------------------------
    # A helper method to simply clear out the output folder
    def clean_output_folder(self):
        """ Remove DCM files on disk from a folder """
        files = list(Path(self._output_folder).rglob("*.dcm"))
        for file in files:
            os.remove(file)
