"""Coiled cluster information displayed in a Jupyter Notebook-like context."""
from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from types import TracebackType
from typing import Iterable, Type

import jmespath
from IPython.display import DisplayHandle, clear_output, display
from jinja2 import Environment, FileSystemLoader, Template
from jinja2.exceptions import TemplateNotFound

from ...errors import ClusterCreationError
from ..states import (
    DISPLAY_DATETIME_FORMAT,
    CombinedProcessStateEnum,
    ProcessStateEnum,
    State,
    StatefulObjectType,
)
from .util import get_instance_types, get_worker_statuses

try:
    import ipywidgets as ipyw
except ImportError:
    pass


def format_state(state: State) -> str:
    """Format the state of a worker or scheduler consistently.

    The output is intended for the status logs views in the cluster status widgets.
    """
    state_names = {
        StatefulObjectType.cluster: "Cluster",
        StatefulObjectType.scheduler: "Scheduler Process",
        StatefulObjectType.scheduler_instance: "Scheduler Instance",
        StatefulObjectType.cluster_infra: "Network Infrastructure",
        StatefulObjectType.worker: "Worker Process",
        StatefulObjectType.worker_instance: "Worker Instance",
    }
    if state.type in (StatefulObjectType.worker, StatefulObjectType.worker_instance):
        max_type_length = 15
    elif state.type in (
        StatefulObjectType.scheduler,
        StatefulObjectType.scheduler_instance,
    ):
        max_type_length = 18
    else:
        max_type_length = max(len(v) for v in state_names.values())
    time = datetime.strftime(state.updated.astimezone(), DISPLAY_DATETIME_FORMAT)
    return (
        f"{state_names[state.type]:<{max_type_length}} | {state.state:<8} | {time} "
        f"| {state.reason}"
    )


def format_error_state(state: State) -> str:
    """Format the error state of a worker or scheduler consistently.

    The output is intended for the status logs views in the cluster status widgets.
    """
    state_names = {
        StatefulObjectType.cluster: "Cluster",
        StatefulObjectType.scheduler: "Scheduler Process",
        StatefulObjectType.scheduler_instance: "Scheduler Instance",
        StatefulObjectType.cluster_infra: "Network Infrastructure",
        StatefulObjectType.worker: "Worker Process",
        StatefulObjectType.worker_instance: "Worker Instance",
    }
    max_type_length = max(len(v) for v in state_names.values())
    time = datetime.strftime(state.updated.astimezone(), DISPLAY_DATETIME_FORMAT)
    return f"{state_names[state.type]:<{max_type_length}} | {time} | {state.reason}"


TEMPLATE_PATHS = [Path(__file__).parent / "templates"]
FILTERS = {
    "format_state": format_state,
    "format_error_state": format_error_state,
}


def get_environment() -> Environment:
    """Create a Jinja Environment instance."""
    loader = FileSystemLoader(TEMPLATE_PATHS)
    environment = Environment(loader=loader)
    environment.filters.update(FILTERS)

    return environment


def get_template(name: str) -> Template:
    """Load a Jinja template."""
    try:
        return get_environment().get_template(name)
    except TemplateNotFound as e:
        raise TemplateNotFound(
            f"Unable to find {name} in coiled.widgets.TEMPLATE_PATHS {TEMPLATE_PATHS}"
        ) from e


def _update_cluster_status(cluster_status: Iterable[State]) -> dict[str, list[State]]:
    """Separates cluster status into error, scheduler, and worker buckets.

    Each bucket corresponds to a key in the return dictionary. Errors are collected for
    all the object types, whereas the scheduler and worker keys group status messages
    for the * and *_instance types.
    """
    output = defaultdict(list)
    for state in cluster_status:
        if state.state == "error":
            output["error"].append(state)
        elif state.type in (
            StatefulObjectType.scheduler,
            StatefulObjectType.scheduler_instance,
        ):
            output["scheduler"].append(state)
        elif state.type in (
            StatefulObjectType.worker,
            StatefulObjectType.worker_instance,
        ):
            output["worker"].append(state)
    return output


CLOUDS: dict[str | None, str] = {
    "vm_aws": "Amazon Web Services",
    "vm_gcp": "Google Cloud Platform",
    None: "Unknown",
}

PUBLIC_IP_ADDRESS = jmespath.compile("scheduler.instance.public_ip_address")


class ClusterStatusWidget:  # pragma: no cover
    """Shows the status of a Coiled cluster using ipywidgets.

    The format is handled by Jinja templates in the local 'templates' directory.

    This widget is not recommended for use at this time. It's functional but not
    polished.
    """

    _display_id: DisplayHandle | None

    def __init__(self):
        """Set up the top-level widget and the display machinery."""
        self._display_id = None
        self._received_data = False
        self.tab_box = ipyw.Tab()

        # Compatibility for ipywidgets 7/8
        if hasattr(self.tab_box, "titles"):
            self.tab_box.titles = ("Overview", "Configuration", "Status Logs")
        else:
            self.tab_box.set_title(0, "Overview")
            self.tab_box.set_title(1, "Configuration")
            self.tab_box.set_title(2, "Status Logs")

        self.scheduler_status_logs = []
        self.worker_status_logs = []
        self.error_logs = []

        self.overview_tab_template = get_template("overview.html.j2")
        self.overview_tab = ipyw.HTML()

        self.configuration_template = get_template("configuration.html.j2")
        self.configuration_tab = ipyw.HTML()

        self.status_logs_template = get_template("status_logs.html.j2")
        self.status_output_tab = ipyw.HTML()

        self.tab_box.children = (
            self.overview_tab,
            self.configuration_tab,
            self.status_output_tab,
        )

    def __enter__(self) -> ClusterStatusWidget:
        """Enter a live-updating context.

        Example
        -------
        with ClusterStatusWidget() as w:
            # do stuff
            w.update(cluster_details, cluster_status)
        """
        self._display_id = display_id = DisplayHandle()
        display_id.display(self)
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the live-updating context and reset the display ID.

        Keep the widget around for user inspection if there was a cluster creation
        error, otherwise remove it.
        """
        if exc_type != ClusterCreationError:
            clear_output(wait=True)
        self._display_id = None

    def _ipython_display_(self):
        if self._display_id:
            # Don't bother displaying if we haven't set the data yet
            if self._received_data:
                self._display_id.display(self.tab_box)
        else:
            display(self.tab_box)

    def update(self, cluster_details, cluster_status):
        """Update the widget display data."""
        # Overview tab
        dashboard_address = PUBLIC_IP_ADDRESS.search(cluster_details)
        n_workers = len(jmespath.search("workers[*]", cluster_details) or [])
        statuses = get_worker_statuses(cluster_details)
        overall_cluster_status = jmespath.search("current_state.state", cluster_details)
        current_scheduler_state = jmespath.search(
            "scheduler.current_state.state", cluster_details
        )
        scheduler_ready = (
            ProcessStateEnum(current_scheduler_state) == ProcessStateEnum.started
        )

        status_logs = _update_cluster_status(cluster_status)
        scheduler_status_logs = status_logs["scheduler"]
        worker_status_logs = status_logs["worker"]
        error_logs = status_logs["error"]

        n_starting = (
            statuses[CombinedProcessStateEnum.instance_queued]
            + statuses[CombinedProcessStateEnum.instance_starting]
        )
        self.overview_tab.value = self.overview_tab_template.render(
            cluster_name=cluster_details["name"],
            overall_cluster_status=overall_cluster_status,
            dashboard_address=dashboard_address if scheduler_ready else None,
            n_workers=n_workers,
            n_starting=n_starting,
            n_running=statuses[CombinedProcessStateEnum.instance_running],
            n_ready=statuses[CombinedProcessStateEnum.ready],
            n_errored=statuses[CombinedProcessStateEnum.error],
            error_logs=error_logs,
        )

        # Configuration tab
        scheduler_instance_type, worker_instance_types = get_instance_types(
            cluster_details
        )
        # TODO: This will awkwardly wrap to the next line in the output if there are
        # too many worker types. It'd be nice to format that more nicely.
        worker_instance_types_label = ", ".join(
            f"{k} ({v:,})" for k, v in worker_instance_types.items()
        )
        worker_instance_types_label = worker_instance_types_label or None
        # TODO: This value is not yet deployed to the staging API
        software_environment_name = None
        cloud_name = CLOUDS.get(
            jmespath.search("cluster_options.type", cluster_details), "Unknown"
        )
        region_name = jmespath.search("cluster_options.region_name", cluster_details)
        self.configuration_tab.value = self.configuration_template.render(
            scheduler_instance_type=scheduler_instance_type,
            worker_instance_type=worker_instance_types_label,
            software_environment_name=software_environment_name,
            cloud_name=cloud_name,
            region_name=region_name,
        )

        # Status logs tab
        self.status_output_tab.value = self.status_logs_template.render(
            scheduler_status_logs=scheduler_status_logs,
            worker_status_logs=worker_status_logs,
        )

        # Handle an initial display
        if not self._received_data:
            self._received_data = True
            if self._display_id:
                self._display_id.display(self.tab_box)


class HTMLClusterWidget:
    """Shows the status of a Coiled cluster using plain HTML.

    The format is handled by Jinja templates in the local 'templates' directory.
    """

    _display_id: DisplayHandle | None

    def __init__(self) -> None:
        """Set up the template and other machinery."""
        self._display_id = None
        self._received_data = False
        self.template = get_template("cluster_status.html.j2")
        self.scheduler_status_logs = []
        self.worker_status_logs = []
        self.error_logs = []

    def __enter__(self) -> HTMLClusterWidget:
        """Enter a live-updating context.

        Example
        -------
        with HTMLClusterWidget() as w:
            # do stuff
            w.update(cluster_details, cluster_status)
        """
        self._display_id = display_id = DisplayHandle()
        display_id.display(self)
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the live-updating context and reset the display ID.

        Update the widget to the interactive state. Keep the widget around for user
        inspection if there was a cluster creation error, otherwise remove it.
        """
        if self._display_id and self._received_data:
            mimebundle = {
                "text/html": self.template.render(
                    interactive=True, unique=uuid.uuid4(), **self.__dict__
                )
            }
            self._display_id.update(mimebundle, raw=True)

        # If we got a cluster creation error, let the output hang around
        # for user inspection.
        if exc_type != ClusterCreationError:
            clear_output(wait=True)
        self._display_id = None

    def _ipython_display_(self):
        # Don't bother displaying if we haven't set the data.
        if self._received_data:
            interactive = not self._display_id
            mimebundle = {
                "text/html": self.template.render(
                    interactive=interactive, unique=uuid.uuid4(), **self.__dict__
                )
            }
            if self._display_id:
                self._display_id.display(mimebundle, raw=True)
            else:
                display(mimebundle, raw=True)

    def update(self, cluster_details, cluster_status, *args, **kwargs):
        """Update the widget display data."""
        self.cluster_name = jmespath.search("name", cluster_details)
        self.cloud_name = CLOUDS.get(
            jmespath.search("cluster_options.type", cluster_details), "Unknown"
        )
        self.region_name = jmespath.search(
            "cluster_options.region_name", cluster_details
        )
        self.software_environment_name = None
        self.overall_cluster_status = jmespath.search(
            "current_state.state", cluster_details
        )
        self.scheduler_status = jmespath.search(
            "scheduler.current_state.state", cluster_details
        )
        scheduler_ready = (
            ProcessStateEnum(self.scheduler_status) == ProcessStateEnum.started
        )
        self.dashboard_address = (
            PUBLIC_IP_ADDRESS.search(cluster_details) if scheduler_ready else None
        )
        self.n_workers = len(jmespath.search("workers[*]", cluster_details) or [])

        statuses = get_worker_statuses(cluster_details)
        self.n_starting = (
            statuses[CombinedProcessStateEnum.instance_queued]
            + statuses[CombinedProcessStateEnum.instance_starting]
        )
        self.n_running = statuses[CombinedProcessStateEnum.instance_running]
        self.n_ready = statuses[CombinedProcessStateEnum.ready]
        self.n_errored = statuses[CombinedProcessStateEnum.error]
        status = _update_cluster_status(cluster_status)
        self.scheduler_status_logs = status["scheduler"]
        self.worker_status_logs = status["worker"]
        self.error_logs = status["error"]
        # TODO: Add software_environment_name into this check/update as well
        self.scheduler_instance_type, worker_instance_types = get_instance_types(
            cluster_details
        )
        self.worker_instance_type = ", ".join(
            f"{k} ({v:,})" for k, v in worker_instance_types.items()
        )
        self.worker_instance_type = self.worker_instance_type or None

        # Include a UUID so that the bundled script, which refers to elements by ID,
        # grabs only the one that is rendered here, rather than any others that might
        # be on the page.
        interactive = not self._display_id
        mimebundle = {
            "text/html": self.template.render(
                interactive=interactive, unique=uuid.uuid4(), **self.__dict__
            )
        }

        if self._display_id:
            # Handle an initial display
            if not self._received_data:
                self._display_id.display(mimebundle, raw=True)
            else:
                self._display_id.update(mimebundle, raw=True)
        self._received_data = True
