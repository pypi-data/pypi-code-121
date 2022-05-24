import json
import requests


class MasteryInfo:
    def __init__(self, api_key) -> None:
        self.api_key = api_key

    def ex(self):
        r = requests.get(f"https://eun1.api.riotgames.com/lol/summoner/v4/summoners/by-name/Daramianek?api_key={self.api_key}")

        return r.json()

    def champion_maestry(self, nickname):
        r = requests
