import requests
import uuid

class Cracked:
    key = None
    error = '"error":"invalid key"'

    def __init__(self, key):
        self.key = key
        self.CrackedAuth()
        self.res = res
        self.error = '"error":"invalid key"'
        self.username = ''

    def CrackedAuth(self):
        global res
        jsons = {
            "a": "auth",
            "k": str(self.key),
            "hwid": str(uuid.getnode())
        }
        res = requests.post(url='https://cracked.io/auth.php', data=jsons).text