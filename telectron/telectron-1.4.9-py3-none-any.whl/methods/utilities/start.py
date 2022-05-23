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

import logging

from telectron import raw
from telectron.scaffold import Scaffold
from copy import copy

log = logging.getLogger(__name__)


class Start(Scaffold):
    async def start(self):
        """Start the client.

        This method connects the client to Telegram and, in case of new sessions, automatically manages the full
        authorization process using an interactive prompt.

        Returns:
            :obj:`~telectron.Client`: The started client itself.

        Raises:
            ConnectionError: In case you try to start an already started client.

        Example:
            .. code-block:: python

                from telectron import Client

                app = Client("my_account")
                app.start()

                ...  # Call API methods

                app.stop()
        """
        is_authorized = await self.connect()

        try:
            if not is_authorized:
                await self.authorize()

            if not await self.storage.is_bot() and self.takeout:
                self.takeout_id = (await self.send(raw.functions.account.InitTakeoutSession())).id
                log.warning(f"Takeout session {self.takeout_id} initiated")

            backup_state = copy(self.state)
            state = await self.send(raw.functions.updates.GetState())
        except (Exception, KeyboardInterrupt):
            await self.disconnect()
            raise
        else:
            self.cached_me = await self.get_me()
            await self.initialize()
            if backup_state:
                if state.pts > backup_state.pts:
                    diff = await self.send(
                        raw.functions.updates.GetDifference(
                            pts=backup_state.pts,
                            date=backup_state.date,
                            qts=-1
                        )
                    )

                    for msg in diff.new_messages:
                        self.dispatcher.updates_queue.put_nowait((
                            raw.types.UpdateNewMessage(
                                message=msg,
                                pts=state.pts,
                                pts_count=-1
                            ),
                            {u.id: u for u in diff.users},
                            {c.id: c for c in diff.chats}
                        ))
                    for update in diff.other_updates:
                        self.dispatcher.updates_queue.put_nowait((update, {}, {}))
            self.update_state(state)
            return self
