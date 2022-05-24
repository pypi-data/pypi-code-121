#!/usr/bin/python
""" efi x509 certificates """

from pkg_resources import resource_filename

# redhat: PK + KEK key
REDHAT_PK = resource_filename('virt.firmware', 'certs/RedHatSecureBootPKKEKkey1.pem')

# microsoft: KEK key
MS_KEK = resource_filename('virt.firmware', 'certs/MicrosoftCorporationKEKCA2011.pem')

# microsoft: used to sign windows
MS_WIN = resource_filename('virt.firmware', 'certs/MicrosoftWindowsProductionPCA2011.pem')

# microsoft: used to sign 3rd party binaries (shim.efi, drivers).
MS_3RD = resource_filename('virt.firmware', 'certs/MicrosoftCorporationUEFICA2011.pem')
