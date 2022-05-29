import six
from rook.com_ws.envelope_wrappers.i_envelope_wrapper import IEnvelopeWrapper
from rook.processor.namespace_serializer2 import NamespaceSerializer2
from rook.protobuf.messages_pb2 import AugReportMessage


class Protobuf2EnvelopeWrapper(IEnvelopeWrapper):
    def __init__(self, agent_id, aug_id, message_id, arguments):
        self.message = AugReportMessage()
        self.message.agent_id = agent_id
        self.message.aug_id = aug_id
        self.message.report_id = message_id

        self.serializer = NamespaceSerializer2()
        self.serializer.dump(arguments, self.message.arguments2)

        self.buffer = None
        self.estimated_length = self.serializer.get_estimated_pending_bytes()

    def get_buffer(self):
        if self.buffer is not None:
            return self.buffer

        for k, v in six.iteritems(self.serializer.get_buffer_cache()):
            self.message.buffer_cache_indexes.append(v)
            self.message.buffer_cache_buffers.append(k)

        for k, v in six.iteritems(self.serializer.get_string_cache()):
            self.message.strings_cache[k] = v

        self.buffer = IEnvelopeWrapper.get_serialized_envelope(self.message)

        self.serializer = None
        self.message = None

        return self.buffer

    def __len__(self):      
        return self.estimated_length
