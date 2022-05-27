import json
from types import SimpleNamespace

import requests

from ikologikapi.IkologikApiCredentials import IkologikApiCredentials
from ikologikapi.IkologikException import IkologikException
from ikologikapi.services.AbstractIkologikInstallationService import AbstractIkologikInstallationService


class TagAlertTypeService(AbstractIkologikInstallationService):

    def __init__(self, jwtHelper: IkologikApiCredentials):
        super().__init__(jwtHelper)

    # CRUD Actions

    def get_url(self, customer: str, installation: str, tag: str) -> str:
        return f'{self.jwtHelper.get_url()}/api/v2/customer/{customer}/installation/{installation}/tag/{tag}/tagalerttype/update'

    def update(self, customer: str, installation: str, tag: str, o: object) -> object:
        try:
            data = json.dumps(o, default=lambda o: o.__dict__)
            response = requests.post(
                self.get_url(customer, installation, tag),
                data=data,
                headers=self.get_headers()
            )
            if response.status_code == 200:
                result = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
                return result
            else:
                raise IkologikException("Error while performing update, the request returned status " + str(response.status_code))
        except IkologikException as ex:
            raise ex
        except Exception as ex:
            raise IkologikException("Error while performing update")
