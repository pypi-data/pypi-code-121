"""dsc.py: Dynamic Security Codes module
"""

# Standard library imports

# Third party imports

# Local application imports
from common import hstr
from crypto import des

def generate_dcvv(udk: str, pan: str, atc: str, expiration_date: str):
    alternate_pan = F"{atc}{pan[4:]}"

    input_block = F"{alternate_pan}{expiration_date}"
    input_block = input_block + '0' * (32 - len(input_block))

    udk_a = udk[0:16]
    udk_b = udk[16:32]
    block_a = input_block[0:16]
    block_b = input_block[16:32]

    block_c = des.dea_e(udk_a, block_a)
    block_d = hstr.xor(block_c, block_b)
    block_e = des.dea_e(udk_a, block_d)
    block_f = des.dea_d(udk_b, block_e)
    block_g = des.dea_e(udk_a, block_f)
    block_h = hstr.dscan_decimalize(block_g)

    return block_h[0:3]

def generate_ivcvc3(udk: str, track: str) -> str:
    if (len(track) % 16) == 0:
        block = track + "8000000000000000"
    else:
        block = track + "80" + "0" * (16 - len(track) % 16 - 2)

    mac = des.mac_2_ede(udk, block)

    return mac[-4:]

def generate_cvc3(udk: str, block: str) -> str:
    return F"{int(des.tdea_2_ede(udk, block)[-4:], 16):05d}"
