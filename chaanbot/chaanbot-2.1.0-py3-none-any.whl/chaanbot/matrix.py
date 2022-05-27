import logging
from typing import Optional, Dict

from nio import MatrixRoom, AsyncClient, MatrixUser

logger = logging.getLogger("matrix_utility")


class Matrix:
    """ Contains the matrix client and help methods """

    def __init__(self, config, matrix_client: AsyncClient):
        self.matrix_client = matrix_client
        blacklisted_rooms = config.get("chaanbot", "blacklisted_room_ids", fallback=None)
        if blacklisted_rooms:
            self.blacklisted_room_ids = [str.strip(room) for room in blacklisted_rooms.split(",")]
        else:
            self.blacklisted_room_ids = []
        logger.debug("Blacklisted rooms: {}".format(self.blacklisted_room_ids))

        whitelisted_rooms = config.get("chaanbot", "whitelisted_room_ids", fallback=None)
        if whitelisted_rooms:
            self.whitelisted_room_ids = [str.strip(room) for room in whitelisted_rooms.split(",")]
        else:
            self.whitelisted_room_ids = []
        logger.debug("Whitelisted rooms: {}".format(self.whitelisted_room_ids))

    def get_room(self, rooms: Dict[str, MatrixRoom], id_or_name_or_alias) -> Optional[MatrixRoom]:
        """ Attempt to get a room. Prio: room_id > canonical_alias > name.
        Will not be able to get room if not in room
        """

        for room in rooms.values():
            if room.room_id == id_or_name_or_alias:
                return room

        for room_id in rooms:
            room = rooms.get(room_id)
            if room.canonical_alias == id_or_name_or_alias:
                return room

        for room_id in rooms:
            room = rooms.get(room_id)
            if room.name == id_or_name_or_alias:
                return room
        return None

    def get_user(self, room: MatrixRoom, user_id_or_display_name) -> Optional[MatrixUser]:
        for user in room.users.values():
            if (user_id_or_display_name.lower() == user.user_id.lower()) or (
                    user_id_or_display_name.lower() == user.display_name.lower()):
                return user
        return None

    def is_online(self, room_id, user_id):
        presence = self.get_presence(room_id, user_id)
        logger.debug("presence: {}".format(presence))
        return presence == "online"

    def get_presence(self, room_id, user_id):
        """Returns an object like this:
        {
            "application/json": {
            "last_active_ago": 420845,
            "presence": "unavailable"
            }
        }
        """
        return self.matrix_client.rooms[room_id].users[user_id].presence

    async def send_text_to_room(self, message: str, room_id: str):
        content = {
            "msgtype": "m.text",
            "format": "org.matrix.custom.html",
            "body": message,
        }
        await self.matrix_client.room_send(
            room_id,
            "m.room.message",
            content
        )

    async def join_room(self, room_id_or_alias):
        room = self.get_room(self.matrix_client.rooms, room_id_or_alias)
        room_id = room.room_id if room else room_id_or_alias  # Might not be able to get room_id if room was unlisted
        if self.whitelisted_room_ids and len(self.whitelisted_room_ids) > 0:
            for whitelisted_room_id_or_alias in self.whitelisted_room_ids:
                whitelisted_room = self.get_room(self.matrix_client.rooms, whitelisted_room_id_or_alias)
                if whitelisted_room and whitelisted_room.room_id == room_id:
                    logger.info("Room {} is whitelisted, joining it".format(room_id_or_alias))
                    await self.matrix_client.join(whitelisted_room_id_or_alias)
            logger.info("Room {} is not whitelisted, will not join it".format(room_id_or_alias))
        elif self.blacklisted_room_ids and len(self.blacklisted_room_ids) > 0:
            for blacklisted_room_id_or_alias in self.blacklisted_room_ids:
                blacklisted_room = self.get_room(self.matrix_client.rooms, blacklisted_room_id_or_alias)
                if blacklisted_room and blacklisted_room.room_id == room_id:
                    logger.info("Room {} is blacklisted, will not join it".format(blacklisted_room_id_or_alias))
                    return
            logger.info("Room {} is not blacklisted, will join it".format(room_id_or_alias))
            await self.matrix_client.join(room_id_or_alias)
        else:
            logger.info("Joining room {}".format(room_id_or_alias))
            await self.matrix_client.join(room_id_or_alias)
