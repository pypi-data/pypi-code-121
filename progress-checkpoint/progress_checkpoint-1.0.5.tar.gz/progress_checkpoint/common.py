import sys
from typing import Callable, Optional, Sequence, Coroutine, Generator, Iterable

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    Protocol = object

ProgressFraction = float  # from 0 to 1
StatusMessage = str


class Checkpoint(Protocol):
    def __call__(self, progress: ProgressFraction, status: Optional[StatusMessage] = None) -> None:
        pass


AsyncCheckpoint = Callable[[ProgressFraction, Optional[StatusMessage]], Coroutine]


def subcheckpoint(checkpoint: Optional[Checkpoint], start: ProgressFraction, stop: ProgressFraction,
                  parent_status: Optional[str] = None) -> Optional[Checkpoint]:
    if checkpoint is None:
        return None

    def new_checkpoint(progress: ProgressFraction, status: Optional[StatusMessage] = None) -> None:
        if not status:
            st = parent_status
        elif not parent_status:
            st = status
        else:
            st = parent_status + " / " + status
        assert checkpoint is not None
        checkpoint(progress * (stop - start) + start, st)

    return new_checkpoint


def subcheckpoints(checkpoint: Checkpoint, weights: Optional[Iterable[float]] = None,
                   statuses: Optional[Iterable[Optional[str]]] = None,
                   status_pattern: Optional[str] = None, size: Optional[int] = None) -> Generator[
    Checkpoint, None, None]:
    if size is None:
        if isinstance(weights, Sequence):
            size = len(weights)
        else:
            assert weights is not None
            weights = list(weights)
            size = len(weights)

    if isinstance(weights, Sequence):
        assert (len(weights) == size)

    if isinstance(statuses, Sequence):
        assert (len(statuses) == size)

    if weights is None and size is not None:
        weights = [1] * size

    if statuses is None:
        statuses = [None] * size

    total_weight = sum(weights)
    weight_done = 0

    for i, w, status in zip(range(size), weights, statuses):
        if status_pattern:
            status = status_pattern.format(i=i + 1, size=size, weight_done=weight_done, total_weight=total_weight)
        sc = subcheckpoint(checkpoint,
                           weight_done / total_weight,
                           (weight_done + w) / total_weight,
                           status)
        assert sc is not None
        yield sc
        weight_done += w
