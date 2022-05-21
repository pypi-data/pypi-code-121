# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
#
# Copyright 2008-2021 Neongecko.com Inc. | All Rights Reserved
#
# Notice of License - Duplicating this Notice of License near the start of any file containing
# a derivative of this software is a condition of license for this software.
# Friendly Licensing:
# No charge, open source royalty free use of the Neon AI software source and object is offered for
# educational users, noncommercial enthusiasts, Public Benefit Corporations (and LLCs) and
# Social Purpose Corporations (and LLCs). Developers can contact developers@neon.ai
# For commercial licensing, distribution of derivative works or redistribution please contact licenses@neon.ai
# Distributed on an "AS IS” basis without warranties or conditions of any kind, either express or implied.
# Trademarks of Neongecko: Neon AI(TM), Neon Assist (TM), Neon Communicator(TM), Klat(TM)
# Authors: Guy Daniels, Daniel McKnight, Regina Bloomstine, Elon Gasper, Richard Leeds
#
# Specialized conversational reconveyance options from Conversation Processing Intelligence Corp.
# US Patents 2008-2021: US7424516, US20140161250, US20140177813, US8638908, US8068604, US8553852, US10530923, US10530924
# China Patent: CN102017585  -  Europe Patent: EU2156652  -  Patents Pending

import hashlib
# import json
# import array
import struct

from .logger import LOG


def generate_hash(to_be_hashed):
    """
    Generates an SHA hash for the input string
    :param to_be_hashed: string to be hashed
    :return: list(int) hash
    """
    md = hashlib.sha512()
    input_array = bytearray()
    input_array.extend(map(ord, to_be_hashed))
    LOG.debug(list(input_array))
    md.update(bytearray(input_array))
    byte_data = md.digest()
    num_ints = int(len(byte_data))
    hashed = list(struct.unpack("b"*num_ints, byte_data))
    LOG.debug(hashed)
    return hashed


def encrypt(string):
    return string


def decrypt(string):
    return string
