
import asyncio
import logging 

from ..core import base_client
from .start_callback_type import StartCallbackType

logger = logging.getLogger(__name__)

class ProcessDefinitionClient(base_client.BaseClient):

    def __init__(self, url, session=None, identity=None):
        super(ProcessDefinitionClient, self).__init__(url, session, identity)

    async def __start_process_instance(self, process_model_id, **options):
        start_callback_type = options.get('start_callback', StartCallbackType.ON_PROCESSINSTANCE_CREATED)
        path = f"/atlas_engine/api/v1/process_models/{process_model_id}/start"

        initial_token = options.get('inital_token', {})

        payload = {
            "returnOn": int(start_callback_type),
            "processModelId": process_model_id,
            "initialToken": initial_token
        }

        logger.info(f"start process with uri '{path}' and payload '{payload}'")

        result = await self.do_post(path, payload)

        return result

    async def __start_process_instance_by_start_event(self, process_model_id, start_event_id, end_event_id, **options):
        start_callback_type = options.get('start_callback', StartCallbackType.ON_PROCESSINSTANCE_CREATED)
        path = f"/atlas_engine/api/v1/process_models/{process_model_id}/start"

        initial_token = options.get('initial_token', {})

        payload = {
            "returnOn": int(start_callback_type),
            "processModelId": process_model_id,
            "startEventId": start_event_id,
            "initialToken": initial_token
        }

        if end_event_id is not None:
            payload["endEventId"] = end_event_id

        logger.info(f"start process with uri '{path}' and payload '{payload}'")

        result = await self.do_post(path, payload)

        return result

    def __start_process_instance_wrapper(self, process_model_id, start_event_id=None, end_event_id=None, **options):

        async def run_loop(process_model_id, start_event_id, **options):
            result = None
            
            if start_event_id is not None:
                result = await self.__start_process_instance_by_start_event(process_model_id, start_event_id, end_event_id, **options)
            else:
                result = await self.__start_process_instance(process_model_id, **options)

            await self.close()

            return result

        logger.info(f"Connection to process engine at url '{self._url}'.")
        logger.info(f"Starting process instance process_model_id '{process_model_id}' and start_event_id '{start_event_id}'.")

        loop = asyncio.new_event_loop()

        task = run_loop(process_model_id, start_event_id, **options)
        result = loop.run_until_complete(task)

        loop.close()

        return result

    def start_process_instance(self, process_model_id, start_event_id=None, **options):
        options['start_callback'] = StartCallbackType.ON_PROCESSINSTANCE_CREATED

        return self.__start_process_instance_wrapper(process_model_id, start_event_id, **options)

    def start_process_instance_and_await_end_event(self, process_model_id, start_event_id=None, **options):
        options['start_callback'] = StartCallbackType.ON_PROCESSINSTANCE_FINISHED

        return self.__start_process_instance_wrapper(process_model_id, start_event_id, **options)

    def start_process_instance_and_await_specific_end_event(self, process_model_id, start_event_id=None, end_event_id=None, **options):
        options['start_callback'] = StartCallbackType.ON_ENDEVENT_REACHED

        return self.__start_process_instance_wrapper(process_model_id, start_event_id, end_event_id, **options)

    def get_process_definition(self, process_model_id):

        async def run_loop(process_model_id):
            url = f"/atlas_engine/api/v1/process_models/{process_model_id}/process_definition"


            result = await self.do_get(url)

            return result

        logger.info(f"Get the definition of process_model '{process_model_id}' from atlas engine at url '{self._url}'.")

        loop = asyncio.new_event_loop()

        task = run_loop(process_model_id)
        result = loop.run_until_complete(task)

        loop.close()

        return result
