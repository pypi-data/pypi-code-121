""" The Darksky weather module allows users to broadcast the current weather of a (their?) location.

Available commands:
!addcoordinates [LATITUDE] [LONGITUDE]          - Sets the coordinates for a user
!weather                                        - Send today's weather for user's location
!weather [DAY IN FUTURE] [DAY IN FUTURE] ...    - Send several days' weather for user's location

Usage example:
!addcoordinates 59.3293 18.0686
!weather 0 1 2

Would results in (something similar to):
"Bot:   Today: Min: 15.1, Max: 19.3. Cloudy with a high chance of rain
        Tomorrow: Min: 25.1, Max: 30.3. Sunny
        2 days from now: Min: -15, Max: -10. Heavy snow"
"""
import logging
import re
from typing import Optional

from nio import MatrixRoom, RoomMessage

from chaanbot import command_utility
from chaanbot.database import Database
from chaanbot.matrix import Matrix

logger = logging.getLogger("weather")


class DarkskyWeather:
    always_run = False
    max_days_to_send_at_once = 5
    darksky_api_url = 'https://api.darksky.net'
    operations = {
        "weather": {
            "commands": ["!weather"],
            "argument_regex": re.compile(r"[\d( \d)*]?", re.IGNORECASE)
        },
        "add_weather_coordinates": {
            "commands": ["!addcoordinates", "!addcoords", "!setcoordinates", "!setcoords"],
            "argument_regex": re.compile(r"-?\d{1,2}\.?\d+(,|\s|,\s)-?\d{1,2}\.?\d", re.IGNORECASE)
            # Lat&Long are 2 digits followed by decimals
        }
    }

    def __init__(self, config, matrix: Matrix, database: Database, requests):
        self.matrix = matrix
        self.requests = requests
        api_key = config.get("darksky_weather", "api_key", fallback=None)
        if api_key:
            self.api_key = api_key
        else:
            self.disabled = True
            logger.info("No API key provided for darksky weather, module disabled")

        if database:
            self.database = database
            logger.debug("Initializing highlight database if needed")
            conn = database.connect()
            conn.execute('''CREATE TABLE IF NOT EXISTS user_coordinates
            (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            ROOM_ID TEXT NOT NULL,
            USER_ID TEXT NOT NULL,
            LATITUDE TEXT NOT NULL,
            LONGITUDE TEXT NOT NULL,
            UNIQUE(ROOM_ID, USER_ID));    
            ''')
            conn.commit()
        else:
            self.disabled = True
            logger.info("No database provided, darksky weather module disabled")

    async def run(self, room: MatrixRoom, event: RoomMessage, message) -> bool:
        if self.should_run(message):
            logger.debug("Should run darksky weather, checking next command")
            if command_utility.matches(self.operations["weather"], message):
                logger.debug("Showing weather")
                await self._send_weather(room, event.sender, message)
            elif command_utility.matches(self.operations["add_weather_coordinates"], message):
                logger.debug("Adding coordinates")
                await self._add_coordinates(room, event.sender, message)
            else:
                raise RuntimeError("Could not find command to run on message, but should have been able to")
            return True
        return False

    def should_run(self, message) -> bool:
        return not hasattr(self, "disabled") and command_utility.matches(self.operations, message)

    async def _send_weather(self, room: MatrixRoom, user_id, message):
        latitude, longitude = self._get_coordinates(room, user_id)
        if not latitude or not longitude:
            await self.matrix.send_text_to_room("Set your coordinates by using !setcoordinates [LATITUDE] [LONGITUDE].",
                                                room.room_id)
            return

        argument = command_utility.get_argument(message)

        if argument:
            days = argument.strip().split(" ")
            await self._send_several_days_weather(room, latitude, longitude, days)
            return
        else:
            await self._send_todays_weather(room, latitude, longitude)
            return

    async def _send_several_days_weather(self, room: MatrixRoom, latitude, longitude, days):
        if len(days) > self.max_days_to_send_at_once:
            await self.matrix.send_text_to_room(
                "Can only look up {} days at once.".format(self.max_days_to_send_at_once),
                room.room_id)
            return

        url = "{}/forecast/{}/{},{}?units=si&exclude=currently,minutely,hourly,alerts,flags" \
            .format(self.darksky_api_url, self.api_key, latitude, longitude)

        contents = self.requests.get(url).json()
        message_for_one_day = "{} Max: {}, Min: {}\t{}\n"
        message = ""
        for days_from_today in days:
            day = "Today\t\t\t" if days_from_today == "0" \
                else "Tomorrow\t\t" if days_from_today == "1" \
                else "{} days from now\t".format(days_from_today)
            min_temp = contents["daily"]["data"][int(days_from_today)]["temperatureLow"]
            max_temp = contents["daily"]["data"][int(days_from_today)]["temperatureHigh"]
            summary = contents["daily"]["data"][int(days_from_today)]["summary"]
            message += message_for_one_day.format(day, max_temp, min_temp, summary)

        await self.matrix.send_text_to_room(message, room.room_id)

    async def _send_todays_weather(self, room: MatrixRoom, latitude, longitude):
        url = "{}/forecast/{}/{},{}?units=si&exclude=minutely,hourly,alerts,flags" \
            .format(self.darksky_api_url, self.api_key, latitude, longitude)

        contents = self.requests.get(url).json()
        current_temp = str(contents["currently"]["temperature"])
        min_temp = str(contents["daily"]["data"][0]["temperatureLow"])
        max_temp = str(contents["daily"]["data"][0]["temperatureHigh"])
        summary = contents["currently"]["summary"]

        message = "Currently: {} (Max: {}, Min: {})\t{}" \
            .format(current_temp, max_temp, min_temp, summary)
        await self.matrix.send_text_to_room(message, room.room_id)

    async def _add_coordinates(self, room: MatrixRoom, user_id, message):
        argument = command_utility.get_argument(message).strip()

        split_argument = re.split(';|,|\\s', argument, 1)
        latitude = split_argument[0].strip()
        longitude = split_argument[1].strip()
        conn = self.database.connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO user_coordinates(ROOM_ID, USER_ID, LATITUDE, LONGITUDE) "
            "VALUES(?,?,?,?)",
            (room.room_id, user_id, latitude, longitude))
        conn.commit()
        logger.debug(
            "Inserted Lat {} Long {} for user_id {} and room {} with id {}".format(latitude, longitude, user_id,
                                                                                   room.room_id, cursor.lastrowid))
        await self.matrix.send_text_to_room("Coordinates set to {},{}.".format(latitude, longitude), room.room_id)

    def _get_coordinates(self, room: MatrixRoom, user_id) -> (Optional[str], Optional[str]):
        conn = self.database.connect()
        result = conn.execute(
            "SELECT LATITUDE,LONGITUDE FROM user_coordinates WHERE ROOM_ID = ? AND USER_ID = ?",
            (room.room_id, user_id))
        conn.commit()
        result = result.fetchone()
        return (result[0], result[1]) if result else (None, None)
