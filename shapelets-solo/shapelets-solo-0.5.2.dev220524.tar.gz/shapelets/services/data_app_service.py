# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import typing
from enum import Enum

from shapelets.dsl import DataApp, SupportedTypes
from shapelets.services.base_service import BaseService


class Endpoint(Enum):
    DATAAPPS = "api/dataapps"
    DATAAPP_BY_ID = f"{DATAAPPS}/###dataapp_id###"

    def replace(self, data_app_id: str) -> str:
        template = str(self.value)
        return template.replace("###dataapp_id###", data_app_id)


class DataAppService(BaseService):

    def get_data_apps(self) -> typing.List[DataApp]:
        return self.request_get(Endpoint.DATAAPPS.value)

    def register_data_app(self, app: DataApp) -> typing.Dict[str, SupportedTypes]:
        data_app_json = self.request_post(
            Endpoint.DATAAPPS.value,
            {
                "name": app.name,
                "description": app.description,
                "spec": app.to_json()
            })
        return DataApp(data_app_json['name'],
                       data_app_json['description'],
                       data_app_json['creationDate'],
                       data_app_json['updateDate'])

    def delete_data_app(self, data_app_id: str) -> bool:
        return self.request_delete(
            Endpoint.DATAAPP_BY_ID.replace(data_app_id))
