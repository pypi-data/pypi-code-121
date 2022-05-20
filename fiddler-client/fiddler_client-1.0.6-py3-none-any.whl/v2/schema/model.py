from typing import Optional

from fiddler.v2.schema.base import BaseDataSchema


class Model(BaseDataSchema):
    id: Optional[int] = None
    name: str
    # @TODO: OAS says info is optional. Check it.
    info: Optional[dict] = None
    file_list: Optional[dict] = None
    model_type: Optional[str] = None
    framework: Optional[str] = None
    requirements: Optional[str] = None
    # @TODO: Return deployment obj instead of deployment_id
    model_deployment_id: Optional[int] = None
