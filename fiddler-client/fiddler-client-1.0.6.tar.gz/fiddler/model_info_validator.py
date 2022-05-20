from fiddler.core_objects import (
    DatasetInfo,
    DataType,
    ModelInfo,
    ModelInputType,
    ModelTask,
)


class ModelInfoValidator:
    def __init__(self, model_info: ModelInfo, dataset_info: DatasetInfo):
        self.model_info = model_info
        self.dataset_info = dataset_info

    def validate_categoricals(self, modify=False):
        for col in self.model_info.inputs:
            possible_values_floats = None
            if col.data_type == DataType.CATEGORY.value:
                try:
                    possible_values_floats = [
                        str(float(raw_val)) for raw_val in col.possible_values
                    ]
                except ValueError:
                    pass
            if possible_values_floats is not None:
                if not modify:
                    for f_val, c_val in zip(
                        possible_values_floats, col.possible_values
                    ):
                        if str(f_val) != str(c_val):
                            raise ValueError(
                                f'Categoricals have invalid values: {f_val} != {c_val}'
                            )
                else:
                    col.possible_values = possible_values_floats

    def validate(self):
        if self.model_info.input_type != ModelInputType.TABULAR:
            raise ValueError('Only tabular models supported')

        if not self.model_info.targets:
            raise ValueError('Target not specified')

        if len(self.model_info.targets) != 1:
            raise ValueError('More than one target specified')

        if len(self.model_info.inputs) < 1:
            raise ValueError('Input features not specified')

        if len(self.model_info.outputs) < 1:
            raise ValueError('Model outputs not defined')

        if self.model_info.model_task == ModelTask.REGRESSION:
            self.validate_regression_model()
        elif self.model_info.model_task == ModelTask.BINARY_CLASSIFICATION:
            self.validate_binary_classification_model()
        elif self.model_info.model_task == ModelTask.MULTICLASS_CLASSIFICATION:
            self.validate_multiclass_classification()
        elif self.model_info.model_task == ModelTask.RANKING:
            self.validate_ranking()
        else:
            raise ValueError('unsupported model task')

    def validate_regression_model(self):
        if len(self.model_info.outputs) != 1:
            raise ValueError('only one model output can be specified')
        if self.model_info.outputs[0].data_type != DataType.FLOAT:
            raise ValueError('model output must be of type FLOAT')

    def validate_binary_classification_model(self):
        if len(self.model_info.outputs) != 1:
            raise ValueError('only one model output can be specified')
        if self.model_info.outputs[0].data_type != DataType.FLOAT:
            raise ValueError('model output must be of type FLOAT')
        if self.model_info.targets[0].data_type == DataType.STRING:
            raise ValueError(
                'Target cannot be of type string. Please review dataset schema to be type category.'
            )
        if (
            self.model_info.targets[0].data_type
            in [DataType.CATEGORY, DataType.BOOLEAN]
        ) and (len(self.model_info.targets[0].possible_values) != 2):
            raise ValueError('target must have two possible values')

    def validate_multiclass_classification(self):
        if len(self.model_info.outputs) < 1:
            raise ValueError('model output should be more than one')
        for item in self.model_info.outputs:
            if item.data_type != DataType.FLOAT:
                raise ValueError(
                    f'model output "{item.name}" ' f'must be of type FLOAT'
                )
        if self.model_info.targets[0].data_type == DataType.STRING:
            raise ValueError(
                'Target cannot be of type string. Please review dataset schema to be type category.'
            )
        if (
            self.model_info.targets[0].data_type
            in [DataType.CATEGORY, DataType.BOOLEAN]
        ) and (
            len(self.model_info.targets[0].possible_values)
            != len(self.model_info.outputs)
        ):
            raise ValueError(
                f'possible values in target does not match model '
                f'outputs target: {self.model_info.targets[0]} '
                f'outputs: {self.model_info.outputs} '
            )

    def validate_ranking(self):
        if len(self.model_info.outputs) != 1:
            raise ValueError('only one model output can be specified')
        if self.model_info.outputs[0].data_type != DataType.FLOAT:
            raise ValueError('model output must be of type FLOAT')
        if self.model_info.targets[0].data_type == DataType.STRING:
            raise ValueError(
                'Target cannot be of type string. Please review dataset schema.'
            )
