from typing import List, Union
import requests, json
from ddd_objects.infrastructure.ao import exception_class_dec
from ddd_objects.infrastructure.repository_impl import error_factory
from ddd_objects.domain.exception import return_codes
from ddd_objects.lib import Logger as _Logger
from .do import LogRecordDO

logger = _Logger()
logger.set_labels(file_name=__file__)
class LogController:
    def __init__(self, ip: str=None, port: int=None) -> None:
        if port is None:
            port = 8080
        if ip is None:
            ip = 'log-control-svc.system-service.svc.cluster.local'
        self.url = f"http://{ip}:{port}"

    def _check_error(self, status_code, info):
        if status_code>299:
            if isinstance(info['detail'], str):
                return_code = return_codes['OTHER_CODE']
                error_info = info['detail']
            else:
                return_code = info['detail']['return_code']
                error_info = info['detail']['error_info']
            logger.error(f'Error detected by log-control-ao:\nreturn code: {return_code}\n'
                f'error info: {error_info}')

    @exception_class_dec(max_try=1)
    def add_record(self, record: LogRecordDO, timeout=30):
        try:
            data = json.dumps(record.to_json())
            response=requests.post(f'{self.url}/record', data=data, timeout=timeout)
            info = json.loads(response.text)
            self._check_error(response.status_code, info)
            return True
        except:
            logger.error(f'Error detected by log-control-ao when connecting to log collector')
            return False

class Logger:
    def __init__(
        self, domain, location, labels=None, life_time=None,
        controller_ip=None, controller_port=None, local:bool=False
    ) -> None:
        self.domain = domain
        self.location = location
        if labels is None:
            labels = ['default']
        if life_time is None:
            life_time = 600
        self.labels = labels
        self.life_time =life_time
        self.local = local
        self.controller = LogController(controller_ip, controller_port)

    def _send_record(
        self, 
        content, 
        record_type, 
        domain=None, 
        location=None, 
        labels=None, 
        life_time=None,
        datetime = None
    ):
        if domain is None:
            domain = self.domain
        if location is None:
            location = self.location
        if labels is None:
            labels = self.labels
        if life_time is None:
            life_time = self.life_time
        record = LogRecordDO(
            log_type = record_type,
            log_domain = domain,
            log_location = location,
            log_inhalt = content,
            log_label = labels,
            log_datetime = datetime,
            _life_time = life_time
        )
        return self.controller.add_record(record)

    def info(
        self, 
        content, 
        domain=None, 
        location=None, 
        labels=None, 
        life_time=None,
        datetime = None
    ):
        if self.local:
            logger.info(content)
        return self._send_record(content, 'info', domain, location, labels, life_time, datetime)

    def error(
        self, 
        content, 
        domain=None, 
        location=None, 
        labels=None, 
        life_time=None,
        datetime = None
    ):
        if self.local:
            logger.error(content)
        return self._send_record(content, 'error', domain, location, labels, life_time, datetime)

