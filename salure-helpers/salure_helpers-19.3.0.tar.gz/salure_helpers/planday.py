import pandas as pd
import requests
import json
import datetime


class Planday:

    def __init__(self, refresh_token: str, client_id: str, planday_base_url: str = 'https://openapi.planday.com/'):
        self.base_url = planday_base_url
        self.refresh_token = refresh_token
        self.client_id = client_id

    def __get_access_token(self):
        """
        In this function, the access_token for planday is retrieved.
        :return: returns the retrieved access_token that can be used to generate child tokens per portal
        """
        url = 'https://id.planday.com/connect/token'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        body = {
            "client_id": self.client_id,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        response = requests.post(url=url, headers=headers, data=body).json()
        access_token = response['access_token']

        return access_token

    def __get_child_token(self, portal_id: str):
        """
        In this function, the access_token for a specified portal is retrieved.
        :return: returns the retrieved access_token that can be used to access data in a portal
        """
        access_token = self.__get_access_token()
        url = 'https://id.planday.com/connect/token'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        body = {
            "client_id": self.client_id,
            "grant_type": "token_exchange",
            "subject_token_type": "openapi:access_token",
            "subject_token": access_token,
            "resource": portal_id
        }
        response = requests.post(url=url, headers=headers, data=body).json()
        child_token = response['access_token']

        return child_token

    def __get_headers(self, access_token: str):
        """
        Returns headers for a planday request
        :param access_token: child token for a portal request
        :return: headers
        """
        headers = {
            'X-ClientId': self.client_id,
            'Authorization': f'Bearer {access_token}',
            'Content-Type': "application/json"
        }

        return headers

    def get_portals(self) -> pd.DataFrame:
        """
        This function returns all possible portals (environments) for the access token
        :return: dataframe with results
        """
        url = f'{self.base_url}portal/v1.0/info'
        access_token = self.__get_access_token()
        headers = self.__get_headers(access_token=access_token)
        response = requests.get(url=url, headers=headers)
        if 200 <= response.status_code < 300:
            df = pd.DataFrame(response.json()['data']['portals'])
            return df
        else:
            raise ConnectionError(f"Planday returned an error while retrieving portals: {response.status_code, response.text}")

    def get_departments(self, portal_id: str) -> pd.DataFrame:
        """
        This function returns all departments in the specified portal.
        :param portal_id: portal ID from planday. See get_portals
        :return: dataframe with results
        """
        url = f'{self.base_url}hr/v1/departments'
        access_token = self.__get_child_token(portal_id=portal_id)
        headers = self.__get_headers(access_token=access_token)
        response = requests.get(url=url, headers=headers)
        if 200 <= response.status_code < 300:
            df = pd.DataFrame(response.json()['data'])
            return df
        else:
            raise ConnectionError(f"Planday returned an error while retrieving departments: {response.status_code, response.text}")

    def get_shifts(self, portal_id: str, from_date: datetime, to_date: datetime) -> pd.DataFrame:
        """
        This function returns all shifts in the specified portal for the specified period.
        :param portal_id: portal ID from planday. See get_portals
        :param from_date: startdate for shift entries to get
        :param to_date: enddate for shift entries to get
        :return: dataframe with results
        """
        url = f"{self.base_url}scheduling/v1.0/shifts"
        access_token = self.__get_child_token(portal_id=portal_id)
        headers = self.__get_headers(access_token=access_token)
        total_response = []
        got_all_results = False
        no_of_loops = 0
        while not got_all_results:
            params = {"limit": "50", "offset": f"{50 * no_of_loops}", "to": to_date, "from": from_date}
            response = requests.get(url=url, headers=headers, params=params)
            if response.status_code == 200:
                response_json = response.json()
                no_of_loops += 1
                got_all_results = False if len(response_json['data']) == 50 else True
                total_response += response_json['data']
            else:
                raise ConnectionError(f"Planday returned an error while retrieving shifts: {response.status_code, response.text}")

        print(f"Received {len(total_response)} shifts from Planday")

        df = pd.DataFrame(total_response)

        return df

    def get_shift_types(self, portal_id: str) -> pd.DataFrame:
        """
        This function returns all shifttypes in the specified portal.
        :param portal_id: portal ID from planday. See get_portals
        :return: dataframe with results
        """
        url = f"{self.base_url}scheduling/v1.0/shifttypes"
        access_token = self.__get_child_token(portal_id=portal_id)
        headers = self.__get_headers(access_token=access_token)
        total_response = []
        got_all_results = False
        no_of_loops = 0
        while not got_all_results:
            params = {"limit": "50", "offset": f"{50 * no_of_loops}"}
            response = requests.get(url=url, headers=headers, params=params)
            if response.status_code == 200:
                response_json = response.json()
                no_of_loops += 1
                got_all_results = False if len(response_json['data']) == 50 else True
                total_response += response_json['data']
            else:
                raise ConnectionError(f"Planday returned an error while retrieving shifttypes: {response.status_code, response.text}")

        print(f"Received {len(total_response)} shifttypes from Planday")

        df = pd.DataFrame(total_response)

        return df

    def get_payroll_report(self, portal_id: str, from_date: datetime, to_date: datetime, department_id: str) -> pd.DataFrame:
        """
        This function returns the payroll report for the specified portal with the give dates and give department.
        :param portal_id: portal ID from planday. See get_portals
        :param from_date: startdate for payroll report
        :param to_date: enddate for payroll report
        :param department_id: department for payroll report. See get_departments
        :return: dataframe with results
        """
        url = f'{self.base_url}/payroll/v1/payroll'
        access_token = self.__get_child_token(portal_id=portal_id)
        headers = self.__get_headers(access_token=access_token)
        response = requests.get(url=url, headers=headers, params={"departmentIds": department_id, "from": from_date, "to": to_date})
        if 200 <= response.status_code < 300:
            df = pd.DataFrame(response.json()['shiftsPayroll'])
            return df
        else:
            raise ConnectionError(f"Planday returned an error while retrieving payroll report: {response.status_code, response.text}")

    def get_employees(self, portal_id: str) -> pd.DataFrame:
        """
        This function returns all employees in the specified portal.
        :param portal_id: portal ID from planday. See get_portals
        :return: dataframe with results
        """
        url = f'{self.base_url}hr/v1.0/employees'
        access_token = self.__get_child_token(portal_id=portal_id)
        headers = self.__get_headers(access_token=access_token)
        total_response = []
        got_all_results = False
        no_of_loops = 0
        while not got_all_results:
            params = {"limit": "50", "offset": f"{50 * no_of_loops}"}
            response = requests.get(url=url, headers=headers, params=params)
            if response.status_code == 200:
                response_json = response.json()
                no_of_loops += 1
                got_all_results = False if len(response_json['data']) == 50 else True
                total_response += response_json['data']
            else:
                raise ConnectionError(f"Planday returned an error while retrieving employees: {response.status_code, response.text}")

        print(f"Received {len(total_response)} employees from Planday")

        df = pd.DataFrame(total_response)

        return df

    def upload_data(self, method: str, endpoint: str, portal_id: str, data: dict):
        """
        Generic function to upload data to Zenegy via POST, PUT or DELETE. Should be made more specific to ensure easy operation
        :param endpoint: the url endpoint
        :param portal_id: portal ID from planday. See get_portals
        :param data: the payload which should be sent as body to Planday. Only with PUT or POST
        :param method: choose between POST, PUT or DELETE
        :return:
        """
        if method != 'PUT' and method != 'POST' and method != 'DELETE':
            raise ValueError('Parameter method should be PUT, POST or DELETE (in uppercase)')

        url = f'{self.base_url}{endpoint}'
        access_token = self.__get_child_token(portal_id=portal_id)
        headers = self.__get_headers(access_token=access_token)

        if method == 'POST' or method == 'PUT':
            response = requests.request(method, url, headers=headers, data=json.dumps(data))
        else:
            response = requests.request(method, url, headers=headers)

        return response
