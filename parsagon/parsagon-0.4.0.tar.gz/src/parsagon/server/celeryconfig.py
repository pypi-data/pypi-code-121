broker_url = 'redis://localhost:6379/0'
broker_transport_options = {'visibility_timeout': 5184000}
accept_content = ['json']
task_serializer = 'json'
result_serializer = 'json'

task_ignore_result = True

task_routes = {
    'server.tasks.run_code': {'queue': 'run_code'},
}
