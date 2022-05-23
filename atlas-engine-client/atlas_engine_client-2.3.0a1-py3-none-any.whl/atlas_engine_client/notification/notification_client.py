import asyncio
import logging 

from ..core import BaseClient, LoopHelper

logger = logging.getLogger(__name__)

class NotificationClient(BaseClient):
    def __init__(self, url, session=None, identity=None):
        super(NotificationClient, self).__init__(url, session, identity)

        self.__loop_helper = LoopHelper(on_shutdown=self.__on_shutdown)
        self.__notification_callbacks = {}

    async def __on_shutdown(self):
        for task in self.__notification_callbacks.values():
            self.__loop_helper.unregister_background_task(task)

        await self.close()

    def start(self):
        logger.info(f"Connecting to process engine at url '{self._url}'.")
        self.__loop_helper.start()

    def __on_register_event(self, event_name, callback):

        async def bg_on_event():

            url = f"/atlas_engine/api/v1/notifications/long_polling/{event_name}"

            result = await self.do_get(url)

            logger.debug(f"handling event '{event_name}' with {result}")

            if asyncio.iscoroutine(callback):
                await callback(result)
            else:
                callback(result)

        async_bg_task = self.__loop_helper.register_background_task(bg_on_event)
        self.__notification_callbacks[event_name] = async_bg_task

    def on_activity_reached(self, callback):
        self.__on_register_event('activity_reached', callback)

    def on_activity_finished(self, callback):
        self.__on_register_event('activity_finished', callback)

    def on_boundary_event_triggered(self, callback):
        self.__on_register_event('boundary_event_triggered', callback)

    def on_empty_activity_waiting(self, callback):
        self.__on_register_event('empty_activity_waiting', callback)

    def on_empty_activity_finished(self, callback):
        self.__on_register_event('empty_activity_finished', callback)

    def on_manual_task_waiting(self, callback):
        self.__on_register_event('manual_task_waiting', callback)

    def on_manual_task_finished(self, callback):
        self.__on_register_event('manual_task_finished', callback)

    def on_process_started(self, callback):
        self.__on_register_event('process_started', callback)

    def on_process_ended(self, callback):
        self.__on_register_event('process_ended', callback)

    def on_process_error(self, callback):
        self.__on_register_event('process_error', callback)

    def on_user_task_waiting(self, callback):
        self.__on_register_event('user_task_waiting', callback)

    def on_user_task_finished(self, callback):
        self.__on_register_event('user_task_finished', callback)

    def on_user_task_reserved(self, callback):
        self.__on_register_event('user_task_reserved', callback)

    def on_user_task_reservation_canceled(self, callback):
        self.__on_register_event('user_task_reservation_canceled', callback)

    def on_empty_activity_finished(self, callback):
        self.__on_register_event('empty_activity_finished', callback)

    def on_empty_activity_waiting(self, callback):
        self.__on_register_event('empty_activity_waiting', callback)

    def on_manual_task_finished(self, callback):
        self.__on_register_event('manual_task_finished', callback)

    def on_manual_task_waiting(self, callback):
        self.__on_register_event('manual_task_waiting', callback)

    def on_intermediate_throw_event_triggered(self, callback):
        self.__on_register_event('intermediate_throw_event_triggered', callback)

    def on_intermediate_catch_event_reached(self, callback):
        self.__on_register_event('intermediate_catch_event_reached', callback)

    def on_intermediate_catch_event_finished(self, callback):
        self.__on_register_event('intermediate_catch_event_finished', callback)

