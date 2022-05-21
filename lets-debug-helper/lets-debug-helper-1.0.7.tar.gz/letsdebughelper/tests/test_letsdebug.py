#!/usr/bin/env python3
import argparse
import mock
import json
import unittest

from letsdebughelper import letsdebug


class TestLetsdebug(unittest.TestCase):

    def setUp(self):
        self.url = 'https://letsdebug.net'
        self.domain = 'jeffistotallyawesome.space'
        self.test_id = 359646
        self.post_data = {"method": "http-01", "domain": self.domain}
        self.bad_post_data = {"metho": "http=01", "domain": self.domain}
        self.test_id_url = '{}/{}/{}'.format(self.url, self.domain, str(self.test_id))
        self.get_bad_result = 'Invalid request parameters.\n'
        self.post_result_text = '{"Domain":"jeffistotallyawesome.space","ID":359640}\n'
        self.post_bad_result = 'Please provide a valid domain name and validation method.\n'
        self.get_result_text = '{"id":359646,"domain":"jeffistotallyawesome.space","method":"http-01",\
"status":"Complete","created_at":"2020-11-16T20:39:19.970198Z","started_at":"2020-11-16T20:39:19.973775Z",\
"completed_at":"2020-11-16T20:39:22.855617Z","result":{"problems":[{"name":"CloudflareCDN","explanation":"The \
domain jeffistotallyawesome.space is being served through Cloudflare CDN. Any Let\'s Encrypt certificate installed \
on the origin server will only encrypt traffic between the server and Cloudflare. It is strongly recommended that \
the SSL option \'Full SSL (strict)\' be enabled.","detail":"https://support.cloudflare.com/hc/en-us/articles/\
200170416-What-do-the-SSL-options-mean-","severity":"Warning"}]}}\n'
        self.get_result_dict = {'id': 359646,
                                'domain': 'jeffistotallyawesome.space',
                                'method': 'http-01',
                                'status': 'Complete',
                                'created_at': '2020-11-16T20:39:19.970198Z',
                                'started_at': '2020-11-16T20:39:19.973775Z',
                                'completed_at': '2020-11-16T20:39:22.855617Z',
                                'result': {'problems': [{'name': 'CloudflareCDN',
                                                         'explanation': "The domain jeffistotallyawesome.space is being \
served through Cloudflare CDN. Any Let's Encrypt certificate installed on the origin server will only encrypt \
traffic between the server and Cloudflare. It is strongly recommended that the SSL option 'Full SSL (strict)' \
be enabled.", 'detail': 'https://support.cloudflare.com/hc/en-us/articles/200170416-What-do-the-SSL-options-mean-',
                                                         'severity': 'Warning'}]}}

    def _mock_response(self, status=200, text=None, json_data=None):
        mock_resp = mock.Mock()
        # set status code and content
        mock_resp.status_code = status
        # add json data if provided
        mock_resp.json = mock.Mock(return_value=json_data)
        mock_resp.text = text
        return mock_resp

    @mock.patch('requests.get')
    def test_le_get_call(self, mock_get):
        mock_resp = self._mock_response(text=self.get_result_text)
        mock_get.return_value = mock_resp
        result = letsdebug.le_get_call(self.test_id_url)
        self.assertEqual(result.text, self.get_result_text)

    @mock.patch('requests.get')
    def test_fail_le_get_call(self, mock_get):
        mock_resp = self._mock_response(status=400, text=self.get_bad_result)
        mock_get.return_value = mock_resp
        result = letsdebug.le_get_call(self.test_id_url)
        self.assertEqual(result.text, self.get_bad_result)

    @mock.patch('requests.post')
    def test_le_post_call(self, mock_post):
        mock_resp = self._mock_response(text=self.post_result_text)
        mock_post.return_value = mock_resp
        result = letsdebug.le_post_call(self.post_data)
        self.assertEqual(result.text, self.post_result_text)

    @mock.patch('requests.post')
    def test_fail_le_post_call(self, mock_post):
        mock_resp = self._mock_response(status=400, text=self.post_bad_result)
        mock_post.return_value = mock_resp
        result = letsdebug.le_post_call(self.bad_post_data)
        self.assertEqual(result.text, self.post_bad_result)

    @mock.patch('requests.get')
    def test_success_decode_result(self, mock_get):
        mock_resp = self._mock_response(json_data=json.loads(self.get_result_text))
        mock_get.return_value = mock_resp
        result = letsdebug.le_get_call(self.post_data)
        actual = letsdebug.decode_result(result)
        self.assertEqual(actual, self.get_result_dict)

    def test_fail_decode_result(self):
        with self.assertRaises(SystemExit):
            letsdebug.decode_result('Bad Data')

    @mock.patch('requests.get')
    def test_success_check_status(self, mock_get):
        mock_resp = self._mock_response(text=self.get_result_text)
        mock_get.return_value = mock_resp
        result = letsdebug.le_get_call(self.post_data)
        actual = letsdebug.check_status(result, self.get_bad_result)
        self.assertIsNone(actual)

    @mock.patch('requests.get')
    def test_fail_check_status(self, mock_get):
        mock_resp = self._mock_response(status=400, text=self.get_bad_result)
        mock_get.return_value = mock_resp
        result = letsdebug.le_get_call(self.bad_post_data)
        with self.assertRaises(SystemExit):
            letsdebug.check_status(result, self.get_bad_result)

    @mock.patch('argparse.ArgumentParser.parse_args')
    def test_parse_args(self, mock_args):
        mock_args.return_value = argparse.Namespace(domain='jeditest.com')
        expected = {'domain': 'jeditest.com'}
        actual = letsdebug.parse_args()
        actual_dict = vars(actual)
        self.assertEqual(actual_dict, expected)

    @mock.patch('argparse.ArgumentParser.parse_args')
    def test_parse_args_none(self, mock_args):
        mock_args.return_value = argparse.Namespace()
        with mock.patch('argparse._sys.argv', ['letsdebug.py']):
            with self.assertRaises(SystemExit):
                letsdebug.parse_args()
