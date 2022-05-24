from unittest.mock import MagicMock, patch

from chaosreliably.controls import experiment
from chaosreliably.types import EventType


@patch("chaosreliably.controls.experiment.create_run_event")
def test_after_hypothesis_control_calls_create_run_event(
    mock_create_run_event: MagicMock,
) -> None:
    refs = experiment.populate_event_refs()
    hypo_ref = refs["hypo"]
    configuration = {"chaosreliably": {"run_ref": "run-123", "refs": refs}}
    ssh = {}  # type: ignore
    state = {}  # type: ignore
    x = {}  # type: ignore

    experiment.after_hypothesis_control(
        context=ssh,
        experiment=x,
        experiment_ref="XYZ",
        state=state,
        configuration=configuration,
        secrets=None,
    )

    mock_create_run_event.assert_called_once_with(
        "XYZ",
        "run-123",
        event_ref=hypo_ref,
        event_type=EventType.HYPOTHESIS_END,
        experiment=x,
        output=state,
        title="Steady-State Hypothesis",
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
    ssh = {}  # type: ignore
    state = {}  # type: ignore
    x = {}  # type: ignore

    mock_create_run_event.side_effect = Exception("'chaosreliably'")
    experiment.after_hypothesis_control(
        context=ssh,
        experiment=x,
        experiment_ref="XYZ",
        state=state,
        configuration=configuration,
        secrets=None,
    )
    mock_logger.debug.assert_called_once_with(
        "An error occurred: 'chaosreliably', while running the After "
        "Hypothesis control, the Experiment execution won't be affected.",
        exc_info=True,
    )
