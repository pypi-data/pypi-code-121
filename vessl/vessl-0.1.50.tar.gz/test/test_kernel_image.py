import pytest

import vessl
from test.conftest import USE_MOCK


@pytest.mark.skipif(USE_MOCK, reason="Does not run if mocking is used.")
class TestKernelImage:
    @pytest.mark.order(index=1)
    def test_list_kernel_images(self):
        images = vessl.list_kernel_images()
        pytest.image = images[0]

    def test_read_kernel_image(self):
        vessl.read_kernel_image(pytest.image.id)
