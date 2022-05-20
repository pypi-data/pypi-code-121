''' TelegramBot '''
from typing import Any, Union

from requests import Response, Session


class Telegram(Session):
    ''' Telegram '''

    def __init__(self, token: str):
        super().__init__()
        self.url = f'https://api.telegram.org/bot{token}'

    def get_me(self) -> Response:
        ''' Get me '''
        return self.post(f'{self.url}/getMe')

    def send_message(self, chat_id: str, text: str,
                     parse_mode: str = 'Markdown',
                     reply_markup: Union[dict[str, Any], None] = None) -> Response:
        ''' Send message '''
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode}  # type: dict[str, Union[str, dict[str, Any]]]

        if reply_markup is not None:
            data['reply_markup'] = reply_markup

        return self.post(f'{self.url}/sendMessage', json=data)

    def set_webhook(self, url: str) -> Response:
        ''' Set webhook '''
        return self.post(f'{self.url}/setWebhook', json={'url': url})

    def get_webhook_info(self, url: str) -> Response:
        ''' Get webhook info '''
        return self.post(f'{self.url}/getWebhookInfo', json={'url': url})

    def delete_webhook(self) -> Response:
        ''' delete webhook '''
        return self.post(f'{self.url}/deleteWebhook')

    @staticmethod
    def is_command_start(data: dict[str, Any]) -> bool:
        ''' command start '''
        if data['message']['from']['is_bot']:
            return False

        if data['message']['text'].strip() == '/start':
            return True

        return False

    @staticmethod
    def is_command_start_linkme(data: dict[str, Any]) -> bool:
        ''' command start '''
        if 'message' not in data:
            return False

        if data['message']['from']['is_bot']:
            return False

        if data['message']['text'].strip() in ('/start linkme', '/linkme'):
            return True

        return False
