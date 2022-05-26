import requests
from discord.ext import commands

class Client:
    """This `class` represents a `Client`, the main item used in the package.
    """
    def __init__(self, client: commands.Bot, token: str):
        """Initializes a new `Client`

        Args:
            client (commands.Bot): Your `DiscordPY` client
            token (str): Your `Radar Bot Directory` token.
        """
        self.client = client
        self.token = token

    def stats(self, server_count: int, shard_count=1):
        """Posts your server stats to the Radar Bot Directory.

        Args:
            server_count (int): The server count for your bot
            shard_count (int): The amount of shards your bot has
        """
        if not server_count:
            raise SyntaxError("Server Count is required!")

        r = requests.post(
            url=f"https://radarbotdirectory.xyz/api/bot/{str(self.client.user.id)}/stats",
            headers={
                "Content-Type": "application/json",
                "Authorization": self.token
            },
            json={
                "servers": server_count,
                "shards": shard_count
            }
        )
        if r.status_code != 200:
            return print(f"[RadarBots.py]: {r.status_code} - {r.json()}")
        return print(f"[RadarBots.py]: {r.json()}")

    def botInfo(self):
        """Gets your bot info
        """
        r = requests.get(f"https://radarbotdirectory.xyz/api/bot/{str(self.client.user.id)}")
        if r.status_code != 200:
            return print(f"[RadarBots.py]: {r.status_code} - {r.json()}")
        return print(f"[RadarBots.py]: {r.json()}")

    def lastVoted(self, user_id: int):
        """Returns the Unix Epoch timestamp of the last time the provided user voted for your bot.

        Args:
            user_id (int): The user ID

        Returns:
            None: A console log with the JSON (whether the request is good or not)
        """
        if not user_id:
            raise SyntaxError("The user ID is required!")
        user_id = str(user_id)
        r = requests.get(f"https://radarbotdirectory.xyz/api/lastvoted/{user_id}/{str(self.client.user.id)}")
        if r.status_code != 200:
            return print(f"[RadarBots.py]: {r.status_code} - {r.json()}")
        return print(f"[RadarBots.py]: {r.json()}")
