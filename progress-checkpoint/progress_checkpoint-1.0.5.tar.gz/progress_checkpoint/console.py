from typing import Optional

from progressbar import ProgressBar, widgets as pbwidgets  # type: ignore

from progress_checkpoint.common import ProgressFraction, StatusMessage


def status_string(status: str, size: int = 50) -> str:
    status += " " * (size - len(status))
    if len(status) > size:
        status = "..." + status[-size + 3:]
    return status


class ProgressbarCheckpoint:
    def __init__(self) -> None:
        self.status_label = pbwidgets.FormatLabel(status_string(""))
        self.pb = ProgressBar(1.0, widgets=[self.status_label,
                                            pbwidgets.Percentage(), ' ', pbwidgets.Bar(),
                                            pbwidgets.FormatLabel(" %(elapsed)s "),
                                            pbwidgets.AdaptiveETA(),
                                            ])
        self.last_status: Optional[str] = None
        self.pb.start()

    def __call__(self, progress: ProgressFraction, status: Optional[StatusMessage] = None) -> None:
        if status != self.last_status:
            if status:
                self.status_label.format_string = status_string(status)
                print(status)
            self.last_status = status
        if progress >= 1.0:
            self.pb.finish()
        else:
            self.pb.update(progress)


class ProgressbarCheckpointAsync:
    def __init__(self) -> None:
        self.sync = ProgressbarCheckpoint()

    async def __call__(self, progress: ProgressFraction, status: Optional[StatusMessage] = None) -> None:
        return self.sync(progress, status)
