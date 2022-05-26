from __future__ import annotations

import datetime
from collections import Counter
from textwrap import dedent
from types import TracebackType
from typing import Any, Iterable, Mapping, Optional, Type

import jmespath
import rich
import rich.align
import rich.bar
import rich.console
import rich.layout
import rich.live
import rich.panel
import rich.progress

from ...errors import ClusterCreationError
from ..states import CombinedProcessStateEnum, ProcessStateEnum
from .util import get_instance_types, get_worker_statuses

LOCAL_TIMEZONE = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo

# This is annoying. I think Ian explained to me that the reason
# we need to manage the size so manually is that if we aren't explicit,
# Jupyter notebooks (but not IPython terminal) messes up the size.
WAITING_CONSOLE_HEIGHT = 26
WAITING_PROGRESS_HEIGHT = 9
DONE_PROGRESS_HEIGHT = 6
DONE_CONSOLE_HEIGHT = WAITING_CONSOLE_HEIGHT - (
    WAITING_PROGRESS_HEIGHT - DONE_PROGRESS_HEIGHT
)
CONSOLE_WIDTH = 100


class RichClusterWidget:
    """A Rich renderable showing cluster status."""

    n_workers: int
    _cluster_details: Mapping[str, Any] | None
    _progress: rich.progress.Progress

    def __init__(
        self,
        n_workers: int = 0,
        transient: bool = False,
        console: rich.console.Console | None = None,
        *,
        server,
        account,
    ):
        """Set up the renderable widget."""
        self.server = server
        self.account = account
        self._cluster_details = None
        self._final_update = None
        self._loader_frames = ["...", " ..", "  .", "   ", ".  ", ".. "]
        self._frame = 0
        self.last_updated_utc = datetime.datetime.now(datetime.timezone.utc)
        if console:
            self.console = console
        else:
            self.console = rich.console.Console()
            self.console.size = (CONSOLE_WIDTH, WAITING_CONSOLE_HEIGHT)

        self._progress = progress = rich.progress.Progress(
            "{task.description}",
            rich.progress.BarColumn(complete_style="progress.remaining"),
            rich.progress.TextColumn("[progress.percentage]{task.completed}"),
        )
        self._error_progress = error_progress = rich.progress.Progress(
            "{task.description}",
            rich.progress.BarColumn(complete_style="red", finished_style="red"),
            rich.progress.TextColumn("[progress.percentage]{task.completed}"),
        )
        self._provision_task = progress.add_task("Provisioning", total=n_workers)
        self._boot_task = progress.add_task("Booting Instance", total=n_workers)

        self._downloading_extracting_task = progress.add_task(
            "Launching Software Environment", total=n_workers
        )
        self._ready_task = progress.add_task("Ready", total=n_workers)
        self._stopping_task = progress.add_task("Stopping", total=n_workers)
        self._stopped_task = progress.add_task("Stopped", total=n_workers)

        # In order to make the bar red for errors, the error progress bar is a different instance
        # of rich.progress.Progress.
        # But we still want this bar aligned with the others, since rich doesn't know these two groups
        # are related, it doesn't automatically know how much right-padding to add
        # after the word "Error", so we calculate that ourselves here.
        max_len = max(len(t.description) for t in progress.tasks)
        self._error_task = error_progress.add_task(
            "Error" + " " * (max_len - len("Error")), total=n_workers, visible=False
        )

        # Calls _get_renderable, so the progress bar must be set up first.
        self.live = rich.live.Live(
            transient=transient,
            console=self.console,
            get_renderable=self._get_renderable,
        )

    def start(self):
        """Start the live instance."""
        self.live.start(refresh=False)

    def stop(self):
        """Stop the live instance."""
        self.live.stop()

    def __enter__(self) -> RichClusterWidget:
        """Enter a live-updating context.

        Example
        -------
        with RichClusterWidget(n_workers) as w:
            # do stuff
        """
        self.start()
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
        if exc_type == ClusterCreationError and self.live.transient:
            self.live.transient = False
        self.stop()

    def update(
        self,
        cluster_details: Optional[Mapping[str, Any]],
        logs,
        *args,
        final_update=None,
        **kwargs,
    ) -> None:
        """Update cluster data.

        Note: this does not trigger any refreshing, that is handled by the Live
        instance, which does it periodically.
        """
        self._cluster_details = cluster_details

        # track when the widget last received new data about the cluster
        # (which is less often than the widget renders)
        self.last_updated_utc = datetime.datetime.now(datetime.timezone.utc)

        if final_update:
            self._final_update = final_update

        # We explicitly refresh to make sure updated info is shown.
        # (Bad timing can lead auto-refresh to not show the update before we stop.)
        self.live.refresh()

    def _ipython_display_(self) -> None:
        """Render in a notebook context.

        Note: this is *not* called in an IPython terminal context. Instead,
        _repr_mimebundle_ is used in the IPython terminal.
        """
        self.console.print(self._get_renderable(), new_line_start=True)

    def __rich_console__(
        self, console: rich.console.Console, options: rich.console.ConsoleOptions
    ) -> rich.console.RenderResult:
        """Implement the Rich console interface.

        In particular, this is used in ``_repr_mimebundle_`` to display to an IPython
        terminal.
        """
        yield self._get_renderable()

    def _repr_mimebundle_(
        self, include: Iterable[str], exclude: Iterable[str], **kwargs
    ) -> dict[str, str]:
        """Display the widget in an IPython console context.

        This is adapted from the code in `rich.jupyter.JupyterMixin`. We can't
        use that mixin because it doesn't allow you to specify your own console
        (instead using the global one). We want our own console because we
        manually set the size to not take up the full terminal.
        """
        console = self.console
        segments = list(console.render(self, console.options))  # type: ignore
        text = console._render_buffer(segments)  # Unfortunate private member access...
        data = {"text/plain": text}
        if include:
            data = {k: v for (k, v) in data.items() if k in include}
        if exclude:
            data = {k: v for (k, v) in data.items() if k not in exclude}
        return data

    def _get_renderable(self) -> rich.console.RenderableType:
        """Construct the rendered layout."""
        progress = self._progress
        error_progress = self._error_progress
        current_loader_frame = self._loader_frames[self._frame]
        if self._cluster_details:
            desired_workers = self._cluster_details["desired_workers"]
            n_workers = len(jmespath.search("workers[*]", self._cluster_details) or [])
            overall_cluster_status = self._cluster_details["current_state"]["state"]
            if self._cluster_details["current_state"]["state"] != "ready":
                overall_cluster_status += current_loader_frame

            scheduler_status = self._cluster_details["scheduler"]["current_state"][
                "state"
            ]
            scheduler_ready = (
                ProcessStateEnum(scheduler_status) == ProcessStateEnum.started
            )
            if not scheduler_ready:
                scheduler_status += current_loader_frame

            dashboard_address = (
                jmespath.search(
                    "scheduler.instance.public_ip_address", self._cluster_details
                )
                if scheduler_ready
                else None
            )
            scheduler_instance_type, worker_instance_types = get_instance_types(
                self._cluster_details
            )
            region = self._cluster_details["cluster_options"]["region_name"]
            zone = self._cluster_details["cluster_options"]["zone_name"]
            zone_desc = f" ({zone})" if zone else ""
            cluster_name = self._cluster_details["name"]

            statuses = get_worker_statuses(self._cluster_details)
            progress.update(
                self._provision_task,
                total=n_workers,
                completed=statuses[CombinedProcessStateEnum.instance_queued]
                + statuses[CombinedProcessStateEnum.instance_starting],
            )
            progress.update(
                self._downloading_extracting_task,
                total=n_workers,
                completed=statuses[CombinedProcessStateEnum.downloading],
            )
            progress.update(
                self._boot_task,
                total=n_workers,
                completed=statuses[CombinedProcessStateEnum.instance_running],
            )
            progress.update(
                self._ready_task,
                total=n_workers,
                completed=statuses[CombinedProcessStateEnum.ready],
            )
            progress.update(
                self._stopping_task,
                total=n_workers,
                completed=statuses[CombinedProcessStateEnum.stopping],
            )
            progress.update(
                self._stopped_task,
                total=n_workers,
                completed=statuses[CombinedProcessStateEnum.stopped],
            )
            error_progress.update(
                self._error_task,
                visible=statuses[CombinedProcessStateEnum.error] > 0,
                total=n_workers,
                completed=statuses[CombinedProcessStateEnum.error],
            )
        else:
            overall_cluster_status = current_loader_frame
            scheduler_status = current_loader_frame
            dashboard_address = None
            scheduler_instance_type = current_loader_frame
            worker_instance_types = Counter()
            region = current_loader_frame
            zone_desc = ""
            cluster_name = ""
            desired_workers = ""

        dashboard_address = (
            f"http://{dashboard_address}:8787" if dashboard_address else None
        )
        dashboard_label = (
            f"[link={dashboard_address}]{dashboard_address}[/link]"
            if dashboard_address
            else current_loader_frame
        )
        if any(k for k, v in worker_instance_types.items()):
            worker_instance_types_label = ", ".join(
                f"{k or 'Unknown'} ({v:,})" for k, v in worker_instance_types.items()
            )
        else:
            worker_instance_types_label = current_loader_frame
        config = dedent(
            f"""
            [bold green]Region:[/bold green] {region}{zone_desc}

            [bold green]Scheduler Instance Type:[/bold green] {scheduler_instance_type or current_loader_frame}

            [bold green]Worker Instance Type(s):[/bold green] {worker_instance_types_label or current_loader_frame}

            [bold green]Workers Requested:[/bold green] {desired_workers}"""
        )

        status = dedent(
            f"""
            [bold green]Cluster Name:[/bold green] {cluster_name}

            [bold green]Cluster Status:[/bold green] {overall_cluster_status}

            [bold green]Scheduler Status:[/bold green] {scheduler_status}

            [bold green]Dashboard Address:[/bold green] {dashboard_label}"""
        )

        """Define the layout."""
        layout = rich.layout.Layout(name="root")
        self._frame = (self._frame + 1) % len(self._loader_frames)

        if self._final_update is None:
            progress_height = WAITING_PROGRESS_HEIGHT
            console_size = (CONSOLE_WIDTH, WAITING_CONSOLE_HEIGHT)
        else:
            progress_height = DONE_PROGRESS_HEIGHT
            console_size = (CONSOLE_WIDTH, DONE_CONSOLE_HEIGHT)

        self.console.size = console_size

        if self._cluster_details is None:
            link = ""
        else:

            link = f"{self.server}/{self.account}/clusters/{self._cluster_details['id']}/details"
        # Make the link clickable on jupyterlab notebooks
        if not self.console.is_terminal:
            link = f"[link={link}]{link}[/link]"
        layout.split(
            rich.layout.Layout(
                rich.panel.Panel(
                    rich.align.Align.center(link),
                    title="[bold green frame]Coiled Cluster",
                ),
                name="header",
                size=3,
            ),
            rich.layout.Layout(name="body", size=12),
            rich.layout.Layout(name="progress", size=progress_height),
        )
        layout["body"].split_row(
            rich.layout.Layout(name="overview"),
            rich.layout.Layout(name="configuration"),
        )

        time = self.last_updated_utc.astimezone(LOCAL_TIMEZONE).strftime(
            "%Y/%m/%d %H:%M:%S %Z"
        )
        if self._final_update is None:
            layout["progress"].update(
                rich.panel.Panel(
                    rich.align.Align.center(
                        rich.console.Group(
                            progress.get_renderable(), error_progress.get_renderable()
                        ),
                        vertical="middle",
                    ),
                    title=f"Dask Worker States ({time})",
                )
            )
        else:
            layout["progress"].update(
                rich.panel.Panel(
                    rich.align.Align.center(self._final_update, vertical="middle"),
                    title=f"({time})",
                )
            )
        layout["body"]["overview"].update(rich.panel.Panel(status, title="Overview"))
        layout["body"]["configuration"].update(
            rich.panel.Panel(config, title="Configuration")
        )
        return layout
