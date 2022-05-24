#!/usr/bin/python
""" linux efivarfs varstore parser """
import os
import logging

from virt.firmware.efi import guids
from virt.firmware.efi import ucs16
from virt.firmware.efi import efivar

# pylint: disable=too-few-public-methods
class LinuxVarStore:
    """  class for linux efivarfs varstore """

    @staticmethod
    def get_varlist(path = '/sys/firmware/efi/efivars',
                    volatile = False):

        varlist = efivar.EfiVarList()
        if not os.path.isdir(path):
            return varlist

        logging.info('reading linux varstore from %s', path)
        with os.scandir(path) as it:
            for entry in it:
                if not entry.is_file():
                    continue
                name = entry.name[ : len(entry.name) - 37 ]
                guid = entry.name[ len(entry.name) - 36 : ]
                filename = os.path.join(path, entry.name)
                with open(filename, "rb") as f:
                    attr = int.from_bytes(f.read(4), byteorder='little', signed=False)
                    data = f.read()
                if attr & efivar.EFI_VARIABLE_NON_VOLATILE or volatile:
                    var = efivar.EfiVar(ucs16.from_string(name),
                                        guid = guids.parse_str(guid),
                                        attr = attr, data = data)
                    varlist[name] = var
        return varlist
