import requests

class Notifier:
    def __init__(self, botToken, members=dict()):
        self.bot_token = botToken
        self.members = members

    def sendMessage(self, member, message):
        chatId = ""
        if member in self.members.keys():
            chatId = self.members[member]
        else:
            chatId = member

        send_text = (
            "https://api.telegram.org/bot"
            + self.bot_token
            + "/sendMessage?chat_id="
            + chatId
            + "&parse_mode=Markdown&text="
            + message
        )

        try:
            response = requests.get(send_text).json()
            if response["ok"] == False:
                print(f"{response['error_code']} : {response['description']}")
        except:
            print("Telegram API call failed.")

    def printMembers(self):
        for member in self.members.keys():
            print(f"Alias : {member} \t| ID : {self.members[member]}")

    def printChatIds(self):
        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"

        try:
            response = requests.get(url).json()
            if response["ok"] == False:
                print(f"{response['error_code']} : {response['description']}")
            else:
                for x in response["result"]:
                    chatId = x["message"]["chat"]["id"]
                    userName = x["message"]["chat"]["username"]
                    print(f"Username : {userName} \t| Chat ID : {chatId}")
        except:
            print("Telegram API call failed.")
