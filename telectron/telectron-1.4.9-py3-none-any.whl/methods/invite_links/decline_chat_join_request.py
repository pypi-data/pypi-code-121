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

from typing import Union

from telectron import raw
from telectron.scaffold import Scaffold


class DeclineChatJoinRequest(Scaffold):
    async def decline_chat_join_request(
        self,
        chat_id: Union[int, str],
        user_id: int,
    ) -> bool:
        """Decline a chat join request.

        The bot must be an administrator in the chat for this to work and must have the *can_invite_users* administrator
        right.

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier for the target chat or username of the target channel/supergroup
                (in the format @username).

            user_id (``int``):
                Unique identifier of the target user.

        Returns:
            ``bool``: True on success.
        """
        await self.send(
            raw.functions.messages.HideChatJoinRequest(
                peer=await self.resolve_peer(chat_id),
                user_id=await self.resolve_peer(user_id),
                approved=False
            )
        )

        return True
