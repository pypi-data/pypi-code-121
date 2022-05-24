# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.

import base64
from enum import Enum
import typing
import dill

import pyarrow as pa
from shapelets.model import (
    Model
)
from shapelets.services.base_service import BaseService


class Endpoint(Enum):
    MODELS = "api/models"
    MODEL_BY_ID = f"{MODELS}/###model_id###"
    MODEL_DATA_BY_ID = f"{MODEL_BY_ID}/data"

    def replace(self, model_id: str):
        template = str(self.value)
        return template.replace("###model_id###", model_id)


class ModelsService(BaseService):

    def get_model(self, model_id: str) -> Model:
        model = self.request_get(Endpoint.MODEL_BY_ID.replace(model_id))
        return Model.from_dict(model)

    def create_model(self,
                     data,
                     name: str = None,
                     description: str = None,
                     metadata: typing.Dict[str, str] = None) -> Model:

        content = self.request_post(
            Endpoint.MODELS.value,
            {
                "name": name if name else "",
                "description": description if description else "",
                "data": str(base64.b64encode(dill.dumps(data)), encoding='utf-8'),
                "metadata": metadata
            }
        )
        return Model.from_dict(content)

    def get_model_data(self, model: Model) -> str:
        response = self.request_get(
            Endpoint.MODEL_DATA_BY_ID.replace(model.model_id),
            raw_content=True)
        return base64.decodebytes(response).decode("utf-8")

    def update_model(self, model: Model, data) -> Model:
        content = self.request_put(
            Endpoint.MODEL_BY_ID.replace(model.model_id),
            {
                "name": model.name,
                "description": model.description,
                "data": str(base64.b64encode(dill.dumps(data)), encoding='utf-8') if data is not None else None,
                "metadata":  model.metadata
            }
        )
        return Model.from_dict(content)

    def delete_model(self, model: Model) -> bool:
        return self.request_delete(Endpoint.MODEL_BY_ID.replace(model.model_id))

