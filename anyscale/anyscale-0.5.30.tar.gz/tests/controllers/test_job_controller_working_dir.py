import os
from pathlib import Path
import random
import shutil
import tempfile
import uuid
from zipfile import ZipFile

import pytest
import smart_open
import yaml

from anyscale.sdk.anyscale_client.models import CreateProductionJob
from anyscale.sdk.anyscale_client.sdk import (
    _upload_and_rewrite_working_dir_in_create_production_job,
)
from anyscale.utils.ray_utils import (  # type: ignore
    _dir_travel,
    _get_excludes,
    zip_directory,
)
from anyscale.utils.runtime_env import (
    _get_remote_storage_object_name,
    upload_and_rewrite_working_dir,
)


CONDA_DICT = {"dependencies": ["pip", {"pip": ["pip-install-test==0.5"]}]}
PIP_LIST = ["requests==1.0.0", "pip-install-test"]
GS_BUCKET_NAME = "anyscale-bk-e2e-test-job"


@pytest.fixture
def test_directory():
    with tempfile.TemporaryDirectory() as tmp_dir:
        path = Path(tmp_dir)
        subdir = path / "subdir"
        subdir.mkdir(parents=True)
        requirements_file = subdir / "requirements.txt"
        with requirements_file.open(mode="w") as f:
            print("\n".join(PIP_LIST), file=f)

        good_conda_file = subdir / "good_conda_env.yaml"
        with good_conda_file.open(mode="w") as f:
            yaml.dump(CONDA_DICT, f)

        bad_conda_file = subdir / "bad_conda_env.yaml"
        with bad_conda_file.open(mode="w") as f:
            print("% this is not a YAML file %", file=f)

        yield subdir, requirements_file, good_conda_file, bad_conda_file


@pytest.mark.parametrize(
    "upload_path,expected_output",
    [
        ("gs://bucket", "file.zip"),
        ("gs://bucket/path", "path/file.zip"),
        ("gs://bucket/path/", "path/file.zip"),
    ],
)
def test_get_remote_storage_object_name(upload_path, expected_output):
    assert (
        _get_remote_storage_object_name(upload_path, upload_filename="file.zip")
        == expected_output
    )


class TestUploadLocalWorkingDir:
    def test_upload_and_rewrite_working_dir_with_fake_upload(self, test_directory):
        def fake_upload_file_to_remote_storage(
            source_file: str, upload_path: str, upload_filename: str
        ) -> str:
            shutil.copyfile(source_file, upload_filename)
            return os.path.join(upload_path, upload_filename)

        upload_path = "s3://fake/dir"
        runtime_env = {
            "pip": ["blah"],
            "working_dir": str(test_directory),
            "upload_path": upload_path,
        }
        new_runtime_env = upload_and_rewrite_working_dir(
            runtime_env,
            upload_file_to_remote_storage_fn=fake_upload_file_to_remote_storage,
        )

        assert new_runtime_env["working_dir"].startswith(upload_path)
        assert Path(new_runtime_env["working_dir"]).suffix == ".zip"

    @pytest.mark.skipif(
        os.environ.get("CI") != "true",
        reason="Skip test if not running in CI because S3/GS credentials are not available",
    )
    @pytest.mark.parametrize(
        "upload_path",
        [
            "s3://bk-premerge-first-jawfish-artifacts/e2e_tests/job",
            f"gs://{GS_BUCKET_NAME}",
        ],
    )
    @pytest.mark.parametrize("mode", ["sdk", "cli"])
    def test_upload_and_rewrite_working_dir(
        self, test_directory, upload_path: str, mode
    ):
        """Test that the working_dir correctly gets uploaded to upload_path in the runtime_env."""
        subdir, _, _, _ = test_directory
        runtime_env = {
            "pip": ["blah"],
            "working_dir": str(subdir),
            "upload_path": upload_path,
        }
        if mode == "sdk":
            job_config = {
                "compute_config_id": "cpt_U8RCfD7Wr1vCD4iqGi4cBbj1",
                "build_id": "bld_1277XIinoJmiM8Z3gNdcHN",
                "runtime_env": runtime_env,
                "entrypoint": "python my_job_script.py --option1=value1",
                "max_retries": 3,
            }

            create_production_job = CreateProductionJob(
                name="my-production-job",
                description="A production job running on Anyscale.",
                project_id="prj_7S7Os7XBvO6vdiVC1J0lgj",
                config=job_config,
            )

            _upload_and_rewrite_working_dir_in_create_production_job(
                create_production_job
            )
            new_runtime_env = create_production_job.config.get("runtime_env")
        elif mode == "cli":
            # Upload the working_dir and rewrite the working_dir field to point to the new remote URI
            new_runtime_env = upload_and_rewrite_working_dir(runtime_env)
        else:
            raise ValueError(f"Invalid mode: {mode}")

        # Check all non-working_dir fields in the runtime_env are unchanged
        runtime_env_copy = runtime_env.copy()
        new_runtime_env_copy = new_runtime_env.copy()
        runtime_env_copy.pop("working_dir")
        new_runtime_env_copy.pop("working_dir")
        assert runtime_env_copy == new_runtime_env_copy

        # Check the format of the remote URI
        remote_uri = new_runtime_env["working_dir"]
        assert remote_uri.startswith(upload_path)
        assert Path(remote_uri).suffix == ".zip"

        # Download the zip file from the remote bucket
        local_zip_file = "test_job_controller_working_dir.zip"
        with smart_open.open(remote_uri, "rb") as package_zip:
            with open(local_zip_file, "wb") as fin:
                fin.write(package_zip.read())

        # Check the downloaded zip is the same directory that was uploaded
        unzip_target_dir = os.path.join("unzip_target_dir")
        with ZipFile(local_zip_file, "r") as zip_ref:
            zip_ref.extractall(unzip_target_dir)
        assert set(os.listdir(os.path.join(unzip_target_dir, "subdir"))) == {
            "requirements.txt",
            "good_conda_env.yaml",
            "bad_conda_env.yaml",
        }

    def test_remote_uri_working_dir_noop(self):
        runtime_env = {"working_dir": "s3://already-a-uri"}
        assert runtime_env == upload_and_rewrite_working_dir(runtime_env)

    @pytest.mark.parametrize("include_parent_dir", [True, False])
    def test_zip_directory(self, test_directory, include_parent_dir):
        subdir, _, _, _ = test_directory
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_file = os.path.join(tmpdir, "test_zip.zip")
            # NOTE(architkulkarni): Must use "requirements.txt" in excludes instead of requirements_file
            # until https://github.com/ray-project/ray/issues/23473 is fixed.
            zip_directory(
                subdir,
                excludes=["requirements.txt"],
                output_path=zip_file,
                include_parent_dir=include_parent_dir,
            )
            unzip_target_dir = os.path.join(tmpdir, "unzip_target_dir")
            with ZipFile(zip_file, "r") as zip_ref:
                zip_ref.extractall(unzip_target_dir)
            if include_parent_dir:
                assert os.listdir(unzip_target_dir) == ["subdir"]
                unzip_target_dir = os.path.join(unzip_target_dir, "subdir")
            assert set(os.listdir(unzip_target_dir)) == {
                "good_conda_env.yaml",
                "bad_conda_env.yaml",
            }

    def test_travel(self, tmp_path):
        """Copied from OSS Ray at python/ray/tests/test_runtime_env_packaging.py"""
        dir_paths = set()
        file_paths = set()
        item_num = 0
        excludes = []
        root = tmp_path / "test"

        def construct(path, excluded=False, depth=0):
            nonlocal item_num
            path.mkdir(parents=True)
            if not excluded:
                dir_paths.add(str(path))
            if depth > 8:
                return
            if item_num > 500:
                return
            dir_num = random.randint(0, 10)
            file_num = random.randint(0, 10)
            for _ in range(dir_num):
                uid = str(uuid.uuid4()).split("-")[0]
                dir_path = path / uid
                exclud_sub = random.randint(0, 5) == 0
                if not excluded and exclud_sub:
                    excludes.append(str(dir_path.relative_to(root)))
                if not excluded:
                    construct(dir_path, exclud_sub or excluded, depth + 1)
                item_num += 1
            if item_num > 1000:
                return

            for _ in range(file_num):
                uid = str(uuid.uuid4()).split("-")[0]
                v = random.randint(0, 1000)
                with (path / uid).open("w") as f:
                    f.write(str(v))
                if not excluded:
                    if random.randint(0, 5) == 0:
                        excludes.append(str((path / uid).relative_to(root)))
                    else:
                        file_paths.add((str(path / uid), str(v)))
                item_num += 1

        construct(root)
        exclude_spec = _get_excludes(root, excludes)
        visited_dir_paths = set()
        visited_file_paths = set()

        def handler(path):
            if path.is_dir():
                visited_dir_paths.add(str(path))
            else:
                with open(path) as f:
                    visited_file_paths.add((str(path), f.read()))

        _dir_travel(root, [exclude_spec], handler)
        assert file_paths == visited_file_paths
        assert dir_paths == visited_dir_paths


@pytest.mark.skipif(
    os.environ.get("CI") != "true",
    reason="Skip test if not running in CI because credentials are not available.",
)
def test_gs_upload_download():
    """Test that the CI machine has access to the Google Storage bucket used for testing."""
    random_int = random.randint(0, 100000)
    filename = f"test_gs_upload_download_{random_int}.txt"

    from google.cloud import storage

    storage_client = storage.Client()
    bucket_obj = storage_client.bucket(GS_BUCKET_NAME)
    blob = bucket_obj.blob(filename)
    try:
        random_str = str(random_int)
        blob.upload_from_string(random_str)
        assert blob.exists()

        from smart_open import open

        uri = f"gs://{GS_BUCKET_NAME}/{filename}"

        with open(uri, "r") as f:
            assert random_str == f.read()
    finally:
        # Delete the file from the Google Storage bucket
        blob.delete()
