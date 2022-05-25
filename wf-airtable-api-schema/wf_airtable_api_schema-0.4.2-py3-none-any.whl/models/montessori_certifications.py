from typing import Optional

from pydantic import BaseModel

MODEL_TYPE = "montessori_certification"


class CreateAPIMontessoriCertificationsFields(BaseModel):
    year_certified: Optional[int] = None
    certification_levels: Optional[list[str]] = None
    certifier: Optional[str] = None
    is_montessori_certified: bool = False
    is_seeking_montessori_certification: bool = False


class APIMontessoriCertificationsFields(CreateAPIMontessoriCertificationsFields):
    full_name: Optional[str] = None
    certifier_other: Optional[str] = None
