import json
import requests

class MasteryInfo:
    def __init__(self, api_key) -> None:
        self.api_key = api_key

    def get_basic_info(self, nickname):
        r = requests.get(f"https://eun1.api.riotgames.com/lol/summoner/v4/summoners/by-name/Daramianek?api_key={self.api_key}")

        return r.json()

    def champion_maestry(self, nickname):
        encrypted_summoner_id = self.get_basic_info(nickname)["id"]
        r = requests.get(f"https://eun1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{encrypted_summoner_id}?api_key={self.api_key}")

        return r.json()
