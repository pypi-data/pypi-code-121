"""key_management.py
"""

# Standard library imports

# Third party imports

# Local application imports
from common import hstr
from crypto import des

def master_key_derivation_A(imk, pan, psn = '00'):
    """master_key_derivation_A(): ICC Master Key derivation (Option A)
    """
    X = pan + psn
    if len(X) < 16:
        X = '0' * (16 - len(X)) + X

    Y = X[-16:]

    Zl = des.tdea_2_ede(imk, Y)
    Zr = des.tdea_2_ede(imk, hstr.not_hstr(Y))

    return Zl + Zr
