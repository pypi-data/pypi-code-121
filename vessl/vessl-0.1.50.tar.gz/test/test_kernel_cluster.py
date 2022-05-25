from test.conftest import TEST_CLUSTER_NAME, USE_MOCK

import pytest

import vessl


@pytest.mark.skipif(USE_MOCK, reason="Does not run if mocking is used.")
class TestKernelCluster:
    def test_read_cluster(self):
        vessl.read_cluster(TEST_CLUSTER_NAME)

    def test_list_clusters(self):
        vessl.list_clusters()

    def test_delete_cluster(self):
        # Do not test delete cluster because only one cluster exists.
        pass

    def test_rename_cluster(self):
        # Only applies to custom clusters
        pass

    def test_list_cluster_nodes(self):
        # Only applies to custom clusters
        pass
