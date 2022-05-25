import shutil
from test.conftest import USE_MOCK

import pytest

import vessl
from vessl.util.exception import VesslApiException
from vessl.util.random import random_string


@pytest.mark.skipif(USE_MOCK, reason="Does not run if mocking is used.")
class TestDataset:
    dataset_name = random_string()

    @classmethod
    def teardown_class(cls):
        shutil.rmtree("test/fixture/tmp/", ignore_errors=True)

    @pytest.mark.order(index=1)
    def test_create_dataset(self):
        vessl.create_dataset(
            dataset_name=self.dataset_name,
            description=random_string(),
        )

    @pytest.mark.order(index=2)
    def test_upload_dataset_volume_file(self):
        vessl.upload_dataset_volume_file(
            self.dataset_name, "test/fixture/file1.txt", "file1.txt"
        )
        vessl.upload_dataset_volume_file(
            self.dataset_name, "test/fixture/folder1", "folder1",
        )

    def test_read_dataset(self):
        vessl.read_dataset(self.dataset_name)

    def test_list_datasets(self):
        vessl.list_datasets()

    def test_list_dataset_volume_files(self):
        vessl.list_dataset_volume_files(self.dataset_name)

    def test_download_dataset_volume_file(self):
        vessl.download_dataset_volume_file(
            self.dataset_name, "file1.txt", "test/fixture/tmp/file2.txt"
        )
        vessl.download_dataset_volume_file(
            self.dataset_name, "folder1", "test/fixture/tmp/folder1",
        )

    def test_copy_dataset_volume_file(self):
        vessl.copy_dataset_volume_file(self.dataset_name, "file1.txt", "file1_copy.txt")
        vessl.copy_dataset_volume_file(
            self.dataset_name, "folder1", "folder1_copy",
        )

    @pytest.mark.order(index=-1)
    def test_delete_dataset_volume_file(self):
        vessl.delete_dataset_volume_file(self.dataset_name, "file1.txt")
        vessl.delete_dataset_volume_file(self.dataset_name, "folder1")
        with pytest.raises(VesslApiException):
            vessl.delete_dataset_volume_file(self.dataset_name, "folder1")
