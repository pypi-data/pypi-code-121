from directory_api_client.base import AbstractAPIClient

url_lookup_by_postcode = '/exporting/offices/{postcode}/'


class ExportingAPIClient(AbstractAPIClient):
    def lookup_regional_offices_by_postcode(self, postcode):
        return self.get(
            url=url_lookup_by_postcode.format(postcode=postcode),
            use_fallback_cache=True,
        )
