from apeman.model.openapi import TaskStatus, TaskLaunchType, TaskType
from apeman.model.openapi import apeman_open_api_client

endpoint = apeman_open_api_client.get_endpoint(model_instance_id='')
# cancel task
apeman_open_api_client.cancel_task(task_id='', force_delete=True, token='')

# report status
response = apeman_open_api_client.report_and_get_status(task_id='', status=TaskStatus.RUNNING, progress=0.1,
                                                        message='Task is running', token='')

if response.status == TaskStatus.CANCELED:
    raise Exception('Task already has been canceled.')

# add instance task
apeman_open_api_client.add_model_instance_task(model_instance_id='', tenant_id='', task_token='', task_parameters='',
                                               job_context='', start_time=1, end_time=2,
                                               launch_type=TaskLaunchType.TASK_ADHOC, task_type=TaskType.TASK_TRAIN)
