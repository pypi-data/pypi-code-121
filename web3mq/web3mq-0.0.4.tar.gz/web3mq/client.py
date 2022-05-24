"""web3mq client"""

from .sync_request import SyncRequestHandler
from .singleton_utils import Singleton

from . import user, room, message, contact


class Web3mqClient(Singleton):

    def __init__(self, env='prod', base_uri=None):
        self.reqhandler = SyncRequestHandler(env=env, base_uri=base_uri)

        self.__auth_headers = {'Content-Type': 'application/json'}

    def get_auth_headers(self):
        return self.__auth_headers

    def do_register(self, wallet_address: str, platform: str, user_name: str):
        return user.do_register(self, wallet_address, platform, user_name)

    def do_login(self, login_random_secret: str, signature: str, wallet_address: str):
        result = user.do_login(self, login_random_secret, signature, wallet_address)

        access_token = result['access_token']

        self.__auth_headers.update({'Authorization': 'Bearer {}'.format(access_token)})

        return result

    def get_login_random_secret(self, wallet_address: str):
        return user.get_login_random_secret(self, wallet_address)

    def get_user_info(self, platform: str, user_name: str):
        return user.get_user_info(self, platform, user_name)

    def search_users(self, keyword: str):
        return user.search_users(self, keyword)

    def create_chat_room(self, user_ids: list):
        return room.create_chat_room(self, user_ids)

    def get_room_info(self, room_id: str):
        return room.get_room_info(self, room_id)

    def get_my_chats(self, page: int, size: int):
        return room.get_my_chats(self, page, size)

    def get_my_room_ids(self):
        return room.get_my_room_ids(self)

    def add_user_to_my_contact(self, user_id: str):
        return contact.add_user_to_my_contact(self, user_id)

    def get_my_contact(self, page: int, size: int):
        return contact.get_my_contact(self, page, size)

    def get_history_messages(self, room_id: str, page: int, size: int, after_time_stamp: int):
        return contact.get_history_messages(self, room_id, page, size, after_time_stamp)
