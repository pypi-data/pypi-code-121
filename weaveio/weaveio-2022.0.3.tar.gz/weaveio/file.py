import re
from pathlib import Path
from typing import Union, List, Tuple, Dict

from astropy.io import fits
from astropy.io.fits.hdu.base import _BaseHDU

from weaveio.graph import Graph
from weaveio.hierarchy import Hierarchy, Multiple


class File(Hierarchy):
    is_template = True
    idname = 'fname'
    factors = ['path']
    match_pattern = '*.file'
    antimatch_pattern = '^$'
    recommended_batchsize = None
    parts = [None]

    @classmethod
    def length(cls, path, part=None):
        raise NotImplementedError

    def open(self):
        try:
            return fits.open(self.data.rootdir / self.fname)
        except AttributeError:
            return fits.open(self.fname)

    def __init__(self, **kwargs):
        if 'fname' in kwargs:
            kwargs['fname'] = str(kwargs['fname'])
        if 'path' in kwargs:
            kwargs['path'] = str(kwargs['path'])
        else:
            kwargs['path'] = None
        super().__init__(tables=None, **kwargs)

    @classmethod
    def get_batches(cls, path, batch_size, parts: List[Union[str, None]] = None):
        if parts is None:
            parts = cls.parts
        parts = {p for p in parts if p in cls.parts}
        if batch_size is None:
            return ((slice(None, None), part) for part in parts)
        return ((slice(i, i + batch_size), part) for part in parts for i in range(0, cls.length(path, part), batch_size))

    @classmethod
    def match_file(cls, directory: Union[Path, str], fname: Union[Path, str], graph: Graph):
        """Returns True if the given fname in a given directory can be read by this class of file hierarchy object"""
        fname = Path(fname)
        return re.match(cls.match_pattern, fname.name, re.IGNORECASE) and not re.match(cls.antimatch_pattern, fname.name, re.IGNORECASE)

    @classmethod
    def match_files(cls,  directory: Union[Path, str], graph: Graph):
        """Returns all matching files within a directory"""
        return (f for f in Path(directory).rglob('*.fit*') if cls.match_file(directory, f, graph))

    @classmethod
    def check_mos(cls, path):
        return 'IFU' not in fits.open(path)[0].header['OBSMODE']

    @classmethod
    def read(cls, directory: Union[Path, str], fname: Union[Path, str], slc: slice = None, part=None) -> 'File':
        raise NotImplementedError

    @classmethod
    def read_hdus(cls, directory: Union[Path, str], fname: Union[Path, str],
                  **hierarchies: Union[Hierarchy, List[Hierarchy]]) -> Tuple[Dict[int,'HDU'], 'File', List[_BaseHDU]]:
        path = Path(directory) / Path(fname)
        relative_path = path.relative_to(Path(directory))
        file = cls(fname=path.name, path=str(relative_path), **hierarchies)
        hdus = [i for i in fits.open(path)]
        if len(hdus) != len(cls.hdus):
            raise TypeError(f"Class {cls} asserts there are {len(cls.hdus)} HDUs ({list(cls.hdus.keys())})"
                            f" whereas {path} has {len(hdus)} ({[i.name for i in hdus]})")
        hduinstances = {}
        for i, ((hduname, hduclass), hdu) in enumerate(zip(cls.hdus.items(), hdus)):
            hduinstances[i] = hduclass.from_hdu(hduname, hdu, i, file)
        return hduinstances, file, hdus

    def read_product(self, product_name):
        self.build_index()
        return getattr(self, f'read_{product_name}')()


class HDU(Hierarchy):
    is_template = True
    parents = [File]
    factors = ['extn', 'name']
    identifier_builder = ['file', 'extn', 'name']
    products = ['header', 'data']

    @classmethod
    def from_hdu(cls, name, hdu, extn, file):
        input_dict = {}
        input_dict[cls.parents[0].singular_name] = file
        input_dict['extn'] = extn
        input_dict['name'] = name
        hdu = cls(**input_dict)
        for product in cls.products:
            hdu.attach_product(product, hdu)
        return hdu


class BaseDataHDU(HDU):
    is_template = True


class PrimaryHDU(HDU):
    products = ['header']


class TableHDU(BaseDataHDU):
    pass


class BinaryHDU(BaseDataHDU):
    pass
