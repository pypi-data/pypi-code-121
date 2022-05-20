# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""Authenticate to Google API and download data from google drive."""
import os
import sys
import io
import pickle
import logging
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2 import service_account

logging.getLogger("googleapiclient").setLevel(logging.CRITICAL)
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/sqlservice.admin']


class BaseGoogleDrive:  # pragma: no cover
    """The base class for google driver reader (and writer) classes. This class implements the methods that the child
    classes share. These are methods like authentication, etc.
    """
    def __init__(self, write_token=True, keys=None):
        """Initialize the object using the sheet id, range and a flag that defines whether a token should be written
        onto the disk or not.

        :param write_token: a boolean flag that determines if the refresh token should be stored on disk or not. This is
        useful in situation where we don't have permission to write or don't want to write the refresh token for other
        reasons.
        """
        self.write_token = write_token
        self.keys = keys
        self.service = self.authenticate()

    def authenticate(self):
        """Authenticate to Google API.

        :return: an authenticated build object
        """
        if self.keys:
            creds = service_account.Credentials.from_service_account_info(
                self.keys, scopes=SCOPES)
        else:
            creds = None
            # The file token.pickle stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.
            path_to_token = os.path.join(os.path.dirname(__file__), "..", "credentials", 'gdrive_token.pickle')
            if os.path.exists(path_to_token):
                with open(path_to_token, 'rb') as token:
                    creds = pickle.load(token)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    path_to_credentials = os.path.join(os.path.dirname(__file__), "..", "credentials", '.gdrive_credentials.json')
                    flow = InstalledAppFlow.from_client_secrets_file(path_to_credentials, SCOPES)
                    # the default port may not work here
                    creds = flow.run_local_server(port=8899)
                # Save the credentials for the next run
                if self.write_token:
                    with open(path_to_token, 'wb') as token:
                        pickle.dump(creds, token)

        service = build('drive', 'v3', credentials=creds, cache_discovery=False)
        return service

    def get_file_name(self, id):
        """Given a file id, return the name of that file. This is useful in situations where we know the file id and
        we want to preserve the filename when downloading it.

        :param id: the id of the file on google drive
        :return: the string filenameit
        """
        # populate the filename attribute in case one may need to use it
        file = self.service.files().get(fileId=id).execute()
        return file["name"]

    @staticmethod
    def get_url(id):
        """Construct complete google drive url from id.

        :param id: id for google drive object.
        :type id: string
        :return: full url for google drive object.
        :rtype: string
        """
        return "https://drive.google.com/open?id={}".format(id)

    def get_file_owner(self, id):
        """Accept a file id and return the email address of the file owner

        :param id: id for google drive object.
        :return: the email address of the file owner
        """
        try:
            permissions = self.service.permissions().list(fileId=id).execute()
        except Exception:
            logging.critical("Something went wrong when trying to obtain the owner of the file. Exiting...")
            sys.exit(1)
        permission_items = permissions.get('items', [])
        for item in permission_items:
            if item["role"] == "owner":
                return item["emailAddress"]
        logging.critical("No owner was found for the file. Exiting...")
        sys.exit(1)

    @staticmethod
    def _call_back(request_id, response, exception):
        """Call back function used in sending request to google drive api for logging information.

        :param request_id: placeholder. needed in order to be correctly passed to `new_batch_http_request`
        :param response: http call result from request.
        :param exception: Exception that would cause warning log
        :return: None
        """
        if exception:
            # Handle error
            logging.warning(exception)
        else:
            logging.info("Permission Id: {}".format(response.get('id')))


class GoogleDriveReader(BaseGoogleDrive):  # pragma: no cover
    """Download files and obtain various information about the files stored on google drive. Information such as
    file_id, file_name, etc"""

    def __init__(self, write_token=True, keys=None):
        super().__init__(write_token, keys)
        self.values = None

    def read_file_get_handle(self, id):
        """Read a file (identified by its id) and get a file handler. The file handler can then be used to write the
        data to disk. The file handler has methods such as get_values(), seek(), etc, which enables navigation and other
        operations.

        :param id: the id of the file on google drive
        :return: a file handler (BytesIO object)
        """
        request = self.service.files().export_media(fileId=id,
                                                    mimeType='text/plain')
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            logging.info("Download %d%%." % int(status.progress() * 100))

        return fh

    def get_file_id(self, filename):
        """Given a filename on google drive, try to search and find the file id. If there are multiple file stored with
        the filename, raise an error.

        :param filename: the name of the file to be searched on google drive
        :return: the id of the file on google drive
        """
        results = self.service.files().list(pageSize=10,
                                            spaces='drive',
                                            fields="nextPageToken, files(id, name)",
                                            q="name = '{filename}'".format(filename=filename)).execute()
        item = results.get('files', [])
        if not item:
            logging.error('No files found.')
        elif len(item) > 1:
            logging.error("More than one file found using the name {filename}. Update the name or use a different "
                          "method if this is the expected behavior. Exiting...".format(filename=filename))
        else:
            return item[0]['id']

    def download_to_file(self, id, filename):
        """Read a file (identified by its id) and get a file handler. The file handler can then be used to write the
        data to disk. The file handler has methods such as get_values(), seek(), etc, which enables navigation and other
        operations.

        :param id: the id of the file on google drive
        :params filename: the full path (path + name) to be saved on disk
        :return: a file handler (BytesIO object)
        """
        request = self.service.files().get_media(fileId=id)
        fh = io.FileIO(filename, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            logging.info("Download %d%%." % int(status.progress() * 100))


class GoogleDriveWriter(BaseGoogleDrive):  # pragma: no cover
    """Upload files and obtain various information about the files stored on google drive. Information such as
        file_id, file_name, etc
    """

    def __init__(self, write_token=True, keys=None):
        super().__init__(write_token, keys)
        self.values = None

    def write_file(self, filename, name=None, mimetype=None, resumable=True):
        """Given a filename on local machine, try to upload the file into google drive, and return the id of the
        uploaded file

        :param filename: the name of the file to be uploaded to google drive
        :type filename: string
        :param name: title of file to be shown in google drive. If None, will use same filename. Default is None.
        :type name: None or string
        :param mimetype: Mime-type of the file. If None then a mime-type will be guessed from the file extension.
        :type mimetype: string
        :param resumable: whether to use resumable upload or not. For large files, use True. Default is True.
        :type resumable: bool
        :return: the id of the file on google drive
        """
        file_metadata = {'name': name if name is not None else os.path.split(filename)[-1]}
        media = MediaFileUpload(filename,
                                mimetype=mimetype,
                                resumable=resumable)
        file = self.service.files().create(body=file_metadata,
                                           media_body=media,
                                           fields='id').execute()
        return file.get("id")

    def delete_file(self, id):
        """Delete the file with the given id

        :param id: id of the file on google drive
        :type id: string
        :return: return the name of the deleted file
        :rtype: string
        """
        filename = self.get_file_name(id=id)
        self.service.files().delete(fileId=id).execute()
        return filename
