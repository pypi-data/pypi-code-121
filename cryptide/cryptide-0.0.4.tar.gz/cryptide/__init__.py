"""

                                   888    d8b      888
                                   888    Y8P      888
                                   888             888
 .d8888b 888d888 888  888 88888b.  888888 888  .d88888  .d88b.
d88P"    888P"   888  888 888 "88b 888    888 d88" 888 d8P  Y8b
888      888     888  888 888  888 888    888 888  888 88888888
Y88b.    888     Y88b 888 888 d88P Y88b.  888 Y88b 888 Y8b.
 "Y8888P 888      "Y88888 88888P"   "Y888 888  "Y88888  "Y8888
                      888 888
                 Y8b d88P 888
                  "Y88P"  888

The cryptide functions
"""

from cryptide.IC import *
from cryptide.ascii import *
from cryptide.bytes import *
from cryptide.enigma_bf import *
from cryptide import enigma_bf as enigma

__all__ = ['get_ascii_readable_stat', 'compute_ic', 'what_ic', 'checker_and_compute_ic', 'list_aggregation',
           'checker_ic', 'bytes_representation', 'get_unascii_stat', 'unascii_stoper', 'ascii_readable_stoper', 'check_config', 'check_permutation_letter', 'check_permutation_refletor_and_rotor', 'try_plugboard', 'full_try']

__version__ = '0.0.4'

__author__ = "Ursial"
