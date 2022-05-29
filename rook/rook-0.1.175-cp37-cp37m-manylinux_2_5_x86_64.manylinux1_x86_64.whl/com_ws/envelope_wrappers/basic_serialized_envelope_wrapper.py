from rook.com_ws.envelope_wrappers.i_envelope_wrapper import IEnvelopeWrapper


class BasicSerializedEnvelopeWrapper(IEnvelopeWrapper):
    def __init__(self, message):
        self.buffer = IEnvelopeWrapper.get_serialized_envelope(message)

    def get_buffer(self):
        return self.buffer

    def __len__(self):
        return len(self.buffer)
