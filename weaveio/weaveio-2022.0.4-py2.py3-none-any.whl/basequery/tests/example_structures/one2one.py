from typing import Tuple, Dict

from weaveio.data import Data
from weaveio.file import File
from weaveio.hierarchy import Hierarchy, Multiple

"""
File1<-HierarchyA<-HierarchyB<-Multiple(HierarchyC)
                             <-HierarchyD
"""

class HierarchyF(Hierarchy):
    factors = ['f_factor_a']
    idname = 'id'


class HierarchyD(Hierarchy):
    factors = ['shared_factor_name']
    idname = 'id'


class HierarchyC(Hierarchy):
    factors = ['c_factor_a', 'c_factor_b', 'shared_factor_name']
    idname = 'id'


class HierarchyB(Hierarchy):
    parents = [Multiple(HierarchyC, 2, 2), HierarchyD]
    factors = ['b_factor_a', 'b_factor_b']
    idname = 'otherid'


class HierarchyA(Hierarchy):
    parents = [HierarchyB, Multiple(HierarchyF, 1, 3)]
    factors = ['a_factor_a', 'a_factor_b']
    idname = 'id'
    version_on = ['hierarchyb']


class File1(File):
    parents = [HierarchyA]
    match_pattern = '*.fits'

    @classmethod
    def read(cls, directory, fname) -> 'File':
        fname = str(fname)
        hierarchyf = HierarchyF(id=fname, f_factor_a='a')
        hierarchyd = HierarchyD(id=fname, shared_factor_name='shared_d')
        hierarchyc1 = HierarchyC(id=fname+'1', c_factor_a='a', c_factor_b='b', shared_factor_name='shared_c1')
        hierarchyc2 = HierarchyC(id=fname+'2', c_factor_a='a', c_factor_b='b', shared_factor_name='shared_c2')
        hierarchyb = HierarchyB(otherid=fname, b_factor_b='b',  b_factor_a='a', hierarchycs=[hierarchyc1, hierarchyc2], hierarchyd=hierarchyd)
        return cls(fname, hierarchya=HierarchyA(id=fname, hierarchyb=hierarchyb, a_factor_a='a', a_factor_b='b', hierarchyfs=[hierarchyf]))


class MyDataOne2One(Data):
    filetypes = [File1]
