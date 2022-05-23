from .imports import *

from .low_level import *
from .utils import tee_output


class LogEvent(enum.Enum):
    INIT = "INIT"
    PROGRESS = "PROGRESS"
    CHECKPOINT = "CHECKPOINT"


Evaluation = Callable[[], Iterable[tuple[torch.Tensor, pd.DataFrame]]]


def simple_logging(
    model: nn.Module,
    *,
    name: str,
    evaluation: Optional[Evaluation],
    comment: Optional[str] = None,
    progress_freq: int = 200,
    checkpoint_freq: int = 200,
    heartbeat_freq: int = 20,
    window_size: int = 1,
) -> Callable[[int, pd.DataFrame], Iterable[LogEvent]]:
    def logging_step(
        iteration: int,
        losses: pd.DataFrame,
    ) -> Iterable[LogEvent]:
        with directory(name) as exists_already:
            if not exists_already:
                init_logging(name, model, comment)
                yield LogEvent.INIT

            if iteration % progress_freq == 0:
                yield progress_logging(losses, window_size)

            if iteration % checkpoint_freq == 0:
                with directory(
                    f"checkpoints/{iteration//checkpoint_freq:05d}"
                ):  # todo move inside, tricky
                    yield checkpoint_logging(model, evaluation)

            if iteration % heartbeat_freq == 0:
                heartbeat_logging()

    return logging_step


def init_logging(name: str, model: nn.Module, comment: Optional[str]) -> LogEvent:
    if "pytest" not in sys.argv[0]: # todo figure out why this fails in tests
        tee_output("out.log")

    log_pid()
    log_config()
    log_max_memory()

    log_architecture(model)

    if comment is not None:
        log_comment(comment)

    create_symbolic_link(name)

    return LogEvent.INIT


def progress_logging(losses: pd.DataFrame, window_size: int) -> LogEvent:
    losses = losses.rolling(window_size).mean().iloc[::window_size, :][1:]
    # Some windowing operations also support an online method after constructing a windowing object which returns a new object that supports passing in new DataFrame or Series objects to continue the windowing calculation with the new values (i.e. online calculations).

    log_losses(losses)
    plot_losses(window_size)

    return LogEvent.PROGRESS


def checkpoint_logging(model: nn.Module, evaluation: Evaluation) -> LogEvent:
    if evaluation is not None:
        for j, (preds, scores) in enumerate(evaluation()):
            with directory("predictions"):
                log_predictions(j, preds)

        with directory("../.."):
            log_scores(scores)
            plot_scores()

    log_model(model)
    log_weights(model)

    return LogEvent.CHECKPOINT


def heartbeat_logging():
    log_last_modified()
    log_max_memory()

