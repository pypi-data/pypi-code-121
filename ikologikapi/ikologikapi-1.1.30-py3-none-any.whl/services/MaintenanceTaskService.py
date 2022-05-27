import json
from types import SimpleNamespace

import requests

from ikologikapi.IkologikApiCredentials import IkologikApiCredentials
from ikologikapi.IkologikException import IkologikException
from ikologikapi.domain.Search import Search
from ikologikapi.services.AbstractIkologikInstallationService import AbstractIkologikInstallationService


class MaintenanceTaskService(AbstractIkologikInstallationService):

    def __init__(self, jwtHelper: IkologikApiCredentials):
        super().__init__(jwtHelper)

    # CRUD Actions

    def get_url(self, customer: str, installation: str) -> str:
        return f'{self.jwtHelper.get_url()}/api/v2/customer/{customer}/installation/{installation}/maintenancetaskaction'

    def update_status(self, customer: str, installation: str, id: str, status) -> object:
        try:
            response = requests.put(
                f'{self.get_url(customer, installation)}/{id}/status',
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

    def get_by_name(self, customer: str, installation: str, name: str) -> object:
        # Prepare the search
        search = Search()
        search.add_filter("name", "EQ", [name])
        search.add_order("name", "ASC")
        search.set_pagination(0, 1)

        # Query
        result = self.search(customer, installation, search)
        if result and len(result) == 1:
            return result[0]
        else:
            return None
