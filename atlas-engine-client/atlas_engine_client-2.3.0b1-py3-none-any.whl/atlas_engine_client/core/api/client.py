from pathlib import Path
import os

from typing import Any, Callable, Dict, List

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, LetterCase

from .helpers.application_info import ApplicationInfo, ApplicationInfoHandler
from .helpers.data_object_instances import DataObjectInstanceHandler, DataObjectInstancesQuery, DataObjectInstanceResponse
from .helpers.empty_tasks import EmptyTaskHandler, EmptyTaskQuery, EmptyTaskResponse
from .helpers.events import EventsHandler, MessageTriggerRequest
from .helpers.external_tasks import ExtendLockRequest, FetchAndLockRequestPayload, ExternalTask
from .helpers.external_tasks import ExternalTaskHandler, FinishExternalTaskRequestPayload
from .helpers.flow_node_instances import FlowNodeInstanceHandler, FlowNodeInstanceResponse, FlowNodeInstancesQuery
from .helpers.manual_tasks import ManualTaskHandler, ManualTaskQuery, ManualTaskResponse
from .helpers.external_tasks import BpmnErrorRequest, ServiceErrorRequest
from .helpers.process_definitions import ProcessDefinitionUploadPayload, ProcessDefinitionHandler
from .helpers.process_instances import ProcessInstanceHandler, ProcessInstanceQueryRequest, ProcessInstanceQueryResponse
from .helpers.process_models import ProcessStartRequest, ProcessStartResponse, ProcessModelHandler
from .helpers.user_tasks import UserTaskHandler, UserTaskQuery, UserTaskResponse, ReserveUserTaskRequest


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DeployResult:
    filename: str
    deployed: bool = True


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DeployResults:
    deployed_files: List[DeployResult] = field(default_factory=list)


class Client(object):

    def __init__(self, url: str, identity: Callable = None):
        self._url = url
        self._identity = identity

    def info(self) -> ApplicationInfo:
        handler = ApplicationInfoHandler(self._url, self._identity)

        application_info = handler.info()

        return application_info

    def authority(self) -> str:
        handler = ApplicationInfoHandler(self._url, self._identity)

        authority = handler.authority()

        return authority

    def data_object_instance_get(self, query: DataObjectInstancesQuery, options: dict = {}) -> DataObjectInstanceResponse:
        handler = DataObjectInstanceHandler(self._url, self._identity)

        response = handler.get_data_object_instances(query, options)

        return response

    def empty_task_get(self, empty_task_query: EmptyTaskQuery, options: dict = {}) -> EmptyTaskResponse:
        handler = EmptyTaskHandler(self._url, self._identity)

        response = handler.get_empty_tasks(empty_task_query, options)

        return response

    def empty_task_finish(self, empty_task_instance_id: str, options: dict = {}):
        handler = EmptyTaskHandler(self._url, self._identity)

        _ = handler.finish_empty_task(empty_task_instance_id, options)

        return True

    def events_trigger_message(self, event_name: str, request: MessageTriggerRequest, options: dict = {}):
        handler = EventsHandler(self._url, self._identity)

        handler.trigger_message(event_name, request, options)

    def events_trigger_signal(self, signal_name: str, options: dict = {}):
        handler = EventsHandler(self._url, self._identity)

        handler.trigger_signal(signal_name, options)

    def external_task_fetch_and_lock(self, request: FetchAndLockRequestPayload, options: dict = {}) -> List[ExternalTask]:
        handler = ExternalTaskHandler(self._url, self._identity)

        reponse = handler.fetch_and_lock(request, options)

        return reponse

    def external_task_extend_lock(self, request: ExtendLockRequest, options: dict = {}) -> List[ExternalTask]:
        handler = ExternalTaskHandler(self._url, self._identity)

        reponse = handler.extend_lock(request, options)

        return reponse

    def external_task_finish(self, external_task_id: str, request: FinishExternalTaskRequestPayload, options: dict = {}):
        handler = ExternalTaskHandler(self._url, self._identity)

        response = handler.finish(external_task_id, request, options)

        return response

    def external_task_handle_bpmn_error(self, external_task_id: str, request: BpmnErrorRequest, options: dict = {}):
        handler = ExternalTaskHandler(self._url, self._identity)

        response = handler.handle_bpmn_error(
            external_task_id, request, options)

        return response

    def external_task_handle_service_error(self, external_task_id: str, request: ServiceErrorRequest, options: dict = {}):
        handler = ExternalTaskHandler(self._url, self._identity)

        response = handler.handle_service_error(
            external_task_id, request, options)

        return response

    def flow_node_instance_get(self, query: FlowNodeInstancesQuery, options: dict = {}) -> FlowNodeInstanceResponse:
        handler = FlowNodeInstanceHandler(self._url, self._identity)

        response = handler.get_flow_node_instances(query, options)

        return response

    def manual_task_get(self, manual_task_query: ManualTaskQuery, options: dict = {}) -> ManualTaskResponse:
        handler = ManualTaskHandler(self._url, self._identity)

        response = handler.get_manual_tasks(manual_task_query, options)

        return response

    def manual_task_finish(self, manual_task_instance_id: str, options: dict = {}):
        handler = ManualTaskHandler(self._url, self._identity)

        _ = handler.finish_manual_task(manual_task_instance_id, options)

        return True

    def process_defintion_deploy(self, request: ProcessDefinitionUploadPayload, options: dict = {}):
        handler = ProcessDefinitionHandler(self._url, self._identity)

        handler.deploy(request, options)

    def process_defintion_deploy_by_pathname(self, pathname: str, exit_on_fail: bool = False, overwrite_existing: bool = True, options: dict = {}) -> DeployResults:

        handler = ProcessDefinitionHandler(self._url, self._identity)

        deploy_results = DeployResults()

        filenames = []

        if Path(pathname).is_file():
            filenames.append(pathname)
        else:
            found_paths = Path(os.getcwd()).rglob(pathname)
            filenames = [str(path) for path in found_paths]

        if len(filenames) == 0 and exit_on_fail:
            raise Exception(f"No files found for pathname {pathname}")

        has_failed_deployments = False

        for filename in filenames:

            deployed_file = DeployResult(filename=filename)
            deploy_results.deployed_files.append(deployed_file)

            with open(filename) as file:
                xml = file.read()

            request = ProcessDefinitionUploadPayload(
                xml=xml, overwrite_existing=overwrite_existing)

            try:
                handler.deploy(request, options=options)
                deployed_file.deployed = True
            except Exception as e:
                if exit_on_fail:
                    raise e
                else:
                    deployed_file.deployed = False
                    has_failed_deployments = True

        if has_failed_deployments and exit_on_fail:
            failed_filenames = [
                deploy_result.filename for deploy_result in deploy_results if deploy_result.deployed == False]
            msg = f'Failed to deploy {",".join(failed_filenames)}'
            raise Exception(msg)

        if len(filenames) != len(deploy_results.deployed_files) or len(deploy_results.deployed_files) == 0:
            if exit_on_fail:
                msg = f"Nothing to deploy with '{pathname}' in current working dir '{os.getcwd()}'"
                raise Exception(msg)

        return deploy_results

    def process_instanceq_query(self, request: ProcessInstanceQueryRequest, options: dict = {}) -> ProcessInstanceQueryResponse:
        handler = ProcessInstanceHandler(self._url, self._identity)

        response = handler.query(request, options)

        return response

    def process_instance_terminate(self, process_instance_id: str, options: dict = {}):
        handler = ProcessInstanceHandler(self._url, self._identity)

        response = handler.terminate(process_instance_id, options)

        return response

    def process_model_start(self, process_model_id: str, request: ProcessStartRequest, options: dict = {}) -> ProcessStartResponse:
        handler = ProcessModelHandler(self._url, self._identity)

        response = handler.start(process_model_id, request, options)

        return response

    def user_task_get(self, query: UserTaskQuery = UserTaskQuery(), options: dict = {}) -> UserTaskResponse:
        handler = UserTaskHandler(self._url, self._identity)

        response = handler.get_user_tasks(query, options)

        return response

    def user_task_reserve(self, user_task_instance_id: str, request: ReserveUserTaskRequest, options: dict = {}):
        handler = UserTaskHandler(self._url, self._identity)

        response = handler.reserve_user_task(
            user_task_instance_id, request, options)

        return response

    def user_task_cancel_reservation(self, user_task_instance_id: str, options: dict = {}):
        handler = UserTaskHandler(self._url, self._identity)

        response = handler.cancel_reservation(user_task_instance_id, options)

        return response

    def user_task_finish(self, user_task_instance_id: str, request: Dict[str, Any], options: dict = {}):
        handler = UserTaskHandler(self._url, self._identity)

        response = handler.finish_user_task(
            user_task_instance_id, request, options)

        return response
