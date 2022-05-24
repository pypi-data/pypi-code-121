from typing import Callable, List, Dict, Optional
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from skill_sdk.utils.util import CamelModel


class SessionRequestDto(CamelModel):
    new_session: bool
    id: str
    attributes: Dict[str, str]


class SkillContextAttributeValueDto(CamelModel):
    id: int
    value: str
    nested_in: List[int]
    overlaps_with: List[int]
    extras: Dict[str, str]


class SkillContextDto(CamelModel):
    intent: str
    skill_id: str
    attributes: Optional[Dict[str, List[str]]]
    attributesV2: Optional[Dict[str, List[SkillContextAttributeValueDto]]]
    tokens: Dict[str, str]
    locale: str
    configuration: Dict[str, List[str]]
    user_profile_config: str
    client_type_name: str


class SkillFitnessInitiateJudgement(CamelModel):
    context: SkillContextDto
    session: SessionRequestDto
    spi_version: str


class SkillFitContentMap(CamelModel):
    skill_fit_confidence: str


class SkillFitAssessmentObject(CamelModel):
    code: int
    content_version: str
    content_map: SkillFitContentMap


class SkillFitAssessmentSingleton(object):
    _instance = None
    _skill_fit_assess_func: Callable

    def __init__(self):
        if SkillFitAssessmentSingleton._instance is None:
            raise RuntimeError('Call SkillFitAssessmentSingleton.instance() instead')
        else:
            SkillFitAssessmentSingleton._instance = self

    def set_response_implementation(self, func_name):
        self._skill_fit_assess_func = func_name

    def get_response_implementation(self, r: SkillFitnessInitiateJudgement):
        response_object = self._skill_fit_assess_func(r)
        return JSONResponse(status_code=response_object.code,
                            content=dict(contentMap=jsonable_encoder(response_object.content_map),
                                         contentVersion=response_object.content_version))

    def return_default_response_implementation(self, r: SkillFitnessInitiateJudgement):
        return SkillFitAssessmentObject(code=501, content_version=1.0,
                                        content_map=SkillFitContentMap(skill_fit_confidence="0.0"))

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._skill_fit_assess_func = cls.return_default_response_implementation

        return cls._instance
