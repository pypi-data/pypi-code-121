import json
from types import SimpleNamespace

import requests

from ikologikapi.IkologikApiCredentials import IkologikApiCredentials
from ikologikapi.IkologikException import IkologikException
from ikologikapi.services.AbstractIkologikInstallationService import AbstractIkologikInstallationService


class ReportService(AbstractIkologikInstallationService):

    def __init__(self, jwtHelper: IkologikApiCredentials):
        super().__init__(jwtHelper)

    # CRUD Actions

    def get_url(self, customer: str, installation: str, report_type: str) -> str:
        return f'{self.jwtHelper.get_url()}/api/v2/customer/{customer}/installation/{installation}/reporttype/{report_type}/report'

    def build(self, customer: str, installation: str, report_type: str) -> object:
        try:
            response = requests.get(
                f'{self.get_url(customer, installation, report_type)}/build',
                headers=self.get_headers()
            )
            if response.status_code == 200:
                result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
                return result
            else:
                raise IkologikException("Error while performing build, the request returned status " + str(response.status_code))
        except IkologikException as ex:
            raise ex
        except Exception as ex:
            raise IkologikException("Error while performing build")

    def create(self, customer: str, installation: str, report_type: str, o: object) -> object:
        try:
            data = json.dumps(o, default=lambda o: o.__dict__)
            response = requests.post(
                self.get_url(customer, installation, report_type),
                data=data,
                headers=self.get_headers()
            )
            if response.status_code == 201:
                result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
                return result
            else:
                raise IkologikException("Error while performing create, the request returned status " + str(response.status_code))
        except IkologikException as ex:
            raise ex
        except Exception as ex:
            raise IkologikException("Error while performing create")

    def update_status(self, customer: str, installation: str, report_type: str, report_id: str, status: str) -> object:
        try:
            response = requests.put(
                f'{self.get_url(customer, installation, report_type)}/{report_id}/status',
                data=status,
                headers=self.get_headers({'Content-Type': 'text/plain'})
            )
            if response.status_code == 200:
                result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
                return result
            else:
                raise IkologikException("Error while performing update_status, the request returned status " + str(response.status_code))
        except IkologikException as ex:
            raise ex
        except Exception as ex:
            raise IkologikException("Error while performing update_status")

    def upload(self, customer: str, installation: str, report_type: str, report_id: str) -> object:
        try:
            response = requests.get(
                f'{self.get_url(customer, installation, report_type)}/{report_id}/upload',
                headers=self.get_headers()
            )
            if response.status_code == 200:
                result = response.content.decode("utf-8")
                return result
            else:
                raise IkologikException("Error while performing upload, the request returned status " + str(response.status_code))
        except IkologikException as ex:
            raise ex
        except Exception as ex:
            raise IkologikException("Error while performing upload")
