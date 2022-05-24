import secrets as secrets_module
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Type, Union, cast

from chaoslib.exceptions import InvalidControl
from chaoslib.types import (
    Activity,
    Configuration,
    Control,
    Experiment,
    Hypothesis,
    Journal,
    Run,
    Secrets,
)
from logzero import logger

from chaosreliably import encoded_selector, get_session
from chaosreliably.types import (
    EventType,
    ExperimentEntity,
    ExperimentLabels,
    ExperimentMetadata,
    ExperimentRunEntity,
    ExperimentRunEventEntity,
    ExperimentRunEventLabels,
    ExperimentRunEventMetadata,
    ExperimentRunEventSpec,
    ExperimentRunLabels,
    ExperimentRunMetadata,
    ExperimentRunSpec,
    ExperimentSpec,
)

__all__ = [
    "after_activity_control",
    "after_experiment_control",
    "after_hypothesis_control",
    "after_method_control",
    "after_rollback_control",
    "before_activity_control",
    "before_experiment_control",
    "before_hypothesis_control",
    "before_method_control",
    "before_rollback_control",
]


def validate_control(control: Control) -> None:
    """
    Ensures the control defines an identifier for the experiment. It will
    be more stable than the title.
    """
    xid = control.get("provider", {}).get("arguments", {}).get("experiment_ref")
    if not xid:
        raise InvalidControl(
            "\nThe `chaostoolkit-reliably` control expects an argument called "
            "`experiment_ref`.\nIt can be any random string which must remain "
            "stable across time."
        )


def before_experiment_control(
    context: Experiment,
    experiment_ref: str,
    configuration: Configuration = None,
    secrets: Secrets = None,
    **kwargs: Any,
) -> None:
    """
    Control run *before* the execution of an Experiment.

    For a given Experiment, the control creates (if not already created) an
    Experiment

    Entity Context and an Experiment Version Entity Context in the Reliably
    service.

    A unique Experiment Run Entity Context is also created, with an Experiment
    Event. Entity Context of type `EXPERIMENT_START` created, relating to the
    run.

    The control requires the `arguments` of `commit_hash`, `source`, and `user`
    to be provided to the control definition. If not provided, the control will
    simply not create any Entity Contexts.

    Once the Entity Contexts have been created, an entry into the configuration
    is made under configuration["chaosreliably"]["experiment_run_labels"] to
    allow for other controls to create events relating to the Experiment Run.

    :param context: Experiment object representing the Experiment that will be
        executed
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :param **kwargs: Expected required `kwargs` are 'commit_hash' (str),
        `source` (str), and `user` (str), optional is
        `experiment_related_to_labels` (List[Dict[str, str]]) representing
        labels of entities the Experiment relates to

    ```json
    {
        "controls": [
            {
                "name": "chaosreliably",
                "provider": {
                    "type": "python",
                    "module": "chaosreliably.controls.experiment",
                    "arguments": {
                        "experiment_ref": "xyz1234"
                    }
                }
            }
        ]
    }
    ```
    """
    try:
        reliably_secrets = secrets.get("reliably", None) if secrets else None

        run_ref = secrets_module.token_hex(8)
        configuration.update(
            {
                "chaosreliably": {
                    "experiment_ref": experiment_ref,
                    "run_ref": run_ref,
                    "start_time": datetime.utcnow()
                    .replace(tzinfo=timezone.utc)
                    .isoformat(),
                    "refs": populate_event_refs(),
                }
            }
        )

        x = get_experiment(experiment_ref, configuration, reliably_secrets)
        if not x:
            logger.debug(
                "Experiment does not yet exist in Reliably, creating it now"
            )
            labels = collect_all_objective_labels(context)
            create_experiment(
                experiment_ref, context, configuration, reliably_secrets, labels
            )
        else:
            mark_experiment_as_running(
                x, context, configuration, reliably_secrets
            )

        logger.debug(f"Creating experiment run with reference: {run_ref}")
        create_run(
            experiment_ref,
            run_ref,
            context,
            {"experiment_ref": experiment_ref},
            configuration,
            reliably_secrets,
        )

        create_run_event(
            experiment_ref,
            run_ref,
            event_ref=configuration["chaosreliably"]["refs"]["experiment"],
            event_type=EventType.EXPERIMENT_START,
            experiment=context,
            output=None,
            title=context.get("title"),
            experiment_run_labels={"experiment_run_ref": run_ref},
            configuration=configuration,
            secrets=reliably_secrets,
        )

    except Exception as ex:
        logger.debug(
            f"An error occurred: {ex}, whilst running the Before Experiment "
            "control, no further entities will be created, the Experiment "
            "execution won't be affected",
            exc_info=True,
        )


def after_experiment_control(
    context: Experiment,
    experiment_ref: str,
    state: Journal,
    configuration: Configuration = None,
    secrets: Secrets = None,
    **kwargs: Any,
) -> None:
    """
    Control run *after* the execution of an Experiment.

    For a given Experiment and its state in Journal form, the control creates an
    Experiment Event Entity Context in the Reliably service.

    The Event has the `event_type` of `EXPERIMENT_END`

    :param context: Experiment object representing the Experiment that was
        executed
    :param state: Journal object representing the state of the Experiment after
        execution
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :param **kwargs: Any additional keyword arguments passed to the control
    """
    try:
        reliably_secrets = secrets.get("reliably", None) if secrets else None

        c = configuration["chaosreliably"]
        run_ref = c["run_ref"]

        create_run_event(
            experiment_ref=experiment_ref,
            run_ref=run_ref,
            event_ref=c["refs"]["experiment"],
            event_type=EventType.EXPERIMENT_END,
            experiment=context,
            output=state,
            title=context.get("title"),
            experiment_run_labels={
                "experiment_run_ref": configuration["chaosreliably"]["run_ref"]
            },
            configuration=configuration,
            secrets=reliably_secrets,
        )
        complete_experiment(experiment_ref, state, configuration, secrets)

        complete_run(run_ref, context, state, configuration, secrets)
    except Exception as ex:
        logger.debug(
            f"An error occurred: {ex}, while running the After Experiment "
            "control, the Experiment execution won't be affected.",
            exc_info=True,
        )


def before_hypothesis_control(
    context: Hypothesis,
    experiment: Experiment,
    experiment_ref: str,
    configuration: Configuration = None,
    secrets: Secrets = None,
    **kwargs: Any,
) -> None:
    """
    Control run *before* the execution of an Experiments Steady State
    Hypothesis.

    For a given Steady State Hypothesis, the control creates an Experiment
    Event Entity
    Context in the Reliably service.

    The Event has the `event_type` of `HYPOTHESIS_START`.

    :param context: Hypothesis object representing the Steady State Hypothesis
        that is to be executed
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :param **kwargs: Any additional keyword arguments passed to the control
    """
    try:
        reliably_secrets = secrets.get("reliably", None) if secrets else None

        c = configuration["chaosreliably"]
        run_ref = c["run_ref"]

        create_run_event(
            experiment_ref,
            run_ref,
            c["refs"]["hypo"],
            event_type=EventType.HYPOTHESIS_START,
            experiment=experiment,
            output=None,
            title="Steady-State Hypothesis",
            experiment_run_labels={"experiment_run_ref": run_ref},
            configuration=configuration,
            secrets=reliably_secrets,
        )
    except Exception as ex:
        logger.debug(
            f"An error occurred: {ex}, while running the Before Hypothesis "
            "control, the Experiment execution won't be affected.",
            exc_info=True,
        )


def after_hypothesis_control(
    context: Hypothesis,
    experiment: Experiment,
    state: Dict[str, Any],
    experiment_ref: str,
    configuration: Configuration = None,
    secrets: Secrets = None,
    **kwargs: Any,
) -> None:
    """
    Control run *after* the execution of an Experiments Steady State
    Hypothesis.

    For a given Steady State Hypothesis and its state, post execution, the
    control creates an Experiment Event Entity Context in the Reliably service.

    The Event has the `event_type` of `HYPOTHESIS_END`.

    :param context: Hypothesis object representing the Steady State Hypothesis
        that has been executed
    :param state: Dict[str, Any] representing the output of
        `run_steady_state_hypothesis` in `chaoslib`
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :param **kwargs: Any additional keyword arguments passed to the control
    """
    try:
        reliably_secrets = secrets.get("reliably", None) if secrets else None

        c = configuration["chaosreliably"]
        run_ref = c["run_ref"]
        hypo_ref = c["refs"]["hypo"]
        # hypothesis can run many times, we need to differentiate them
        c["refs"]["hypo"] = secrets_module.token_hex(8)

        create_run_event(
            experiment_ref,
            run_ref,
            event_ref=hypo_ref,
            event_type=EventType.HYPOTHESIS_END,
            experiment=experiment,
            output=state,
            title="Steady-State Hypothesis",
            experiment_run_labels={"experiment_run_ref": run_ref},
            configuration=configuration,
            secrets=reliably_secrets,
        )
    except Exception as ex:
        logger.debug(
            f"An error occurred: {ex}, while running the After Hypothesis "
            "control, the Experiment execution won't be affected.",
            exc_info=True,
        )


def before_method_control(
    context: Experiment,
    experiment: Experiment,
    experiment_ref: str,
    configuration: Configuration = None,
    secrets: Secrets = None,
    **kwargs: Any,
) -> None:
    """
    Control run *before* the execution of an Experiments Method.

    For a given Experiment, the control creates an Experiment Event Entity
    Context in the Reliably service.

    The Event has the `event_type` of `METHOD_START`.

    :param context: Experiment object representing the Experiment that will be
        executed
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :param **kwargs: Any additional keyword arguments passed to the control
    """
    try:
        reliably_secrets = secrets.get("reliably", None) if secrets else None
        run_ref = configuration["chaosreliably"]["run_ref"]

        c = configuration["chaosreliably"]
        run_ref = c["run_ref"]

        create_run_event(
            experiment_ref,
            run_ref,
            c["refs"]["method"],
            event_type=EventType.METHOD_START,
            experiment=experiment,
            output=None,
            title="Method",
            experiment_run_labels={"experiment_run_ref": run_ref},
            configuration=configuration,
            secrets=reliably_secrets,
        )
    except Exception as ex:
        logger.debug(
            f"An error occurred: {ex}, while running the Before Method "
            "control, the Experiment execution won't be affected.",
            exc_info=True,
        )


def after_method_control(
    context: Experiment,
    experiment: Experiment,
    state: List[Run],
    experiment_ref: str,
    configuration: Configuration = None,
    secrets: Secrets = None,
    **kwargs: Any,
) -> None:
    """
    Control run *after* the execution of an Experiments Method.

    For a given Experiment Method and its state, the control creates an
    Experiment
    Event Entity Context in the Reliably service.

    The Event has the `event_type` of `METHOD_END`.

    :param context: Experiment object representing the Experiment that will be
        executed
    :param state: List[Run] object presenting the executed Activities within
        the Experiments Method
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :param **kwargs: Any additional keyword arguments passed to the control
    """
    try:
        reliably_secrets = secrets.get("reliably", None) if secrets else None

        c = configuration["chaosreliably"]
        run_ref = c["run_ref"]

        create_run_event(
            experiment_ref,
            run_ref,
            c["refs"]["method"],
            event_type=EventType.METHOD_END,
            experiment=experiment,
            output=state,
            title="Method",
            experiment_run_labels={"experiment_run_ref": run_ref},
            configuration=configuration,
            secrets=reliably_secrets,
        )
    except Exception as ex:
        logger.debug(
            f"An error occurred: {ex}, while running the After Method "
            "control, the Experiment execution won't be affected.",
            exc_info=True,
        )


def before_rollback_control(
    context: Experiment,
    experiment: Experiment,
    experiment_ref: str,
    configuration: Configuration = None,
    secrets: Secrets = None,
    **kwargs: Any,
) -> None:
    """
    Control run *before* the execution of an Experiments Rollback.

    For a given Experiment, the control creates an Experiment Event Entity
    Context in the Reliably service.

    The Event has the `event_type` of `ROLLBACK_START`.

    :param context: Experiment object representing the Experiment that will be
        executed
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :param **kwargs: Any additional keyword arguments passed to the control
    """
    try:
        reliably_secrets = secrets.get("reliably", None) if secrets else None

        c = configuration["chaosreliably"]
        run_ref = c["run_ref"]

        create_run_event(
            experiment_ref,
            run_ref,
            c["refs"]["rollback"],
            event_type=EventType.ROLLBACK_START,
            experiment=experiment,
            output=None,
            title="Rollbacks",
            experiment_run_labels={"experiment_run_ref": run_ref},
            configuration=configuration,
            secrets=reliably_secrets,
        )
    except Exception as ex:
        logger.debug(
            f"An error occurred: {ex}, while running the Before Rollback "
            "control, the Experiment execution won't be affected.",
            exc_info=True,
        )


def after_rollback_control(
    context: Experiment,
    experiment: Experiment,
    state: List[Run],
    experiment_ref: str,
    configuration: Configuration = None,
    secrets: Secrets = None,
    **kwargs: Any,
) -> None:
    """
    Control run *after* the execution of an Experiments Rollback.

    For a given Experiment Rollback and its state, the control creates an
    Experiment
    Event Entity Context in the Reliably service.

    The Event has the `event_type` of `ROLLBACK_END`.

    :param context: Experiment object representing the Experiment that will be
        executed
    :param state: List[Run] object presenting the executed Activities within
        the Experiments Rollback
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :param **kwargs: Any additional keyword arguments passed to the control
    """
    try:
        reliably_secrets = secrets.get("reliably", None) if secrets else None

        c = configuration["chaosreliably"]
        run_ref = c["run_ref"]

        create_run_event(
            experiment_ref,
            run_ref,
            event_ref=c["refs"]["rollback"],
            event_type=EventType.ROLLBACK_END,
            experiment=experiment,
            output=state,
            title="Rollbacks",
            experiment_run_labels={
                "experiment_run_ref": configuration["chaosreliably"]["run_ref"]
            },
            configuration=configuration,
            secrets=reliably_secrets,
        )
    except Exception as ex:
        logger.debug(
            f"An error occurred: {ex}, while running the After Rollback "
            "control, the Experiment execution won't be affected.",
            exc_info=True,
        )


def before_activity_control(
    context: Activity,
    experiment: Experiment,
    experiment_ref: str,
    configuration: Configuration = None,
    secrets: Secrets = None,
    **kwargs: Any,
) -> None:
    """
    Control run *before* the execution of an Experiment Activity.

    For a given Experiment Activity, the control creates an Experiment Event
    Entity Context in the Reliably service.

    The Event has the `event_type` of `ACTIVITY_START`.

    :param context: Activity object representing the Experiment Activity
        that will be executed
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :param **kwargs: Any additional keyword arguments passed to the control
    """
    try:
        reliably_secrets = secrets.get("reliably", None) if secrets else None

        c = configuration["chaosreliably"]
        run_ref = c["run_ref"]
        c["refs"]["activity"] = secrets_module.token_hex(8)

        create_run_event(
            experiment_ref,
            run_ref,
            c["refs"]["activity"],
            event_type=EventType.ACTIVITY_START,
            experiment=experiment,
            output=None,
            title=f"Activity {context.get('name')}",
            experiment_run_labels={"experiment_run_ref": run_ref},
            configuration=configuration,
            secrets=reliably_secrets,
        )
    except Exception as ex:
        logger.debug(
            f"An error occurred: {ex}, while running the Before Activity "
            "control, the Experiment execution won't be affected.",
            exc_info=True,
        )


def after_activity_control(
    context: Activity,
    experiment: Experiment,
    state: Run,
    experiment_ref: str,
    configuration: Configuration = None,
    secrets: Secrets = None,
    **kwargs: Any,
) -> None:
    """
    Control run *after* the execution of an Experiment Activity.

    For a given Experiment Activity and its state, the control creates an "
    Experiment Event Entity Context in the Reliably service.

    The Event has the `event_type` of `ACTIVITY_END`.

    :param context: Activity object representing the Experiment Activity
        that was executed
    :param state: Run object representing the state of the executed Experiment
        Activity
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    :param **kwargs: Any additional keyword arguments passed to the control
    """
    try:
        reliably_secrets = secrets.get("reliably", None) if secrets else None

        c = configuration["chaosreliably"]
        run_ref = c["run_ref"]

        create_run_event(
            experiment_ref,
            run_ref,
            event_ref=c["refs"]["activity"],
            event_type=EventType.ACTIVITY_END,
            experiment=experiment,
            output=state,
            title=context.get("name"),
            experiment_run_labels={
                "experiment_run_ref": configuration["chaosreliably"]["run_ref"]
            },
            configuration=configuration,
            secrets=reliably_secrets,
        )
    except Exception as ex:
        logger.debug(
            f"An error occurred: {ex}, while running the After Activity "
            "control, the Experiment execution won't be affected.",
            exc_info=True,
        )


###############################################################################
# Private functions
###############################################################################
def collect_all_objective_labels(
    experiment: Experiment,
) -> List[Dict[str, str]]:
    probes = experiment.get("steady-state-hypothesis", {}).get("probes", [])
    labels = []
    for probe in probes:
        p = probe["provider"]
        if p["module"] == "chaosreliably.slo.probes":
            a = p.get("arguments", {}).get("labels")
            if a:
                labels.append(a.copy())
    return labels


def get_entity(
    endpoint: str,
    qs: Dict[str, str],
    entity_type: Union[Type[ExperimentEntity], Type[ExperimentRunEntity]],
    configuration: Configuration,
    secrets: Secrets,
) -> Optional[Union[ExperimentEntity, ExperimentRunEntity]]:
    q = encoded_selector(qs)
    with get_session("chaostoolkit.org/v1", configuration, secrets) as session:
        resp = session.get(f"/{endpoint}?selector={q}")
        logger.debug(f"Response from {resp.url}: {resp.status_code}")
        if resp.status_code == 200:
            payload = resp.json()
            if payload:
                payload = sorted(
                    payload,
                    key=lambda x: x["metadata"]["annotations"][  # type: ignore
                        "reliably.com/createdAt"
                    ],
                )
                return entity_type.parse_obj(payload[-1])
    return None


def get_experiment(
    experiment_ref: str, configuration: Configuration, secrets: Secrets
) -> Optional[ExperimentEntity]:
    qs = {"experiment_ref": experiment_ref}
    return cast(
        ExperimentEntity,
        get_entity("experiment", qs, ExperimentEntity, configuration, secrets),
    )


def get_experiment_run(
    run_ref: str, configuration: Configuration, secrets: Secrets
) -> Optional[ExperimentRunEntity]:
    qs = {"experiment_run_ref": run_ref}
    return cast(
        ExperimentRunEntity,
        get_entity("run", qs, ExperimentRunEntity, configuration, secrets),
    )


def send_to_reliably(
    entity: Union[
        ExperimentEntity, ExperimentRunEntity, ExperimentRunEventEntity
    ],
    endpoint: str,
    configuration: Configuration,
    secrets: Secrets,
) -> None:
    """
    For a given EntityContext, create it on the Reliably services.

    :param entity_context: EntityContext which will be created on the Reliably
        service
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    """
    with get_session("chaostoolkit.org/v1", configuration, secrets) as session:
        j = entity.json(
            by_alias=True, exclude_none=True, indent=False, sort_keys=True
        )
        logger.debug(f"Payload sent:\n{j}")
        resp = session.put(
            f"/{endpoint}",
            headers={"Content-Type": "application/json"},
            content=j,
        )

        try:
            logger.debug(f"Response received from {resp.url}: {resp.json()}")
        except Exception:
            logger.debug(
                f"Error response received from {resp.url}: {resp.text}"
            )
        resp.raise_for_status()


def create_experiment(
    experiment_ref: str,
    experiment: Experiment,
    configuration: Configuration,
    secrets: Secrets,
    objective_labels: Optional[List[Dict[str, str]]] = None,
) -> None:
    """
    For a given Experiment title, create a Experiment Entity Context
    on the Reliably services.

    :param experiment_title: str representing the name of the Experiment
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    """
    entity = ExperimentEntity(
        metadata=ExperimentMetadata(
            labels=ExperimentLabels(ref=experiment_ref),
            annotations={
                "title": experiment.get("title"),
                "last_results": "",
                "previous_deviated": "",
                "currently_running": "true",
            },
            related_to=objective_labels,
        ),
        spec=ExperimentSpec(experiment=experiment),
    )

    send_to_reliably(
        entity=entity,
        endpoint="experiment",
        configuration=configuration,
        secrets=secrets,
    )


def mark_experiment_as_running(
    entity: ExperimentEntity,
    experiment: Experiment,
    configuration: Configuration,
    secrets: Secrets,
) -> None:
    """
    For a given Experiment title, create a Experiment Entity Context
    on the Reliably services.

    :param experiment_title: str representing the name of the Experiment
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    """
    if not entity.metadata.annotations:
        entity.metadata.annotations = {}

    entity.metadata.annotations["currently_running"] = "true"
    if not entity.spec:
        entity.spec = ExperimentSpec(experiment=experiment)
    else:
        # always keep the most up to date version
        entity.spec.experiment = experiment

    send_to_reliably(
        entity=entity,
        endpoint="experiment",
        configuration=configuration,
        secrets=secrets,
    )


def complete_experiment(
    experiment_ref: str,
    state: Journal,
    configuration: Configuration,
    secrets: Secrets,
) -> None:
    """
    For a given Experiment title, create a Experiment Entity Context
    on the Reliably services.

    :param experiment_title: str representing the name of the Experiment
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    """
    x = get_experiment(experiment_ref, configuration, secrets)
    if not x:
        logger.debug(
            f"Experiment with ref '{experiment_ref}' could not be found in "
            "Reliably. Cannot mark experiment as complete."
        )
        return

    if not x.metadata.annotations:
        x.metadata.annotations = {}

    x.metadata.annotations["currently_running"] = "false"
    lr = x.metadata.annotations["last_results"]
    lasts = lr.split(",") if lr else []
    if lasts:
        d = lasts[-1] == "1"
        x.metadata.annotations["previous_deviated"] = "true" if d else "false"
    lasts.append("1" if state.get("deviated") else "0")
    x.metadata.annotations["last_results"] = ",".join(
        lasts[5:] if len(lasts) > 5 else lasts
    )

    send_to_reliably(
        entity=x,
        endpoint="experiment",
        configuration=configuration,
        secrets=secrets,
    )


def create_run(
    experiment_ref: str,
    run_ref: str,
    experiment: Experiment,
    experiment_labels: Dict[str, Any],
    configuration: Configuration,
    secrets: Secrets,
) -> None:
    """
    For a given user and Experiment labels, create a ExperimentRun
    Entity Context on the Reliably services.

    :param user: str representing the name of the user that is running the
        Experiment
    :param experiment_labels: EntityContextExperimentLabels
        object representing the labels of the Experiment Version this run is
        related to
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    """
    entity = ExperimentRunEntity(
        metadata=ExperimentRunMetadata(
            labels=ExperimentRunLabels(
                ref=run_ref, experiment_ref=experiment_ref
            ),
            annotations={
                "name": "Run",
                "title": experiment.get("title"),
                "status": "started",
            },
            related_to=[experiment_labels],
        )
    )

    send_to_reliably(
        entity=entity,
        endpoint="run",
        configuration=configuration,
        secrets=secrets,
    )


def complete_run(
    run_ref: str,
    experiment: Experiment,
    state: Journal,
    configuration: Configuration,
    secrets: Secrets,
) -> None:
    """
    For a given Experiment title, create a Experiment Entity Context
    on the Reliably services.

    :param experiment_title: str representing the name of the Experiment
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    """
    x = get_experiment_run(run_ref, configuration, secrets)
    if not x:
        logger.debug(
            f"Experiment run with ref '{run_ref}' could not be found in "
            "Reliably. Cannot mark experiment run as complete."
        )
        return

    if not x.metadata.annotations:
        x.metadata.annotations = {}

    a = x.metadata.annotations
    a.update(prepare_annotations_dict(state))  # type: ignore

    x.spec = ExperimentRunSpec(experiment=experiment, result=state)

    send_to_reliably(
        entity=x,
        endpoint="run",
        configuration=configuration,
        secrets=secrets,
    )


def create_run_event(
    experiment_ref: str,
    run_ref: str,
    event_ref: str,
    event_type: EventType,
    experiment: Experiment,
    title: str,
    output: Any,
    experiment_run_labels: Dict[str, Any],
    configuration: Configuration,
    secrets: Secrets,
) -> None:
    """
    For a given event type, name, output, and Experiment Run labels, create a
    ExperimentEvent Entity Context on the Reliably services.

    :param event_type: EventType representing the type of the Event that has
        happened
    :param name: str representing the name of the Event in the Experiment
    :param output: Any object representing the output of the event in the
        Experiment
    :param experiment_run_labels: EntityContextExperimentRunLabels object
        representing the labels of the Experiment Run this Event is related to
    :param configuration: Configuration object provided by Chaos Toolkit
    :param secrets: Secret object provided by Chaos Toolkit
    """
    # until we have figured out where to store large outputs, we will not be
    # sending it. Instead, we'll send enough information to make sense of the
    # results.

    annotations = prepare_annotations_dict(output)
    annotations["name"] = title
    entity = ExperimentRunEventEntity(
        metadata=ExperimentRunEventMetadata(
            labels=ExperimentRunEventLabels(
                event_type=event_type,
                ref=event_ref,
                experiment_run_ref=run_ref,
                experiment_ref=experiment_ref,
            ),
            annotations=annotations,
            related_to=[experiment_run_labels],
        )
    )

    if output:
        entity.spec = ExperimentRunEventSpec(result=output)

    send_to_reliably(
        entity=entity,
        endpoint="event",
        configuration=configuration,
        secrets=secrets,
    )


def prepare_annotations_dict(
    output: Optional[Dict[str, Any]]
) -> Dict[str, Optional[str]]:
    utc = timezone.utc
    s = e = d = t = status = node = None
    s = e = datetime.utcnow().replace(tzinfo=utc).isoformat()

    if isinstance(output, dict):
        status = output.get("status", "unknown")
        node = cast(str, output.get("node"))
        d = output.get("deviated", output.get("steady_state_met"))
        t = output.get("duration")

        if ("start" in output) and ("end" in output):
            s = (
                datetime.fromisoformat(cast(str, output.get("start")))
                .replace(tzinfo=utc)
                .isoformat()
            )
            e = (
                datetime.fromisoformat(cast(str, output.get("end")))
                .replace(tzinfo=utc)
                .isoformat()
            )

    return {
        "status": status,
        "deviated": str(d).lower() if d else None,
        "duration": str(t) if t else None,
        "started": s,
        "ended": e,
        "node": node,
    }


def populate_event_refs() -> Dict[str, str]:
    """
    Create uniq random strings to identify each step of the run.

    Activities do not have a static one like this because they can be
    used in many places so we generate a new one for each activity run.
    """
    refs = {}

    r = secrets_module.token_hex(8)
    refs["experiment"] = r

    r = secrets_module.token_hex(8)
    refs["hypo"] = r

    r = secrets_module.token_hex(8)
    refs["method"] = r

    r = secrets_module.token_hex(8)
    refs["rollback"] = r

    return refs
