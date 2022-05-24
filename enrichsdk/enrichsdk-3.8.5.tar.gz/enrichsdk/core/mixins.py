"""
Mixins to handle common situations
"""
import os
import sys
import json
import copy
import shutil
import logging
import tempfile
from inspect import signature
import multiprocessing as mp
import numpy as np
import pandas as pd
from inspect import getframeinfo, stack
from functools import partial

import s3fs
import gcsfs

from ..lib.misc import get_checksum, get_file_size
from ..lib.integration import send_html_email

from .frames import PandasDataFrame

logger = logging.getLogger("app")

__all__ = [
    "S3Mixin",
    "GCSMixin",
    "PandasMixin",
    "ParallelMixin",
    "AWSMixin",
    "FilesMixin",
    "CheckpointMixin",
    "EmailMixin",
]


class CloudMixin(object):
    """
    Mixin baseclass for S3 and GCSFS.
    """

    def _cloud_get_fshandles(self, fshandle=None, bucket=None, fsonly=False, attr="s3"):
        """ """
        if fshandle is None:
            fshandle = getattr(self, attr, None)
        if fshandle is None:
            logger.error(
                "{} handle is missing".format(attr),
                extra=self.config.get_extra(
                    {
                        "transform": self.name,
                    }
                ),
            )
            raise Exception("Invalid {} handle".format(attr))

        if fsonly:
            return fshandle, None

        if bucket is None:
            bucket = getattr(self, "bucket", None)
        if bucket is None:
            logger.error(
                "Invalid bucket",
                extra=self.config.get_extra(
                    {
                        "transform": self.name,
                    }
                ),
            )
            raise Exception("Invalid/missing bucket")

        return fshandle, bucket

    def _cloud_list_files(self, fshandle, bucket, path, include=None):

        files = []
        try:
            fullpath = bucket + "/" + path
            files = fshandle.glob(fullpath)
        except:
            logger.exception(
                "Unable to access path",
                extra=self.config.get_extra({"transform": self.name}),
            )
            raise Exception("Unable to access path")

        # lstrip the bucket name..
        files = [f[len(bucket) + 1 :] for f in files]

        # => Split the files
        if include is None:
            include = lambda x: True

        if not callable(include):
            raise Exception("Include parameter should be a function")

        included_files = []
        excluded_files = []
        for f in files:
            if include(f):
                included_files.append(f)
            else:
                excluded_files.append(f)

        return included_files, excluded_files

    def _cloud_list_directories(self, fshandle, bucket, path, normalizer=None):
        files = []
        try:
            fullpath = bucket + "/" + path
            files = fshandle.ls(path, detail=True)
        except:
            logger.exception(
                "Unable to access path",
                extra=self.config.get_extra({"transform": self.name}),
            )
            raise Exception("Unable to access path")

        dirs = []
        excluded_files = []

        for f in files:

            # Normalize
            if normalizer is not None and callable(normalizer):
                f = normalizer(f)

            if f["StorageClass"] == "DIRECTORY":
                dirs.append(f["Key"])
            else:
                excluded_files.append(f["Key"])

        return dirs, excluded_files

    def _cloud_open_file(self, fshandle, bucket, path):

        try:
            path = bucket + "/" + path
            fd = fshandle.open(path, "rb")
        except:
            logger.exception(
                "Unable to read file",
                extra=self.config.get_extra(
                    {"transform": self.name, "data": bucket + "/" + path}
                ),
            )
            raise Exception("Unable to read blockstore file")

        return fd

    def _cloud_read_file(self, fshandle, bucket, path):

        try:
            path = bucket + "/" + path
            content = fshandle.open(path, "rb").read()
        except:
            logger.exception(
                "Unable to read file",
                extra=self.config.get_extra(
                    {"transform": self.name, "data": bucket + "/" + path}
                ),
            )
            raise Exception("Unable to read blockstore file")

        return content

    def _cloud_write_file(self, fshandle, bucket, path, content):

        try:
            path = bucket + "/" + path
            with fshandle.open(path, "wb") as fd:
                fd.write(content)
        except:
            logger.exception(
                "Unable to write file",
                extra=self.config.get_extra(
                    {"transform": self.name, "data": bucket + "/" + path}
                ),
            )
            raise Exception("Unable to read blockstore file")


class S3Mixin(CloudMixin):
    """
    AWS S3 functions usable by any module
    """

    def get_s3_handle(self, cred=None, client_kwargs=None):
        """
        Backward compatability. Calls s3_init_fshandle
        """
        return self.s3_init_fshandle(cred, client_kwargs=client_kwargs)

    def s3_init_fshandle(self, cred=None, client_kwargs=None):
        """
        Open a S3 connection. Takes credentials as an explicit
        argument or can pickup from 'aws_cred' attribute of self.

        Args:

          cred (object): Optional Credentials (a dictionary with 'secret_key' and 'access_key' parameters)

        Returns:

          object: S3FS handle

        """

        if cred is None:
            if hasattr(self, "aws_cred"):
                cred = self.aws_cred

        fail = True
        msg = ""
        if cred is None:
            msg += "\ncred is None"

        if not isinstance(cred, dict):
            msg += "\naws credentials is not a dictionary"
        else:
            if "access_key" not in cred:
                msg += "\naccess_key missing in credentials"
            elif "secret_key" not in cred:
                msg += "\secret_key missing in credentials"
            else:
                fail = False

        if fail:
            logger.error(
                "Invalid aws credentials",
                extra=self.config.get_extra({"transform": self.name, "data": msg}),
            )
            raise Exception("Could not find the credentials")

        # Insert region if required.
        if 'region' in cred:
            if client_kwargs is None:
                client_kwargs = {}
            client_kwargs['region_name'] = cred.get('region')

        return s3fs.S3FileSystem(
            anon=False,
            key=cred.get("access_key",None),
            secret=cred.get("secret_key",None),
            token=cred.get('token', None),
            use_listings_cache=False,
            client_kwargs=client_kwargs,
        )

    def _s3_get_fshandles(self, s3, bucket=None, fsonly=False):
        """
        Get S3 and bucket tuple. If fsonly specified, then
        get s3 handle only.

        Args:

           s3 (object): s3fs instance obtained from get_s3_handle
                        If not specified, 's3' object attribute used
           bucket (str): S3 bucket name
                        If not specified, 'bucket' object attribute used
           fsonly (bool): Filesystem handle only (default=False)

        Returns:

          tuple: (fileystem handle, bucket name). Bucket name is None if fs only has been specified.

        """
        return self._cloud_get_fshandles(
            fshandle=s3, bucket=bucket, fsonly=fsonly, attr="s3"
        )

    def s3_list_files(self, path, bucket=None, s3=None, include=None):
        """
        List files specified by a glob (path)

        Args:

           s3 (object): s3fs instance obtained from get_s3_handle
                        If not specified, 's3' object attribute used
           bucket (str): S3 bucket name
                        If not specified, 'bucket' object attribute used
           path (str): Glob of files
                       Note that it should not include the bucket name
           include (method): Function that is called for every file to determine whether to include or not

        Returns:

           tuple: List of included and excluded files

           first value is the list of included and the second is the list of excluded

        """

        s3, bucket = self._s3_get_fshandles(s3=s3, bucket=bucket)
        return self._cloud_list_files(
            fshandle=s3, bucket=bucket, path=path, include=include
        )

    def s3_list_directories(self, path, bucket=None, s3=None):
        """
        List files specified by a glob (path)

        Args:

           s3 (object): s3fs instance obtained from get_s3_handle
                        If not specified, 's3' object attribute used
           bucket (str): S3 bucket name
                        If not specified, 'bucket' object attribute used
           path (str): Glob of files
                       Note that it should not include the bucket name

        Returns:

           tuple: List of directories and non directories

           first value is the list of directories and the second is the list of  non directories

        """

        s3, bucket = self._s3_get_fshandles(s3, bucket)
        return self._cloud_list_directories(fshandle=s3, bucket=bucket, path=path)

    def s3_open_file(self, path, bucket=None, s3=None):
        """
        Open a S3 file and return a file descriptor

        Args:

          s3 (object): s3fs instance obtained from get_s3_handle
                       If not specified, 's3' object attribute used
          bucket (str): S3 bucket name
                        If not specified, 'bucket' object attribute used
          path (str): Path of the file that must be opened

        Returns:

          object: File descriptor

        """
        s3, bucket = self._s3_get_fshandles(s3, bucket)
        return self._cloud_open_file(fshandle=s3, bucket=bucket, path=path)

    def s3_read_file(self, path, bucket=None, s3=None):
        """
        Read the contents of a S3 object

        Args:

          s3 (object): s3fs instance obtained from get_s3_handle
                       If not specified, 's3' object attribute used
          bucket (str): S3 bucket name
                       If not specified, 'bucket' object attribute used
          path (str): Path of the file that must be opened

        Returns:

          str: content of the path

        """
        s3, bucket = self._s3_get_fshandles(s3, bucket)
        return self._cloud_read_file(fshandle=s3, bucket=bucket, path=path)

    def s3_write_file(self, path, content, bucket=None, s3=None):
        """
        Write the contents to a S3 object

        Args:

          s3 (object): s3fs instance obtained from get_s3_handle
                       If not specified, 's3' object attribute used
          bucket (str): S3 bucket name
                       If not specified, 'bucket' object attribute used
          path (str): Path of the file that must be opened
          content (bytes): Content of the file

        Returns:

          str: content of the path

        """

        s3, bucket = self._s3_get_fshandles(s3, bucket)
        return self._cloud_write_file(
            fshandle=s3, bucket=bucket, path=path, content=content
        )

    def s3_cache_files(self, files, localdir, bucket=None, s3=None):
        """
        Cache files from S3 into local directory

        Args:
          files (list): List of paths within the bucket
          localdir (str): Path to cache the file
          s3 (object): s3fs instance obtained from get_s3_handle
                       If not specified, 's3' object attribute used
          bucket (str): S3 bucket name
                        If not specified, 'bucket' object attribute used
        Returns:
          list: list of updated files
        """

        assert hasattr(self, "get_cache_dir")

        s3, bucket = self._s3_get_fshandles(s3, bucket)

        metadatafile = os.path.join(localdir, "__cache_metadata__.json")
        try:
            metadata = json.load(open(metadatafile))
        except:
            metadata = {}

        refreshed = []

        for f in files:

            fullpath = os.path.join(bucket, f)
            basename = os.path.basename(f)
            localfile = os.path.join(localdir, basename)

            # First collect metadata. f doesnt have bucket name
            info = s3.info(fullpath)

            # Fix the format
            info["LastModified"] = info["LastModified"].isoformat()

            # Collect the filename on local disk
            if os.path.exists(localfile):
                statinfo = os.stat(localfile)
                size = statinfo.st_size
            else:
                size = -1

            # Add a md5 sum check
            #
            if (
                (basename in metadata)
                and (metadata[basename]["ETag"] == info["ETag"])
                and (size == info["Size"])
            ):
                continue

            # Receive the file...
            metadata[basename] = info
            refreshed.append(basename)

            # Get the file content
            fd = self.s3.open(fullpath, "rb")
            content = fd.read()
            fd.close()

            # Write it locally
            with open(localfile, "wb") as fd:
                fd.write(content)

            # Save the state as well
            with open(metadatafile, "w") as fd:
                fd.write(json.dumps(metadata, indent=4))

            logger.debug(
                "Cached file {}".format(basename),
                extra=self.config.get_extra(
                    {
                        "transform": self.name,
                        "data": "{} => {}".format(basename, localfile),
                    }
                ),
            )

        return refreshed


class GCSMixin(CloudMixin):
    """
    GCS Blockstore functions usable by any module
    """

    def metadata_normalizer(self, detail):
        """
        Modify the GCP Metadata to be consistent with S3 metadata

        """
        mapping = {
            # S3 Key: GCP Key
            "StorageClass": "storageClass",
            "ETag": "etag",
            "Key": "path",
            "Size": "size",
            # This is a string. Last modified is a datetime object
            "LastModified": "updated",
        }
        for k, v in mapping.items():
            detail[k] = detail[v]

        return detail

    def get_gcs_handle(self, cred=None):
        """
        Backward compatability. Calls gcs_init_fshandle
        """
        return self.gcs_init_fshandle(cred)

    def gcs_init_handle(self, cred=None):
        """
        Open a GCS connection. Takes credentials as an explicit
        argument or can pickup from 'gcs_cred' attribute of self.

        Args:

          cred (object): Credentials (a dictionary with 'keyfile')

        Returns:

          object: GCSFS handle

        """

        if cred is None:
            if hasattr(self, "gcs_cred"):
                cred = self.gcs_cred

        fail = True
        msg = ""
        if cred is None:
            msg += "\ncred is None"

        if not isinstance(cred, dict):
            msg += "\ngcs credentials is not a dictionary"
        else:
            if "keyfile" not in cred:
                msg += "\nkeyfile missing in credentials"
            else:
                fail = False

        if fail:
            logger.error(
                "Invalid GCS credentials",
                extra=self.config.get_extra({"transform": self.name, "data": msg}),
            )
            raise Exception("Could not find the credentials")

        return gcsfs.GCSFileSystem(token=cred["keyfile"])

    def _gcs_get_fshandles(self, gcs, bucket, fsonly=False):
        """
        Get GCS handle and bucket tuple. If fsonly specified, then
        get GCS handle only.

        Args:

           gcs (object): GCSFS instance obtained from get_gcs_handle
                        If not specified, 'gcs' object attribute used
           bucket (str): GCS bucket name
                        If not specified, 'bucket' object attribute used
           fsonly (bool): Filesystem handle only (default=False)

        Returns:

          tuple: (fileystem handle, bucket name). Bucket name is None if fs only has been specified.

        """
        return self._cloud_get_fshandles(
            fshandle=gcs, bucket=bucket, fsonly=fsonly, attr="gcs"
        )

    def gcs_list_files(self, path, gcs=None, bucket=None, include=None):
        """
        List files specified by a glob (path)

        Args:

           path (str): Glob of files
                       Note that it should not include the bucket name
           gcs (object): gcsfs instance obtained from get_gcs_handle
                        If not specified, 'gcs' object attribute used
           bucket (str): GCS bucket name
                        If not specified, 'bucket' object attribute used
           include (def): Function that is called for every file to determine whether to include or not

        Returns:

           tuple: List of included and excluded files

           first value is the list of included and the second is the list of excluded

        """
        gcs, bucket = self._gcs_get_fshandles(gcs, bucket)
        return self._cloud_list_files(
            fshandle=gcs, bucket=bucket, path=path, include=include
        )

    def gcs_list_directories(self, path, gcs=None, bucket=None):
        """
        List files specified by a glob (path)

        Args:

           path (str): Glob of files
                       Note that it should not include the bucket name
           gcs (object): gcsfs instance obtained from get_gcs_handle
                        If not specified, 'gcs' object attribute used
           bucket (str): GCS bucket name
                        If not specified, 'bucket' object attribute used

        Returns:

           tuple: List of directories and non directories

           first value is the list of directories and the second is the list of  non directories

        """

        gcs, bucket = self._gcs_get_handles(gcs, bucket)
        return self._cloud_list_directories(
            fshandle=gcs, bucket=bucket, path=path, normalizer=self.metadata_normalizer
        )

    def gcs_open_file(self, path, gcs=None, bucket=None):
        """
        Open a GCS file and return a file descriptor

        Args:

          path (str): Path of the file that must be opened
          gcs (object): gcsfs instance obtained from get_gcs_handle
                       If not specified, 'gcs' object attribute used
          bucket (str): GCS bucket name
                        If not specified, 'bucket' object attribute used

        Returns:

          object: File descriptor

        """
        gcs, bucket = self._gcs_get_handles(gcs, bucket)
        return self._cloud_open_file(fshandle=gcs, bucket=bucket, path=path)

    def gcs_read_file(self, path, gcs=None, bucket=None):
        """
        Read the contents of a GCS object

        Args:

          path (str): Path of the file that must be opened
          gcs (object): gcsfs instance obtained from get_gcs_handle
                       If not specified, 'gcs' object attribute used
          bucket (str): GCS bucket name
                       If not specified, 'bucket' object attribute used


        Returns:

          str: content of the path

        """
        gcs, bucket = self._gcs_get_fshandles(gcs, bucket)
        return self._cloud_read_file(fshandle=gcs, bucket=bucket, path=path)

    def gcs_write_file(self, path, content, gcs=None, bucket=None):
        """
        Write the contents to a GCS object

        Args:

          path (str): Path of the file that must be opened
          content (bytes): Content of the file
          gcs (object): gcsfs instance obtained from get_gcs_handle
                       If not specified, 'gcs' object attribute used
          bucket (str): GCS bucket name
                       If not specified, 'bucket' object attribute used

        Returns:

          str: content of the path

        """

        gcs, bucket = self._gcs_get_handles(gcs, bucket)
        return self._cloud_write_file(
            fshandle=gcs, bucket=bucket, path=path, content=content
        )


class ParallelMixin(object):
    """
    Execute a function in parallel
    """

    def pexec_single(
        self,
        df,
        func,
        partitions=10,
        cores=1,
    ):
        """
        Take a single DF, split it and run funcs. Get either a combined
        dataframe or a list of computed outputs

        Args:

          df (obj): Pandas dataframe
          func (def): Function that must be called
          partitions (int): Number of dataframe partitions
          cores (int): Number of cores to run on

        Returns:
          object: list of func outputs or a combined dataframe

        """
        if df is None:
            return []

        assert callable(func)

        df_split = np.array_split(df, partitions)
        pool = mp.Pool(cores)
        _dfs = pool.map(func, df_split)
        pool.close()
        pool.join()

        return _dfs

    def pexec_multiple(self, dfs, func, cores=1):
        """
        Take a list of DFs, and run a func on each in parallel. Get
        either a combined dataframe or a list of computed outputs

        Args:

          dfs (obj): List of Pandas dataframes
          func (def): Function that must be called
          cores (int): Number of cores to run on

        Returns:
          object: list of func outputs or a combined dataframe

        """

        # Execute...
        pool = mp.Pool(cores)
        _dfs = pool.map(func, dfs)
        pool.close()
        pool.join()

        return _dfs


class PandasMixin(object):
    """
    Helper functions that load/store files
    """

    def pandas_read_file(self, name, path, params=None, test=False):
        """
        Read a pandas file

        Args:
           name (str): Label for the object. We use it to get the params
           path (str): Path of the local file that must be read
           params (dict): If explicitly passed then the function will not lookup
                          the pandas_params dictionary
           test (bool): Whether this is a test run. This gets a limited number of rows

        Returns:
           obj: a Pandas dataframe

        """

        if params is None:
            if not hasattr(self, "pandas_params"):
                raise Exception(
                    "Either params should be passed or it could be specified in pandas params"
                )
            if name not in self.pandas_params:
                raise Exception("{} params should be specified in pandas_params")
            params = self.pandas_params[name]

        if not os.path.exists(path):
            raise Exception("Missing file: {}".format(path))

        params = copy.copy(params)
        if test:
            params["nrows"] = 10000

        # Now load the file...
        df = pd.read_csv(path, **params)

        return df

    def pandas_read_s3file(self, name, path, params=None, test=False):
        """
        Read a pandas file but one that is in s3

        Args:
           name (str): Label for the object. We use it to get the params
           path (str): Path of the s3 file that must be read including the bucket
           params (dict): If explicitly passed then the function will not lookup
                          the pandas_params dictionary
           test (bool): Whether this is a test run. This gets a limited number of rows

        Returns:
           obj: a Pandas dataframe

        """

        if params is None:
            if not hasattr(self, "pandas_params"):
                raise Exception(
                    "Either params should be passed or it could be specified in pandas params"
                )
            if name not in self.pandas_params:
                raise Exception("{} params should be specified in pandas_params")
            params = self.pandas_params[name]

        params = copy.copy(params)
        if test:
            params["nrows"] = 10000

        # Now load the file...
        with self.s3_open_file(path) as fd:
            df = pd.read_csv(fd, **params)

        return df


class AWSMixin(object):
    """
    AWS helper functions..
    """

    def get_aws_attributes(self, name):
        """
        Lookup credentials

        Credentials are stored in siteconf on a enrich deployment site. This
        function looks up the credentials, opens the s3 connections, and cleans
        the paths

        Args:
           name (str): Name for credentials

        Returns:
           dict: A dictionary with credentials, s3 hangle, bucket, and path

        """

        # First check what is in the s3
        cred = self.args[name]["credentials"]
        aws_cred = self.get_credentials(cred)

        # Now get the handle
        s3 = self.get_s3_handle(cred=aws_cred)

        # Get the rest of the parameters
        bucket = self.args[name]["bucket"]
        path = self.args[name]["path"]
        if path.endswith("/"):
            path = path[:-1]
        path = path

        return {"cred": aws_cred, "s3": s3, "bucket": bucket, "path": path}


class FilesMixin(object):
    """
    Helper functions for file operations
    """

    def file_split_apply(self, label, files, splitfunc, applyfunc):
        """
        A function to split a list based on a name obtained from a
        splitting function

        Args:
          label (str): name to be used for documentation
          files (list): List of strings/files/names
          splitfunc (def): func name -> partition-name
          applyfunc (def): func list -> result

        Returns:
          dict: A dictionary with an entry for each partition provided by splitfunc

        """

        # => Validate parameters
        checks = [
            ["label", isinstance(label, str)],
            ["files", isinstance(files, list)],
            ["splitfunc", callable(splitfunc)],
            ["applyfunc", callable(applyfunc)],
        ]

        for c in checks:
            if not c[1]:
                raise Exception("Invalid parameter: {}".format(c[0]))

        # First split the list into groups using the
        # split function
        groups = {}
        for f in files:
            name = splitfunc(f)
            if name in ["", None]:
                raise Exception("Invalid name resulted from split function")
            if name not in groups:
                groups[name] = []
            groups[name].append(f)

        result = {}
        keys = sorted(list(groups.keys()))
        for k in keys:
            res = applyfunc(k, groups[k])
            result[k] = res

            logger.debug(
                "Processed {}: {}".format(label, k),
                extra=self.config.get_extra(
                    {
                        "transform": self.name,
                    }
                ),
            )

        return result

    def file_preprocessed_read(self, root, load=True, create=True):
        """
        Load the metadata of preprocessed files

        Args:
          root (str): Directory of preprocessed files
          load (bool): if True load the preprocessed files into dataframes
          create (bool): if True create the root directory

        Returns:
          dict: Metadata dictionary

        """

        now = self.config.now()

        metadatafile = os.path.join(root, "__preprocess_metadata__.json")
        metadata = {"dfs": {}, "files": []}

        # Create the root if required
        try:
            if create:
                os.makedirs(root)
        except:
            pass

        if os.path.exists(metadatafile):
            try:
                metadata = json.load(open(metadatafile))
            except:
                logger.exception(
                    "Unable to read preprocessed metadata file",
                    extra=self.config.get_extra(
                        {
                            "transform": self.name,
                        }
                    ),
                )

        metadata["dfs"] = {}

        # Fix the root
        data_root = self.config.get_file("%(data_root)s")
        metadata["root"] = os.path.relpath(root, start=data_root)

        # Look through the
        if load:
            for detail in metadata["files"]:
                datafile = os.path.join(root, detail["filename"])
                params = detail["params"]
                name = detail["name"]
                if not os.path.exists(datafile):
                    raise Exception("Missing data file: {}".format(datafile))
                metadata["dfs"][name] = pd.read_csv(datafile, **params)
                detail["timestamp"] = now.isoformat()

        return metadata

    def file_preprocessed_write(self, metadata):
        """
        Write the preprocessed files

        Load the metadata of preprocessed files

        Args:
          metadata (dict): Loaded metadata with updates

        """

        # Create a temporary root
        root = metadata["root"]
        if not os.path.isabs(root):
            data_root = self.config.get_file("%(data_root)s")
            root = os.path.join(data_root, root)

        newroot = os.path.join(root, ".new")
        try:
            os.makedirs(newroot)
        except:
            pass
        dfs = metadata["dfs"]

        metadatafile = os.path.join(newroot, "__preprocess_metadata__.json")

        # => Write the files
        for detail in metadata["files"]:
            name = detail["name"]
            filename = detail["filename"]
            params = detail["params"]
            path = os.path.join(newroot, filename)
            try:
                os.makedirs(os.path.dirname(path))
            except:
                pass

            df = dfs[name]
            df.to_csv(path, index=False, **params)

        # Make a copy and dump the file
        metadatacopy = copy.copy(metadata)
        metadatacopy.pop("dfs")
        with open(metadatafile, "w") as fd:
            fd.write(json.dumps(metadatacopy, indent=4))

        data_root = self.config.get_file("%(data_root)s")
        metadata["root"] = os.path.relpath(root, start=data_root)
        metadata["dfs"] = dfs

        # Now move the contents to a old directory
        oldroot = os.path.join(metadata["root"], ".old")

        # Clear old data
        try:
            if os.path.exists(oldroot):
                shutil.rmtree(oldroot)
            os.makedirs(oldroot)
        except:
            pass

        # Move the current files to the old directory
        for f in os.listdir(root):
            if os.path.basename(f) in [".old", ".new"]:  # skip self.
                continue
            shutil.move(
                src=os.path.join(root, os.path.basename(f)),
                dst=os.path.join(oldroot, os.path.basename(f)),
            )

        # Move the current files to the old directory
        for f in os.listdir(newroot):
            shutil.move(
                src=os.path.join(newroot, os.path.basename(f)),
                dst=os.path.join(root, os.path.basename(f)),
            )

        # Remove the the new
        shutil.rmtree(newroot)

        return

    def file_preprocessed_update(self, metadata, name, filename, df, params, context):
        """
        Update the preprocessed metadata with new information

        Args:
          metadata (dict): Loaded metadata
          name (str): Label for the dataframe/filename being updated
          filename (str): Expected filename on the disk
          df (object): Dataframe that must be stored
          params (dict): Params to be used while saving the dataframe
          context (dict): Any additional information


        """

        assert metadata is not None
        assert "files" in metadata

        # => First check if the entry exists
        found = False
        for detail in metadata["files"]:
            if detail["name"] == name:
                detail.update(
                    {"filename": filename, "params": params, "context": context}
                )
                found = True

        if not found:
            metadata["files"].append(
                {
                    "name": name,
                    "filename": filename,
                    "params": params,
                    "context": context,
                }
            )

        # Update the df in all cases
        metadata["dfs"][name] = df

        return

    def file_preprocessed_get(self, metadata, name):
        """
        Lookup the preprocessed metadata for a given name

        Args:
          metadata (dict): Loaded metadata
          name (str): Label for the dataframe/filename to lookup

        Returns:
          tuple: A tuple of (loaded dataframe, details)
        """

        df = metadata["dfs"].get(name, None)
        for detail in metadata["files"]:
            if detail["name"] == name:
                return df, detail

        return None, None


class CheckpointMixin(object):
    def checkpoint(
        self,
        df,
        filename,
        output="pq",
        metafile=None,
        extra_metadata={},
        state=None,
        **kwargs,
    ):
        """
        Checkpoint a dataframe. Collect all stats

        Args:

          df (object): Dataframe
          filename (str): Output filename. Probably unresolved
          metafile (str): Metadata filename. If not specified filename +'.metadata.json'
          extra_metadata (dict): Any additional information to be logged
          state (object): Enrich pipeline state.
          kwargs (dict): Any extra parameters to be passed to the pandas

        Returns:

          dict: Metadata

        """

        if state is None:
            if not hasattr(self, "state"):
                logger.error(
                    "State is required as parameter or transform attribute",
                    extra={"transform": self.name},
                )
            else:
                state = self.state

        root = self.config.get_file("%(enrich_data_dir)s")
        filename = self.config.get_file(filename)
        relpath = os.path.relpath(filename, start=root)

        if metafile is None:
            metafile = filename + ".metadata.json"

        metarelpath = os.path.relpath(metafile, start=root)

        # Dump the dataframe
        if output == "pq":
            handler = partial(df.to_parquet, filename)
        elif output == "csv":
            handler = partial(df.to_csv, filename)
        elif output == "tsv":
            handler = partial(df.to_csv, filename, sep="\t")
        else:
            raise Exception("Unsupported checkpoint output format: {}".format(output))

        try:

            try:
                # Create a target directory..
                os.makedirs(os.path.dirname(filename))
            except:
                pass

            # First try storing the filename
            if output != "pq":
                handler(**kwargs)
                status = "success"
                error = ""
            else:
                # Parquet
                kwargs.pop("engine", "")
                status = "failure"
                for engine in ["fastparquet", "pyarrow"]:
                    try:
                        handler(engine=engine, **kwargs)
                        status = "success"
                        error = ""
                        break
                    except:
                        logger.exception(
                            "{}: Failed to write {}".format(
                                engine, os.path.basename(filename)
                            ),
                            extra={"transform": self.name},
                        )

                if status == "failure":
                    raise Exception("Both parquet engines failed to write")

        except Exception as e:
            logger.exception(
                "Failed to store checkpoint", extra={"transform": self.name}
            )
            raise

        metadata = self.get_default_metadata(state)

        # Collect caller information
        info = []
        for s in stack()[1:3]:
            caller = getframeinfo(s[0])
            info.append("%s:%d" % (caller.filename, caller.lineno))

        # Now if the output file exists, collect information
        # about the output file
        metadata.update(
            {
                "status": status,
                "error": error,
                "extra": extra_metadata,
                "stack": info,
                "filename": relpath,
                "size": get_file_size(filename),
                "metadata": metarelpath,
                "checksum": get_checksum(filename),
                "rows": df.shape[0],
            }
        )

        if "columns" not in metadata:
            framemgr = PandasDataFrame()
            columns = {}
            for c in list(df.columns):
                columns[c] = {
                    "touch": self.name,  # Who is introducing this column
                    "datatype": framemgr.get_generic_dtype(df, c),  # What is its type
                }
            metadata["columns"] = columns

        with open(metafile, "w") as fd:
            fd.write(json.dumps(metadata, indent=4))

        # Done
        return metadata


class EmailMixin(object):
    """
    Send email
    """

    def send_email_helper(
        self,
        sender,
        receivers,
        subject,
        body,
        attachment_prefix="",
        attachment_suffix="",
        frames={},
    ):
        """
        Send email to a destination..
        """

        assert isinstance(frames, dict)

        try:
            tmpdir = tempfile.mkdtemp()

            filenames = []
            for name, df in frames.items():
                filename = os.path.join(
                    tmpdir, f"{attachment_prefix}{name}{attachment_suffix}.csv"
                )
                filenames.append(filename)
                df.to_csv(filename, index=False)

            send_html_email(
                body,
                sender=sender,
                receivers=receivers,
                subject=subject,
                attachments=filenames,
            )

            logger.debug(
                "Email notification sent",
                extra={
                    "transform": self.name,
                    "data": "Receivers: " + json.dumps(receivers),
                },
            )
        except:
            logger.exception(
                "Unable to send email",
                extra={
                    "transform": self.name,
                },
            )

        if os.path.exists(tmpdir):
            try:
                shutil.rmtree(tmpdir)
            except:
                logger.exception(
                    "Unable to cleanup temporary directory",
                    extra={"transform": self.name, "data": tmpdir},
                )
