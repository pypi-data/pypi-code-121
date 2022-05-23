
import asyncio
import logging 

from ..core import base_client

logger = logging.getLogger(__name__)

class ProcessInstanceClient(base_client.BaseClient):

    def __init__(self, url, session=None, identity=None):
        super(ProcessInstanceClient, self).__init__(url, session, identity)

    def terminate(self, process_instance_id):

        async def run_loop(process_instance_id):
            url = f"/atlas_engine/api/v1/process_instances/{process_instance_id}/terminate"

            result = await self.do_put(url, {})

            return result

        logger.info(f"Connection to process engine at url '{self._url}'.")
        logger.info(f"Terminate the process-instance '{process_instance_id}'.")

        loop = asyncio.new_event_loop()

        task = run_loop(process_instance_id)
        result = loop.run_until_complete(task)

        loop.close()

        return result

    def retry(self, process_instance_id):

        async def run_loop(process_instance_id):
            url = f"/atlas_engine/api/v1/process_instances/{process_instance_id}/retry"

            result = await self.do_put(url, {})

            return result

        logger.info(f"Retry process instance '{process_instance_id}' for atlas engine at url '{self._url}'.")

        loop = asyncio.new_event_loop()

        task = run_loop(process_instance_id)
        result = loop.run_until_complete(task)

        loop.close()

        return result
