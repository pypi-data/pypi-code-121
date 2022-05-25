import pytest

import vessl
from test.conftest import USE_MOCK


@pytest.mark.skipif(USE_MOCK, reason="Does not run if mocking is used.")
class TestKernelResourceSpec:
    def test_read_kernel_resource_spec(self):
        vessl.read_kernel_resource_spec(30064771072, "v1.cpu-0.mem-1")

    def test_list_kernel_resource_specs(self):
        vessl.list_kernel_images()
