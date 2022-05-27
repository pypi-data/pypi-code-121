import hashlib
import os
import re
import time

import kamzik3
from kamzik3 import DeviceError
from kamzik3.constants import *
from kamzik3.devices.device import Device
from kamzik3.devices.deviceFileServer import DeviceFileServer
from kamzik3.snippets.snippetDataAccess import compute_MD5
from kamzik3.snippets.snippetsDecorators import expose_method


class DeviceVirtualDirectory(DeviceFileServer):
    def __init__(
        self, host, port, workers_count=2, drives=None, device_id=None, config=None
    ):
        DeviceFileServer.__init__(
            self, device_id, host, port, workers_count, config=config
        )
        self.set_value(ATTR_DRIVES, drives)

    def _init_attributes(self):
        Device._init_attributes(self)
        self.create_attribute(ATTR_DRIVES, set_function=self._set_drives, readonly=True)
        self.create_attribute(ATTR_HOST, default_value=self.host, readonly=True)
        self.create_attribute(ATTR_PORT, default_value=self.port, readonly=True)

    def handle_configuration(self):
        start_at = time.time()
        self._config_commands()
        self._config_attributes()
        self.start()
        self.set_status(STATUS_CONFIGURED)
        self.logger.info(
            "Device configuration took {} sec.".format(time.time() - start_at)
        )

    def _set_drives(self, drives):
        """
        Initiate drives for current virtual directory.

        :param drives: dict
        """
        for value in drives.values():
            value["path"] = os.path.normpath(value["path"])
        self.set_value(ATTR_DRIVES, drives)

    def _check_allowed_path(self, drive, path):
        """
        Check if requested path on drive is actually allowed and exists.

        :param drive: str
        :param path: str
        :return: bool
        """
        drives = self.get_value(ATTR_DRIVES)

        if drive not in drives:
            raise DeviceError("Drive {} does not exists!".format(drive))

        drive_meta = self.get_value(ATTR_DRIVES)[drive]
        source = drive_meta.get("source", LOCAL_FILESYSTEM)
        if source == LOCAL_FILESYSTEM:
            if not os.path.exists(path):
                raise DeviceError("Path does not exists!")
            for allowed_path in self.get_value(ATTR_DRIVES)[drive]["path"]:
                if allowed_path in path:
                    return True
            raise DeviceError("Path does not exists!")
        else:
            return True

    @expose_method(
        {
            "drive": "Drive",
            "input_dir": "Path to the directory",
            "file_filter": "Regexp filter",
        }
    )
    def get_dir_content(self, drive, input_dir, file_filter=None):
        """
        Get all files, dirs and metadata (modtime, filesize) within input_dir and drive.

        You can set file_filter regexp to filter out file names.

        :param drive: str
        :param input_dir:  str
        :param file_filter: regexp str
        :return: str, list, list, list, list
        """
        self._check_allowed_path(drive, input_dir)
        drive_meta = self.get_value(ATTR_DRIVES)[drive]
        source = drive_meta.get("source", LOCAL_FILESYSTEM)
        if file_filter is None:
            file_filter_pattern = re.compile(drive_meta.get("file_filter", ".*"))
        else:
            file_filter_pattern = re.compile(file_filter)

        if source == LOCAL_FILESYSTEM:
            root_dir, dirs, files = next(
                os.walk(input_dir, topdown=True, onerror=None, followlinks=False)
            )
            filtered_files = list(
                filter(
                    lambda i, p=file_filter_pattern: file_filter_pattern.match(i), files
                )
            )
            files_meta = []
            dirs_meta = []
            for d_dir in dirs:
                absolute_path = "/".join((root_dir, d_dir))
                dirs_meta.append([0, os.path.getmtime(absolute_path)])
            for d_file in filtered_files:
                absolute_path = "/".join((root_dir, d_file))
                files_meta.append(
                    [os.path.getsize(absolute_path), os.path.getmtime(absolute_path)]
                )
            return root_dir, dirs, dirs_meta, filtered_files, files_meta
        else:
            return source.get_dir_content(
                drive=drive, input_dir=input_dir, file_filter=file_filter
            )

    @expose_method(
        {
            "drive": "Drive",
            "input_dir": "Path to the directory",
            "file_name": "File name",
        }
    )
    def get_meta_hash(self, drive, input_dir, file_name):
        """
        Get hash of device_id+drive+file_path.

        This should ensure unique hash for any filepath. The return value is used as a
        path for cached file.

        :param drive: str
        :param input_dir: str
        :param file_name: str
        :return: str
        """
        self._check_allowed_path(drive, input_dir)
        drive_meta = self.get_value(ATTR_DRIVES)[drive]
        source = drive_meta.get("source", LOCAL_FILESYSTEM)
        if source == LOCAL_FILESYSTEM:
            file_path = "/".join((input_dir, file_name))
            with open(file_path, "rb") as file_to_check:
                # read contents of the file
                data = file_to_check.read()
                # pipe contents of the file through
                md5_hash = hashlib.md5(data).hexdigest()
            return (
                compute_MD5("{}{}{}".format(self.device_id, drive, file_path)),
                os.path.getsize(file_path),
                os.path.getmtime(file_path),
                md5_hash,
            )
        else:
            return source.get_meta_hash(
                drive=drive, input_dir=input_dir, file_name=file_name
            )

    @expose_method(
        {
            "drive": "Drive",
            "input_dir": "Path to the directory",
            "file_name": "File name",
        }
    )
    def get_local_path(self, drive, input_dir, file_name):
        """
        Get local path to either cache or file on local fs.

        :param drive: str
        :param input_dir: str
        :param file_name: str
        :return: tuple (bool, str)
        """
        self._check_allowed_path(drive, input_dir)
        drive_meta = self.get_value(ATTR_DRIVES)[drive]
        source = drive_meta.get("source", LOCAL_FILESYSTEM)
        file_path = "/".join((input_dir, file_name))
        if source == LOCAL_FILESYSTEM:
            return True, file_path
        else:
            cached, cache_path = self.is_cached(drive, input_dir, file_name)
            if os.path.exists(cache_path):
                return cached, cache_path
            else:
                return cached, None

    def is_cached(self, drive, input_dir, file_name):
        """
        Check if path on drive from input_dir is cached.

        :param drive: str
        :param input_dir: str
        :param file_name: str
        :return: tuple (bool, path_hash)
        """
        cache_directory = kamzik3.session.get_value(ATTR_CACHE_DIRECTORY)
        path_hash, _file_size, _file_mod_time, file_md5_hash = self.get_meta_hash(
            drive, input_dir, file_name
        )
        path_hash = "/".join((cache_directory, path_hash))
        if os.path.exists(path_hash):
            with open(path_hash, "rb") as file_to_check:
                # read contents of the file
                data = file_to_check.read()
                # pipe contents of the file through
                cached_file_hash = hashlib.md5(data).hexdigest()

            if cached_file_hash == file_md5_hash:
                return True, path_hash

        return False, path_hash

    @expose_method({"input_files": "List of tuples (drive, file_path)"})
    def prepare_files(self, input_files):
        """
        Get through all files and get real drive / path combination.

        :param files: list of files
        :return: tuple (list of files, metadata)
        """
        prepared_files = []
        metadata = {}
        for drive, file_path in input_files:
            if not self.on_fs(drive, file_path):
                drive_meta = self.get_value(ATTR_DRIVES)[drive]
                source = drive_meta["source"]
                source_prepared_files, source_metadata = source.prepare_files(
                    input_files=[(drive, file_path)]
                )
                prepared_files += source_prepared_files
                metadata.update(source_metadata)
            else:
                prepared_files.append((drive, file_path))
        return prepared_files, metadata

    def sync_files(self, requested_files):
        """
        Request files from fileserver.

        :param requested_files:
        :return: list
        """
        sync_parts = [INSTRUCTION_SYNC, str(len(requested_files)).encode()]
        for drive, file_path in requested_files:
            sync_parts += [drive.encode(), file_path.encode()]
        self.frontend_connector.send_multipart(sync_parts)
        reply = self.frontend_connector.recv_multipart()
        return reply[1].decode()

    @expose_method({"drive": "Drive", "path": "Path to the file"})
    def on_fs(self, drive, path):
        """
        Check if file path from drive exists on local drive.

        :param drive: str
        :param path: str
        :return: bool
        """
        self._check_allowed_path(drive, path)
        drive_meta = self.get_value(ATTR_DRIVES)[drive]
        source = drive_meta.get("source", LOCAL_FILESYSTEM)
        return source == LOCAL_FILESYSTEM and os.path.exists(path)
