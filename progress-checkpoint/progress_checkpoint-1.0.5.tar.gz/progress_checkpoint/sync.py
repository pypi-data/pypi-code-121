from typing import Sequence, Iterable, Sized, Optional, TypeVar, Generator, Tuple

from .common import Checkpoint, subcheckpoints, StatusMessage

T = TypeVar("T")


# noinspection PyUnusedLocal
def dummy_checkpoint(progress: float, status: Optional[str] = None) -> None:
    return


def with_progress(seq: Iterable[T], checkpoint: Checkpoint, size: Optional[int] = None, status: Optional[str] = None,
                  div: int = 1) -> Generator[T, None, None]:
    checkpoint(0, status or '')
    if size is None:
        assert isinstance(seq, Sized), '`seq` must be a sequence unless `size` is given'
        size = len(seq)

    for i, e in enumerate(seq):
        yield e

        if i % div == 0:
            checkpoint(i / size, status)

    checkpoint(1.0, status)


def with_progress_sub(seq: Iterable[T], checkpoint: Checkpoint, size: Optional[int] = None, status: Optional[str] = None,
                      statuses: Optional[Iterable[StatusMessage]] = None, status_pattern: Optional[str] = None,
                      weights: Iterable[float] = None, div: int = 1) -> Generator[Tuple[T, Checkpoint], None, None]:
    if size is None:
        assert isinstance(seq, Sized), '`seq` must be a sequence unless `size` is given'
        size = len(seq)

    checkpoints = subcheckpoints(checkpoint, weights=weights, statuses=statuses, status_pattern=status_pattern,
                                 size=size)

    if isinstance(seq, Sequence):
        assert (len(seq) == size)

    checkpoint(0, status or '')

    for i, (e, c) in enumerate(zip(seq, checkpoints)):
        yield e, c

        if i % div == 0:
            c(1.0)
