class TelegramArgumentMixin:
    """
    Добавляет параметры
        --telegram_bot_api_token
    """

    def patch_arguments_schema(self):
        super().patch_arguments_schema()

        self._arguments_schema.extend(
            (
                {
                    'section': 'telegram',
                    'option': 'bot_api_token',
                    'help': 'Telegram BOT API токен.',
                },
            )
        )