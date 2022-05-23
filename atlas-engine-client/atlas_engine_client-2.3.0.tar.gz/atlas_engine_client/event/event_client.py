import asyncio
from atlas_engine_client import event
import logging 

from ..core.base_client import BaseClient

logger = logging.getLogger(__name__)

# using nested event loops e.g. jupyter-notebook see https://github.com/nteract/papermill/issues/490
import nest_asyncio 
nest_asyncio.apply()
class EventClient(BaseClient):

    def __init__(self, url, session=None, identity=None):
        super(EventClient, self).__init__(url, session, identity)

    async def __trigger_message(self, event_name, payload, process_instance_id):
        
        url = f"/atlas_engine/api/v1/messages/{event_name}/trigger"

        if process_instance_id is not None:
            url = f"{url}?process_instance_id={process_instance_id}"

        result = await self.do_post(url, payload)

        return result

    def trigger_message(self, event_name, payload={}, process_instance_id=None):

        async def run_loop():

            result = await self.__trigger_message(event_name, payload, process_instance_id)

            return result

        logger.info(f"Connection to atlas engine at url '{self._url}'.")
        logger.info(f"Trigger message event {event_name} for process instance {process_instance_id} with payload {payload}.")

        loop = asyncio.new_event_loop()

        task = run_loop()
        result = loop.run_until_complete(task)

        loop.close()

        return result

    async def __trigger_signal(self, signal_name):

        url = f"/atlas_engine/api/v1/signals/{signal_name}/trigger"

        result = await self.do_post(url, {})

        return result

    def trigger_signal(self, signal_name):

        async def run_loop():
            result = await self.__trigger_signal(signal_name)

            return result

        logger.info(f"Connection to atlas engine at url '{self._url}'.")
        logger.info(f"Trigger signal event {signal_name}.")

        loop = asyncio.new_event_loop()

        task = run_loop()
        result = loop.run_until_complete(task)

        loop.close()

        return result