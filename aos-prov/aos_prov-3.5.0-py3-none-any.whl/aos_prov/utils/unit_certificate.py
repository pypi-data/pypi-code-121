#
#  Copyright (c) 2018-2022 Renesas Inc.
#  Copyright (c) 2018-2022 EPAM Systems Inc.
#

"""Unit certificate object."""


class UnitCertificate:
    """Unit certificate object."""

    def __init__(self):
        """Unit certificate object."""
        self._cert_type = None
        self._csr = None
        self._certificate = None

    @property
    def cert_type(self) -> str:
        """Certificate type (Required type list is taken from unit)."""
        return self._cert_type

    @cert_type.setter
    def cert_type(self, cert_type):
        self._cert_type = cert_type

    @property
    def csr(self) -> str:
        """Certificate Signing Request."""
        return self._csr

    @csr.setter
    def csr(self, csr_value):
        self._csr = csr_value

    @property
    def certificate(self) -> str:
        """Certificate."""
        return self._certificate

    @certificate.setter
    def certificate(self, cert):
        self._certificate = cert
