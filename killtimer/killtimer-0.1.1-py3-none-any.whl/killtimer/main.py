#!/usr/bin/env python
import argparse
import datetime
import math
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Optional, List, Callable

import pytimeparse
from desktop_notifier import DesktopNotifier, Urgency
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.console import Console
from rich import print as rprint


MINIMAL_WORK_DURATION = datetime.timedelta(seconds=15)
WORK_DURATION = datetime.timedelta(seconds=35) - MINIMAL_WORK_DURATION
OVERTIME_DURATION = datetime.timedelta(seconds=13)


def format_time(t: datetime.datetime) -> str:
    return t.strftime("%H:%M")


def format_duration(duration: datetime.timedelta, round_up: bool = False) -> str:
    total_seconds = duration.total_seconds()
    total_seconds = math.ceil(total_seconds) if round_up else math.floor(total_seconds)
    minutes, seconds = divmod(math.floor(total_seconds), 60)
    return f"{int(minutes)}:{seconds:02}"


def parse_timedelta(time_delta_representation: str) -> datetime.timedelta:
    return datetime.timedelta(seconds=pytimeparse.parse(time_delta_representation))


@dataclass
class RuntimeConfiguration:
    minimal_effort_duration: datetime.timedelta = datetime.timedelta(minutes=10)
    work_duration: datetime.timedelta = datetime.timedelta(hours=1)
    overtime_duration: datetime.timedelta = datetime.timedelta(minutes=15)
    command_to_run: Optional[List[str]] = None


def parse_configuration(args: [str]) -> RuntimeConfiguration:
    parser = argparse.ArgumentParser(
        prog="killtimer",
        description="Close application when time runs out",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-m", "--minimal-effort",
        type=parse_timedelta,
        default=RuntimeConfiguration.minimal_effort_duration,
        metavar="duration",
        help="Minimal work duration"
    )
    parser.add_argument(
        "-w", "--work",
        type=parse_timedelta,
        default=RuntimeConfiguration.work_duration,
        metavar="duration",
        help="Proper work duration"
    )
    parser.add_argument(
        "-o", "--overtime",
        type=parse_timedelta,
        default=RuntimeConfiguration.overtime_duration,
        metavar="duration",
        help="Overtime duration"
    )
    parser.add_argument(
        "command_to_run",
        nargs="*",
        help="Executable (with arguments) to run"
    )

    config = parser.parse_args(args)

    if config.minimal_effort > config.work:
        print("Minimal effort cannot take longer than actual work!")
        sys.exit(1)

    return RuntimeConfiguration(
        command_to_run=config.command_to_run,
        minimal_effort_duration=config.minimal_effort,
        work_duration=config.work,
        overtime_duration=config.overtime
    )


notify = DesktopNotifier(app_name="Killtimer")


def show_notification(message: str, icon_name: str, stay_visible: bool = False):
    urgency = Urgency.Critical if stay_visible else Urgency.Normal
    notify.send_sync(title="", message=message, icon=icon_name, sound=True, urgency=urgency)


def show_information(message: str):
    show_notification(message, "data-information")


def show_warning(message: str):
    show_notification(message, "data-warning", stay_visible=True)


def main() -> int:
    args = sys.argv[1:]
    config = parse_configuration(args)

    Console().clear()

    # Show deadlines
    start_time = datetime.datetime.now()
    display_configuration(config, start_time)

    # Start program under time limit
    user_command = start_monitored_command(config)

    display_progress_continuously(config, start_time, user_command)

    total_work_duration = datetime.datetime.now() - start_time

    # Kill program under test if it is still running
    if user_command and user_command.poll() is None:
        print("Overtime depleted - terminating user command...")
        user_command.terminate()
        # CHECK: wait a bit and kill it if still running?

    # Show total time spent
    rprint(f"Total work duration: {format_duration(total_work_duration)}")

    return 0


def display_progress_continuously(config: RuntimeConfiguration, start_time: datetime.datetime, user_command: Optional[subprocess.Popen]):
    def should_countdown_continue() -> bool:
        return user_command is None or user_command.poll() is None

    # Report progress
    progress_display_columns = (
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TextColumn("{task.fields[elapsed]}"),
        BarColumn(bar_width=None),
        TaskProgressColumn(),
        TextColumn("{task.fields[left]}")
    )
    with Progress(*progress_display_columns, expand=True) as progress:
        try:
            show_time_progress(should_countdown_continue, progress, "[green]Minimal effort", start_time,
                               start_time + config.minimal_effort_duration)
            if not should_countdown_continue():
                return
            show_information("Minimal effort done!")

            show_time_progress(should_countdown_continue, progress, "[bold white]Work", start_time,
                               start_time + config.work_duration)
            if not should_countdown_continue():
                return
            show_warning("Work done! You are doing overtime!")

            overtime_start_time = datetime.datetime.now()
            show_time_progress(should_countdown_continue, progress, "[red]Overtime", overtime_start_time,
                               overtime_start_time + config.overtime_duration)
        except KeyboardInterrupt:
            return


def start_monitored_command(config: RuntimeConfiguration) -> Optional[subprocess.Popen]:
    user_command: Optional[subprocess.Popen] = None
    if config.command_to_run:
        user_command = subprocess.Popen(" ".join(["exec"] + config.command_to_run), shell=True,
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # print(f"New process PID: {user_command.pid}")
    return user_command


def display_configuration(config: RuntimeConfiguration, start_time: datetime.datetime):
    rprint(f"{format_time(start_time)}\t-->"
           f"\t{format_time(start_time + config.minimal_effort_duration)}\t-->"
           f"\t{format_time(start_time + config.work_duration)}\t-->"
           f"\t[red]X[/red]")
    rprint(f"\t[green]{format_duration(config.minimal_effort_duration)}[/green]\t-->"
           f"\t[white]{format_duration(config.work_duration)}[/white]\t-->"
           f"\t[red]{format_duration(config.overtime_duration)}[/red]")


def show_time_progress(should_countdown_continue: Callable[[], bool], progress: Progress, label: str, start_time: datetime.datetime, end_time: datetime.datetime):
    task_duration = (end_time - start_time)
    task_progress = progress.add_task(label, total=task_duration.total_seconds(), elapsed="0:00", left="--:--")
    elapsed = datetime.datetime.now() - start_time
    while elapsed < task_duration:
        time_left = task_duration - elapsed
        progress.update(task_progress,
                        completed=elapsed.total_seconds(),
                        elapsed=format_duration(elapsed),
                        left=format_duration(time_left, round_up=True))
        time.sleep(1)
        elapsed = datetime.datetime.now() - start_time
        if not should_countdown_continue():
            return

    time_left = task_duration - elapsed
    progress.update(task_progress,
                    completed=elapsed.total_seconds(),
                    elapsed=format_duration(elapsed),
                    left=format_duration(time_left, round_up=True))


if __name__ == '__main__':
    sys.exit(main())
