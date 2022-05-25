from test.conftest import USE_MOCK

import pytest

import vessl


@pytest.mark.skipif(USE_MOCK, reason="Does not run if mocking is used.")
class TestSweep:
    @pytest.mark.order(index=1)
    def test_create_sweep(self):
        # Requires sweep suggestion server
        # pytest.sweep = vessl.create_sweep(
        #     objective_type=SWEEP_OBJECTIVE_TYPE_MAXIMIZE,
        #     objective_goal=0.99,
        #     objective_metric="val_accuracy",
        #     max_experiment_count=2,
        #     parallel_experiment_count=1,
        #     max_failed_experiment_count=1,
        #     algorithm=SWEEP_ALGORITHM_TYPE_RANDOM,
        #     parameters=[
        #         {"name": "a", "type": "int", "range": {"list": ["1", "2", "3"]}}
        #     ],
        #     cluster_name="local",
        #     start_command="echo 'Hello world!'",
        #     kernel_resource_spec_name="v1.cpu-0.mem-1",
        #     kernel_image_url=IMAGE_NAME,
        # )
        pass

    def test_read_sweep(self):
        # Requires sweep suggestion server
        pass

    def test_list_sweeps(self):
        vessl.list_sweeps()

    def test_terminate_sweep(self):
        # Requires sweep suggestion server
        pass

    def test_list_sweep_logs(self):
        # Requires sweep suggestion server
        pass
