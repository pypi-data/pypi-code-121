import sys
import os
import unittest
from common.variables import PRESENCE, STATUS, USER, ACCOUNT_NAME, \
    TIME, ACTION, RESPONSE, ERROR
from client import create_presence, process_ans
from common.errors import ReqFieldMissingError

sys.path.append(os.path.join(os.getcwd(), '../../messenger'))


class TestClass(unittest.TestCase):
    def test_presence(self):
        """тест запроса"""
        test1 = create_presence(account_name='Guest')
        test1[TIME] = 6.6
        self.assertEqual(test1, {
            ACTION: PRESENCE,
            TIME: 6.6,
            TYPE: STATUS,
            USER: {
                ACCOUNT_NAME: 'Guest',
                STATUS: "Yep, I am here!"
            }
        })

    def test_process_ans_200(self):
        """тест ответа 200"""
        test2 = process_ans({'response': 200})
        self.assertEqual(test2, '200 : OK')

    def test_process_ans_400(self):
        """тест ответа 400"""
        test3 = process_ans({
            RESPONSE: 400,
            ERROR: 'Bad Request'
        })
        self.assertEqual(test3, '400 : Bad Request')

    def test_without_response(self):
        """тест отсутствия RESPONSE"""
        self.assertRaises(
            ReqFieldMissingError, process_ans, {
                ERROR: 'Bad Request'})


if __name__ == '__main__':
    unittest.main()
