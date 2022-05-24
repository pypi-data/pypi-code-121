from unittest.mock import MagicMock, patch

from chaosreliably.controls import experiment
from chaosreliably.types import EventType


@patch("chaosreliably.controls.experiment.create_run_event")
@patch("chaosreliably.controls.experiment.complete_experiment")
@patch("chaosreliably.controls.experiment.complete_run")
def test_after_experiment_control_calls_create_experiment_event(
    mock_complete_run: MagicMock,
    mock_complete_experiment: MagicMock,
    mock_create_run_event: MagicMock,
) -> None:
    refs = experiment.populate_event_refs()
    configuration = {"chaosreliably": {"run_ref": "run-123", "refs": refs}}
    journal = {
        "chaoslib-version": None,
        "platform": None,
        "node": None,
        "experiment": None,
        "start": None,
        "status": None,
        "deviated": None,
        "steady_states": None,
        "run": None,
        "rollbacks": None,
        "end": None,
        "duration": None,
    }
    x = {"title": "hello"}

    experiment.after_experiment_control(
        context=x,
        experiment_ref="XYZ",
        state=journal,
        configuration=configuration,
        secrets=None,
    )

    mock_create_run_event.assert_called_once_with(
        experiment_ref="XYZ",
        run_ref="run-123",
        event_ref=refs["experiment"],
        event_type=EventType.EXPERIMENT_END,
        experiment=x,
        output=journal,
        title="hello",
        experiment_run_labels={"experiment_run_ref": "run-123"},
        configuration=configuration,
        secrets=None,
    )

    mock_complete_experiment.assert_called_once_with(
        "XYZ",
        journal,
        configuration,
        None,
    )

    mock_complete_run.assert_called_once_with(
        "run-123",
        x,
        journal,
        configuration,
        None,
    )


@patch("chaosreliably.controls.experiment.logger")
@patch("chaosreliably.controls.experiment.create_run_event", autospec=True)
def test_than_an_exception_does_not_get_raised_and_warning_logged(
    mock_create_run_event: MagicMock,
    mock_logger: MagicMock,
) -> None:
    configuration = {
        "chaosreliably": {
            "run_ref": "run-123",
            "refs": experiment.populate_event_refs(),
        }
    }
    x = {}  # type: ignore
    journal = {}  # type: ignore

    mock_create_run_event.side_effect = Exception("'chaosreliably'")
    experiment.after_experiment_control(
        context=x,
        experiment_ref="XYZ",
        state=journal,
        configuration=configuration,
        secrets=None,
    )

    mock_logger.debug.assert_called_once_with(
        "An error occurred: 'chaosreliably', while running the After Experiment"
        " control, the Experiment execution won't be affected.",
        exc_info=True,
    )
