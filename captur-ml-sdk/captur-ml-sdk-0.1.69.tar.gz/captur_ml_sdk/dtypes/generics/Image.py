from pydantic import (
    BaseModel, validator, root_validator, AnyUrl
)

from typing import Optional, List, Union


# def coord0_less_than_coord1(coord0, length):
#     if coord0 >= coord1:
#         return False
#     return True


class BoundingBox(BaseModel):
    xMin: float
    yMin: float
    xMax: float
    yMax: float
    value: str

    @root_validator
    def between_zero_and_one(cls, values):
        for key in values:
            if key != "value":
                if values[key] > 1 or values[key] < 0:
                    raise ValueError(
                        f"{key} must be greater or equal to zero and less than or equal to one."
                    )
        return values

    # @root_validator
    # def x0_less_than_x1(cls, values):
    #     if not coord0_less_than_coord1(values["x0"], values["x1"]):
    #         raise ValueError("x1 must be greater than x0")
    #     return values

    # @root_validator
    # def y0_less_than_y1(cls, values):
    #     if not coord0_less_than_coord1(values["y0"], values["y1"]):
    #         raise ValueError("y1 must be greater than y0")
    #     return values


# class Polygon(BaseModel):
#     pass


class Classification(BaseModel):
    model_name: str
    type: str
    value: str


class Objects(BaseModel):
    model_name: str
    type: str
    objects: List[BoundingBox]


class Prediction(BaseModel):
    id: str
    name: str
    confidence: float


class Predictions(BaseModel):
    prediction_set: List[Prediction]
    model_name: str


class Image(BaseModel):
    id: str
    uri: AnyUrl
    labels: Optional[List[Union[Classification, Objects]]]
    predictions: Optional[List[Predictions]]

    @ validator('uri')
    def check_valid_uri(cls, uri):
        legal_schemes = ['gs', 'http', 'https']
        if uri.scheme not in legal_schemes:
            raise ValueError(
                f'{uri} scheme must be one of {" ".join(legal_schemes)}'
            )

        return uri
