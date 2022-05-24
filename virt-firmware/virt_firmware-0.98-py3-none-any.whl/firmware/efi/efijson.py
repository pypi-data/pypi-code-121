#!/usr/bin/python
""" json support for efi """
import json

from virt.firmware.efi import guids
from virt.firmware.efi import ucs16
from virt.firmware.efi import efivar

# pylint: disable=no-self-use
class EfiJSONEncoder(json.JSONEncoder):
    """  serialise efi data types as json """

    def efivar(self, o):
        retval = {
            'name' : str(o.name),
            'guid' : str(o.guid),
            'attr' : int(o.attr),
            'data' : bytes(o.data).hex(),
        }
        if o.time:
            retval['time'] = o.bytes_time().hex()
        return retval

    def efivarlist(self, o):
        l = []
        for (key, item) in o.items():
            l.append(item)
        r = {
            'version' : 2,
            'variables' : l,
        }
        return r

    def default(self, o):
        if isinstance(o, efivar.EfiVar):
            return self.efivar(o)
        if isinstance(o, efivar.EfiVarList):
            return self.efivarlist(o)
        return json.JSONEncoder.default(self, o)

def efi_decode(obj):
    if 'guid' in obj:
        var = efivar.EfiVar(ucs16.from_string(obj.get('name')),
                            guid = guids.parse_str(obj.get('guid')),
                            attr = obj.get('attr'),
                            data = bytes.fromhex(obj.get('data')))
        if obj.get('time'):
            var.parse_time(bytes.fromhex(obj.get('time')), 0)
        return var

    if 'variables' in obj:
        varlist = efivar.EfiVarList()
        for var in obj.get('variables'):
            varlist[str(var.name)] = var
        return varlist

    return obj
