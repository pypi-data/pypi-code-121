from apalib.AminoAcid import AminoAcid
from apalib.Atom import Atom
from apalib.DNA import DNA
from apalib.RNA import RNA
from apalib.HETATM import HETATM

class Container:
    def __init__(self):
        self.current_fetch = None
        self.PeptideChains = None
        self.DNAChains = None
        self.RNAChains = None
        self.HETATMChains = None

    def ClearAll(self):
        self.__init__()

    def SetFetch(self, fetch):
        self.current_fetch = fetch

    def GetFetch(self):
        return self.current_fetch

    def ClearFetch(self):
        self.current_fetch = None

    def SetProteinChains(self, pchain):
        self.PeptideChains = pchain

    def GetPeptideChains(self):
        return self.PeptideChains

    def SetDNAChains(self,dchain):
        self.DNAChains = dchain

    def GetDNAChains(self):
        return self.DNAChains

    def GetRNAChains(self):
        return self.RNAChains

    def SetRNAChains(self, rchain):
        self.RNAChains = rchain

    def GetHETATMChains(self):
        return self.HETATMChains

    def SetHETATMChains(self, hchain):
        self.HETATMChains = hchain

    #Return all residues from all chains as a single list
    def AsList(self, ordered=True):
        fullLst = []
        retLst = []
        lst = [self.PeptideChains, self.DNAChains, self.RNAChains, self.HETATMChains]
        for val in lst:
            if val is not None and len(val.keys()) != 0:
                fullLst = fullLst + list(val.values())
        for val in fullLst:
            retLst = retLst + list(val.values())
        return sorted(retLst, key=lambda val : val.number) if ordered else retLst
