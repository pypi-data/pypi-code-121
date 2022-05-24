from typing import (
    Tuple,
)

import requests


class TelegramMessageSender:
    """
    Отправитель сообщения в телеграм-бота
    """

    _bot_send_url_template = 'https://api.telegram.org/bot{token}/sendMessage'

    def __init__(
        self,
        bot_api_token: str,
        chat_ids: Tuple[str],
    ):
        super().__init__()

        self._bot_api_token = bot_api_token
        self._chat_ids = chat_ids

    def send(self, message):
        """
        Отправить сообщение в указанные чаты
        """
        responses = []

        for chat_id in self._chat_ids:
            response = requests.get(
                url=(
                    self._bot_send_url_template.format(
                        token=self._bot_api_token,
                    )
                ),
                params={
                    'parse_mode': 'HTML',
                    'chat_id': chat_id,
                    'text': message,
                },
            )

            responses.append(
                f'{response.status_code} - {response.text}'
            )

        return '\n'.join(responses)
