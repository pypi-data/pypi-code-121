import datetime
from typing import Dict
from typing import List
from math import isnan
from typing import Optional
from typing import Union

from pydantic import BaseModel as PyDanticBaseModel
from pydantic import conlist
from pydantic import constr
from pydantic import Extra
from pydantic import StrictFloat
from pydantic import StrictInt
from pydantic import StrictStr
from pydantic import StrictBool
from pydantic import Field
from pydantic import StrRegexError
from pydantic import ValidationError
from pydantic.error_wrappers import ErrorWrapper
from pydantic.errors import EnumMemberError
from pydantic import validator
from pydantic.validators import strict_str_validator
from pydantic.validators import strict_float_validator
from pydantic.validators import strict_int_validator
from pydantic.validators import number_multiple_validator
from pydantic.color import Color
from pydantic.color import ColorType

from superannotate_schemas.schemas.enums import CreationTypeEnum
from superannotate_schemas.schemas.enums import BaseImageRoleEnum
from superannotate_schemas.schemas.enums import VectorAnnotationTypeEnum
from superannotate_schemas.schemas.enums import AnnotationStatusEnum
from superannotate_schemas.schemas.enums import ClassTypeEnum
from superannotate_schemas.schemas.enums import DocumentAnnotationTypeEnum
from superannotate_schemas.schemas.constances import DATE_REGEX
from superannotate_schemas.schemas.constances import DATE_TIME_FORMAT_ERROR_MESSAGE
from superannotate_schemas.schemas.constances import POINT_LABEL_VALUE_FORMAT_ERROR_MESSAGE
from superannotate_schemas.schemas.constances import POINT_LABEL_KEY_FORMAT_ERROR_MESSAGE
from superannotate_schemas.schemas.constances import INVALID_DICT_MESSAGE


def enum_error_handling(self) -> str:
    permitted = ", ".join(repr(v.value) for v in self.enum_values)
    return f"Invalid value, permitted: {permitted}"


EnumMemberError.__str__ = enum_error_handling

NotEmptyStr = constr(strict=True, min_length=1)

StrictNumber = Union[StrictInt, StrictFloat]


class EmailStr(StrictStr):
    @classmethod
    def validate(cls, value: Union[str]) -> Union[str]:
        try:
            constr(
                regex=r"^(?=.{1,254}$)(?=.{1,64}@)[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
            ).validate(value)
        except StrRegexError:
            raise ValueError("Invalid email")
        return value


class BaseModel(PyDanticBaseModel):

    class Config:
        extra = Extra.allow
        use_enum_values = True
        error_msg_templates = {
            "type_error.integer": "integer type expected",
            "type_error.string": "str type expected",
            "value_error.missing": "field required",
        }


class StrictPointNumber(BaseModel):
    __root__: Union[StrictInt, StrictFloat]

    @classmethod
    def __get_validators__(cls):
        yield cls._validate_types

    @classmethod
    def _validate_types(cls, value):
        is_valid_float, is_valid_int = True, True
        try:
            cls._validate_float(value)
        except TypeError:
            is_valid_float = False
        if not is_valid_float:
            try:
                cls._validate_int(value)
            except TypeError:
                is_valid_int = False
        if is_valid_float or is_valid_int:
            return value
        raise TypeError("is not a valid number. Integer or float types are expected")

    @classmethod
    def _validate_int(cls, value):
        return strict_int_validator(value)

    @classmethod
    def _validate_float(cls, value):
        strict_float_validator(value)
        return cls._validate_nan(value)

    @staticmethod
    def _validate_nan(v):
        if isnan(v):
            raise TypeError("NaN is not a valid float")
        return v


class AxisPoint(BaseModel):
    x: StrictNumber
    y: StrictNumber


class BaseAttribute(BaseModel):
    id: Optional[StrictInt]
    group_id: Optional[StrictInt] = Field(alias="groupId")
    name: Optional[NotEmptyStr]
    group_name: Optional[NotEmptyStr] = Field(alias="groupName")


class Tag(BaseModel):
    __root__: NotEmptyStr


class BboxPoints(BaseModel):
    x1: StrictNumber
    x2: StrictNumber
    y1: StrictNumber
    y2: StrictNumber


class TimedBaseModel(BaseModel):
    created_at: Optional[constr(regex=DATE_REGEX)] = Field(None, alias="createdAt")
    updated_at: Optional[constr(regex=DATE_REGEX)] = Field(None, alias="updatedAt")

    @validator("created_at", "updated_at", pre=True, always=True)
    def validate_created_at(cls, value):
        if value:
            try:
                if value is not None:
                    constr(regex=DATE_REGEX, strict=True).validate(value)
            except (TypeError, StrRegexError):
                raise TypeError(DATE_TIME_FORMAT_ERROR_MESSAGE)
            return value
        else:
            return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


class UserAction(BaseModel):
    email: EmailStr
    role: BaseImageRoleEnum


class TrackableModel(BaseModel):
    created_by: Optional[UserAction] = Field(None, alias="createdBy")
    updated_by: Optional[UserAction] = Field(None, alias="updatedBy")
    creation_type: Optional[CreationTypeEnum] = Field(
        CreationTypeEnum.PRE_ANNOTATION.value, alias="creationType"
    )

    @validator("creation_type", always=True)
    def clean_creation_type(cls, _):
        return CreationTypeEnum.PRE_ANNOTATION.value


class LastUserAction(BaseModel):
    email: EmailStr
    timestamp: StrictInt


class BaseInstance(TrackableModel, TimedBaseModel):
    class_id: Optional[StrictInt] = Field(None, alias="classId")
    class_name: Optional[NotEmptyStr] = Field(None, alias="className")


class BaseInstanceTagAttribute(BaseAttribute):
    name: NotEmptyStr
    group_name: NotEmptyStr = Field(alias="groupName")


class BaseInstanceTag(BaseInstance):
    type: ClassTypeEnum
    probability: Optional[StrictInt] = Field(100)
    attributes: Optional[List[BaseInstanceTagAttribute]] = Field(list())
    class_name: NotEmptyStr = Field(alias="className")


class BaseMetadata(BaseModel):
    name: NotEmptyStr
    url: Optional[StrictStr]
    status: Optional[AnnotationStatusEnum]
    annotator_email: Optional[EmailStr] = Field(None, alias="annotatorEmail")
    qa_email: Optional[EmailStr] = Field(None, alias="qaEmail")
    last_action: Optional[LastUserAction] = Field(None, alias="lastAction")
    project_id: Optional[StrictInt] = Field(None, alias="projectId")


class BaseImageMetadata(BaseMetadata):
    width: Optional[StrictInt]
    height: Optional[StrictInt]
    pinned: Optional[StrictBool]


class Correspondence(BaseModel):
    text: NotEmptyStr
    email: EmailStr


class Comment(TimedBaseModel, TrackableModel):
    x: Union[StrictInt, StrictFloat]
    y: Union[StrictInt, StrictFloat]
    resolved: Optional[StrictBool] = Field(False)
    correspondence: conlist(Correspondence, min_items=1)


class BaseImageAnnotationInstance(BaseInstance):
    visible: Optional[StrictBool]
    locked: Optional[StrictBool]
    probability: Optional[StrictInt] = Field(100)
    attributes: Optional[List[BaseAttribute]] = Field(list())
    error: Optional[StrictBool]

    class Config:
        error_msg_templates = {
            "value_error.missing": "field required for annotation",
        }


class StringA(BaseModel):
    string: StrictStr


class PointLabels(BaseModel):
    __root__: Dict[constr(regex=r"^[0-9]+$", min_length=1,  strict=True), StrictStr]

    @classmethod
    def __get_validators__(cls):
        yield cls.validate_type
        yield cls.validate_value

    @validator("__root__", pre=True)
    def validate_value(cls, values):
        result = {}
        errors = []
        validate_key, validate_value = None, None
        for key, value in values.items():
            try:
                validate_key = constr(regex=r"^[0-9]+$", min_length=1,  strict=True).validate(key)
            except ValueError:
                errors.append(
                    ErrorWrapper(
                        ValueError(POINT_LABEL_KEY_FORMAT_ERROR_MESSAGE), str(key)
                    )
                )
            try:
                validate_value = strict_str_validator(value)
            except ValueError:
                errors.append(
                    ErrorWrapper(
                        ValueError(POINT_LABEL_VALUE_FORMAT_ERROR_MESSAGE), str(key)
                    )
                )
            if validate_key and validate_value:
                result.update({validate_key: validate_value})
        if errors:
            raise ValidationError(errors, cls)
        return result

    @classmethod
    def validate_type(cls, values):
        if not issubclass(type(values), dict):
            raise TypeError(INVALID_DICT_MESSAGE)
        return values


class BaseVectorInstance(BaseImageAnnotationInstance):
    type: VectorAnnotationTypeEnum
    point_labels: Optional[PointLabels] = Field(alias="pointLabels")
    tracking_id: Optional[str] = Field(alias="trackingId")
    group_id: Optional[int] = Field(alias="groupId")


class BaseDocumentInstance(BaseInstance):
    type: DocumentAnnotationTypeEnum


class HexColor(BaseModel):
    __root__: ColorType

    @validator("__root__")
    def validate_color(cls, v):
        return '#{:02X}{:02X}{:02X}'.format(*Color(v).as_rgb_tuple())
