import os
import tempfile

import pytest

import vessl
from test.conftest import USE_MOCK
from vessl.util.file_object import UploadableS3Object
from vessl.util.random import random_string


@pytest.mark.skipif(USE_MOCK, reason="Does not run if mocking is used.")
class TestVolume:
    file_name = random_string()

    @pytest.mark.order(index=1)
    def test_create_volume_file(self):
        volume_id = vessl.vessl_api.project.volume_id
        skeleton = vessl.create_volume_file(volume_id, False, self.file_name)

        # create an actual file on local
        local_path = os.path.join(tempfile.gettempdir(), self.file_name)
        with open(local_path, 'w') as f:
            f.write("dummy")

        UploadableS3Object(
            local_path,
            skeleton.upload_url.federation_token.bucket,
            skeleton.upload_url.federation_token.key,
            skeleton.upload_url.federation_token.token,
        ).upload()

        # remove the local file
        os.remove(local_path)

    def test_read_volume_file(self):
        volume_id = vessl.vessl_api.project.volume_id
        vessl.read_volume_file(volume_id, self.file_name)

    def test_list_volume_files(self):
        volume_id = vessl.vessl_api.project.volume_id
        vessl.list_volume_files(volume_id)

    @pytest.mark.order(index=-1)
    def test_delete_volume_file(self):
        volume_id = vessl.vessl_api.project.volume_id
        vessl.delete_volume_file(volume_id, path=self.file_name)
