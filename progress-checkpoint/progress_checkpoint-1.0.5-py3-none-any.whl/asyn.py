from typing import Sequence, Iterable, AsyncGenerator, Optional

from .common import AsyncCheckpoint, StatusMessage, ProgressFraction


async def with_progress_async(seq: Iterable, checkpoint: AsyncCheckpoint, size: Optional[int] = None,
                              status: Optional[StatusMessage] = None, div: int = 1
                              ) -> AsyncGenerator[AsyncCheckpoint, None]:
    await checkpoint(0, status or '')
    if size is None:
        if not isinstance(seq, Sequence):
            seq = list(seq)
        size = len(seq)

    for i, e in enumerate(seq):
        yield e

        if i % div == 0:
            await checkpoint(i / size, status)


# noinspection PyUnusedLocal
async def dummy_checkpoint_async(progress: ProgressFraction, status: Optional[StatusMessage] = None
                                 ) -> AsyncGenerator[None, None]:
    pass
