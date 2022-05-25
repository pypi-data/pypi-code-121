import json
import requests
from zeno_etl_libs.config.common import Config


class GoogleSheet:
    def __init__(self):
        configobj = Config.get_instance()
        secrets = configobj.get_secrets()
        self.url = secrets['NODE_NOTIFICATION_BASE_URL']
        self.auth_token = secrets['NOTIFICATION_AUTH_TOKEN']

    def download(self, data):
        """
        sample data
        {
            "spreadsheet_id":"1fhQPO7qkbly1q-iDoMN6jmc9VNhzmYBwIFpSsh76m0M",
            "sheet_name":"Sheet1",
            "listedFields": ["posting_date","id","store_id"]
        }
        """

        payload = {
            'spreadsheet_id': data['spreadsheet_id'],
            'sheet_name': data['sheet_name'],
            'listedFields': data['listedFields']
        }

        response = requests.post(
            url=self.url + "api/v1/googlesheet-access/read",
            headers={'Authorization': self.auth_token, 'Content-Type': 'application/json'},
            data=json.dumps(payload), timeout=(1, 60))
        if 200 >= response.status_code <= 299:
            response_data = response.json()
            if not response_data.get('is_error'):
                return response.json().get('data', [])
            else:
                raise ValueError(f"Error: {str(response.text)}")
        else:
            raise Exception(f"API call failed, error: {response.text}")

    def upload(self, data):
        data = {
            'spreadsheet_id': data['spreadsheet_id'],
            'sheet_name': data['sheet_name'],
            'headers': data['headers'],
            'data': data['data'],
        }

        response = requests.post(
            url=self.url + "api/v1/googlesheet-access/write",
            headers={'Authorization': self.auth_token, 'Content-Type': 'application/json'},
            data=json.dumps(data), timeout=(1, 60))

        if 200 >= response.status_code <= 299:
            print(f"Data uploaded successfully. spreadsheet_id: {data['spreadsheet_id']}, name: {data['sheet_name']}")
        else:
            raise Exception(f"API call failed, error: {response.text}")
