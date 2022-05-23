from lumipy import get_atlas
from lumipy.query.expression.direct_provider.read import DriveRead
from lumipy.query.expression.direct_provider.save import DriveSave
from lumipy.drive.drive_client import DriveClient
import pandas as pd
from lumipy.common.lockable import Lockable
from lumipy.atlas.atlas import Atlas
from typing import Optional, Union
import io
import os


class Drive(Lockable):
    """Class that represents a directory in drive with functionality around listing contents, file read data source
    for use in fluent query syntax and batch saving of table variables.

    """

    drive_base_url_env_variable = 'FBN_LUSID_DRIVE_URL'

    def __init__(self, atlas: Atlas):
        """__init__ method of the DriveDirectory class

        Args:
            atlas (Atlas): luminesce data providers atlas. Must contain Drive.File.
            env vars.
        """

        self._client = atlas.get_client()
        self._atlas = atlas
        token = self._client.get_token()
        drive_url = os.getenv(self.drive_base_url_env_variable)
        self._drive_client = DriveClient(token=token, drive_url=drive_url)

        if not hasattr(atlas, 'drive_file'):
            raise ValueError("Atlas has no Drive.File provider - check permissions.")

        self._drive_files_cls = self._atlas.drive_file

        super().__init__()

    def delete(self, path: str):
        """Delete a file or folder in drive.

        Args:
            path: path of file or folder to delete.

        """
        self._drive_client.delete(path)

    def upload(self, content: Union['ModelProto', pd.DataFrame, io.IOBase], path: str, overwrite: Optional[bool] = False):
        """Upload an object to drive.

        Args:
            content (Union[ModelProto, pd.DataFrame, io.IOBase]): object to upload to drive. Must be a ModelProto
            (ONNX graph), a pandas DataFrame or a python IO reader object.
            path (str): path in drive to upload to.
            overwrite (Optional[bool]): whether to overwrite the file if it already exists (default: False).

        """
        self._drive_client.upload(content, path, overwrite)

    def create_folder(self, path: str):
        """Create a folder in drive.

        Args:
            path: path of the folder to create.

        """
        self._drive_client.create_folder(path)

    def download(self, drive_path: str, local_path: str):
        """Download a file from drive

        Args:
            drive_path: path in drive to get file from.
            local_path: local path to download file to.

        """
        self._drive_client.download(drive_path, local_path)

    def use_csv_file(self, file_path: str) -> DriveRead:
        """Use a CSV file in drive as a data provider.

        Args:
            file_path (str): File path in drive. If path str doesn't start with '/' (relative path) it will
            be relative to the current directory.

        Returns:
            DriveRead: DriveRead source table instance that represents the drive CSV data file.

        """

        if not file_path.endswith('.csv'):
            raise ValueError(f"Drive path input doesn't end in .csv: {file_path}")
        if not file_path.startswith('/'):
            raise ValueError()
        else:
            in_path = file_path
        return DriveRead(in_path, self._client, 'csv')

    def use_excel_file(self, file_path: str, range_arg: str) -> DriveRead:
        """Use an excel file in drive as a data provider.

        Args:
            file_path (str): File path in drive. If path str doesn't start with '/' (relative path) it will
            be relative to the current directory.
            range_arg (str): Cell range or table in the excel document to return (e.g. 'A1:E9' or 'table_name')

        Returns:
            DriveRead: DriveRead source table instance that represents the drive excel data file.

        """
        if not file_path.endswith('.xlsx'):
            raise ValueError(f"Drive path input doesn't end in .xlsx: {file_path}")
        if not file_path.startswith('/'):
            raise ValueError()
        else:
            in_path = file_path
        return DriveRead(in_path, self._client, 'excel', range_arg)

    def use_sqlite_file(self, file_path: str) -> DriveRead:
        """Use a sqlite in drive as a data provider.

        Args:
            file_path (str): File path in drive. If path str doesn't start with '/' (relative path) it will
            be relative to the current directory.

        Returns:
            DriveRead: DriveRead source table instance that represents the drive sqlite data file.

        """
        if not file_path.endswith('.sqlite'):
            raise ValueError(f"Drive path input doesn't end in .sqlite: {file_path}")
        if not file_path.startswith('/'):
            raise ValueError()
        else:
            in_path = file_path
        return DriveRead(in_path, self._client, 'sqlite')

    def _list_content(self, path: str, content_type=None, depth=1):
        if not isinstance(path, str) or not path.startswith('/'):
            raise ValueError()

        content = self._drive_files_cls(
            recurse_depth=depth,
            root_path=path
        )

        qry = content.select(
            content.full_path,
            content.type,
            content.size,
            content.created_on,
            content.updated_on
        )
        if content_type is not None:
            qry = qry.where(
                content.type == content_type
            )

        return qry.order_by(
            content.path.ascending(),
            content.name.ascending()
        ).go()

    def list_files(self, path: str) -> pd.DataFrame:
        """Get information on the files in a drive folder

        Args:
            path (Optional[str]): path to the folder to list files from. Defaults to current location.

        Returns:
            DataFrame: dataframe containing data on files in the folder and their metadata.

        """
        return self._list_content(path, 'File')

    def list_folders(self, path: str) -> pd.DataFrame:
        """Get information on the folders in a drive folder

        Args:
            path (Optional[str]): path to the folder to list folders from. Defaults to current location.

        Returns:
            DataFrame: dataframe containing data on folders in the folder and their metadata.

        """
        return self._list_content(path, 'Folder')

    def list_all(self, path: str) -> pd.DataFrame:
        """Get information on the files and folders in a drive folder

        Args:
            path (Optional[str]): path to the folder to list content from. Defaults to current location.

        Returns:
            DataFrame: dataframe containing data on all content in the folder and their metadata.

        """
        return self._list_content(path)

    def search(self, target: str, path: str) -> pd.DataFrame:
        """Search drive for paths that contain a target string (case-insensitive) and return these data as a DataFrame.

        Args:
            path (Optional[str]): path to search on. Can be relative or absolute path. Optional: will default to current
            location.
            target (str): the string to search the paths of the files and folders for.

        Returns:
            DataFrame: dataframe containing the search result data.
        """
        if not path.startswith('/'):
            raise ValueError()

        content = self._drive_files_cls(
            recurse_depth=99,
            root_path=path
        )
        return content.select(
            content.full_path,
            content.type,
            content.size,
            content.created_on,
            content.updated_on
        ).where(
            content.full_path.like(f'%{target}%')
        ).order_by(
            content.path.ascending(),
            content.name.ascending()
        ).go()

    def batch_save(self, path: Optional[str] = None, file_type: Optional[str] = 'csv', **batch) -> DriveSave:
        """Create a drive save as expression that will save a collection of table variables to a directory as a given
        file format.

        Args:
            path (Optional[str]): path to where to save the data to - can be an absolute or relative path. Defaults to
            the current location.
            file_type: file type to save the table variables as (valid types are csv, sqlite and xlsx)
            **batch: batch of table variable expressions specified as keyword args. The keyword is to be the name of the
            file saved in drive.

        Returns:
            DriveSave: DriveSave instance representing the save as call to drive.
        """
        if len(batch) == 0:
            raise ValueError()

        if not path.startswith('/'):
            raise ValueError()

        return DriveSave(path, self._client, file_type, **batch)


def get_drive(**kwargs) -> Drive:
    """Get drive instance by passing any of the following: a token, api_url and app_name; a path to a secrets file
       via api_secrets_filename; or by passing in proxy information. If none of these are provided then lumipy will try
       to find the credentials information as environment variables.

    Keyword Args:
        token (str): Bearer token used to initialise the API
        api_secrets_filename (str): Name of secrets file (including full path)
        api_url (str): luminesce API url
        app_name (str): Application name (optional)
        certificate_filename (str): Name of the certificate file (.pem, .cer or .crt)
        proxy_url (str): The url of the proxy to use including the port e.g. http://myproxy.com:8888
        proxy_username (str): The username for the proxy to use
        proxy_password (str): The password for the proxy to use
        correlation_id (str): Correlation id for all calls made from the returned finbournesdkclient API instances

    Returns:
        Drive: the drive instance.
    """
    atlas = get_atlas(**kwargs)
    return Drive(atlas)
