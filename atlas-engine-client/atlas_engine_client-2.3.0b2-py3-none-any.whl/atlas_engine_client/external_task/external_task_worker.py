import asyncio
import inspect
import logging
from operator import truediv
import traceback
import concurrent.futures

from ..core import BaseClient, LoopHelper
from .functional_error import FunctionalError


logger = logging.getLogger(__name__)


class ExternalTaskWorker(BaseClient):

    LOCK_DURATION_IN_MS = (60 * 1000)
    
    def __init__(self, url, session, identity, loop_helper, handler, external_task, options={}):
        super(ExternalTaskWorker, self).__init__(url, session, identity)
        self._loop_helper = loop_helper
        self._handler = handler
        self._external_task = external_task
        self._payload = self._external_task.get('payload', {})
        self._options = options

    def __get_lock_duration_in_ms(self):
        lock_duration_in_ms = self._options.get("lock_duration_in_ms", ExternalTaskWorker.LOCK_DURATION_IN_MS)

        if lock_duration_in_ms is None:
            logger.info(f"lock_duration_in_ms is not given, set to default {ExternalTaskWorker.LOCK_DURATION_IN_MS}")
            lock_duration_in_ms = ExternalTaskWorker.LOCK_DURATION_IN_MS

        return lock_duration_in_ms

    def __lock_timeout_in_ms(self):
        lock_duration_in_ms = self.__get_lock_duration_in_ms()
        lock_timeout_in_ms = lock_duration_in_ms * 0.9

        return lock_timeout_in_ms

    def __delay_in_seconds(self):
        delay_in_seconds = self.__lock_timeout_in_ms() / 1000

        return delay_in_seconds

    def __with_external_task_param(self):

        def is_handler_a_func(func):
            spec = inspect.getfullargspec(func)
            is_func = inspect.isroutine(func)

            result = (len(spec.args) == 2 and is_func)

            return result

        def is_handler_callable(caller):
            spec = inspect.getfullargspec(caller)
            is_func = inspect.isroutine(caller)

            result = (len(spec.args) == 3 and not is_func)

            return result

        return is_handler_a_func(self._handler) or is_handler_callable(self._handler)

    async def start(self):

        def is_async_handler(handler):
            if asyncio.iscoroutinefunction(handler):
                return True
            elif hasattr(handler, '__call__') and inspect.iscoroutinefunction(handler.__call__):
                return True
            else:
                return False

        async def extend_lock_task_wrapper():
            worker_id = self._external_task['workerId']
            external_task_id = self._external_task['id']

            lock_duration_in_ms = self.__get_lock_duration_in_ms()

            await self.extend_lock(worker_id, external_task_id, lock_duration_in_ms)

        delay_in_seconds = self.__delay_in_seconds()

        options = {'delay_in_seconds': delay_in_seconds}
        extend_lock = self._loop_helper.register_background_task(extend_lock_task_wrapper, **options)
        
        external_task_id = self._external_task['id']
        logger.info(f"starting external task '{external_task_id}'")

        try:
            result = None
            
            if is_async_handler(self._handler): #asyncio.iscoroutinefunction(self._handler):
                def handler_wrapper():
                    async def async_handler():
                        if self.__with_external_task_param():
                            return await self._handler(self._payload, self._external_task)
                        else:
                            return await self._handler(self._payload)

                    new_loop = asyncio.new_event_loop()
                    result = new_loop.run_until_complete(async_handler())

                    return result
                
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    result = await self._loop_helper._loop.run_in_executor(pool, handler_wrapper)

            else:
                fkt = None
                if self.__with_external_task_param():
                    def with_all_args():
                        result = self._handler(self._payload, self._external_task)
                        return result
                    fkt = with_all_args
                else:
                    def with_some_args():
                        result = self._handler(self._payload)
                        return result
                    fkt = with_some_args

                with concurrent.futures.ThreadPoolExecutor() as pool:
                    result = await self._loop_helper._loop.run_in_executor(pool, fkt)

            await self.__finish_task_successfully(result)
        except FunctionalError as fe:
            logger.warning(f"Finish external task with functional error (code: {fe.get_code()}, message: {fe.get_message()})")
            await self.__finish_task_with_functional_errors(fe.get_code(), fe.get_message())

        except Exception as e:
            formatted_lines = traceback.format_exc().splitlines()
            logger.error(f"Finish external task with technial error ({str(e)} -> {formatted_lines})")
            await self.__finish_task_with_technical_errors(str(e), str(formatted_lines))
        finally:
            self._loop_helper.unregister_background_task(extend_lock, "extend_lock background task")
            logger.info(f"finish external task '{external_task_id}'")

    async def extend_lock(self, worker_id, external_task_id, additional_duration):
        path = f"/atlas_engine/api/v1/external_tasks/{external_task_id}/extend_lock"
        
        logger.debug(f"Extend lock for worker {worker_id} with external_task_id {external_task_id} for {additional_duration}ms")

        request = {
            "workerId": worker_id,
            "additionalDuration": additional_duration
        }
        try:
            await self.do_put(path, request)
        except Exception as e:
            logger.error(f"Error on extend lock for worker {worker_id} for {additional_duration}ms with error {e}")

    async def __finish_task_successfully(self, result):
        logger.info(f"finish task {self._external_task['id']} successfully.")
        path = f"/atlas_engine/api/v1/external_tasks/{self._external_task['id']}/finish"

        payload = {
            "workerId": self._external_task['workerId'],
            "result": result
        }

        result = await self.do_put(path, payload)
        logger.debug(f"finished task {self._external_task['id']} successfully.")

    async def __finish_task_with_functional_errors(self, error_code, error_message):
        logger.warn(f"finished external task_with functional errors '{self._external_task}', '{error_code}', '{error_message}'.")
        path = f"/atlas_engine/api/v1/external_tasks/{self._external_task['id']}/handle_bpmn_error"

        payload = {
            "workerId": self._external_task['workerId'],
            "bpmnError": {
                "errorCode": error_code,
                "errorMessage": error_message
            }
        }

        await self.do_put(path, payload)

    async def __finish_task_with_technical_errors(self, error_message, error_details):
        logger.warn(f"finished task with technical errors '{self._external_task}', '{error_message}', '{error_details}'.")
        path = f"/atlas_engine/api/v1/external_tasks/{self._external_task['id']}/handle_service_error"

        payload = {
            "workerId": self._external_task['workerId'],
            "error": {
                "errorMessage": error_message,
                "errorDetails": error_details
            }
        }

        await self.do_put(path, payload)
