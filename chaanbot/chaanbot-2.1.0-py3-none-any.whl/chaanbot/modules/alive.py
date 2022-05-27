""" The Alive module allows users to check if bot is alive

Available commands:
!alive                  - Bot will respond "Yes." if it's running and allowed to send to room.

Usage example:
!alive

Would results in:
"Bot: Yes."
"""
import logging

from nio import MatrixRoom, RoomMessage

from chaanbot import command_utility
from chaanbot.database import Database
from chaanbot.matrix import Matrix

logger = logging.getLogger("ping")


class Alive:
    def __init__(self, config, matrix: Matrix, database: Database, requests):
        self.matrix = matrix

    always_run = False
    operations = {
        "alive": {
            "commands": ["!alive", "!running"]
        }
    }

    async def run(self, room: MatrixRoom, event: RoomMessage, message) -> bool:
        if self.should_run(message):
            await self.matrix.send_text_to_room("Yes.", room.room_id)
            return True
        return False

    def should_run(self, message) -> bool:
        return command_utility.matches(self.operations, message)
