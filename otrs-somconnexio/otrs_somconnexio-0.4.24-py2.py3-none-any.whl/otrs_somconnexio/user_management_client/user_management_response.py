import logging

from otrs_somconnexio.exceptions import UserManagementResponseEmpty

logger = logging.getLogger('otrs_somconnexio')


class UserManagementResponse:

    def __init__(self, raw_response, user_id, call):
        self.raw_data = raw_response.json()['Result']
        if self.raw_data == []:
            raise UserManagementResponseEmpty(user_id, call)

    def get_data(self):
        """
        Recieves a list with elements ordered as key-value pairs and returns a dict
        Ex: ['key1', 'value1', 'key2', 'value2'] -> {'key1': 'value1', 'key2': 'value2'}
        """
        iter_list = iter(self.raw_data)
        dct = {}

        for element in iter_list:
            try:
                dct[element] = next(iter_list)
            except StopIteration:
                pass
        return dct
