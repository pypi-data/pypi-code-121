# coding: utf-8
import unittest
from mock import patch, Mock
import os

from otrs_somconnexio.otrs_models.customer_user import CustomerUser


class CustomerUserTestCase(unittest.TestCase):

    def setUp(self):
        self.customer_id = 'customer@test.coop'
        self.MockClient = Mock(spec=[])
        self.MockClient.return_value = Mock(spec=['get_preferences', 'set_preference',
                                                  'get_data', 'user_id'])
        self.preferences = {
            'key1': 'value1',
            'key2': 'value2'
        }

    def test_change_language(self):
        new_lang = 'ca'
        preference_key = 'UserLanguage'

        CustomerUser(self.customer_id, self.MockClient).change_language(new_lang)

        self.MockClient.return_value.set_preference.assert_called_once_with(
            preference_key, new_lang)

    def test_set_mm_account_id(self):
        mm_account_id = '123'
        preference_key = 'MMAccountId'

        CustomerUser(self.customer_id, self.MockClient).set_mm_account_id(mm_account_id)

        self.MockClient.return_value.set_preference.assert_called_once_with(
            preference_key, mm_account_id)

    def test_get_mm_account_id_true(self):
        self.preferences['MMAccountId'] = '123'
        self.MockClient.return_value.get_preferences.return_value = self.preferences

        mm_account_id = CustomerUser(self.customer_id, self.MockClient).get_mm_account_id()

        self.MockClient.return_value.get_preferences.assert_called_once_with()
        self.assertEquals(mm_account_id, '123')

    def test_get_mm_account_id_empty(self):
        self.MockClient.return_value.get_preferences.return_value = self.preferences

        mm_account_id = CustomerUser(self.customer_id, self.MockClient).get_mm_account_id()

        self.MockClient.return_value.get_preferences.assert_called_once_with()
        self.assertEquals(mm_account_id, None)

    def test_get_data(self):
        self.MockClient.return_value.get_data.return_value = self.preferences

        data = CustomerUser(self.customer_id, self.MockClient).get_data()

        self.MockClient.return_value.get_data.assert_called_once_with()
        self.assertEquals(data, self.preferences)
