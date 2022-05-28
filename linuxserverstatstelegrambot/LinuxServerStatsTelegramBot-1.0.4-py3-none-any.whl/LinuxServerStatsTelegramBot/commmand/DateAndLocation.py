import geocoder
from datetime import datetime
from LinuxServerStatsTelegramBot.commmand.Command import Command
from LinuxServerStatsTelegramBot.DI import DI


class DateAndLocation(Command):
    def execute(self) -> str:
        g = geocoder.ip("me")
        location = g.geojson["features"][0]["properties"]["address"]
        now = datetime.now()
        return f"Informing from {DI.get_server_name()} located in: {location} at {now}"


if __name__ == "__main__":
    from LinuxServerStatsTelegramBot.commmand.ConvertTextToImage import ConvertTextToImage
    data = DateAndLocation().execute()
    ConvertTextToImage(data=data, image_path="/tmp/testing.png").execute()
