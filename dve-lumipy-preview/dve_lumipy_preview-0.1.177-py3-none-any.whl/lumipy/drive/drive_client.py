import io
import json
import os
from importlib.util import find_spec
from typing import Union

import lusid_drive
import pandas as pd
from lusid_drive import models as ldm
from lusid_drive.utilities import ApiClientFactory
from lusid_drive.utilities.utility_functions import get_folder_id, name_to_id


def _check_path(path, filetype):
    if not path.startswith('/'):
        raise ValueError("All drive paths must be absolute.")
    if filetype is not None and not path.endswith(f".{filetype}"):
        raise ValueError(f"File type in path {path} was not {filetype}.")


class DriveClient:

    def __init__(self, token: str, drive_url: str):

        self.drive_factory = ApiClientFactory(token=token, drive_url=drive_url)

        self.folders = self.drive_factory.build(lusid_drive.api.FoldersApi)
        self.files = self.drive_factory.build(lusid_drive.api.FilesApi)

    def delete(self, path: str):
        _check_path(path, None)

        if path.endswith('/'):
            path = path[:-1]

        # Get ID
        obj_id = self._id_from_path(path)

        # Delete the object
        if '.' in path:
            self.files.delete_file(obj_id)
        else:
            self.folders.delete_folder(obj_id)

    def create_folder(self, path: str):
        _check_path(path, None)

        path_parts = [p for p in path.split('/') if p != '']
        base_path = '/'

        for folder in path_parts:
            try:
                self.folders.create_folder(ldm.CreateFolder(path=base_path, name=folder))
            except lusid_drive.exceptions.ApiException as e:
                if json.loads(e.body)["code"] == 664:
                    pass
            base_path += f'{folder}/'

    def _upload_file_bytes(self, content: str, file_path: str, overwrite: bool):

        path_parts = file_path.split('/')

        file_name = path_parts[-1]

        drive_path = "/".join(path_parts[:-1])
        if drive_path == '':
            drive_path = '/'

        try:
            self.files.create_file(
                x_lusid_drive_filename=file_name,
                x_lusid_drive_path=drive_path,
                content_length=len(content),
                body=content
            )
        except lusid_drive.exceptions.ApiException as e:
            if json.loads(e.body)["code"] == 671 and not overwrite:
                # File exists but we don't want to overwrite - rethrow
                print(f"{drive_path}/{file_name} already exists!")
                print("If you want to update the file set overwrite=True in upload().")
                raise e
            elif json.loads(e.body)["code"] == 671 and overwrite:
                # Update file instead
                file_id = self._id_from_path(file_path)
                self.files.update_file_contents(
                    id=file_id,
                    content_length=len(content),
                    body=content
                )
            else:
                # Something else has happened
                raise e

    def _id_from_path(self, path):
        path_parts = [p for p in path.split('/') if p != '']
        base_id = get_folder_id(self.drive_factory, path_parts[0])
        for folder in path_parts[1:]:
            content = self.folders.get_folder_contents(id=base_id)
            base_id = name_to_id(content, folder)

        if base_id is None:
            raise ValueError()

        return base_id

    def upload(self, content: Union['ModelProto', pd.DataFrame, io.IOBase], path: str, overwrite=False):
        if find_spec('onnx') is not None:
            from onnx.onnx_ml_pb2 import ModelProto
            if isinstance(content, ModelProto):
                _check_path(path, 'onnx')
                content_str = content.SerializeToString()
                self._upload_file_bytes(content_str, path, overwrite)
                return
        if isinstance(content, pd.DataFrame):
            _check_path(path, 'csv')
            s = io.StringIO()
            content.to_csv(s, index=False)
            self._upload_file_bytes(s.getvalue(), path, overwrite)
        elif issubclass(type(content), io.IOBase):
            _check_path(path, None)
            self._upload_file_bytes(content.read(), path, overwrite)
        else:
            raise NotImplementedError(
                f"Lumipy mini drive only supports ONNX model proto, pandas DataFrame objects and python io readers. "
                f"Received: {type(content).__name__}"
            )

    def download(self, drive_path, local_path):
        file_id = self._id_from_path(drive_path)
        response = self.files.download_file(file_id)
        os.rename(response, local_path)
