from .imports import *

from .low_level import *


class Event(enum.Enum):
    INIT = "INIT"
    PROGRESS = "PROGRESS"
    CHECKPOINT = "CHECKPOINT"


def simple_logs(
    name: str,
    iteration: int,
    model: nn.Module,
    losses: pd.DataFrame,
    progress_freq: int = 1_000,
    checkpoint_freq: int = 10_000,
) -> set[Event]:
    events = set() if os.path.exists(name) else set([Event.INIT])

    with experiment(name):
        if iteration % progress_freq == 0:
            log_progress(losses)
            events.add(Event.PROGRESS)

        if iteration % checkpoint_freq == 0:
            with directory(f"{iteration//checkpoint_freq:06d}"):
                log_checkpoint(model)
                events.add(Event.CHECKPOINT)

    return events


@contextlib.contextmanager
def experiment(directory_path: str):
    with directory(directory_path):
        log_pid()
        log_config()
        yield


def log_progress(losses) -> None:
    log_losses(losses)
    plot_losses(losses)


def log_checkpoint(model) -> None:
    log_model(model)
    log_weights(model)


