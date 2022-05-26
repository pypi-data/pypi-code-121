from unittest.mock import MagicMock

class LookupsApiMock:

    def __init__(self):
        self.mock_bulk_query_org_guids = MagicMock()
        self.mock_lookup_org_guid = MagicMock()

    def bulk_query_org_guids(self, *args, **kwargs):
        """
        This method mocks the original api LookupsApi.bulk_query_org_guids with MagicMock.
        """
        return self.mock_bulk_query_org_guids(self, *args, **kwargs)

    def lookup_org_guid(self, *args, **kwargs):
        """
        This method mocks the original api LookupsApi.lookup_org_guid with MagicMock.
        """
        return self.mock_lookup_org_guid(self, *args, **kwargs)

