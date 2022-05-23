from typing import List
import requests
from requests import Response, Session, Request
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.text import Text
from enum import Enum
from .gredients import *
import json
from dateutil.parser import isoparse
from dateutil.tz import gettz, tzutc

console = Console()
datetime_formatter_one = "%Y-%m-%d %H:%M:%S"
datetime_formatter_two = "%Y-%m-%dT%H:%M:%SZ"


class ThingsMatrixResponse():

    code = None
    data = None
    msg = None

    __rawData = None

    def __init__(self, response: Response) -> None:
        self.status_code = response.status_code
        self.__response = response
        try:
            self.__rawData = self.__response.json()
            self.code = self.__rawData.get('code', None)
            self.data = self.__rawData.get('data', None)
            self.msg = self.__rawData.get('msg', None)
        except Exception as e:
            raise e

    @property
    def hasData(self) -> bool:
        return self.code == 0 and self.status_code == 200 and self.data

    @property
    def hasNoData(self) -> bool:
        return self.code != 0 and self.status_code == 200 and ~self.data


class ThingsMatrixRequest:
    ...
    __headers = {'accept': '*/*', 'Authorization': f'ApiKey {API_KEY}'}

    @classmethod
    def get(self, url, params={}):
        return requests.get(url=url, params=params, headers=self.__headers)


class deviceStatus(Enum):
    suspended = -1
    disabled = 0
    offline = 1
    online = 2
    standby = 3
    tracking = 4
    inactive = 5


class gpsLocating(Enum):
    unknown = -1
    LBS = 0
    GPS = 1
    BeiDou = 2
    GLONASS = 3
    Galileo = 4
    GNSS = 5


class severity(Enum):
    Critical = 0
    Major = 1
    Minor = 2


class eventStatus(Enum):
    failed = 0
    success = 1


class ObjBase:

    def __init__(self, raw) -> None:
        self.raw = raw
        self.__json = ''

    def utc_to_local(self, dt):
        if type(dt) is datetime:
            return dt
        dt = isoparse(dt)
        if not dt.tzinfo:
            return dt.replace(tzinfo=tzutc()).astimezone()
        return dt.astimezone()

    @property
    def json(self):
        self.__json


class ObjsBase:

    def __init__(self, objs) -> None:
        self.objs = objs

    @property
    def json(self):
        """Construct every objs' dict format into a list

        Returns:
            list: List of every objects
        """
        return [obj.json for obj in self.objs] if self.objs else []


class Device(ObjBase):

    def __init__(self, device_content: dict) -> None:
        self.raw = device_content
        self.__json = device_content
        self.alias = device_content.get('alias', None)
        self.attributes = device_content.get('attributes', None)
        self.cerOverwrite = device_content.get('cerOverwrite', None)
        self.certificate = device_content.get('certificate', None)
        self.createTime = device_content.get('createTime', None)
        if self.createTime:
            self.createTime = self.utc_to_local(self.createTime)
            self.__json['createTime'] = self.createTime.strftime(
                "%Y-%m-%d %H:%M:%S")
        self.creator = device_content.get('creator', None)
        self.description = device_content.get('description', None)
        self.group = device_content.get('group', None)
        if self.group:
            self.group = Group(self.group)
        self.iccid = device_content.get('iccid', None)
        self.id = device_content.get('id', None)
        self.imei = device_content.get('imei', None)
        self.model = device_content.get('model', None)
        if self.model:
            self.model = Model(self.model)
        self.pid = device_content.get('pid', None)
        self.sn = device_content.get('sn', None)
        self.sensorOverwrite = device_content.get('sensorOverwriteodel', None)
        self.sensorSn = device_content.get('sensorSn', None)
        self.status = deviceStatus(device_content.get('status', None))
        if self.status:
            self.__json['status'] = self.status.name
        self.tags = device_content.get('tags', None)
        self.tempOverwrite = device_content.get('tempOverwrite', None)
        self.template = device_content.get('template', None)
        if self.template is not None and len(self.template) < 3:
            self.template = Template.get_template(self.template['id'])
            self.__json['template'] = self.template.json
        self.updateTime = device_content.get('updateTime', None)
        if self.updateTime:
            self.updateTime = self.utc_to_local(self.updateTime)
            self.__json['updateTime'] = self.updateTime.strftime(
                "%Y-%m-%d %H:%M:%S")
        self.updator = device_content.get('updator', None)
        self.latest = device_content.get('latest', None)
        if self.latest:
            self.latest = Report(self.latest)
            self.__json['latest'] = self.latest.json

    @property
    def json(self):
        return self.__json

    def get_latest(self):
        ...
        return self.latest

    def __repr__(self):
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column('id')
        table.add_column('sn')
        table.add_column('imei')
        table.add_column('iccid')
        table.add_column('status')
        table.add_column('creator')
        table.add_column('create time')
        table.add_column('update time')
        table.add_column('model')
        table.add_column('group')
        table.add_column('pid')
        table.add_row(
            self.id,
            self.sn,
            self.imei,
            self.iccid,
            self.status.name,
            self.creator,
            str(self.createTime),
            str(self.updateTime),
            self.model.name,
            self.group.name,
            self.pid,
        )
        console.print(table)
        return ''

    def is_recently(self):
        ...


class Devices(list):
    ...

    def __init__(self) -> None:
        pass

    def append(self, __object: Device) -> None:
        return super().append(__object)


class Group(ObjBase):
    ...

    def __init__(self, group_dict) -> None:
        self.id = group_dict.get('id', None)
        self.name = group_dict.get('name', None)

    def __repr__(self) -> str:
        return self.name


class Model(ObjBase):
    ...

    def __init__(self, model_dict) -> None:
        self.id = model_dict.get('id', None)
        self.name = model_dict.get('name', None)

    def __repr__(self) -> str:
        return self.name


class Company:
    ...

    def __init__(self) -> None:
        pass


class Location(ObjBase):
    ...

    def __init__(self, location_dict) -> None:
        self.__json = location_dict
        self.radius = location_dict.get('radius', None)
        self.latitude = location_dict.get('latitude', None)
        self.longitude = location_dict.get('longitude', None)
        self.altitude = location_dict.get('altitude', None)

    @property
    def json(self):
        return self.__json


class Report(ObjBase):
    ...

    def __init__(self, report_dict) -> None:
        self.__json = report_dict
        self.chargeFlag = report_dict.get('chargeFlag', None)
        self.gpsLocating = report_dict.get('gpsLocating', None)
        if self.gpsLocating is not None:
            self.gpsLocating = gpsLocating(self.gpsLocating)
            self.__json['gpsLocating'] = self.gpsLocating.name
        self.location = report_dict.get('location', None)
        if self.location:
            self.location = Location(
                self.location) if type(self.location) is dict else Location(
                    json.loads(self.location))
            self.__json['location'] = self.location.json
        self.eid = report_dict.get('eid', None)
        self.ver = report_dict.get('ver', None)
        self.reportLatency = report_dict.get('reportLatency', None)
        self.iccidChange = report_dict.get('iccidChange', None)
        self.pc_vendor = report_dict.get('pc_vendor', None)
        self.prev_report_time = report_dict.get('prev_report_time', None)
        if self.prev_report_time:
            self.prev_report_time = self.utc_to_local(self.prev_report_time)
            self.__json['prev_report_time'] = self.prev_report_time.strftime(
                "%Y-%m-%d %H:%M:%S")
        self.prev_info_time = report_dict.get('prev_report_time', None)
        if self.prev_info_time:
            self.prev_info_time = self.utc_to_local(self.prev_info_time)
            self.__json['prev_info_time'] = self.prev_report_time.strftime(
                "%Y-%m-%d %H:%M:%S")
        self.systemTime = report_dict.get('systemTime', None)
        if self.systemTime:
            self.systemTime = self.utc_to_local(self.systemTime)
            self.__json['systemTime'] = self.systemTime.strftime(
                "%Y-%m-%d %H:%M:%S")
        self.mfg = report_dict.get('mfg', None)
        self.fw = report_dict.get('fw', None)
        self.iccid = report_dict.get('iccid', None)
        self.vendor = report_dict.get('vendor', None)
        self.imei = report_dict.get('imei', None)
        self.timeInterval = report_dict.get('timeInterval', None)
        self.model = report_dict.get('model', None)
        self.time = report_dict.get('time', None)
        if self.time:
            self.time = self.utc_to_local(self.time)
            self.__json['time'] = self.time.strftime("%Y-%m-%d %H:%M:%S")
        self.power = report_dict.get('power', None)
        self.sn = report_dict.get('sn', None)
        self.ipaddr = report_dict.get('ipaddr', None)
        self.net = report_dict.get('net', None)
        self.cellid = report_dict.get('cellid', None)
        self.lac = report_dict.get('lac', None)
        self.mcc = report_dict.get('mcc', None)
        self.mnc = report_dict.get('mnc', None)
        self.rssi = report_dict.get('rssi', None)
        self.battery = report_dict.get('battery', None)

    @property
    def columns(self):
        columns = [
            'sn',
            'ipaddr',
            'net',
            'cellid',
            'lac',
            'mcc',
            'mnc',
            'rssi',
            'power',
            'battery',
            'timeInterval',
            'prev report time',
            'time',
        ]
        return columns

    @property
    def dataRow(self):
        data = [
            self.sn,
            self.ipaddr,
            self.net,
            str(self.cellid),
            str(self.lac),
            str(self.mcc),
            str(self.mnc),
            str(self.rssi),
            str(self.power),
            str(self.battery),
            str(self.timeInterval),
            self.prev_report_time.strftime("%Y-%m-%d %H:%M:%S")
            if self.prev_report_time else None,
            self.time.strftime("%Y-%m-%d %H:%M:%S"),
        ]
        return data

    @property
    def table(self):
        table = Table(show_header=True, header_style="bold magenta")
        for c in self.columns:
            table.add_column(c)
        table.add_row(*self.dataRow)
        return table

    @property
    def columns(self):
        columns = [
            'sn',
            'ipaddr',
            'net',
            'cellid',
            'lac',
            'mcc',
            'mnc',
            'rssi',
            'power',
            'battery',
            'timeInterval',
            'prev report time',
            'time',
        ]
        return columns

    @property
    def json(self):
        return self.__json

    def __repr__(self) -> str:
        ...
        console.print(self.table)
        return ''


class Reports(ObjsBase):
    ...
    # @property
    # def table(self):
    #     table = Table(show_header=True, header_style="bold magenta")
    #     for c in self.columns:
    #         table.add_column(c)
    #     for row in self.dataRows:
    #         table.add_row(*row)
    #     return table

    # @property
    # def dataRows(self):
    #     rows = [report.dataRow for report in self.__reports]
    #     return rows

    # def __repr__(self) -> str:
    #     console.print(self.table)

    #     return ''


class Sensor(ObjBase):

    def __init__(self) -> None:
        pass


class Template(ObjBase):

    base_url = TEMPLATE_URL

    def __init__(self, template_dict) -> None:
        self.__json = template_dict
        self.id = template_dict.get('id', None)
        self.name = template_dict.get('name', None)
        self.configure = template_dict.get('configure', None)
        self.configure_dict = None
        if self.configure:
            self.configure_dict = json.loads(self.configure)
            self.configure = self.Configure(self.configure_dict)
        self.description = template_dict.get('description', None)
        self.creator = template_dict.get('creator', None)
        self.createTime = template_dict.get('createTime', None)
        if self.createTime:
            self.createTime = self.utc_to_local(self.createTime)
        self.updator = template_dict.get('updator', None)
        self.updatetime = template_dict.get('updatetime', None)
        self.model = template_dict.get('model', None)
        if self.model:
            self.model = Model(self.model)
        ...

    def get_config_settings(self, sensorName, ruleName):
        if self.configure_dict:
            for sensor in self.configure_dict['settings']:
                if sensor['sensorName'] == sensorName:
                    for rule in sensor['ruleset']:
                        if rule['ruleName'] == ruleName:
                            return rule['ruleValue'] + ' ' + rule['unit']
        return None

    @property
    def heartbeat_timer(self):
        return self.get_config_settings('Heartbeat_settings',
                                        'heartbeat_timer')

    @property
    def ac_report_interval(self):
        return self.get_config_settings('ac_power_mode_settings',
                                        'ac_report_timer')

    @property
    def dc_report_interval(self):
        return self.get_config_settings('dc_power_mode_settings',
                                        'dc_report_timer')

    @property
    def gps_report_interval(self):
        return self.get_config_settings('positioning_settings', 'gnss_timer')

    @classmethod
    def get_template(self, id):
        response = ThingsMatrixResponse(
            ThingsMatrixRequest.get(f"{self.base_url}/{id}"))
        if response.hasData:
            return Template(response.data)
        return None

    @property
    def json(self):
        if self.__json.get('configure', None):
            self.__json['configure'] = self.configure.json
        return self.__json

    class Configure(object):
        ...
        json = {}

        def __init__(self, configure) -> None:
            if configure:
                for sensor in configure['settings']:
                    setattr(self, sensor['sensorName'], Sensor())
                    for rule in sensor['ruleset']:
                        self.json[rule[
                            'ruleName']] = rule['ruleValue'] + ' ' + rule.get(
                                'unit', '')
                        setattr(getattr(self, sensor['sensorName']),
                                rule['ruleName'],
                                rule['ruleValue'] + ' ' + rule.get('unit', ''))

        def __repr__(self) -> str:
            return self.json


class Event(ObjBase):
    ...

    def __init__(self, event_dict) -> None:
        self.raw = event_dict
        self.__json = event_dict
        self.sn = event_dict.get('sn', None)
        self.status = eventStatus(event_dict.get('status', None))
        if self.status is not None:
            self.__json['status'] = self.status.name
        self.severity = severity(event_dict.get('severity', None))
        if self.severity is not None:
            self.__json['severity'] = self.severity.name
        self.origin = event_dict.get('origin', None)
        self.code = event_dict.get('code', None)
        self.category = event_dict.get('category', None)
        self.additionInfo = event_dict.get('additionInfo', None)
        if self.additionInfo:
            self.additionInfo = json.loads(self.additionInfo)
            self.__json['additionInfo'] = self.additionInfo
        self.time = event_dict.get('time', None)
        if self.time:
            self.time = self.utc_to_local(self.time)
            self.__json['time'] = self.time.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def table(self):
        table = Table(show_header=True, header_style="bold magenta")
        for c in self.columns:
            table.add_column(c)
        table.add_row(*self.dataRow)
        return table

    @property
    def columns(self):
        columns = [
            'sn',
            'status',
            'severity',
            'origin',
            'code',
            'category',
            'additionInfo',
            'time',
        ]
        return columns

    @property
    def dataRow(self):
        data = [
            self.sn,
            str(self.status),
            str(self.severity),
            self.origin,
            self.code,
            self.category,
            json.dumps(self.additionInfo) if self.additionInfo else None,
            self.time.strftime("%Y-%m-%d %H:%M:%S"),
        ]
        return data

    @property
    def json(self):
        return self.__json

    def __repr__(self) -> str:
        ...
        console.print(self.table)
        return ''


class Events(ObjsBase):
    ...


class Pages:

    def __init__(self, response: Response) -> None:
        if response.ok and response.status_code == 200:
            data = response.json()
            self.response = response
            self.code = data.get('code', None)
            self.msg = data.get('msg', None)
            if self.code == 0 and self.msg == 'success':
                self.datas = data.get('data', None)
                self.content = []
                if self.datas.get('content', None):
                    self.content = self.datas['content']
                self.number = self.datas.get('number', None)
                self.size = self.datas.get('size', None)
                self.totalElements = self.datas.get('totalElements', None)
                self.totalPages = self.datas.get('totalPages', None)
                self.sort = self.datas.get('sort', None)
                self.last = self.datas.get('last', None)
                self.first = self.datas.get('first', None)
                self.timestamp = data.get('first', None)
            else:
                raise BaseException(self.msg)

    def collect_contents(self, useClass, params: dict = None):
        ...
        if not self.content: return None, None
        if len(self.content) < self.totalElements:
            # server max get size = 2000
            # if oversize then need to query by page
            with Session() as session:
                prerequest = self.response.request
                if params:
                    params.update({'size': self.totalElements})
                prerequest.prepare_url(
                    prerequest.url[:prerequest.url.index('?')], params)
                response = session.send(prerequest)
                page = Pages(response)
                self.content = page.content
            return response, [useClass(obj) for obj in self.content]
        elif self.number == self.totalPages == 1:  #just one page
            if self.totalElements == 1:
                return self.response, [useClass(self.content[0])]
            else:
                return self.response, [useClass(obj) for obj in self.content]

        return None, None
