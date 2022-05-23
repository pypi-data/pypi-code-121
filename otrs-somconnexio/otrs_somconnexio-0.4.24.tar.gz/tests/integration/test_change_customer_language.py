import os
import unittest
import json
from mock import Mock, patch

from otrs_somconnexio.otrs_models.customer_user import CustomerUser

USER = 'user'
PASSW = 'passw'
URL = 'https://otrs-url.coop/'


class ChangeCustomerUserIntegrationTestCase(unittest.TestCase):

    @patch.dict(os.environ, {
        'OTRS_USER': USER,
        'OTRS_PASSW': PASSW,
        'OTRS_URL': URL
    })
    @patch('otrs_somconnexio.user_management_client.client.requests', spec=['post'])
    def test_change_language(self, requests_mock):
        lang = 'ca_ES'
        user_id = 123

        expected_url = '{}otrs/nph-genericinterface.pl/Webservice/UserManagement/cuser'.format(URL)
        expected_body = {
            "UserLogin": USER,
            "Password": PASSW,
            "Object": "Kernel::System::CustomerUser",
            "Method": "SetPreferences",
            "Parameter": {
                "Key": 'UserLanguage',
                "Value": lang,
                "UserID": user_id
            }
        }

        requests_mock.post.return_value = Mock(spec=['json'])
        requests_mock.post.return_value.json.return_value = {"Result": [1]}

        CustomerUser(user_id).change_language(lang)

        requests_mock.post.assert_called_once_with(expected_url, data=json.dumps(expected_body))
