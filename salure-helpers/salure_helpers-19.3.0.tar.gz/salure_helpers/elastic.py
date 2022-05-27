import datetime
import json
import time
import pandas as pd
import requests
from pandas.io.json import json_normalize
import base64


class Elastic:
    def __init__(self, host, port, user, password, client_user, client_password):
        """
        A package to create indexes, users, roles, getting data, etc.
        :param host: the url or local IP of the elasticsearch cluster. For example http://localhost
        :param port: In most cases 9200 but it can be different
        :param user: The Elasticsearch user in case
        :param password: the password of the user
        """
        self.host = f'{host}:{port}'
        encoded_bytes = base64.b64encode(f'{user}:{password}'.encode("utf-8"))
        self.elastic_token = str(encoded_bytes, "utf-8")
        self.headers = {
            'Authorization': f'Basic {self.elastic_token}',
            'Content-Type': 'application/json'
        }
        self.client_user = client_user
        self.client_password = client_password
        health = self.get_health()
        if not health == 200:
            raise Exception('No connection could be established')

    def create_index_template(self, template_name, index_template):
        """
        Create a index template. A template can be used for the creating of indices. See for documentation https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-templates.html
        :param template_name: The name of the template
        :param index_template: The template with properties etc.
        :return: The response of the request to elasticsearch
        """
        # Check if the index template exists, if not, create it
        url = f'{self.host}/_template/{template_name}'
        response = requests.get(url, headers=self.headers)
        if response.status_code < 300:
            return f'Index template \'{template_name}\' already exists'
        else:
            body = json.dumps(index_template)
            response = requests.put(url=url, data=body, headers=self.headers)
            return response

    def create_index(self, index_name: str, update_role=False, corresponding_role_name=None):
        """
        Creates a new index in the elasticsearch instance. Documentation: https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-create-index.html
        :param index_name: The name of the desired index
        :param update_role: True if you want to update the role of this customer so this new index is added to the roll
        :param corresponding_role_name: The role at which the index should be added so that users with that role can read and update the index
        :return: The response of the request to elasticsearch
        """
        url = f'{self.host}/{index_name}'
        response = requests.get(url=url, headers=self.headers)
        if 200 <= response.status_code < 300:
            return f'Index \'{index_name}\' already exists'
        else:
            response = requests.put(url=url, headers=self.headers)
            if update_role:
                self.create_or_update_role(corresponding_role_name)  # TODO Add indices as input to create_or_update_role()
            return response

    def create_or_update_role(self, role_name: str, index: list):
        """
        Creates or updates a role. All the indexes which start with the same constraint as the role_name, are added to the role
        :param role_name: The name of the desired role. Most often the username which also is used for the mysql database user (sc_customer)
        :param index: one or more index names in a list.
        :return: The response of the request to elasticsearch
        """
        url = f'{self.host}/_security/role/{role_name}'
        # Set the body
        body = {
            'cluster': ['transport_client'],
            'indices': [
                {
                    'names': index,
                    'privileges': ['read', 'write', 'read_cross_cluster', 'view_index_metadata', 'index']
                }
            ],
            'metadata': {
                'version': 1
            }
        }
        body = json.dumps(body)
        response = requests.put(url=url, data=body, headers=self.headers)
        return response

    def create_user(self, user_name: str, password: str, user_description: str, roles: list):
        """
        Creates a user if it doesn't exist.
        :param user_name: The username. Most often the username which also is used for the mysql database user (sc_customer)
        :param password: Choose a safe password. At least 8 characters long
        :param user_description: A readable description. Often the customer name
        :param roles: Give the roles to which the user belongs in a list. Most often the same role_name as the user_name
        :return: The response of the request to elasticsearch
        """
        url = f'{self.host}/_security/user/{user_name}'
        body = {
            'password': f'{password}',
            'roles': roles,
            'full_name': f'{user_description}'
        }
        body = json.dumps(body)
        response = requests.put(url=url, data=body, headers=self.headers)
        return response

    def delete_index(self, index_name):
        """
        Deletes an existing index if it exists. Documentation: https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-delete-index.html
        :param index_name: The index you want to delete
        :return: The response of the request to elasticsearch
        """
        # Check if index exists
        url = f'{self.host}/{index_name}'
        response = requests.get(url=url, headers=self.headers)
        # Delete index if it exists
        if response.status_code >= 400:
            return f'Index \'{index_name}\' does not exist'
        else:
            response = requests.delete(url=url, headers=self.headers)
            return response

    def get_all_docs_from_index(self, index):
        """
        Get all the documents from a certain index
        :param index: the name of the index
        :return: The response of the request to elasticsearch
        """
        size = 10000
        # Get all indices with the given index from the function parameter. For each day a new index.
        indices = requests.get(url=self.host + '/' + index + '*/_settings').json()
        index_list = {}
        for index in indices:
            index_date = datetime.date(int(index[-10:-6]), int(index[-5:-3]), int(index[-2:]))
            index_list[str(index_date)] = index

        for key, value in sorted(index_list.items()):
            if key == str(time.strftime("%Y-%m-%d")):
                url = f'{self.host}/{value}/_search'

        # initial request
        params = {"size": size, "scroll": "10m"}
        response = requests.get(url=url, params=params).json()

        # next requests until finished
        scroll_id = response['_scroll_id']
        total = response['hits']['total']
        response = json_normalize(response['hits']['hits'])
        response.drop(['_id', '_index', '_score', '_type'], axis=1, inplace=True)

        # start all the request to elastic based on the scroll_id and add to the initial response
        loop_boolean = True
        body = json.dumps({"scroll": "10m", "scroll_id": scroll_id})
        url = f'{self.host}/_search/scroll'
        headers = {'Content-Type': 'application/json'}

        while loop_boolean and total > size:
            next_response = json_normalize(requests.post(url=url, data=body, headers=headers).json()["hits"]["hits"])
            next_response.drop(['_id', '_index', '_score', '_type'], axis=1, inplace=True)
            response = pd.concat([loop_boolean, next_response], ignore_index=True)
            print(f'Received {len(next_response)} documents from index {index}')
            if len(next_response) != size:
                loop_boolean = False
        return response

    def get_health(self):
        """
        Check if a there is a connection with elasticsearch
        :return: the statuscode of the request
        """
        # Get the health of the database connection
        health = requests.get(url=f'{self.host}/_cat/health?', headers=self.headers).status_code
        return health

    def get_indices(self):
        # Get all the indices
        indices = requests.get(url=f'{self.host}/_cat/indices?format=json', headers=self.headers).json()
        return indices

    def log_line(self, timestamp: str, information: dict):
        """
        Write a line to the elasticsearch database
        :param timestamp: the date and time of logging
        :param information: the information to be inserted into the database, which should correspond with a template
        :return: the response of the post request
        """
        # Look for template with matching name
        url = f'{self.host}/_template/{self.client_user}?pretty'
        response = requests.get(url, headers=self.headers)
        if response.status_code >= 400:
            return f'Cannot find an index template for index \'{self.client_user}\' with the same name.'
        template = response.json()
        template_properties = template[self.client_user]['mappings']['properties']
        # Check if provided information matches the template
        correct_size = (len(information) == len(template_properties))
        if not correct_size:
            return f'The input argument \'information\' should be a dictionary with {len(template_properties)} keys'
        correct_keys = True
        items = []
        for key, value in template_properties.items():
            items.append(f'{key} ({value["type"]})')
            if correct_keys:
                correct_keys = key in information
        if not correct_keys:
            return f'The input argument \'information\' should be a dictionary with the following keys (type of ' \
                   f'value): {", ".join(items)}'
        # Creating the index of the current date if it does not exist yet
        created_at = timestamp
        index_name = f'{self.client_user}-{created_at[:10]}'
        url = f'{self.host}/{index_name}'
        response = requests.get(url=url, headers=self.headers)
        if response.status_code >= 400:
            self.create_index(index_name)
        # Create or update the role for the current client
        df = json_normalize(self.get_indices())
        df = df[df['index'].str.startswith(self.client_user)]
        client_indices = df['index'].tolist()
        self.create_or_update_role(self.client_user, client_indices)
        # Create user for the current client if it doesn't exist yet
        description = self.client_user
        self.create_user(self.client_user, self.client_password, description, [self.client_user])
        # Add new document
        url = f'{self.host}/{index_name}/_doc/'
        body = json.dumps(information)
        response = requests.post(url=url, data=body, headers=self.headers)
        return response
