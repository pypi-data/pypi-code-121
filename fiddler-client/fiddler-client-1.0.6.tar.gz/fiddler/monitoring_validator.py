from datetime import datetime
from typing import List

from . import constants
from .core_objects import (
    DataType,
    EventTypes,
    FiddlerEventColumns,
    ModelInputType,
    ModelTask,
    MonitoringViolation,
    MonitoringViolationType,
)
from .utils.formatting import formatted_utcnow, pad_timestamp
from .utils.general_checks import is_int_type


class MonitoringValidator:
    def __init__(self):
        pass

    def pre_flight_monitoring_check(
        self, event, model_info, dataset_info
    ) -> List[MonitoringViolation]:

        violations = []
        # lets track all violations we can find. Its much better to find everything
        # wrong with the setup rather than error-ing out on each step and iterating
        # We only return immidiately if we have a FATAL violation

        violations += self._input_types_allowed(model_info)
        violations += self._basic_outputs_checks(model_info)

        violations += self._basic_decision_checks(model_info)
        violations += self._basic_monitoring_single_event_tests(
            dataset_info, model_info, event
        )
        violations += self._basic_data_integrity_checks(dataset_info)
        violations += self._basic_accuracy_checks(model_info)

        return violations

    def _input_types_allowed(self, model_info):
        violations = []
        for col in model_info.inputs:
            if (
                col.data_type != DataType.FLOAT
                and col.data_type != DataType.INTEGER
                and col.data_type != DataType.CATEGORY
            ):
                msg = f'Column {col.name} of type {col.data_type} is not allowed'
                violations.append(
                    MonitoringViolation(MonitoringViolationType.FATAL, msg)
                )

        return violations

    def _check_missing_inputs_outputs(self, dataset_info, model_info, event):
        """Lets make sure we get all not is_nullable features. Also, the outputs
        SHOULD be there in execution type event.
        """
        violations = []
        # We have to check nullability from the dataset info which is what the DI
        # checks are based on.
        input_col_types = {col.name: col for col in dataset_info.columns}
        for col in model_info.inputs:
            if (
                col.name not in event
                and input_col_types[col.name].is_nullable is not None
                and input_col_types[col.name].is_nullable is False
            ) and event[
                FiddlerEventColumns.EVENT_TYPE.value
            ] == EventTypes.EXECUTION_EVENT.value:
                msg = f'Input is_nullable error: `{col.name}` can not be missing'
                violations.append(
                    MonitoringViolation(MonitoringViolationType.WARNING, msg)
                )

        for col in model_info.outputs:
            if (
                col.name not in event
                and event[FiddlerEventColumns.EVENT_TYPE.value]
                == EventTypes.EXECUTION_EVENT.value
            ):

                msg = f'Output error: `{col.name}` can not be missing'
                violations.append(
                    MonitoringViolation(MonitoringViolationType.WARNING, msg)
                )

        return violations

    def _event_type_based_checks(self, model_info, event):
        violations = []
        if FiddlerEventColumns.EVENT_TYPE.value not in event:
            msg = 'Can not ingest event with missing event_type'
            violations.append(MonitoringViolation(MonitoringViolationType.FATAL, msg))
            return violations

        if event[FiddlerEventColumns.EVENT_TYPE.value] == EventTypes.UPDATE_EVENT.value:

            # We dont accept input/output with event_type = 'update_event'
            for col in model_info.inputs:
                if col.name in event.keys():
                    msg = f'Can not send inputs/features in update_event {col.name}'
                    violations.append(
                        MonitoringViolation(MonitoringViolationType.FATAL, msg)
                    )

            for col in model_info.outputs:
                if col.name in event.keys():
                    msg = f'Can not send outputs in update_event {col.name}'
                    violations.append(
                        MonitoringViolation(MonitoringViolationType.FATAL, msg)
                    )

        return violations

    def _check_event_timestamps(self, event):
        violations = []
        date_str = None
        # We are checking to see if event_type is present. Dont want to rely on event_type
        # being present.
        if (
            FiddlerEventColumns.EVENT_TYPE.value in event
            and event[FiddlerEventColumns.EVENT_TYPE.value]
            == EventTypes.EXECUTION_EVENT.value
        ):
            # __occurred_at has to be present for execution_event
            if (
                FiddlerEventColumns.OCCURRED_AT.value not in event
                or event[FiddlerEventColumns.OCCURRED_AT.value] is None
            ):
                msg = f'execution_events need to have `{FiddlerEventColumns.OCCURRED_AT.value}` included in the event'
                violations.append(
                    MonitoringViolation(MonitoringViolationType.FATAL, msg)
                )
            else:
                date_str = event[FiddlerEventColumns.OCCURRED_AT.value]

        if (
            FiddlerEventColumns.EVENT_TYPE.value in event
            and event[FiddlerEventColumns.EVENT_TYPE.value]
            == EventTypes.UPDATE_EVENT.value
        ):
            # __updated_at should be present for update_event
            if (
                FiddlerEventColumns.UPDATED_AT.value not in event
                or event[FiddlerEventColumns.UPDATED_AT.value] is None
            ):
                msg = f'update_events need to have `{FiddlerEventColumns.UPDATED_AT.value}` included in the event'
                violations.append(
                    MonitoringViolation(MonitoringViolationType.FATAL, msg)
                )
            else:
                date_str = event[FiddlerEventColumns.UPDATED_AT.value]

        if date_str is None:
            return violations

        # We expect either date to be in '%Y-%m-%d %H:%M:%S.%f' format or millisecs epoch.
        # Some can potentially send us date in millisecs for 1970. So its worth pointing
        # out if they intend to do that or its just a secs/millisecs problem.
        is_int, int_val = is_int_type(date_str)
        if is_int:
            t_stamp = formatted_utcnow(milliseconds=int_val)
            year = int(t_stamp.split('-')[0])
            if year < 1975:
                msg = f'Is your timestamp ({int_val}) in secs? Please change it to millisecs.'
                violations.append(
                    MonitoringViolation(MonitoringViolationType.WARNING, msg)
                )
        elif isinstance(date_str, str):
            try:
                ts = pad_timestamp(date_str)
                datetime.strptime(ts, constants.TIMESTAMP_FORMAT)
            except Exception:
                # lets check if its valid ms epoch time
                is_int, int_val = is_int_type(ts)
                msg = f'Unable to parse date:{date_str}. Specify date either in millisecs epoch or format:{constants.TIMESTAMP_FORMAT}'
                violations.append(
                    MonitoringViolation(MonitoringViolationType.FATAL, msg)
                )

        return violations

    def _basic_monitoring_single_event_tests(self, dataset_info, model_info, event):
        """These checks would currently apply to only publish_event function and not
        publish_events_log or parquet function. We can potentially convert the df row
        from publish_events_log to json and use this same function.
        However, that might not be the best way since we are not doing that transform on
        server side before ingestion. Once we have the ETL work done, we should figure
        out how to do a single transform to all incoming events (whether publish_events_log
        or publish_event) and use the same transform here before calling this function.
        """
        violations = []
        if event is None or not event:
            msg = 'No event passed'
            violations.append(MonitoringViolation(MonitoringViolationType.WARNING, msg))
            return violations

        violations += self._check_event_timestamps(event)

        violations += self._event_type_based_checks(model_info, event)

        all_cols = model_info.inputs + model_info.outputs + model_info.targets

        if model_info.decisions:
            all_cols += model_info.decisions
        if model_info.metadata:
            all_cols += model_info.metadata

        model_column_type = {}
        for col in all_cols:
            model_column_type[col.name] = col.data_type

        input_col_types = {col.name: col.data_type for col in model_info.inputs}
        fiddler_col_names = [col.value for col in FiddlerEventColumns]

        violations += self._check_missing_inputs_outputs(
            dataset_info, model_info, event
        )

        # lets check if dtype in events match model input schema
        for col_name, value in event.items():
            if col_name in fiddler_col_names:
                continue

            if col_name not in input_col_types.keys():
                continue

            value_dtype = type(value).__name__
            if input_col_types[col_name].is_numeric():
                if value_dtype == 'int' or value_dtype == 'float':
                    continue
                msg = f'Input dtype violation for {col_name}: Found {value_dtype} expected {input_col_types[col_name].value}'
                violations.append(
                    MonitoringViolation(MonitoringViolationType.WARNING, msg)
                )
            elif input_col_types[col_name] == DataType.CATEGORY:
                if value_dtype != 'str':
                    msg = f'Input dtype violation for {col_name}: Found {value_dtype} expected category (string).'
                    violations.append(
                        MonitoringViolation(MonitoringViolationType.WARNING, msg)
                    )
            else:
                if value_dtype != input_col_types[col_name].value:
                    msg = f'Input dtype violation for {col_name}: Found {value_dtype} expected {input_col_types[col_name].value}'
                    violations.append(
                        MonitoringViolation(MonitoringViolationType.WARNING, msg)
                    )

        # lets check if dtype in events match model output schema
        output_col_types = {col.name: col.data_type for col in model_info.outputs}
        for col_name, value in event.items():

            if col_name in fiddler_col_names:
                continue

            if col_name not in output_col_types.keys():
                continue

            value_dtype = type(value).__name__
            if value_dtype != output_col_types[col_name].value:
                msg = f'Output dtype violation for {col_name}: Found {value_dtype} expected {output_col_types[col_name].value}'
                violations.append(
                    MonitoringViolation(MonitoringViolationType.WARNING, msg)
                )

        return violations

    def _basic_decision_checks(self, model_info):
        # TODO: add a check for decision in the event matching dtype mentioned in the model
        violations = []
        if model_info.decisions:
            for col in model_info.decisions:
                if col.data_type != DataType.CATEGORY:
                    msg = 'Decision column can only be of type category'
                    violations.append(
                        MonitoringViolation(MonitoringViolationType.WARNING, msg)
                    )
        return violations

    def _basic_outputs_checks(self, model_info):
        violations = []
        for col in model_info.outputs:
            if not col.data_type.is_numeric():
                msg = 'Model outputs can ONLY be numeric'
                violations.append(
                    MonitoringViolation(MonitoringViolationType.WARNING, msg)
                )
        return violations

    def _basic_data_integrity_checks(self, dataset_info):
        # Lets make sure dataset_info has stats present
        violations = []
        for col in dataset_info.columns:
            if col.is_nullable is None or not hasattr(col, 'is_nullable'):
                msg = f'Data integrity error: {col.name} doesnt have is_nullable'
                violations.append(
                    MonitoringViolation(MonitoringViolationType.WARNING, msg)
                )

            if col.data_type.is_numeric():
                if col.value_range_min is None or not hasattr(col, 'value_range_min'):
                    msg = (
                        f'Data integrity error: {col.name} doesnt have value_range_min'
                    )
                    violations.append(
                        MonitoringViolation(MonitoringViolationType.WARNING, msg)
                    )

                if col.value_range_max is None or not hasattr(col, 'value_range_max'):
                    msg = (
                        f'Data integrity error: {col.name} doesnt have value_range_max'
                    )
                    violations.append(
                        MonitoringViolation(MonitoringViolationType.WARNING, msg)
                    )

        return violations

    def _basic_accuracy_checks(self, model_info):
        violations = []

        # We currently only support Tabular data for monitoring
        if model_info.input_type != ModelInputType.TABULAR:
            msg = f'Model:{model_info.display_name} type:{model_info.input_type} is not supported. Monitoring currently only supports {ModelInputType.TABULAR.value}'
            violations.append(MonitoringViolation(MonitoringViolationType.FATAL, msg))

        for col in model_info.outputs:
            if col.data_type != DataType.FLOAT:
                msg = f'Accuracy metrics can only be computed for models which have floating point output columns:{col.name}'
                violations.append(
                    MonitoringViolation(MonitoringViolationType.WARNING, msg)
                )

        if model_info.model_task == ModelTask.BINARY_CLASSIFICATION:
            if model_info.targets[0].data_type not in [
                DataType.FLOAT,
                DataType.INTEGER,
                DataType.BOOLEAN,
                DataType.CATEGORY,
            ]:
                msg = f'Target columns can only be one of `FLOAT`, `INTEGER`, `BOOLEAN`, or `CATEGORY` for model type:{ModelTask.BINARY_CLASSIFICATION.value}'
                violations.append(
                    MonitoringViolation(MonitoringViolationType.WARNING, msg)
                )
            if model_info.targets[0].possible_values is not None:
                for value in model_info.targets[0].possible_values:
                    if (
                        not isinstance(value, str)
                        and not isinstance(value, float)
                        and not isinstance(value, bool)
                        and not isinstance(value, int)
                    ):
                        msg = f'Accuracy only works if possible values for target/label columns are strings, floats, integers, or booleans. Current target possible values are {model_info.targets[0].possible_values}'
                        violations.append(
                            MonitoringViolation(MonitoringViolationType.WARNING, msg)
                        )
                        # no need at add a warning for each possible value
                        break

        if model_info.model_task == ModelTask.MULTICLASS_CLASSIFICATION:
            if model_info.targets[0].data_type != DataType.CATEGORY:
                msg = f'Target columns can only be categories for model type:{model_info.model_task.value}'
                violations.append(
                    MonitoringViolation(MonitoringViolationType.WARNING, msg)
                )
            if model_info.targets[0].possible_values is not None:
                msg = f'Accuracy will only work if the targets for Multiclass model can point to the winning output probability. For your case, the target possible values should be {list(range(len(model_info.outputs)))}'
                # lets make sure that possible values cover the range of outputs
                # If there are three outputs probs, then target possible values = [0, 1, 2]
                int_target_vals = None
                try:
                    int_target_vals = set(
                        [int(c) for c in model_info.targets[0].possible_values]
                    )
                except ValueError:
                    violations.append(
                        MonitoringViolation(MonitoringViolationType.WARNING, msg)
                    )
                if int_target_vals is not None and not (
                    len(int_target_vals) == len(model_info.outputs)
                    and set(int_target_vals) == set(range(len(model_info.outputs)))
                ):
                    violations.append(
                        MonitoringViolation(MonitoringViolationType.WARNING, msg)
                    )

        return violations
