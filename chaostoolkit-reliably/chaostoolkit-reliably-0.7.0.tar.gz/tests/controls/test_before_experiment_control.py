from unittest.mock import ANY, MagicMock, patch

from chaosreliably.controls import experiment
from chaosreliably.types import (
    ExperimentEntity,
    ExperimentLabels,
    ExperimentMetadata,
)


@patch("chaosreliably.controls.experiment.create_run_event")
@patch("chaosreliably.controls.experiment.mark_experiment_as_running")
@patch("chaosreliably.controls.experiment.create_run")
@patch("chaosreliably.controls.experiment.get_experiment")
def test_before_experiment_control_does_not_call_create_experiment_event(
    mock_get_experiment: MagicMock,
    mock_create_run: MagicMock,
    mock_mark_experiment_as_running: MagicMock,
    mock_create_run_event: MagicMock,
) -> None:
    configuration = {}  # type: ignore
    x = {}  # type: ignore

    mock_get_experiment.return_value = ExperimentEntity(
        metadata=ExperimentMetadata(
            labels=ExperimentLabels(ref="XYZ"),
        )
    )
    experiment.before_experiment_control(
        context=x,
        experiment_ref="XYZ",
        configuration=configuration,
        secrets=None,
    )

    mock_create_run.assert_called_once_with(
        "XYZ",
        ANY,
        x,
        {"experiment_ref": "XYZ"},
        configuration,
        None,
    )


@patch("chaosreliably.controls.experiment.create_run_event")
@patch("chaosreliably.controls.experiment.create_experiment")
@patch("chaosreliably.controls.experiment.create_run")
@patch("chaosreliably.controls.experiment.get_experiment")
def test_before_experiment_control_calls_create_experiment_even(
    mock_get_experiment: MagicMock,
    mock_create_run: MagicMock,
    mock_create_experiment: MagicMock,
    mock_create_run_event: MagicMock,
) -> None:
    configuration = {}  # type: ignore
    x = {}  # type: ignore

    mock_get_experiment.return_value = None
    experiment.before_experiment_control(
        context=x,
        experiment_ref="XYZ",
        configuration=configuration,
        secrets=None,
    )

    mock_create_experiment.assert_called_once_with(
        "XYZ", x, configuration, None, []
    )

    mock_create_run.assert_called_once_with(
        "XYZ",
        ANY,
        x,
        {"experiment_ref": "XYZ"},
        configuration,
        None,
    )


@patch("chaosreliably.controls.experiment.logger")
@patch("chaosreliably.controls.experiment.get_experiment", autospec=True)
def test_than_an_exception_does_not_get_raised_and_warning_logged(
    mock_get_experiment: MagicMock,
    mock_logger: MagicMock,
) -> None:
    configuration = {
        "chaosreliably": {
            "run_ref": "run-123",
            "refs": experiment.populate_event_refs(),
        }
    }
    x = {}  # type: ignore

    mock_get_experiment.side_effect = Exception("'chaosreliably'")
    experiment.before_experiment_control(
        context=x,
        experiment_ref="XYZ",
        configuration=configuration,
        secrets=None,
    )

    mock_logger.debug.assert_called_once_with(
        "An error occurred: 'chaosreliably', whilst running the Before "
        "Experiment control, no further entities will be created, the "
        "Experiment execution won't be affected",
        exc_info=True,
    )
