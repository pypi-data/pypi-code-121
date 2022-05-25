import json
import numpy as np
from ase import Atoms

""" This module includes generic data input/output/manipulation methods. """

def translate_keys(dct, key, transl):
    """ Translates all keys which match 'key' in 'dct' into 'transl' """
    new = {}
    for k, val in dct.items():
        if isinstance(val, dict):
            newval = translate_keys(val, key, transl)
        elif isinstance(val, list):
            newval = []
            for item in val:
                if isinstance(item, dict):
                    newval.append(translate_keys(item, key, transl))
                else:
                    newval.append(item)
        else:
            newval = val
        if k == key:
            new[transl] = newval
        else:
            new[k] = newval
    return new

def ddump(obj):
    """ Dumps a dictionary of objects attributes """
    dct = {}
    lst = [
        attr for attr in dir(obj) if not attr.startswith('__') 
        and not callable(getattr(obj,attr))
        ]
    for item in lst:
        o = getattr(obj,item)
        if type(o) in [bool, int, float, str, None]:
            dct[item] = o
        if type(o) in [list, tuple, dict]:
            dct[item] = o
        elif hasattr(o, 'todict'):
            dct[item] = o.todict()
        elif o.__class__ == np.ndarray:
            dct[item] = o.tolist()
        else:
            pass
    return dct

def jdefault(obj):
    """ Returns a JSON serializable object """
    from ase import Atoms
    from ase.db.row import atoms2dict

    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, Atoms):
        return atoms2dict(obj)
    elif hasattr(obj, 'todict'):
        return obj.todict()
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    else:
        raise TypeError('Not serializable')
'''
def json_load_byteified(file_handle):
    return _byteify(
        json.load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )

def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )


def _byteify(data, ignore_dicts = False):
    if isinstance(data, unicode):
        return data.encode('utf-8')
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.items()
        }
    return data
'''

def single_entry(entry):
    if isinstance(entry, list):
        assert len(entry) == 1, 'can process only one entry at a time'
        entry = entry[0]
    return entry

def dict_update(dct, maplist, filename):
    """ In-place update of dictionary datadict at position specified by 
    maplist with data from file, i.e. dct[maplist[0]][maplist[1]]... = data
    """
    from functools import reduce
    import operator

    with open(filename, 'r') as inp:
        data = json.load(inp)

    if isinstance(data, dict):
        reduce(operator.getitem, maplist[:-1], dct)[maplist[-1]].update(data)
    else:
        reduce(operator.getitem, maplist[:-1], dct)[maplist[-1]] = data

class GeneratorCounter(object):
    """ wrap a generator object to count the number of elements yielded """
    def __init__(self, generator):
        self.total = 0
        self.generator = generator

    def __iter__(self):
        return self

    def __next__(self):
        nxt = next(self.generator)
        self.total += 1
        return nxt

    def __len__(self):
        """ return the current number of elements yielded """
        return self.total

def cleanup_atoms_dict(adict):
    """ delete keywords in dictionary not allowed in Atoms.__init__ """

    dellist = ['unique_id', 'magmom', 'calculator', 'calculator_parameters',
               'energy', 'forces', 'dipole', 'stress']
    subdict = {'initial_magmoms': 'magmoms'}
    for key in subdict:
        if key in adict:
            adict[subdict[key]] = adict.pop(key)
    for key in dellist:
        if key in adict:
            del adict[key]
    return adict

@classmethod
def from_dict(cls, adict):
    """ deserialize json serializable dictionaries to atoms objects """
    from ase.io import jsonio    
    from ase.constraints import dict2constraint

    adict_ = jsonio.decode(jsonio.encode(cleanup_atoms_dict(adict)))
    if 'constraints' in adict_:
        constr = adict_.pop('constraints')
        if isinstance(constr, list):
            adict_['constraint'] = [dict2constraint(c) for c in constr]
        else:
            adict_['constraint'] = [dict2constraint(constr)]

    return cls(**adict_)

Atoms.from_dict = from_dict

def atoms2dict(atoms):
    """ convert Atoms object to a dictionary used to recreate the object """
    from ase.io import jsonio
    from ase.db.row import atoms2dict
    import json

    adict = cleanup_atoms_dict(atoms2dict(atoms))
    return json.loads(jsonio.encode(adict))
