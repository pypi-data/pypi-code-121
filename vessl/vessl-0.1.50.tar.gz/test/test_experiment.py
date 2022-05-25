from test.conftest import TEST_CLUSTER_NAME, TEST_IMAGE_NAME, USE_MOCK

import pytest

import vessl
from vessl.util.exception import InvalidExperimentError


@pytest.mark.skipif(USE_MOCK, reason="Does not run if mocking is used.")
class TestExperiment:
    @pytest.mark.order(index=1)
    def test_create_experiment(self):
        # Use pytest.experiment instead of self.experiment because self gets reset
        # after each test
        pytest.experiment = vessl.create_experiment(
            cluster_name=TEST_CLUSTER_NAME,  # TODO: change when CI server is relocated
            start_command="echo 'Hello world!'",
            kernel_resource_spec_name="v1.cpu-0.mem-1",
            kernel_image_url=TEST_IMAGE_NAME,
            message="test message",
            termination_protection=False,
            hyperparameters=["VAR=value"],
        )
        assert pytest.experiment.is_distributed == False

    @pytest.mark.order(index=2)
    def test_create_distributed_experiment(self):
        pytest.distributed_experiment = vessl.create_experiment(
            cluster_name=TEST_CLUSTER_NAME,  # TODO: change when CI server is relocated
            start_command="echo 'Hello world!'",
            kernel_resource_spec_name="v1.cpu-0.mem-1",
            kernel_image_url=TEST_IMAGE_NAME,
            message="test message",
            termination_protection=False,
            hyperparameters=["VAR=value"],
            worker_count=2,
            framework_type="pytorch",
        )
        assert pytest.distributed_experiment.is_distributed == True

    @pytest.mark.order(index=3)
    def test_create_local_experiment(self):
        pytest.local_experiment = vessl.experiment.create_local_experiment()

    def test_read_experiment(self):
        experiment = vessl.read_experiment(pytest.experiment.number)
        assert experiment.is_distributed == False

    def test_read_distributed_experiment(self):
        distributed_experiment = vessl.read_experiment(
            pytest.distributed_experiment.number
        )
        assert distributed_experiment.is_distributed == True

    def test_read_experiment_by_id(self):
        vessl.read_experiment_by_id(pytest.experiment.id)

    def test_list_experiments(self):
        vessl.list_experiments()

    def test_list_experiment_logs(self):
        vessl.list_experiment_logs(pytest.experiment.number)
        vessl.list_experiment_logs(pytest.distributed_experiment.number)

    def test_list_experiment_output_files(self):
        vessl.list_experiment_output_files(pytest.experiment.number)
        vessl.list_experiment_output_files(pytest.distributed_experiment.number)
        # vessl.list_experiment_logs(pytest.local_experiment.number)

    def test_download_experiment_output_files(self):
        vessl.download_experiment_output_files(pytest.experiment.number)
        vessl.download_experiment_output_files(pytest.distributed_experiment.number)
        vessl.download_experiment_output_files(pytest.local_experiment.number)

    def test_upload_experiment_output_files(self):
        with pytest.raises(InvalidExperimentError):
            # Cannot upload to managed experiment
            vessl.upload_experiment_output_files(pytest.experiment.number, "test/fixture")
        vessl.upload_experiment_output_files(
            pytest.local_experiment.number, "test/fixture"
        )
