import sys
import os
import unittest
from server.common.variables import RESPONSE, ERROR
from server.server import handle

sys.path.append(os.path.join(os.getcwd(), '../../messenger'))


class TestClass(unittest.TestCase):
    def setUp(self) -> None:
        self.bad_response = {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        }

    def tearDown(self) -> None:
        pass

    def test_get_response_200(self):
        """тест ответа 200"""
        test1 = handle({'action': 'presence',
                        'time': 1643050465.6124058,
                        'type': 'status',
                        'user': {'account_name': 'Guest',
                                 'status': 'Yep, I am here!'}})
        self.assertEqual(test1, {RESPONSE: 200})

    def test_get_response_bad_account_name(self):
        """тест ответа 400 при неверном имени пользователя"""
        test2 = handle({'action': 'presence',
                        'time': 1643050465.6124058,
                        'type': 'status',
                        'user': {'account_name': 'Another Name',
                                 'status': 'Yep, I am here!'}})
        self.assertEqual(test2, self.bad_response)

    def test_get_response_without_time(self):
        """тест ответа 400 при отсутствии метки времени"""
        test3 = handle({'action': 'presence', 'type': 'status', 'user': {
            'account_name': 'Guest', 'status': 'Yep, I am here!'}})
        self.assertEqual(test3, self.bad_response)

    def test_get_response_without_user(self):
        """тест ответа 400 при отсутствии пользователя"""
        test4 = handle(
            {'action': 'presence',
             'time': 1643050465.6124058, 'type': 'status'})
        self.assertEqual(test4, self.bad_response)

    def test_get_response_without_action(self):
        """тест ответа 400 при отсутствии действия"""
        test5 = handle({'time': 1643050465.6124058, 'type': 'status', 'user': {
            'account_name': 'Guest', 'status': 'Yep, I am here!'}})
        self.assertEqual(test5, self.bad_response)

    def test_get_response_bad_action(self):
        """тест ответа 400 при неправильном действии"""
        test6 = handle({'action': 'BAD ACTION',
                        'time': 1643050465.6124058,
                        'type': 'status',
                        'user': {'account_name': 'Guest',
                                 'status': 'Yep, I am here!'}})
        self.assertEqual(test6, self.bad_response)


if __name__ == '__main__':
    unittest.main()
