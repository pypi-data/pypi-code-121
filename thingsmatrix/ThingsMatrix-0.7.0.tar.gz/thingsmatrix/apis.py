import rich
from rich import print, console
from typing import Optional
from requests import Request, get, post
from hashlib import md5
from .gredients import *
from .objects import Pages, Device, Report, Reports, ThingsMatrixResponse, Template, Event, Events
from datetime import datetime
from dateutil.tz import tzutc, gettz

console = console.Console()

class ThingsMatrix:

    def __init__(self, api_key=API_KEY, base_url=BASE_URL) -> None:
        self.get = get
        self.__headers = {
            'accept': '*/*',
            'Authorization': f'ApiKey {api_key}'
        }
        self.__requests = None
        self.__reqponse = None

    def login(self, username: str, password: str):
        '''
        return version 1 api token
        '''
        # api version 1
        # https://docs.thingsmatrix.io/apidoc/#tag/User
        json = {
            "loginName": username,
            "password": md5(password.encode('utf-8')).hexdigest().lower()
        }
        token_response = post(f"{USER_URL}/login", json=json)
        if token_response.ok and token_response.status_code == 200:
            data = token_response.json()
            if data['msg'] == 'success':
                return data['data']
            raise BaseException(data['msg'])
        raise BaseException(token_response.status_code)

    #region Device
    def get_devices(self,
                    group: str = None,
                    modelId: str = None,
                    offset: int = None,
                    page: int = 1,
                    pageNumber: int = None,
                    pageSize: int = None,
                    paged: bool = None,
                    searchTerm: str = None,
                    size: int = 2000,
                    sort: str = None,
                    sort_sorted: bool = None,
                    sort_unsorted: bool = None,
                    status: int = None,
                    tags: str = None,
                    unpaged: bool = None,
                    **kwargs):
        ...
        _locals = locals()
        del _locals['self']
        del _locals['kwargs']
        del _locals['sort_sorted']
        del _locals['sort_unsorted']

        for k, v in _locals.items():
            if v:
                kwargs[k] = v

        if sort_sorted:
            kwargs['sort.sorted'] = sort_sorted
        if sort_unsorted:
            kwargs['sort.unsorted'] = sort_unsorted
        devices = None
        response = self.get(f'{BASE_URL}/devices',
                            headers=self.__headers,
                            params=kwargs)
        if response.ok and response.status_code == 200:
            devices = Pages(response).collect_contents(Device)
        else:
            print(response.json())
        return response, devices

    def get_device(self, sn):
        response = ThingsMatrixResponse(
            self.get(f'{BASE_URL}/devices/{sn}', headers=self.__headers))
        if response.hasData:
            return Device(response.data)
        return None

    #endregion

    #region Groups
    def get_groups(self,
                   model_id: str = None,
                   offset: int = None,
                   page: int = None,
                   **kwargs):

        _locals = locals()
        del _locals['self']
        del _locals['kwargs']
        for k, v in _locals.items():
            if v:
                kwargs[k] = v

        response = self.get(f'{BASE_URL}/groups',
                            headers=self.__headers,
                            params=kwargs)
        if response.ok:
            print(response.json())
            return response
        else:
            print(response.json())

        ...

    #endregion

    #region Log Data
    def get_devices_reports(self,
                            sn,
                            startTime=None,
                            endTime=None,
                            size=2000,
                            **kwargs):
        ...
        _locals = locals().copy()
        _kwargs = kwargs
        del _locals['self']
        del _locals['kwargs']
        for k, v in _locals.items():
            if v:
                _kwargs[k] = v

        if startTime:
            _kwargs['startTime'] = self.__convert_to_utc(startTime)
        if endTime:
            _kwargs['endTime'] = self.__convert_to_utc(endTime)

        response = self.get(f'{REPORTS_URL}',
                            headers=self.__headers,
                            params=_kwargs)
        reports = []
        if response.ok:
            response, reports = Pages(response).collect_contents(
                Report, _kwargs)
            reports = Reports(reports)
        else:
            print(response.json())
        return response, reports

    def __convert_to_utc(self, dateString: str) -> str:
        """Convert current timezone time to UTC

        Args:
            dateString (str): date-time string format as %Y-%m-%d %H:%M:%S

        Returns:
            str: utc date-time format as %Y-%m-%d %H:%M:%S
        """
        data_time = datetime.strptime(
            dateString, "%Y-%m-%d %H:%M:%S").replace(tzinfo=gettz())
        utc_data_time = data_time.astimezone(
            tzutc()).strftime("%Y-%m-%d %H:%M:%S")
        return utc_data_time

    def get_devices_events(self,
                           sn,
                           startTime=None,
                           endTime=None,
                           size=2000,
                           **kwargs):
        _locals = locals()
        del _locals['self']
        del _locals['kwargs']
        for k, v in _locals.items():
            if v:
                kwargs[k] = v
        if startTime:
            kwargs['startTime'] = self.__convert_to_utc(startTime)
        if endTime:
            kwargs['endTime'] = self.__convert_to_utc(endTime)

        response = self.get(f'{EVENTS_URL}',
                            headers=self.__headers,
                            params=kwargs)
        events = []
        if response.ok:
            response, events = Pages(response).collect_contents(Event, kwargs)
            events = Events(events)
        else:
            print(response.json())
        return response, events

    #TODO: use ThingsMatrixRequest/ThingsMatrixReponse
    #endregion

    #region Models
    def get_models(self):
        response = self.get(f'{BASE_URL}/models', headers=self.__headers)

    #endregion

    #region Template Config
    def get_template(self, id=None, name=None, **kwargs):
        template = None
        _locals = locals()
        del _locals['self']
        del _locals['kwargs']
        for k, v in _locals.items():
            if v:
                kwargs[k] = v
        if id:
            response = ThingsMatrixResponse(
                self.get(f'{BASE_URL}/configs/{id}', headers=self.__headers))
            if response.hasData:
                template = Template(response.data)
        elif name:
            response = ThingsMatrixResponse(
                self.get(f'{BASE_URL}/configs/name/{name}',
                         headers=self.__headers))
            if response.hasData:
                template = Template(response.data)
        else:
            ...
        return template

    #endregion

    #region
    def get_location(self):
        ...
        location = self.get()

    #endregion

    def request_get_sender(self, url, params, collect):
        ...
        self.request = Request(url=url, params=params, headers=self.__headers)
