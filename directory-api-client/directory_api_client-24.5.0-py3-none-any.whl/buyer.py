from directory_api_client.base import AbstractAPIClient

url_save = '/buyer/'
url_csv_dump = '/buyer/csv-dump/'


class BuyerAPIClient(AbstractAPIClient):
    def send_form(self, form_data):
        return self.post(url_save, data=form_data)

    def get_csv_dump(self, token):
        return self.get(url_csv_dump, params={'token': token}, use_fallback_cache=False)
