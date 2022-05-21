# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azure.ai.ml._restclient.v2022_02_01_preview.models import (
    ClassificationMultilabelPrimaryMetrics,
    TaskType,
)
from azure.ai.ml.constants import AutoMLConstants
from azure.ai.ml._schema.core.fields import fields, StringTransformedEnum
from azure.ai.ml._schema.automl.nlp_vertical.nlp_vertical import NlpVerticalSchema
from azure.ai.ml._utils.utils import camel_to_snake
from marshmallow import post_load


class TextClassificationMultilableSchema(NlpVerticalSchema):
    task_type = StringTransformedEnum(
        allowed_values=TaskType.TEXT_CLASSIFICATION_MULTILABEL,
        casing_transform=camel_to_snake,
        data_key=AutoMLConstants.TASK_TYPE_YAML,
        required=True,
    )
    primary_metric = StringTransformedEnum(
        allowed_values=ClassificationMultilabelPrimaryMetrics.ACCURACY,
        casing_transform=camel_to_snake,
        load_default=camel_to_snake(ClassificationMultilabelPrimaryMetrics.ACCURACY),
    )
    # added here as for text_ner target_column_name is optional
    target_column_name = fields.Str(required=True)

    @post_load
    def make(self, data, **kwargs) -> "TextClassificationMultilabelJob":
        from azure.ai.ml.entities._job.automl.nlp import TextClassificationMultilabelJob

        data.pop("task_type")
        return TextClassificationMultilabelJob(**data)
