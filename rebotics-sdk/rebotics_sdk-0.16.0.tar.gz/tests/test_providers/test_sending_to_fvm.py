import requests_mock

from rebotics_sdk.providers import FVMProvider


def test_sending_to_fvm():
    with requests_mock.Mocker() as m:
        codename = 'retailer_x'
        secret_key = 'secret_key_x'
        products_count = 10
        file_url = 'file_url'
        headers = {
            'HTTP_X_RETAILER_CODENAME': codename,
            'HTTP_X_RETAILER_SECRET_KEY': secret_key,
        }
        json = {
            "retailer_codename": codename,
            "products_count": products_count,
            "file": file_url
        }
        m.post(url='http://test.com/api/synchronization/', status_code=201, headers=headers, json=json)
        provider = FVMProvider('http://test.com')
        provider.set_retailer_identifier(codename=codename, secret_key=secret_key)

        response = provider.send_products_file_to_fvm(codename, products_count, file_url)
        assert response is not None
