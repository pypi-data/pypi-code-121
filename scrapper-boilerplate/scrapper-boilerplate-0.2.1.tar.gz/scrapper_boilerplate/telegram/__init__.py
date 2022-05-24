import os

import telegram
from dotenv import load_dotenv


class TelegramBot:
    """
    Telegram message handler
    - to get chat: access @getidsbot and type start to get id
    - to access token, create bot in @botFather and paste the token
    """ 

    def __init__(self, root_path):
        print('> iniciando módulo do telegram!')
        load_dotenv(os.path.join(root_path, '.env'))
        self.TOKEN = os.environ.get("TELEGRAM_TOKEN")
        self.bot = telegram.Bot(token=self.TOKEN)
        self.CHAT_ID = [1593930824]

    def send_message(self, msg):
        try:
            print('> Enviando mensagem...')
            for chat in self.CHAT_ID:
                self.bot.sendMessage(chat_id=chat, text=msg)

        except Exception as error:
            print(f'> [ERRO] ao enviar mensagem! {error} ')

        else:
            print('> Mensagem enviada com sucesso!')