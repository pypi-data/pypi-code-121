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
from telectron import types
from telectron import utils
from telectron.scaffold import Scaffold
from .inline_session import get_session


class EditInlineReplyMarkup(Scaffold):
    async def edit_inline_reply_markup(
        self,
        inline_message_id: str,
        reply_markup: "types.InlineKeyboardMarkup" = None
    ) -> bool:
        """Edit only the reply markup of inline messages sent via the bot (for inline bots).

        Parameters:
            inline_message_id (``str``):
                Identifier of the inline message.

            reply_markup (:obj:`~telectron.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                from telectron.types import InlineKeyboardMarkup, InlineKeyboardButton

                # Bots only
                app.edit_inline_reply_markup(
                    inline_message_id,
                    InlineKeyboardMarkup([[
                        InlineKeyboardButton("New button", callback_data="new_data")]]))
        """

        unpacked = utils.unpack_inline_message_id(inline_message_id)
        dc_id = unpacked.dc_id

        session = await get_session(self, dc_id)

        return await session.send(
            raw.functions.messages.EditInlineBotMessage(
                id=unpacked,
                reply_markup=await reply_markup.write(self) if reply_markup else None,
            ),
            sleep_threshold=self.sleep_threshold
        )
