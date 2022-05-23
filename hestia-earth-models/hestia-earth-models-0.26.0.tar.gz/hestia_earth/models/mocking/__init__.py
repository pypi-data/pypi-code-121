from hestia_earth.models.utils import measurement, site

from .mock_search import mock as mock_search


def enable_mock(node: dict = None):
    """
    Mock calls to Hestia API using pre-loaded search results.

    Parameters
    ----------
    node : dict
        Optional - The node used to run calculations. This is especially useful when running calculations on a Site.
    """
    # apply mocks on search results
    mock_search()
    # skip fetch bibliography data
    measurement._include_source = lambda v, *args: v

    if node is not None:
        # mock related cycles to return the current node
        fake_node = {'@id': 'fake-cycle', **node}
        site.download_hestia = lambda *args: fake_node
        site.find_related = lambda *args: [fake_node]
