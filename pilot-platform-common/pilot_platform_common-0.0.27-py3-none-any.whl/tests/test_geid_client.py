from common.geid.geid_client import GEIDClient


class TestGEIDClient:
    client = GEIDClient()

    def test_01_get_GEID(self):
        geid = self.client.get_GEID()
        assert type(geid) == str
        assert len(geid) == 47

    def test_02_get_bulk_GEID(self):
        geids = self.client.get_GEID_bulk(5)
        assert type(geids) == list
        assert len(geids) == 5
