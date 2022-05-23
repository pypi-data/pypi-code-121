from ..core import base_client


class UserTaskClient(base_client.BaseClient):

    def __init__(self, url, session=None, identity=None):
        super(UserTaskClient, self).__init__(url, session, identity)

    async def reserve_user_task(self, user_task_instance_id, owner_id):
        path = f"/atlas_engine/api/v1/user_tasks/{user_task_instance_id}/reserve"

        payload = {
            'actualOwnerId': owner_id
        }

        result = await self.do_put(path, payload)

        return result

    async def cancel_reservation_user_task(self, user_task_instance_id):
        path = f"/atlas_engine/api/v1/user_tasks/{user_task_instance_id}/cancel-reservation"

        result = await self.do_delete(path, {})

        return result

    async def finish_user_task(self, user_task_instance_id, answer):
        path = f"/atlas_engine/api/v1/user_tasks/{user_task_instance_id}/finish"

        result = await self.do_put(path, answer)

        return result

    async def get_user_tasks(self, state='suspended'):

        def map_user_tasks(user_task):
            new_user_task = {}
            new_user_task['userTaskInstanceId'] = user_task['flowNodeInstanceId']
            new_user_task['flowNodeId'] = user_task['flowNodeId']
            new_user_task['flowNodeName'] = user_task['flowNodeName']
            new_user_task['processModelId'] = user_task['processModelId']
            new_user_task['processInstanceId'] = user_task['processInstanceId']
            new_user_task['correlationId'] = user_task['correlationId']
            new_user_task['formFields'] = user_task['userTaskConfig']['formFields']
            new_user_task['token'] = user_task['tokens'][1]
            new_user_task['meta_info'] = user_task['metaInfo']

            # only for debug 
            #new_user_task['origin_user_task'] = user_task

            return new_user_task

        bpmn_type = 'bpmn:UserTask'
        path = f"/atlas_engine/api/v1/flow_node_instances?flowNodeType={bpmn_type}&state={state}"

        result = await self.do_get(path)

        user_tasks = []

        if result['totalCount'] > 0:
            user_tasks = list(map(map_user_tasks, result['flowNodeInstances']))

        return user_tasks
