import io
from io import IOBase
from typing import IO, Protocol, runtime_checkable, Iterator, Union


# @contextmanager
# def capture(stream: Literal['stdout', 'stderr']) -> ContextManager[StringIO]:
#     original = getattr(sys, stream)
#     try:
#         new_stream = StringIO()
#         setattr(sys, stream, new_stream)
#         yield new_stream
#     finally:
#         setattr(sys, stream, original)

@runtime_checkable
class _HasReadInto(Protocol):
    def readinto(self, b: bytearray) -> int:
        ...


def chunks(io_stream: Union[IO, IOBase], chunk_size: int = io.DEFAULT_BUFFER_SIZE, reuse: bool = True)\
        -> Iterator[bytes]:
    """
    :param io_stream: the stream to iterate on
    :param chunk_size: the required size of each chunk (last chunk may have a different size)
    :param reuse: if True, an attempt to reuse the memory of each chunk is made
                  (read: if reuse is True, don't store the chunks returned by the iterator)
    :return: an iterator on the chunks composing the given `io_stream`
    """
    if reuse and isinstance(io_stream, _HasReadInto):
        chunk = bytearray(chunk_size)
        while sz := io_stream.readinto(chunk):
            if sz == chunk_size:
                yield chunk
            else:
                yield memoryview(chunk)[:sz]
    else:
        while chunk := io_stream.read(chunk_size):
            yield chunk
