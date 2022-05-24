import json
import requests


class AccountInfo:
    def __init__(self, api_key) -> None:
        self.api_key = api_key

    def account_level(self, nickname):
        r = requests.get(f"https://eun1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{nickname}?api_key={self.api_key}")

        return r.json()["summonerLevel"]