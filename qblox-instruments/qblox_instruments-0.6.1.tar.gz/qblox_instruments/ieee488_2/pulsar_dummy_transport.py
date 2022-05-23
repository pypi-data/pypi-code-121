# ----------------------------------------------------------------------------
# Description    : Transport layer (abstract, IP, file, dummy)
# Git repository : https://gitlab.com/qblox/packages/software/qblox_instruments.git
# Copyright (C) Qblox BV (2020)
# ----------------------------------------------------------------------------


# -- include -----------------------------------------------------------------

from qblox_instruments.ieee488_2 import QcmQrmDummyTransport


# -- class -------------------------------------------------------------------

class PulsarDummyTransport(QcmQrmDummyTransport):
    """
    Class to replace Pulsar device with dummy device to support software
    stack testing without hardware. The class implements all mandatory,
    required and Pulsar specific SCPI calls. Call reponses are largely
    artifically constructed to be inline with the call's functionality
    (e.g. `*IDN?` returns valid, but artificial IDN data.) To assist
    development, the Q1ASM assembler has been completely implemented. Please
    have a look at the call's implentation to know what to expect from its
    response.
    """

    pass
