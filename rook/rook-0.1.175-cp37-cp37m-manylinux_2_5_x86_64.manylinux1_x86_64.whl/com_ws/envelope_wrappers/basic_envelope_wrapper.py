from rook.com_ws.envelope_wrappers.i_envelope_wrapper import IEnvelopeWrapper


class BasicEnvelopeWrapper(IEnvelopeWrapper):
    def __init__(self, message):
        self.buffer = message

    def get_buffer(self):
        return self.buffer

    def __len__(self):
        return len(self.buffer)
