# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""The main DicomClient object"""
from io import BytesIO
from pathlib import Path
import errno as _errno
import hashlib
import logging
import os
import pathlib
import pydicom
from urllib3.filepost import encode_multipart_formdata, choose_boundary
from abc import ABC, abstractmethod
import requests
import requests_toolbelt as tb


class DicomClientInterface(ABC):
    """Abstract base class that represents the interface to DicomClient()"""

    @abstractmethod
    def __init__(self, base_url, token_cache):
        """Constructor providing DICOM server URL and token cache object"""

    @abstractmethod
    def upload_dicom_folder(self, folder_name):
        """Upload DCM files from folder"""

    @abstractmethod
    def upload_dicom_file(self, file_name):
        """Upload a single DCM file"""

    @abstractmethod
    def delete_dicom(self, study_id, series_id=None, instance_id=None):
        """Delete DCM files and DICOM server"""

    @abstractmethod
    def download_dicom(self, output_folder, study_id, series_id=None, instance_id=None):
        """Download DCM files from DICOM server"""

    @abstractmethod
    def get_patient_study_ids(self, patient_id):
        """Get a collection of study IDs based on patient ID"""


class DicomClient(DicomClientInterface):

    """Supports upload, download, delete of DCM Files"""

    # ===========================================================
    def __init__(self, base_url, token_cache):
        """ Initialize """
        super().__init__(base_url, token_cache)
        self._base_url = base_url
        self._token_cache = token_cache

    # -------------------------------------------------
    # Core methods
    # -------------------------------------------------
    def upload_dicom_folder(self, folder_name):
        """Upload DCM files from a folder"""
        # Validate folder exists and has files
        self.validate_folder_name(folder_name)
        # Upload folder
        response = self.do_upload_dicom_folder(folder_name)
        return response

    def upload_dicom_file(self, file_name):
        """ Upload a single DCM file """
        self.validate_file_name(file_name)
        response = self.do_upload_dicom_file(file_name)
        return response

    def delete_dicom(self, study_id, series_id=None, instance_id=None):
        """ Delete Dicom Entries """
        response = self.do_delete_dicom(study_id, series_id, instance_id)
        return response

    def download_dicom(self, output_folder, study_id, series_id=None, instance_id=None):
        """ Download DCM Files """
        self.validate_output_folder(output_folder)
        response, _ = self.do_download_dicom(output_folder, study_id, series_id, instance_id)
        return response

    def get_patient_study_ids(self, patient_id):
        """ Download DCM Files """
        patient_id = "ID00042637202184406822975"
        response = self.do_get_patient_study_ids(patient_id)
        # 0020000D is the reference to the array of study ids for a patient id
        return response.json()[0]["0020000D"]["Value"]

    # -------------------------------------------------
    # Validations
    # -------------------------------------------------
    def validate_output_folder(self, output_folder):
        # Make sure folder exists
        if not os.path.isdir(output_folder):
            raise FileNotFoundError(
                _errno.ENOENT, "Upload folder not found = {}".format(output_folder)
            ) from None

    # -------------------------------------------------
    def validate_folder_name(self, folder_name):
        # Make sure folder exists
        if not os.path.isdir(folder_name):
            raise FileNotFoundError(
                _errno.ENOENT, "Upload folder not found = {}".format(folder_name)
            ) from None
        # Make sure files in folder exists
        files = list(Path(folder_name).rglob("*.dcm"))
        if len(files) == 0:
            raise FileNotFoundError(
                _errno.ENOENT, "No files in folder = {}".format(folder_name)
            ) from None

    # -------------------------------------------------
    def validate_file_name(self, file_name):
        """Validate that local file name exists"""
        if not os.path.isfile(file_name):
            raise FileNotFoundError(
                _errno.ENOENT, "Upload file not found = {}".format(file_name)
            ) from None

    # -------------------------------------------------
    # Supporting methods: OAUTH and Tokens
    # -------------------------------------------------
    def get_token(self):
        """Retrieve a wealth token from ADAL"""
        return self._token_cache.get_token()

    # -------------------------------------------------
    # Supporting methods: HTTP request system
    # -------------------------------------------------
    def do_download_dicom(self, output_folder, study_id, series_id=None, instance_id=None):
        """Download DCM files from DICOM server to output folder"""
        token = self.get_token()
        url = None
        if series_id is None and instance_id is None:
            url = f"/studies/{study_id}"
        if not series_id is None and instance_id is None:
            url = f"/studies/{study_id}/series/{series_id}"

        if not series_id is None and not instance_id is None:
            url = f"/studies/{study_id}/series/{series_id}/instances/{instance_id}"

        requests_session = requests.session()

        url = f"{self._base_url}{url}"

        headers = {
            "Accept": 'multipart/related; type="application/dicom"; transfer-syntax=*',
            "Authorization": "Bearer " + token,
        }

        response = None
        try:
            response = requests_session.get(url, headers=headers)
            response.raise_for_status()
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

        mpd = tb.MultipartDecoder.from_response(response)
        self.write_files(output_folder, mpd)
        return response, len(mpd.parts)

    def do_upload_dicom_file(self, file_name):
        """Upload DCM file to DICOM server"""
        # Upload files and folders
        # Get filenames
        filenames = [Path(file_name)]
        response = self.upload_files(filenames)
        return response

    # -------------------------------------------------
    def do_upload_dicom_folder(self, folder_name):
        """Upload all DCM files and folder to DICOM server"""
        # Upload files and folders
        # Get filenames
        filenames = list(Path(folder_name).rglob("*.dcm"))
        response = self.upload_files(filenames)
        return response

    # -------------------------------------------------
    def do_get_patient_study_ids(self, patient_id):
        """Get collection of study IDs based on patient ID"""
        token = self.get_token()

        # The url that looks up by PatientID
        url = f"{self._base_url}/studies?PatientID={patient_id}"

        headers = {"Accept": "application/dicom+json", "Authorization": "Bearer " + token}

        requests_session = requests.session()

        response = None
        try:
            response = requests_session.get(url, headers=headers)
            response.raise_for_status()
            return response
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
        return response

    # -------------------------------------------------
    def upload_files(self, filenames):
        """Upload DCM files using array of filenames"""
        token = self.get_token()
        # Get file content
        array_of_filecontent = []
        for file in filenames:
            with open(file, mode="rb") as file:  # b is important -> binary
                file_content = file.read()
            array_of_filecontent.append(file_content)
        # Build dictionary of file content to upload later
        dicom_files = {}
        for i in range(0, len(filenames)):
            dicom_files.update(
                {
                    filenames[i].stem: (
                        "dicomfile",
                        array_of_filecontent[i],
                        "application/dicom",
                    )
                }
            )
        # Encode into body
        boundary = choose_boundary()
        # Encode into body
        body, _ = encode_multipart_formdata(dicom_files, boundary)
        content_type = str("multipart/related; boundary=%s" % boundary)
        headers = {
            "Accept": "application/dicom+json",
            "Authorization": "Bearer " + token,
            "Content-Type": content_type,
        }
        url = f"{self._base_url}/studies"
        requests_session = requests.session()
        response = None
        try:
            response = requests_session.post(url, body, headers=headers, verify=False)
            response.raise_for_status()
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
        return response

    def delete_dicom_file(self, study_id) -> bool:
        """Delete DCM files based on study ID"""
        oauth_token = self._token_cache.get_token()
        session = requests.session()

        url = f"{self._base_url}/studies/{study_id}"
        response = None
        try:
            headers = {
                "Accept": "application/dicom+json",
                "Authorization": "Bearer " + oauth_token,
            }
            response = session.delete(url, headers=headers, timeout=3)
            assert response != None
            return True
        except Exception:
            return False

    def do_delete_dicom(self, study_id, series_id=None, instance_id=None):
        """Delete DCM files based on combination of study ID, series ID, and instance ID"""
        token = self.get_token()
        url = None
        if series_id is None and instance_id is None:
            url = f"/studies/{study_id}"
        if not series_id is None and instance_id is None:
            url = f"/studies/{study_id}/series/{series_id}"

        if not series_id is None and not instance_id is None:
            url = f"/studies/{study_id}/series/{series_id}/instances/{instance_id}"

        requests_session = requests.session()

        url = f"{self._base_url}{url}"

        headers = {"Accept": "application/dicom+json", "Authorization": "Bearer " + token}

        response = None
        try:
            response = requests_session.delete(url, headers=headers, timeout=3)
            response.raise_for_status()
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

        return response

    # -------------------------------------------------
    # File System
    # -------------------------------------------------
    def write_files(self, folder, mpd):
        """ Write files from multi-part form """
        filenames = []
        for part in mpd.parts:
            filenames.append(self.write_content(folder, part.content))
        return filenames

    def write_single_file(self, folder, content):
        """ Write single file to disk """
        filenames = []
        filenames.append(self.write_content(folder, content))
        return filenames

    def write_content(self, folder, content):
        """ Write file to disk """
        dcm = pydicom.dcmread(BytesIO(content))
        patient_id = self.right(dcm.PatientID, 3)
        study_id = self.right(dcm.StudyInstanceUID, 3)
        series_id = self.right(dcm.SeriesInstanceUID, 3)
        instance_id = self.right(dcm.SOPInstanceUID, 3)
        filename = (
            folder
            + "/"
            + patient_id
            + "_"
            + study_id
            + "_"
            + series_id
            + "_"
            + instance_id
            + ".dcm"
        )
        # if I want the dcm in bytes
        dcm = pydicom.dcmread(BytesIO(content))
        # if file exists, and different contents, new filename and write
        # if file exists, and same contents, ignore
        if self.file_exists(filename):
            newfn = self.nextnonexistent(filename)
            pydicom.dcmwrite(newfn, dcm)
            if not self.different_contents(newfn, filename):
                os.remove(newfn)
        else:
            pydicom.dcmwrite(filename, dcm)
        return filename

    # ===========================================================
    @staticmethod
    def file_exists(file):
        """ Check if file exists """
        path = pathlib.Path(file)
        if path.is_file():
            return True
        return False

    @staticmethod
    def get_file_digest(filename):
        """ Get hash for file for duplicate check """
        with open(filename, "rb") as file:
            file_hash = hashlib.md5()
            chunk = file.read()
            file_hash.update(chunk)
        return file_hash.digest()

    def different_contents(self, newfn, filename):
        """ Check if file is different """
        return self.get_file_digest(newfn) != self.get_file_digest(filename)

    @staticmethod
    def nextnonexistent(filename):
        """Finds a unique filename in case of conflict with existing file"""
        fnew = filename
        root, ext = os.path.splitext(filename)
        i = 0
        while os.path.exists(fnew):
            i += 1
            fnew = "%s_%i%s" % (root, i, ext)
        return fnew

    # -------------------------------------------------
    @staticmethod
    def left(sourcestring, amount):
        """ Extract left most characters """
        return sourcestring[:amount]

    # -------------------------------------------------
    @staticmethod
    def right(sourcestring, amount):
        """ Extract right most characters """
        return sourcestring[-amount:]

    # -------------------------------------------------
    @staticmethod
    def mid(sourcestring, offset, amount):
        """ Extract middle chars """
        return sourcestring[offset : offset + amount]
