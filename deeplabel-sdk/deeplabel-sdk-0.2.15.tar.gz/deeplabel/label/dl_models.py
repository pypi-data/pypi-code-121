from typing import Any, Dict, List, Optional

from logging import getLogger
import deeplabel.client
import deeplabel
from deeplabel.basemodel import DeeplabelBase, MixinConfig
from enum import Enum

from deeplabel.exceptions import InvalidIdError


logger = getLogger(__name__)

class DlModelStepStatus(Enum):
    TBD = "TBD"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    ABORTED = "ABORTED"
    FAILURE = "FAILURE"


class _Status(MixinConfig):
    status: DlModelStepStatus
    start_time: float
    end_time: float
    error: Optional[None]


class _StatusWithProgress(MixinConfig):
    status: DlModelStepStatus
    start_time: float
    end_time: float
    error: Optional[None]
    progress: float


class DlModelStatus(MixinConfig):
    submission: _Status
    data_preparation: _StatusWithProgress
    training: _StatusWithProgress
    upload: _Status


class SequenceInfo(MixinConfig):
    length: int
    sampling_rate: int


class DlModelCategory(Enum):
    CLASSIFICATION = "CLASSIFICATION"
    DETECTION = "DETECTION"
    ACTION_RECOGNITION = "ACTION-RECOGNITION"


class DlModelType(Enum):
    ACTION = "ACTION"
    OBJECT = "OBJECT"


class DlModel(DeeplabelBase):
    dl_model_id: str
    url: str
    description: str
    learning_rate: float
    sequence: Optional[SequenceInfo]
    status: DlModelStatus
    name: str
    architecture: str
    category: DlModelCategory
    type: DlModelType
    project_id: str

    @classmethod
    def _from_search_params(
        cls, params: Dict[str, Any], client: "deeplabel.client.BaseClient"
    ) -> List["DlModel"]:
        resp = client.get("/dlmodels", params)
        dlmodels = resp.json()["data"]["dlModels"]
        dlmodels = [cls(**dlmodel, client=client) for dlmodel in dlmodels]
        return dlmodels

    @classmethod
    def from_dl_model_id(
        cls, dl_model_id: str, client: "deeplabel.client.BaseClient"
    ) -> "DlModel":
        dlmodels = cls._from_search_params({"dlModelId": dl_model_id}, client)
        if not dlmodels:
            raise InvalidIdError(f"No DlModel found with dlModelId: {dl_model_id}")
        return dlmodels[0]
    
    @property
    def generate_zip_url(self):
        resp = self.client.get("/dlmodels/download", params={"dlModelId":self.dl_model_id})
        if resp.status_code > 200:
            logger.info(f"Failed fetching dlmodel presigned url for {self.dl_model_id}. Please make sure the zip exists in s3")
            return None
        return resp.json()['data']

