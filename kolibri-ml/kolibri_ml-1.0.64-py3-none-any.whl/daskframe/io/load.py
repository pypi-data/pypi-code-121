import ntpath

import dask.bag as dask_bag
import pandas as pd

import os
import glob
import psutil
from dask import dataframe as dd
from kdmt.infer import is_empty_function, is_list, is_str, is_url
from kdmt.lists import one_list_to_val, val_to_list
from daskframe.utils import prepare_path
#from daskframe.helpers.logger import logger
from kdmt.errors import RaiseError
from daskframe.dataframe import DaskFrame
from pathlib import Path
from urllib.parse import unquote
XML_THRESHOLD = 10
JSON_THRESHOLD = 20
BYTES_SIZE = 327680



class Load():

    def __init__(self):
        pass

    def csv(self, filepath_or_buffer, sep=",", header=True, infer_schema=True, encoding="UTF-8", n_rows=None,
            null_value="None", quoting=0, lineterminator='\r\n', on_bad_lines='warn', cache=False, na_filter=False,
            storage_options=None, conn=None, *args, **kwargs) -> 'DataFrameType':
        """
        Loads a dataframe from a csv file. It is the same read.csv Spark function with some predefined
        params


        :param encoding:
        :param storage_options:
        :param quoting:
        :param filepath_or_buffer: path or location of the file.
        :param sep: usually delimiter mark are ',' or ';'.
        :param header: tell the function whether dataset has a header row. True default.
        :param infer_schema: infers the input schema automatically from data.
        :param n_rows:
        :param null_value:
        :param cache:
        :param na_filter:
        :param lineterminator:
        :param on_bad_lines:
        :param conn:
        It requires one extra pass over the data. True default.

        :return dataFrame
        """


        if is_empty_function(self._csv):
            raise NotImplementedError(f"'load.csv' is not implemented on '{self.op.engine_label}'")
        if not is_url(filepath_or_buffer):
            filepath_or_buffer = glob.glob(unquote(str(Path(filepath_or_buffer).resolve())))

        filepath_or_buffer = one_list_to_val(filepath_or_buffer)

        try:

            # Pandas do not support \r\n terminator.
            if lineterminator and lineterminator.encode(encoding='UTF-8', errors='strict') == b'\r\n':
                lineterminator = None

            if conn is not None:
                filepath_or_buffer = conn.path(filepath_or_buffer)
                storage_options = conn.storage_options

            if kwargs.get("chunk_size") == "auto":
                # Chunk size is going to be 75% of the memory available
                kwargs.pop("chunk_size")
                kwargs["chunksize"] = psutil.virtual_memory().free * 0.75

            na_filter = na_filter if null_value else False

            if not is_str(on_bad_lines):
                on_bad_lines = 'error' if on_bad_lines else 'skip'

            def _read(_filepath_or_buffer):
                return self._csv(_filepath_or_buffer, sep=sep, header=0 if header else None, encoding=encoding,
                                 nrows=n_rows, quoting=quoting, lineterminator=lineterminator,
                                 on_bad_lines=on_bad_lines, na_filter=na_filter,
                                 na_values=val_to_list(null_value), index_col=False,
                                 storage_options=storage_options, *args, **kwargs)

            if is_list(filepath_or_buffer) and len(filepath_or_buffer)>0:
                df = _read(filepath_or_buffer[0])
                for f in filepath_or_buffer[1:]:
                    df = df.append(_read(f))
            else:
                df = _read(filepath_or_buffer)

            df = self.df(df)

        except IOError as error:
            logger.print(error)
            raise

        return df

    def dict(self, dict):
        return self.df(pd.DataFrame(dict))

    def excel(self, filepath_or_buffer, sheet_name=0, merge_sheets=False, skiprows=1, n_rows=None, storage_options=None,
              conn=None, n_partitions=1, *args, **kwargs) -> 'DataFrameType':
        """
        Loads a dataframe from a excel file.
        :param path: Path or location of the file. Must be string dataType
        :param sheet_name: excel sheet name
        :param args: custom argument to be passed to the excel function
        :param kwargs: custom keyword arguments to be passed to the excel function
        """

        if is_empty_function(self._excel):
            raise NotImplementedError(f"'load.excel' is not implemented on '{self.op.engine_label}'")

        filepath_or_buffer = unquote_path(filepath_or_buffer)

        if conn is not None:
            filepath_or_buffer = conn.path(filepath_or_buffer)
            storage_options = conn.storage_options

        file, file_name = prepare_path(filepath_or_buffer, "xls")[0]
        header = None
        if merge_sheets is True:
            skiprows = -1
        else:
            header = 0
            skiprows = 0

        df, sheet_names = self._excel(file, sheet_name=sheet_name, skiprows=skiprows, header=header, nrows=n_rows,
                                      storage_options=storage_options, n_partitions=n_partitions, *args, **kwargs)

        df = self.df(df)

        return df

    def tsv(self, filepath_or_buffer, header=True, infer_schema=True, *args, **kwargs):
        return self.csv(filepath_or_buffer, sep='\t', header=header, infer_schema=infer_schema, *args, **kwargs)

    def file(self, path, *args, **kwargs):
        """
        Try to  infer the file data format and encoding
        :param path: Path to the file you want to load.
        :param args:
        :param kwargs:
        :return:
        """
        conn = kwargs.get("conn")

        if conn:
            import boto3
            remote_obj = boto3.resource(
                conn.type, **conn.boto).Object(conn.options.get("bucket"), path)
            body = remote_obj.get()['Body']
            buffer = body.read(amt=BYTES_SIZE)
            full_path = conn.path(path)
            file_name = os.path.basename(path)

        else:

            full_path, file_name = prepare_path(path)[0]
            file = open(full_path, "rb")
            buffer = file.read(BYTES_SIZE)

        # Detect the file type
        try:
            file_ext = os.path.splitext(file_name)[1].replace(".", "")
            import magic
            mime, encoding = magic.Magic(
                mime=True, mime_encoding=True).from_buffer(buffer).split(";")
            mime_info = {"mime": mime, "encoding": encoding.strip().split("=")[
                1], "file_ext": file_ext}

        except Exception as e:
            print(getattr(e, 'message', repr(e)))
            full_path = path
            file_name = path.split('/')[-1]
            file_ext = file_name.split('.')[-1]
            mime = False
            mime_info = {"file_type": file_ext, "encoding": False}

        file_type = file_ext

        if mime:
            if mime in ["text/plain", "application/csv"]:
                if mime_info["file_ext"] == "json":
                    file_type = "json"
                else:
                    file_type = "csv"
            elif mime == "application/json":
                file_type = "json"
            elif mime == "text/xml":
                file_type = "xml"
            elif mime in ["application/vnd.ms-excel",
                          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
                file_type = "excel"
            else:
                RaiseError.value_error(
                    mime, ["csv", "json", "xml", "xls", "xlsx"])

        # Detect the file encoding
        if file_type == "csv":
            # In some case magic get a "unknown-8bit" which can not be use to decode the file use latin-1 instead
            if mime_info.get("encoding", None) == "unknown-8bit":
                mime_info["encoding"] = "latin-1"

            if mime:
                import csv
                dialect = csv.Sniffer().sniff(str(buffer))
                mime_info["file_type"] = "csv"

                r = {"properties": {"sep": dialect.delimiter,
                                    "doublequote": dialect.doublequote,
                                    "escapechar": dialect.escapechar,
                                    "lineterminator": dialect.lineterminator,
                                    "quotechar": dialect.quotechar,
                                    "quoting": dialect.quoting,
                                    "skipinitialspace": dialect.skipinitialspace}}

                mime_info.update(r)
                kwargs.update({
                    "encoding": mime_info.get("encoding", None),
                    **mime_info.get("properties", {})
                })
            df = self.csv(filepath_or_buffer=path, *args, **kwargs)

        elif file_type == "json":
            mime_info["file_type"] = "json"
            df = self.json(full_path, *args, **kwargs)

        elif file_type == "xml":
            mime_info["file_type"] = "xml"
            df = self.xml(full_path, **kwargs)

        elif file_type == "excel":
            mime_info["file_type"] = "excel"
            df = self.excel(full_path, **kwargs)

        else:
            RaiseError.value_error(
                file_type, ["csv", "json", "xml", "xls", "xlsx"])

        return df


    @staticmethod
    def df(*args, **kwargs):
        return DaskFrame(*args, **kwargs)

    @staticmethod
    def _csv(filepath_or_buffer, n_partitions=None, nrows=None, engine="c", na_filter=True,
             na_values=None, index_col=None, on_bad_lines='warn', *args, **kwargs):

        na_filter = na_filter if na_values else False

        if engine == "python":
            on_bad_lines = 'warn'
            df = dd.read_csv(filepath_or_buffer, keep_default_na=True,
                             na_values=None, engine=engine, on_bad_lines=on_bad_lines, *args, **kwargs)

        elif engine == "c":
            df = dd.read_csv(filepath_or_buffer, keep_default_na=True,
                             engine=engine, na_filter=na_filter, na_values=val_to_list(na_values),
                             low_memory=False, *args, **kwargs)

        if index_col:
            df = df.set_index(index_col)

        if nrows:
            logger.warn(f"'load.avro' on Dask loads the whole dataset and then truncates it")
            df = df.head(n=nrows, compute=False)

        if n_partitions is not None:
            df = df.repartition(npartitions=n_partitions)
        print("presisting")
        df = df.persist()

        return df

    @staticmethod
    def _excel(path, nrows, storage_options=None, n_partitions=1, *args, **kwargs):
        pdfs = pd.read_excel(path, nrows=nrows, storage_options=storage_options, *args, **kwargs)
        sheet_names = list(pd.read_excel(path, None, storage_options=storage_options).keys())
        pdf = pd.concat(val_to_list(pdfs), axis=0).reset_index(drop=True)
        df = dd.from_pandas(pdf, npartitions=n_partitions)

        return df, sheet_names
