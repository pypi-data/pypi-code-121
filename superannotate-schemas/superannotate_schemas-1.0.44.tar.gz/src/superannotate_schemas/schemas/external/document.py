from typing import List
from typing import Optional
from typing import Union

from pydantic import Field
from pydantic import StrictStr
from pydantic import ValidationError
from pydantic.error_wrappers import ErrorWrapper

from superannotate_schemas.schemas.base import BaseAttribute
from superannotate_schemas.schemas.base import BaseDocumentInstance
from superannotate_schemas.schemas.base import BaseMetadata as Metadata
from superannotate_schemas.schemas.base import BaseModel
from superannotate_schemas.schemas.base import INVALID_DICT_MESSAGE
from superannotate_schemas.schemas.base import NotEmptyStr
from superannotate_schemas.schemas.base import Tag
from superannotate_schemas.schemas.enums import DocumentAnnotationTypeEnum


class Attribute(BaseAttribute):
    name: NotEmptyStr
    group_name: NotEmptyStr = Field(alias="groupName")


class EntityInstance(BaseDocumentInstance):
    start: int
    end: int
    attributes: Optional[List[Attribute]] = Field(list())


class TagInstance(BaseDocumentInstance):
    attributes: Optional[List[Attribute]] = Field(list())
    class_name: NotEmptyStr = Field(alias="className")


class DocumentInstance(BaseDocumentInstance):
    pass


ANNOTATION_TYPES = {
    DocumentAnnotationTypeEnum.ENTITY: EntityInstance,
    DocumentAnnotationTypeEnum.TAG: TagInstance,
}


class AnnotationInstance(BaseModel):
    __root__: Union[TagInstance, EntityInstance]

    @classmethod
    def __get_validators__(cls):
        yield cls.return_action

    @classmethod
    def return_action(cls, values):
        try:
            try:
                instance_type = values["type"]
            except KeyError:
                raise ValidationError(
                    [ErrorWrapper(ValueError("field required"), "type")], cls
                )
            return ANNOTATION_TYPES[instance_type](**values)
        except KeyError:
            raise ValidationError(
                [
                    ErrorWrapper(
                        ValueError(
                            f"invalid type, valid types are {', '.join(ANNOTATION_TYPES.keys())}"
                        ),
                        "type",
                    )
                ],
                cls,
            )
        except TypeError as e:
            raise TypeError(INVALID_DICT_MESSAGE) from e


class DocumentAnnotation(BaseModel):
    metadata: Metadata
    instances: Optional[List[AnnotationInstance]] = Field(list())
    tags: Optional[List[Tag]] = Field(list())
    free_text: Optional[StrictStr] = Field(None, alias="freeText")
