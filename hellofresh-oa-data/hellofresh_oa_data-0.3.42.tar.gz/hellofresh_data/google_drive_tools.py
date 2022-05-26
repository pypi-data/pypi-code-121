"""
    Returns gdrive connection. Note, if no token.pickle or credentials.json
    files are found, OAuth2 flow is promoted to be completed via UI.
"""
import sys
import csv
import io
import os
import re
import os.path
import json
import pandas as pd
from loguru import logger
from hellofresh_data.parameter_store import get_parameter_store_value

from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

PATH_TO_JSON = "/US/OA/Prod/GoogleAPI/service_account_json"


class GoogleDrive:
    """
    Google Drive Helper Class
    """

    def __init__(self):

        self.__location__ = os.getcwd()

        self._logger = logger.bind(user="GoogleDrive")

        self.number_of_rows_pulled = 0
        self.file_name = None

    def get_google_api_service_account(self):
        """
        Returns Google API service account json as string.
        """
        service_account = get_parameter_store_value(PATH_TO_JSON)

        return service_account

    def get_gdrive_connection(self):
        """
        Uses service account json file, pulled from parameter store, to
        authenticate login. No browser login necessary.
        """
        scopes = ["https://www.googleapis.com/auth/drive"]

        service_account_str = self.get_google_api_service_account()

        cred = json.loads(service_account_str)
        credentials = Credentials.from_service_account_info(
            cred, scopes=scopes)

        return build("drive", "v3", credentials=credentials)

    def get_gsheet_connection(self):
        """
        Uses service account json file, pulled from parameter store, to
        authenticate login. No browser login necessary.
        """
        scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

        creds = None

        service_account_str = self.get_google_api_service_account()

        creds = json.loads(service_account_str)
        creds = Credentials.from_service_account_info(creds, scopes=scopes)

        return build("sheets", "v4", credentials=creds)

    def get_gsheet_file_by_id(self, sheet_key, sheet_range):
        """
        Get google sheet data by spreadsheet id
        """
        service = self.get_gsheet_connection()

        sheet = service.spreadsheets()

        try:
            result = (
                sheet.values().get(spreadsheetId=sheet_key, range=sheet_range).execute()
            )
        except HttpError as err:
            self._logger.warning(
                f"No files or sheet found with id: {sheet_key}")

        values = result.get("values", [])

        return values

    def camel_to_snake(self, column_name):
        return re.sub("(.)([A-Z][a-z]+)", r"\1_\2", column_name)

    def df_column_uniquify(self, data_df):
        """
            Will postfix column name with an index if there are
            duplicate names.
            i.e If there are 2 SKU columns in the google
            sheet then in the database table they will be represented as:
            SKU and SKU_1

        Returns
        -------
        df
            Pandas representation of google sheet
        """
        df_columns = data_df.columns
        new_columns = []
        for item in df_columns:
            counter = 0
            newitem = item
            while newitem in new_columns:
                counter += 1
                newitem = "{}_{}".format(item, counter)
            new_columns.append(newitem)
        data_df.columns = new_columns

        return data_df

    def get_gsheet_file_as_df(
        self, sheet_key, sheet_range, sheet_header_row, clean_col_name_flag=False
    ):
        """
        Returns sheet id for a given range as a pandas df

        Parameters
        ----------
        sheet_key : str
            id of the google sheet
        sheet_range : str
            name of tab and sheet_range to pull in the following format:
            name_of_the_tab!sheet_rangeFrom:sheet_rangeTo
                i.e. forecast_recipes!A1:G
        sheet_header_row : int
            Integer representation of the header row.
            If very first column of the google sheet is the header
            sheet_header_row=0
        clean_col_name_flag : bool
            If set to True will turn columns into snake case and replace any
            non alphanumetic characters with an underscore:
                "This Is a $Col" -> this_is_a_col

        Returns
        -------
        pandas df
            Pandas representation of google sheet
        """

        data = self.get_gsheet_file_by_id(sheet_key, sheet_range)

        try:
            data_df = pd.DataFrame(data)
        except Exception as err:
            self._logger.error(err)

        new_header = data_df.iloc[sheet_header_row]
        data_df = data_df[sheet_header_row + 1:]
        data_df.columns = new_header

        if clean_col_name_flag:
            data_df.columns = [self.camel_to_snake(x) for x in data_df.columns]
            data_df.columns = [
                re.sub("[^0-9a-zA-Z]+", "_", x.lower()) for x in data_df.columns
            ]
            data_df.columns = [x.replace("__", "_") for x in data_df.columns]
            data_df.columns = [x.strip("_") for x in data_df.columns]
            data_df = self.df_column_uniquify(data_df)

        return data_df

    def get_gdrive_csv_by_name(self, file_name):
        """
        Search drive by file name and check if file is present.
        """
        self.file_name = file_name
        gdrive_service = self.get_gdrive_connection()

        response = (
            gdrive_service.files()
            .list(
                q="name='{}'".format(self.file_name),
                spaces="drive",
                fields="nextPageToken, files(id, name)",
            )
            .execute()
        )

        response_obj = response.get("files", [])

        if not response_obj:
            self._logger.warning(f"No files found with name: {self.file_name}")
        else:
            self._logger.info(f"Found file: {response_obj[0]}")

        data_io = self.get_gdrive_csv_by_id(response_obj[0].get("id"))

        return data_io

    def get_gdrive_csv_by_id(self, sheet_key):
        """
        Search drive by file ID and check if file is present.
        If present, download.
        """
        gdrive_service = self.get_gdrive_connection()

        try:
            response = gdrive_service.files().get_media(fileId=sheet_key)
            fh_io = io.BytesIO()
            downloader = MediaIoBaseDownload(
                fh_io, response, 100 * 1024 * 1024)

            self._logger.info(f'Downloading "{self.file_name}" from drive...')
            done = False
            while done is False:
                status, done = downloader.next_chunk(num_retries=2)

        except HttpError as err:
            self._logger.error(err)

        self._logger.info(f'Downloaded "{self.file_name}" successfully!')

        return fh_io.getvalue()

    def convert_drive_io_data_to_df(self, data):
        """
        Get the data streamed from google drive and convert
        to DataFrame.
        """

        self._logger.info("Convert stream drive data to pandas DataFrame")

        decoded_data = data.decode(encoding='utf-8', errors='ignore')
        file_io = io.StringIO(decoded_data)
        reader = csv.reader(file_io, delimiter=",")

        data_df = pd.DataFrame(reader)
        data_df = data_df.infer_objects()

        self.number_of_rows_pulled = len(data_df)

        self._logger.info(
            f"Pulled {self.number_of_rows_pulled} rows from drive file")

        return data_df

    def get_folder_metadata(self, folder_ids, created_timestamp_filter):
        """
            This method takes in folder ids and timestamp filter provided by user and
            calls gdrive api for the metadata information
        Parameters
        ----------
        folder_ids : list
            Google drive folders to search
        created_timestamp_filter : datetime-like or str
            Filter files greater than the given filter. The datetime value will be in UTC

        Returns
        -------
        pandas df
            Dataframe with all the files/folders ids with name,mimeType,webViewLink
            and parent folder description
        """

        gdrive_service = self.get_gdrive_connection()

        if not folder_ids:
            self._logger.error("Please provide google drive folder ids")
            sys.exit(1)

        df_parent_info = pd.DataFrame()
        self._logger.info(f"Total folders to fetch {len(folder_ids)}")
        for i in folder_ids:
            self._logger.info(f"Fetching information for folder: {i}")
            try:
                response = (
                    gdrive_service.files()
                    .get(fileId=i, fields="id,name,webViewLink")
                    .execute()
                )
            except HttpError as err:
                self._logger.error(err)
                sys.exit(1)

            df_parent_info = df_parent_info.append(response, ignore_index=True)

        df_parent_info.rename(
            columns={
                "id": "parent_id",
                "name": "parent_name",
                "webViewLink": "webViewLinkParent",
            },
            inplace=True,
        )

        self._logger.info(
            f"Metadata for {len(df_parent_info)} folders fetched")

        query = "(" + " or ".join("'{}' in parents".format(i)
                                  for i in folder_ids) + ")"

        self._logger.info(
            "Fetching information for files inside requested folders")
        file_response = (
            gdrive_service.files()
            .list(
                q=f"{query} and trashed=false and createdTime >='{created_timestamp_filter}'",
                spaces="drive",
                pageSize=1000,
                fields="nextPageToken, files(id,name, webViewLink,mimeType,parents,createdTime,modifiedTime)",
            )
            .execute()
        )
        file_list = file_response.get("files")

        if not file_list:
            self._logger.error("File metadata not found")
            sys.exit(1)

        df_file_info = pd.DataFrame(file_list)
        df_file_info = df_file_info.explode("parents").reset_index(drop=True)
        ini_len = len(df_file_info)
        df_file_info.rename(columns={"parents": "parent_id"}, inplace=True)

        self._logger.info(
            f"{len(df_file_info)} files found matching the {created_timestamp_filter} filter criteria"
        )
        df_file_info = df_file_info.merge(df_parent_info, on=["parent_id"])

        assert ini_len == len(df_file_info), "Length after merge is not equal"

        return df_file_info
