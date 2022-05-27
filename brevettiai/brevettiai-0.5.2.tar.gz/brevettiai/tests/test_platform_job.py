import unittest
import os
from tempfile import TemporaryDirectory
from brevettiai.platform import Job, JobSettings, PlatformBackend


class TestPlatformJob(unittest.TestCase):
    class TestJob(Job):
        did_run: bool = False

        def run(self):
            self.upload_artifact("modelfile", "")
            self.did_run = True
            assert self.io

    def test_job_cannot_be_used_without_start(self):
        job = self.TestJob(name="Test job")
        self.assertRaises(PermissionError, job.run)

    def test_extra_arguments_on_job(self):
        job = Job(name=str(self), settings=JobSettings(test="value"))
        assert job.settings.extra["test"] == "value"

    def test_job_create_schema(self):
        job = Job(name=str(self), settings=JobSettings(test="value"))
        builder = job.settings.platform_schema()

    def test_job_lifecycle(self):
        with TemporaryDirectory() as tmpdir:
            job = self.TestJob(name=str(self), backend=PlatformBackend(data_bucket=tmpdir))
            job.start()
            self.assertTrue(job.did_run)
            self.assertTrue({"modelfile", "output.json"} == set(os.listdir(job.artifact_path())))


if __name__ == '__main__':
    unittest.main()
