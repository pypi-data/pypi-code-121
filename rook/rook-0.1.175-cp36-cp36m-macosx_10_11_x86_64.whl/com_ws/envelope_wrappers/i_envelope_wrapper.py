from abc import ABCMeta, abstractmethod

import rook.protobuf.envelope_pb2 as envelope_pb


class IEnvelopeWrapper:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_buffer(self):
        pass

    @abstractmethod
    def __len__(self):
        pass

    @staticmethod
    def get_serialized_envelope(message):
        envelope = envelope_pb.Envelope()
        envelope.timestamp.GetCurrentTime()
        envelope.msg.Pack(message)

        return envelope.SerializeToString()