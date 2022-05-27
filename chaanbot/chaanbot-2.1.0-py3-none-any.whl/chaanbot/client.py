#!/usr/bin/env python3

import logging

from nio import MatrixRoom, InviteMemberEvent, RoomMessage

from chaanbot.matrix import Matrix
from chaanbot.module_runner import ModuleRunner

logger = logging.getLogger("chaanbot")


class Client:
    """ Main class for the bot. The client receives messages, joins rooms etc. """

    blacklisted_room_ids, whitelisted_room_ids, loaded_modules, allowed_inviters = [], [], [], []

    def __init__(self, module_runner: ModuleRunner, config, matrix: Matrix):
        try:
            self.module_runner = module_runner
            self.config = config
            self.matrix = matrix

            allowed_inviters = config.get("chaanbot", "allowed_inviters", fallback=None)
            if allowed_inviters:
                self.allowed_inviters = [str.strip(inviter) for inviter in allowed_inviters.split(",")]
                logger.debug("Allowed inviters: {}".format(self.allowed_inviters))
            logger.info("Chaanbot successfully initialized.")

        except Exception as exception:
            logger.exception("Failed with exception: {}".format(str(exception)), exception)
            raise exception

    async def run(self):
        await self._join_rooms(self.config)
        self.matrix.matrix_client.add_event_callback(self._on_invite, (InviteMemberEvent,))
        self.matrix.matrix_client.add_event_callback(self._on_room_event, (RoomMessage,))
        logger.info("Listeners added, now running...")
        await self._run_forever()

    async def _run_forever(self):
        await self.matrix.matrix_client.sync_forever(timeout=30000, full_state=True)

    async def _join_rooms(self, config):
        if not self.matrix.matrix_client.rooms:
            logger.warning("No rooms available")
        else:
            logger.debug("Available rooms: " + str(list(self.matrix.matrix_client.rooms.keys())))
        if config.has_option("chaanbot", "listen_rooms"):
            listen_rooms = [str.strip(room) for room in
                            config.get("chaanbot", "listen_rooms", fallback=None).split(",")]
            logger.info("Rooms to listen to: " + str(listen_rooms) + ". Will attempt to join these now.")
            for room_id in listen_rooms:
                await self.matrix.join_room(room_id)

        for room_id in self.matrix.matrix_client.rooms:
            room = self.matrix.matrix_client.rooms.get(room_id)
            if hasattr(room, "invite_only") and room.invite_only:
                logger.info("Private room detected, will attempt to join it: {}".format(room_id))
                await self.matrix.join_room(room_id)

    async def _on_invite(self, room: MatrixRoom, event: InviteMemberEvent):
        logger.info("Invited to {} by {}".format(room.room_id, event.sender))
        try:
            for inviter in self.allowed_inviters:
                if inviter.lower() == event.sender.lower():
                    logger.info("{} is an approved inviter, attempting to join room".format(event.sender))
                    await self.matrix.join_room(room)
                    return
            logger.info("{} is not an approved inviter, ignoring invite".format(event.sender))
            return
        except AttributeError:
            logger.info("Approved inviters turned off, attempting to join room: {}".format(room.room_id))
            await self.matrix.join_room(room)

    async def _on_room_event(self, room: MatrixRoom, event: RoomMessage):
        if event.sender == self.matrix.matrix_client.user_id:
            return
        if event.source["type"] != "m.room.message":
            return
        if event.source["content"]["msgtype"] != "m.text":
            return
        message = event.source["content"]["body"].strip()
        await self.module_runner.run(event, room, message)
