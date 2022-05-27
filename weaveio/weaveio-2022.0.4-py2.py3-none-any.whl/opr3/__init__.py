from weaveio.data import Data as BaseData
from weaveio.opr3.l1files import RawFile, L1SingleFile, L1StackFile, L1SuperstackFile, L1SupertargetFile
from weaveio.opr3.l2files import L2StackFile, L2SuperstackFile, L2SingleFile, L2SupertargetFile


class Data(BaseData):
    filetypes = [
        RawFile,
        L1SingleFile, L2SingleFile,
        L1StackFile, L2StackFile,
        L1SuperstackFile, L2SuperstackFile,
        L1SupertargetFile, L2SupertargetFile
]