import requests


class TelegramBOT:

    def __init__(self,
                 bot_token,
                 bot_chatID):

        self.bot_token = bot_token
        self.bot_chatID = bot_chatID

    def telegram_bot_sendtext(self,
                              bot_message):

        send_text = 'https://api.telegram.org/bot' + self.bot_token + '/sendMessage?chat_id=' + \
                    self.bot_chatID + '&parse_mode=Markdown&text=' + bot_message

        response = requests.get(send_text)

        return response.json()

    def enter_position_message(self,
                               type,
                               pair,
                               qty,
                               entry_price,
                               tp,
                               sl):
        token = pair[:-4]
        qty = float(qty)
        entry_price = float(entry_price)
        bot_message = f"Enter in {type} position on {pair}. " \
                      f"\nQuantity {token} = {qty} " \
                      f"\nQuantity USDT ≈ {round(qty*entry_price,2)} $" \
                      f"\nActual price = {entry_price}" \
                      f"\nTake profit = {tp} \nStop loss = {sl}"

        self.telegram_bot_sendtext(bot_message=bot_message)

    def takeprofit_message(self,
                           pair,
                           pnl):

        bot_message = f"Take profit price reached on {pair} \U0001F911 \n" \
                      f"Profit = {round(pnl, 2)} $"

        self.telegram_bot_sendtext(bot_message=bot_message)

    def stoploss_message(self,
                         pair,
                         pnl):

        bot_message = f"Stop loss price reached on {pair} \U0001F4C9 \n" \
                      f"Profit = {round(pnl, 2)} $"

        self.telegram_bot_sendtext(bot_message=bot_message)

    def exitsignal_message(self,
                         pair,
                         pnl):

        bot_message = f"Exit {pair} position \U0001F645 \n" \
                      f"Profit = {round(pnl, 2)} $"

        self.telegram_bot_sendtext(bot_message=bot_message)


# self = TelegramBOT(bot_token="5399743657:AAE9nV4cXbzHAGCJZbcKQo_sdxO6AeI4UB0",
#                    bot_chatID="1347365625")
