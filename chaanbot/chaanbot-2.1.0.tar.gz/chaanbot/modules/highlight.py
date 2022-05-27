""" The Highlight module allows users to create groups of users in a room and highlight/notify them.
For example, lets users easily ask everyone who plays game X if they want to play (!hl chess Anyone up for a game?)

Available commands:
!hla [GROUP] [USER1] [USER2] ...    - Adds one or more users to a group
!hld [GROUP] [USER1] [USER2] ...    - Delete one or more users from a group
!hl [GROUP] [OPTIONAL TEXT]         - Notify users in group
!hlall [OPTIONAL TEXT]              - Notify all users in room

Usage example:
!hla developers richard carl
!hl developers anyone comfortable with Perl?

Would results in:
"Bot: @Richard:example.com @Carl:example.com: anyone comfortable with Perl?"

Note: Groups are room-dependent and case-insensitive.
"""
import logging
import re

from nio import RoomMessage, MatrixRoom

from chaanbot import command_utility
from chaanbot.database import Database
from chaanbot.matrix import Matrix

logger = logging.getLogger("highlight")


class Highlight:
    always_run = False
    operations = {
        "highlight_all": {
            "commands": ["!hlall", "!highlightall"],
            "argument_regex": re.compile(r"[.+]?", re.IGNORECASE),
        },
        "add_to_group": {
            "commands": ["!hla", "!hladd", "!highlightadd"],
            "argument_regex": re.compile(r".+ .+", re.IGNORECASE),
        },
        "delete_from_group": {
            "commands": ["!hld", "!hldelete", "!highlightdelete"],
            "argument_regex": re.compile(r".+ .+", re.IGNORECASE),
        },
        "highlight": {
            "commands": ["!hl", "!highlight"],
            "argument_regex": re.compile(r".+", re.IGNORECASE),
        },
    }

    def __init__(self, config, matrix: Matrix, database: Database, requests):
        self.matrix = matrix
        if database:
            self.database = database
            logger.debug("Initializing highlight database if needed")
            conn = database.connect()
            conn.execute('''CREATE TABLE IF NOT EXISTS highlight_groups
            (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            ROOM_ID TEXT NOT NULL,
            "GROUP_NAME" TEXT NOT NULL,
            MEMBER TEXT NOT NULL,
            UNIQUE(ROOM_ID,GROUP_NAME,MEMBER));    
            ''')
            conn.commit()
        else:
            logger.info("No database provided, highlight module disabled")

    async def run(self, room: MatrixRoom, event: RoomMessage, message) -> bool:
        if self._should_run(message):
            if command_utility.matches(self.operations["highlight_all"], message):
                logger.debug("Highlighting all")
                await self._highlight_all(room, event.sender, message)
            elif command_utility.matches(self.operations["highlight"], message):
                logger.debug("Highlighting")
                await self._highlight(room, event.sender, message)
            elif command_utility.matches(self.operations["add_to_group"], message):
                logger.debug("Adding to group")
                await self._add_or_create_group(room, message)
            elif command_utility.matches(self.operations["delete_from_group"], message):
                logger.debug("Deleting from group")
                await self._delete_from_group(room, message)
            else:
                raise RuntimeError("Could not find command to run on message, but should have been able to")
            return True
        return False

    def _should_run(self, message) -> bool:
        return self.database and command_utility.matches(self.operations, message)

    async def _highlight_all(self, room: MatrixRoom, sender_user_id, message):
        user_ids = [user.user_id for user in room.users.values()]
        argument = command_utility.get_argument(message)
        user_ids = self._remove_element(user_ids, sender_user_id)
        if user_ids:
            message = ", ".join(user_ids)
            logger.debug("Highlighting: {}".format(message))
            if argument:
                await self.matrix.send_text_to_room(message + ": " + argument, room.room_id)
            else:
                await self.matrix.send_text_to_room(message, room.room_id)
        else:
            logger.debug("No users to highlight in room {}".format(room.room_id))
            await self.matrix.send_text_to_room("No users to highlight", room.room_id)
        return

    async def _highlight(self, room: MatrixRoom, sender_user_id, message):
        argument = command_utility.get_argument(message)
        if not argument:
            await self.matrix.send_text_to_room("Correct syntax is !hl [group] [optional text].", room.room_id)
            return
        arguments = argument.split(None, 1)
        group = arguments[0].lower()
        member_user_ids = self._get_member_user_ids_except_sender(room, group, sender_user_id)
        if member_user_ids:
            members = ", ".join(member_user_ids)

            if len(arguments) > 1:
                argument = arguments[1]
                await self.matrix.send_text_to_room(members + ": " + argument, room.room_id)
            else:
                await self.matrix.send_text_to_room(members, room.room_id)
        else:
            await self.matrix.send_text_to_room("Group \"{}\" does not have any members to highlight".format(group),
                                                room.room_id)

    async def _add_or_create_group(self, room: MatrixRoom, message):
        arguments = command_utility.get_argument(message).split()
        group = arguments[0].lower()
        users_to_add = arguments[1:]
        logger.debug("User wants to add {} to {}".format(users_to_add, group))
        if group and len(users_to_add) > 0:
            for user in users_to_add:
                found_user = self.matrix.get_user(room, user)
                if not found_user:
                    await self.matrix.send_text_to_room("User: \"{}\" is not in room".format(user), room.room_id)
                    return

            new_members = []

            with self.database.connect() as conn:
                for user in users_to_add:
                    if self._is_in_group(conn, room.room_id, group, user):
                        logger.debug(
                            "User {} is already a member of group {} in room {}".format(user, group, room.room_id))
                    else:
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT OR IGNORE INTO highlight_groups(ROOM_ID,GROUP_NAME,MEMBER) VALUES(?,?,?)",
                            (room.room_id, group, user))
                        conn.commit()
                        logger.debug("Inserted {} into group {} with id {}".format(user, group, cursor.lastrowid))
                        new_members.append(user)

            if new_members:
                await self.matrix.send_text_to_room(
                    "Added \"{}\" to group \"{}\"".format(", ".join(new_members), group),
                    room.room_id)
            else:
                await self.matrix.send_text_to_room(
                    "Could not add \"{}\" to group \"{}\"".format(", ".join(users_to_add), group), room.room_id)
        else:
            await self.matrix.send_text_to_room(
                "Could not add: \"{}\" to group \"{}\". Syntax is incorrect".format(group, users_to_add), room.room_id)
        return

    async def _delete_from_group(self, room: MatrixRoom, message):
        arguments = command_utility.get_argument(message).split()
        group = arguments[0].lower()
        members_to_remove = arguments[1:]
        logger.debug("User wants to remove {} from {}".format(members_to_remove, group))
        if group and len(members_to_remove) > 0:
            for member in members_to_remove:
                if not self.matrix.get_user(room, member):
                    await self.matrix.send_text_to_room("User: {} is not in room".format(member), room.room_id)
                    return

            removed_members = []
            with self.database.connect() as conn:
                for member in members_to_remove:
                    if self._is_in_group(conn, room.room_id, group, member):
                        cursor = conn.cursor()
                        cursor.execute(
                            "DELETE FROM highlight_groups WHERE room_id = ? AND group_name = ? and member = ?",
                            (room.room_id, group, member))
                        conn.commit()
                        removed_members.append(member)
            if removed_members:
                logger.debug(
                    "Removed {} from group {} in room {}".format(", ".join(removed_members), group, room.room_id))
                await self.matrix.send_text_to_room(
                    "Removed \"{}\" from group \"{}\"".format(", ".join(removed_members), group), room.room_id)
            else:
                logger.debug(
                    "Could not remove {} from group {} in room {}".format(", ".join(members_to_remove), group,
                                                                          room.room_id))
                await self.matrix.send_text_to_room(
                    "Could not remove \"{}\" from group \"{}\"".format(", ".join(members_to_remove), group),
                    room.room_id)
        else:
            await self.matrix.send_text_to_room(
                "Could not remove: \"{}\" from group \"{}\". Syntax is incorrect".format(group, members_to_remove),
                room.room_id)
        return

    @staticmethod
    def _is_in_group(conn, room_id, group, member) -> bool:
        result = conn.execute(
            "SELECT 1 FROM highlight_groups WHERE room_id = ? AND group_name = ? AND member = ? LIMIT 1",
            (room_id, group, member))
        result = result.fetchone()
        return result is not None

    def _get_members(self, room: MatrixRoom, group) -> list:
        return [row[0] for row in
                self.database.connect().execute(
                    "SELECT member FROM highlight_groups WHERE room_id = ? AND group_name = ?",
                    (room.room_id, group)).fetchall()]

    def _get_member_user_ids_except_sender(self, room: MatrixRoom, group, sender_user_id) -> list:
        member_user_ids = [self.matrix.get_user(room, member).user_id for member in self._get_members(room, group) if
                           self.matrix.get_user(room, member) is not None]
        return self._remove_element(member_user_ids, sender_user_id)

    def _remove_element(self, list_to_remove_from, element_to_remove):
        return list(filter(lambda element: element != element_to_remove, list_to_remove_from))
