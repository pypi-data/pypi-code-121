"""
    Requires python requests library
    Change the tableau_admin_user_password, old_read_only_username, new_read_only_username, new_read_only_user_password
"""

import json

import requests

tableau_admin_user_password = ''
tableau_baseurl = 'https://tableau.generico.in'
site_id = 'd68c13b5-ae9e-4cb2-8824-25c6d4daf7a2'
db_to_update = 'postgres'
old_read_only_username = ''
new_read_only_username = ''
new_read_only_user_password = ''

# sign in
login_data = {
    "credentials": {
        "name": 'admin',
        "password": tableau_admin_user_password,
        "site": {
            "contentUrl": ""
        }
    }
}
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
response = requests.post(f"{tableau_baseurl}/api/3.7/auth/signin", headers=headers, data=json.dumps(login_data))
login_resp = response.json()

if response.status_code == 200 and 'credentials' in login_resp:
    login_resp = login_resp["credentials"]
    headers['X-Tableau-Auth'] = login_resp["token"]

    # # data source list
    workbook_response = requests.get(f'{tableau_baseurl}/api/3.7/sites/{site_id}/workbooks?pageSize=1000',
                                     headers=headers)
    # print(workbook_response.json())
    if workbook_response.status_code != 200:
        raise Exception(f"workbook_response: {workbook_response.text}")

    workbook_data = workbook_response.json()
    for workbook in workbook_data['workbooks']['workbook']:
        if "" in workbook['name'].lower():
            print(workbook['name'])
            connection_response = requests.get(
                f"{tableau_baseurl}/api/3.7/sites/{site_id}/workbooks/{workbook['id']}/connections?pageSize=1000",
                headers=headers)
            if connection_response.status_code != 200:
                raise Exception(f"workbook_response: {connection_response.text}")

            connection_data = connection_response.json()
            for connection in connection_data['connections']['connection']:
                # print(connection)
                print(f"connection type: {connection['type']}")
                if connection['type'] == db_to_update:
                    if connection['userName'] == old_read_only_username:
                        connection_id = connection['id']
                        request_body = {
                            'connection': {
                                'userName': new_read_only_username,
                                'password': new_read_only_user_password
                            }
                        }
                        print(f"connection to update: {connection}")

                        # update connection
                        data_source_id = connection['datasource']['id']
                        conn_update_response = requests.put(
                            f'{tableau_baseurl}/api/3.7/sites/{site_id}/datasources/{data_source_id}/connections/{connection_id}',
                            data=json.dumps(request_body), headers=headers)

                        update_status = 'failed'
                        if conn_update_response.status_code == 200:
                            update_status = 'successful'
                        print(f"Connection ID: {connection_id} Data Source Name: {connection['datasource']['name']} "
                              f"update {update_status}")

    # project_response = requests.get(f'{tableau_baseurl}/api/3.7/sites/{site_id}/projects?pageSize=1000',
    #                                      headers=headers)
    # # print(project_response.json())
    # project_data = project_response.json()
    # for project in project_data['projects']['project']:
    #     if project['name'] == 'Marketing':
    #         print(f"project: {project}")

    # if data_sources_response.status_code == 200:
    #     counter = 0
    #     data_sources_data = data_sources_response.json()
    #     for data_source in data_sources_data['datasources']['datasource']:
    #         data_source_id = data_source['id']
    #
    #         if data_source['project']['name'].lower() != 'test':
    #             continue
    #         print(f"data_source: {data_source}")
    #         # per data source connections list
    #         connections_response = requests.get(
    #             f'{tableau_baseurl}/api/3.7/sites/{site_id}/datasources/{data_source_id}/connections',
    #             headers=headers)
    #
    #         if connections_response.status_code != 200:
    #             connections_data = connections_response.json()
    #             for connection in connections_data['connections']['connection']:
    #                 # print(f"connection type: {connection['type']}")
    #                 if connection['type'] == db_to_update:
    #                     if connection['userName'] == old_read_only_username:
    #                         connection_id = connection['id']
    #                         request_body = {
    #                             'connection': {
    #                                 'userName': new_read_only_username,
    #                                 'password': new_read_only_user_password
    #                             }
    #                         }
    #                         # print(f"connection to update: {connection}")
    #                         # # update connection
    #                         # conn_update_response = requests.put(
    #                         #     f'{tableau_baseurl}/api/3.7/sites/{site_id}/datasources/{data_source_id}/connections/{connection_id}',
    #                         #     data=json.dumps(request_body), headers=headers)
    #                         #
    #                         # update_status = 'failed'
    #                         # if conn_update_response.status_code == 200:
    #                         #     update_status = 'successful'
    #                         # print(
    #                         #     f'Connection ID: {connection_id} Data Source Name: {data_source["name"]} update {update_status}')
    #             counter += 1
    #     print(f"Total connections: {counter}")
    #
    #     # sign out
    #     sign_out_headers = {'X-Tableau-Auth': headers['X-Tableau-Auth']}
    #     sign_out_response = requests.post(f'{tableau_baseurl}/api/3.7/auth/signout', headers=sign_out_headers)
    #     if sign_out_response.status_code == 204:
    #         print('Successfully Signed Out')
    #     else:
    #         print('Sign Out Failed')

"""
    NOTES:
    > api_version: 3.7, server_version: v2020.1

    > rest-api fundamental concepts
    https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_concepts_fundamentals.htm

    > rest-api-samples
    https://github.com/tableau/rest-api-samples/tree/master/python
    https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_concepts_example_requests.htm (rq_bdy xml to json)

    > Pagination
    https://help.tableau.com/v2020.1/api/rest_api/en-us/REST/rest_api_concepts_paging.htm

    > List Data Sources
    https://help.tableau.com/v2020.1/api/rest_api/en-us/REST/rest_api_ref.htm#query_data_sources

    > List Data Source Connections
    https://help.tableau.com/v2020.1/api/rest_api/en-us/REST/rest_api_ref.htm#query_data_source_connections

    > Update a Data Source
    https://help.tableau.com/v2020.1/api/rest_api/en-us/REST/rest_api_ref.htm#update_data_source_connection

    > Sign Out
    https://help.tableau.com/v2020.1/api/rest_api/en-us/REST/rest_api_ref.htm#sign_out
"""
