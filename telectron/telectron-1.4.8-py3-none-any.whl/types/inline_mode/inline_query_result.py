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

from uuid import uuid4

import telectron
from telectron import types
from ..object import Object

"""- :obj:`~telectron.types.InlineQueryResultCachedAudio`
    - :obj:`~telectron.types.InlineQueryResultCachedDocument`
    - :obj:`~telectron.types.InlineQueryResultCachedGif`
    - :obj:`~telectron.types.InlineQueryResultCachedMpeg4Gif`
    - :obj:`~telectron.types.InlineQueryResultCachedPhoto`
    - :obj:`~telectron.types.InlineQueryResultCachedSticker`
    - :obj:`~telectron.types.InlineQueryResultCachedVideo`
    - :obj:`~telectron.types.InlineQueryResultCachedVoice`
    - :obj:`~telectron.types.InlineQueryResultAudio`
    - :obj:`~telectron.types.InlineQueryResultContact`
    - :obj:`~telectron.types.InlineQueryResultGame`
    - :obj:`~telectron.types.InlineQueryResultDocument`
    - :obj:`~telectron.types.InlineQueryResultGif`
    - :obj:`~telectron.types.InlineQueryResultLocation`
    - :obj:`~telectron.types.InlineQueryResultMpeg4Gif`
    - :obj:`~telectron.types.InlineQueryResultPhoto`
    - :obj:`~telectron.types.InlineQueryResultVenue`
    - :obj:`~telectron.types.InlineQueryResultVideo`
    - :obj:`~telectron.types.InlineQueryResultVoice`"""


class InlineQueryResult(Object):
    """One result of an inline query.

    telectron currently supports results of the following types:

    - :obj:`~telectron.types.InlineQueryResultArticle`
    - :obj:`~telectron.types.InlineQueryResultPhoto`
    - :obj:`~telectron.types.InlineQueryResultAnimation`
    """

    def __init__(
        self,
        type: str,
        id: str,
        input_message_content: "types.InputMessageContent",
        reply_markup: "types.InlineKeyboardMarkup"
    ):
        super().__init__()

        self.type = type
        self.id = str(uuid4()) if id is None else str(id)
        self.input_message_content = input_message_content
        self.reply_markup = reply_markup

    async def write(self, client: "telectron.Client"):
        pass
