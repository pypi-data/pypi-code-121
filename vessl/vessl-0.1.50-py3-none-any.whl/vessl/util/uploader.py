import os
import zlib
from typing import List

from openapi_client.models import StorageFile
from vessl.util.file_object import UploadableS3Object


class Uploader:
    @classmethod
    def upload(
        cls, local_path: str, volume_id: int, remote_path: str
    ) -> StorageFile:
        from vessl.volume import create_volume_file, upload_volume_file

        assert os.path.isfile(local_path), f"Invalid path: {local_path}"
        file = create_volume_file(volume_id=volume_id, is_dir=False, path=remote_path)

        mpu = UploadableS3Object(
            local_path,
            file.upload_url.federation_token.bucket,
            file.upload_url.federation_token.key,
            file.upload_url.federation_token.token,
        ).upload()
        return upload_volume_file(volume_id, remote_path)

    @classmethod
    def bulk_upload(
        cls,
        local_base_path: str,
        local_file_paths: List[str],
        volume_id: int,
        remote_base_path: str,
    ) -> List[StorageFile]:
        # TODO: parallel upload

        files = []

        for local_file_path in local_file_paths:
            local_path = os.path.join(local_base_path, local_file_path)
            remote_path = os.path.join(remote_base_path, local_file_path)

            file = cls.upload(local_path, volume_id, remote_path)
            files.append(file)

        return files

    @classmethod
    def calculate_crc32c(filename):
        try:
            with open(filename, "rb") as fh:
                h = 0
                while True:
                    s = fh.read(65536)
                    if not s:
                        break
                    h = zlib.crc32(s, h)
                return "%X" % (h & 0xFFFFFFFF)
        except Exception as e:
            import sentry_sdk

            sentry_sdk.capture_exception(e)
            sentry_sdk.flush()

            return ""

    @classmethod
    def get_paths_in_dir(cls, local_base_path, hashmap=None):
        local_base_path = local_base_path.rstrip("/")

        paths = []
        for root_path, _, file_names in os.walk(local_base_path):
            for file_name in file_names:
                path = os.path.join(root_path, file_name)
                path = (
                    path[len(local_base_path) + 1 :]
                    if path.startswith(local_base_path)
                    else path
                )
                if hashmap and hashmap[path] == cls.calculate_crc32c(
                    os.path.join(local_base_path, path)
                ):
                    continue
                paths.append(path)
        return paths

    @classmethod
    def get_hashmap(cls, local_base_path):
        files = cls.get_paths_in_dir(local_base_path)
        hashmap = dict()
        for file in files:
            path = os.path.join(local_base_path, file)
            hashmap[file] = cls.calculate_crc32c(path)
        return hashmap
