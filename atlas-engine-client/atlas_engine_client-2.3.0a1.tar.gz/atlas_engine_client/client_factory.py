from atlas_engine_client.app_info import AppInfoClient
from atlas_engine_client.event import EventClient
from atlas_engine_client.external_task import ClientWrapper
from atlas_engine_client.flow_node_instance import FlowNodeInstanceClient
from atlas_engine_client.notification import NotificationClient
from atlas_engine_client.process_instance import ProcessInstanceClient
from atlas_engine_client.process_definition import ProcessDefinitionClient
from atlas_engine_client.user_task import UserTaskClient


class ClientFactory:

    def __init__(self):
        pass

    def create_app_info_client(self, engine_url):
        return AppInfoClient(engine_url)

    def create_event_client(self, engine_url):
        return EventClient(engine_url)

    def create_external_task_client(self, engine_url):
        return ClientWrapper(engine_url)

    def create_flow_node_instance_client(self, engine_url):
        return FlowNodeInstanceClient(engine_url)

    def create_notification_client(self, engine_url):
        return NotificationClient(engine_url)

    def create_process_instance_client(self, engine_url):
        return ProcessInstanceClient(engine_url)

    def create_process_definition_client(self, engine_url):
        return ProcessDefinitionClient(engine_url)

    def create_user_task_client(self, engine_url):
        return UserTaskClient(engine_url)

    
