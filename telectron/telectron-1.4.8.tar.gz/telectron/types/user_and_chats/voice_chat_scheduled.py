#  telectron - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of telectron.
#
#  telectron is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  telectron is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with telectron.  If not, see <http://www.gnu.org/licenses/>.

from telectron import raw
from ..object import Object


class VoiceChatScheduled(Object):
    """A service message about a voice chat scheduled in the chat.

    Parameters:
        start_date (``int``):
            Point in time (Unix timestamp) when the voice chat is supposed to be started by a chat administrator.
    """

    def __init__(
        self, *,
        start_date: int
    ):
        super().__init__()

        self.start_date = start_date

    @staticmethod
    def _parse(action: "raw.types.MessageActionGroupCallScheduled") -> "VoiceChatScheduled":
        return VoiceChatScheduled(start_date=action.schedule_date)
