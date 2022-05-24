from unittest.mock import MagicMock, patch

from chaosreliably.controls import experiment
from chaosreliably.types import EventType


@patch("chaosreliably.controls.experiment.create_run_event")
def test_after_method_control_calls_create_run_event(
    mock_create_run_event: MagicMock,
) -> None:
    refs = experiment.populate_event_refs()
    configuration = {"chaosreliably": {"run_ref": "run-123", "refs": refs}}
    method = []  # type: ignore
    state = []  # type: ignore
    x = {}  # type: ignore

    experiment.after_method_control(
        context=method,
        experiment=x,
        experiment_ref="XYZ",
        state=state,
        configuration=configuration,
        secrets=None,
    )

    mock_create_run_event.assert_called_once_with(
        "XYZ",
        "run-123",
        refs["method"],
        event_type=EventType.METHOD_END,
        experiment=x,
        output=state,
        title="Method",
        experiment_run_labels={"experiment_run_ref": "run-123"},
        configuration=configuration,
        secrets=None,
    )


@patch("chaosreliably.controls.experiment.logger")
@patch("chaosreliably.controls.experiment.create_run_event", autospec=True)
def test_that_an_exception_does_not_get_raised_and_warning_logged(
    mock_create_run_event: MagicMock,
    mock_logger: MagicMock,
) -> None:
    configuration = {
        "chaosreliably": {
            "run_ref": "run-123",
            "refs": experiment.populate_event_refs(),
        }
    }
    method = []  # type: ignore
    state = []  # type: ignore
    x = {}  # type: ignore

    mock_create_run_event.side_effect = Exception("'chaosreliably'")
    experiment.after_method_control(
        context=method,
        experiment=x,
        experiment_ref="XYZ",
        state=state,
        configuration=configuration,
        secrets=None,
    )
    mock_logger.debug.assert_called_once_with(
        "An error occurred: 'chaosreliably', while running the After "
        "Method control, the Experiment execution won't be affected.",
        exc_info=True,
    )
