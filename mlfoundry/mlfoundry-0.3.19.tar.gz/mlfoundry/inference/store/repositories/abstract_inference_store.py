import abc
import typing

from ..inference_packet import BasePacket


class AbstractInferenceStore(abc.ABC):
    @abc.abstractmethod
    def batch_log_inference(self, inference_packets: typing.List[BasePacket]):
        ...

    @abc.abstractmethod
    def list_inference(
        self,
        model_name: str,
        model_version: typing.Optional[str] = None,
        page: int = 0,
        page_size: typing.Optional[int] = None,
    ):
        ...
