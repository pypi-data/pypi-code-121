""" The rewrite youtube shorts module turns short youtube urls into less short urls.
Available commands:
None, will trigger on youtube shorts links.
Usage example:
[Xhark]: https://youtube.com/shorts/_mLniGHJwzI
Would results in:
"Bot: https://youtube.com/watch?v=_mLniGHJwzI"
"""

import os
import re

from nio import RoomMessage, MatrixRoom

from chaanbot.database import Database
from chaanbot.matrix import Matrix


class RewriteYoutubeShorts:
    always_run = True  # Run on all messages, even if other modules has activated
    output_message_prefix = ""

    def __init__(self, config, matrix: Matrix, database: Database, requests):
        self.matrix = matrix
        self.requests = requests
        self.output_message_prefix = config.get("rewrite_youtube_shorts", "prefix_message",
                                                fallback="Fixed your link(s): ")

    async def run(self, room: MatrixRoom, event: RoomMessage, message) -> bool:
        links = re.findall(r"http[s]*://[w{3}.]*youtube\.com/shorts/\w+", message, re.IGNORECASE)
        hits = [link.replace("/shorts/", "/watch?v=") for link in links]
        if hits:
            msg = self.output_message_prefix + os.linesep.join(hits)
            await self.matrix.send_text_to_room(msg, room.room_id)

        return False  # The module does not use commands and should not return that it has handled one
