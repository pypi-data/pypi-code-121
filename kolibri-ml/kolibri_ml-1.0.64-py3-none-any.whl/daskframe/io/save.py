import os

#from daskframe.helpers.functions import prepare_path_local, path_is_local
#from daskframe.helpers.logger import logger


import warnings

#from daskframe.helpers.types import *

DEFAULT_MODE = "w"
DEFAULT_NUM_PARTITIONS = 1



class Save():
    def __init__(self, root):
        self.root = root

    def file(self, path: str, *args, **kwargs):
        """

        :param path:
        :param args:
        :param kwargs:
        :return:
        """
        if "." not in path:
            warnings.warn("No file extension found in path, saving to Parquet file.")
            file_ext = "parquet"
        else:
            file_ext = path.split(".")[-1]

        funcs = {
            'xls': 'excel',
            'xlsx': 'excel'
        }

        func_name = funcs.get(file_ext, file_ext.lower())

        func = getattr(self, func_name, None)

        if not callable(func):
            raise ValueError(f"No function found for extension '{file_ext}'")

        return func(path, *args, **kwargs)


    def csv(self, path, mode=DEFAULT_MODE, index=False, single_file=True, storage_options=None, conn=None, **kwargs):

        df = self.root.data

        if conn is not None:
            path = conn.path(path)
            storage_options = conn.storage_options

        try:
            if path_is_local(path):
                prepare_path_local(path)

            df.to_csv(filename=path, mode=mode, index=index, single_file=single_file, storage_options=storage_options,
                      **kwargs)
        except IOError as error:
            logger.print(error)
            raise

    def excel(self, path, sheet_name=None, conn=None, **kwargs):

        df = self.root.data

        if conn is not None:
            path = conn.path(path)

        try:
            if path_is_local(path):
                prepare_path_local(path)

            df.to_excel(filename=path,sheet_name=sheet_name,  **kwargs)
        except IOError as error:
            logger.print(error)
            raise
