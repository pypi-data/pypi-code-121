import datetime
import json
import os

import requests

from zeno_etl_libs.config.common import Config


class Sql:
    def __init__(self):
        configobj = Config.get_instance()
        secrets = configobj.get_secrets()
        self.url = secrets['DJANGO_ACCOUNTS_BASE_URL']
        self.node_url = secrets['NODE_NOTIFICATION_BASE_URL']
        self.auth_token = secrets['DJANGO_OAUTH_TOKEN']
        self.node_auth_token = secrets['NOTIFICATION_AUTH_TOKEN']
        self.env = os.environ.get('env', 'dev')

    def create_big_query_log_for_mysql_db_update(self, request_body, event_name):
        url = self.node_url + "api/v1/bigQuery-access/event-logs-write"
        headers = {'Content-Type': 'application/json', 'Authorization': self.node_auth_token}
        __BIG_QUERY_PLATFORM = 'data-science-server'
        __BIG_QUERY_PLATFORM_ID = 2
        __BIG_QUERY_PLATFORM_CODE = 'DSS'

        request_dict = {
            "__environment": self.env,
            "logs": [{
                "__platform": __BIG_QUERY_PLATFORM,
                "__platform_properties": {
                    "__id": __BIG_QUERY_PLATFORM_ID,
                    "__code": __BIG_QUERY_PLATFORM_CODE
                },
                "__user_email": "data.science@generico.in",
                "user_properties": {
                    "_id": 5
                },
                "__event": event_name,
                "event_properties": {
                    "_entity_details": {
                        "_entity_name": request_body['database_table_name']
                    },
                    "updated_fields": request_body['data']
                },
                "__trigger_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }]
        }
        requests.post(url, json=request_dict, headers=headers, timeout=(1, 10))

    def update(self, script_data, logger=None) -> tuple:
        """
            Used to hit the django-accounts dynamic-update-api that will make changes to the Mysql Table.
            If you pass the logger_obj as a parameter to this function it will log to the file in case of errors.
        """

        # construct request_body from data
        request_body = {'database_table_name': script_data['table']}

        request_body_data = list()
        for entry in script_data['data_to_be_updated']:
            update_data_dict = dict()
            update_data_dict['id'] = entry.pop('id')
            update_data_dict['update_data'] = entry
            request_body_data.append(update_data_dict)

        request_body['data'] = request_body_data

        url = self.url + 'api/web/v1/dynamic-update-api/'
        authorization_token = 'Bearer {}'.format(self.auth_token)
        headers = {"Content-Type": "application/json", 'Authorization': authorization_token}

        try:
            response = requests.post(url, data=json.dumps(request_body), headers=headers, timeout=(1, 60))
            if response.status_code == 200:
                self.create_big_query_log_for_mysql_db_update(request_body, "DSS_MYSQL_UPDATE")
                return True, response.json()
            return False, response.text
        except Exception as exc:
            if logger:
                logger.info(exc)
                logger.info(json.dumps(headers))
                logger.info(json.dumps(request_body))
            return False, str(exc)


class Django:
    def __init__(self):
        configobj = Config.get_instance()
        secrets = configobj.get_secrets()
        self.url = secrets['DJANGO_ACCOUNTS_BASE_URL']
        self.node_url = secrets['NODE_NOTIFICATION_BASE_URL']
        self.auth_token = secrets['DJANGO_OAUTH_TOKEN']
        self.node_auth_token = secrets['NOTIFICATION_AUTH_TOKEN']
        self.env = os.environ.get('env', 'dev')

    def django_model_execution_log_create_api(self, request_body, logger=None) -> tuple:
        """
        Used to hit django-accounts model-execution-log-admin api that will create entries in model_execution_log table.
        If you pass the logger_obj as a parameter to this function it will log to the file in case of errors.
        e.g. request_body = {
                              "object_id": 1,  # PK (line-item)
                              "content_type": 74  # PK of django tables
                            }
        """

        url = self.url + 'api/web/v1/model-execution-log-admin/'
        headers = {"Content-Type": "application/json", 'Authorization': self.auth_token}

        response = requests.post(url, data=json.dumps(request_body), headers=headers, timeout=(1, 5))
        if response.status_code in [200, 201]:
            return True, response.json()
        return False, response.text
