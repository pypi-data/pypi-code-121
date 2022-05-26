import apalib.apalibExceptions
import apalib.apalibExceptions as apaExcept

from apalib import *

class PDB:
    def __init__(self):
        self.container = Container()

    def Contents(self):
        return self.container

    def Fetch(self, prot):
        # print("Fetching ", prot)
        import urllib.request
        url = r'https://files.rcsb.org/download/' + prot.strip() + '.pdb'
        try:
            with urllib.request.urlopen(url) as f:
                self.container.SetFetch(f.read().decode('utf-8'))
                self.Parse()
        except urllib.error.URLError:
            sys.stderr.write("The requested pdb code could not be retrieved or does not exist\n")

    # Wrapper for the ParsePDB file to allow functionality with a fetched protein
    def Parse(self):
        try:
            if self.container.GetFetch() is None:
                raise apaExcept.NoFetchError
            return self.ParsePDB(self.container.GetFetch().splitlines())
        except apaExcept.NoFetchError as e:
            sys.stderr.write(e.message)

    def ParsePDB(self, pdbFile):
        proteinChains = dict()
        DNAChains = dict()
        RNAChains = dict()
        HETATMChains = dict()
        for line in pdbFile:
            if line[0:4] == "ATOM" or line[0:6] == 'HETATM':
                # Create a new chain if needed
                chain = line[20:22].strip()
                if chain == '':
                    chain = '$'
                groupNumber = int("".join(chr for chr in line[22:27] if chr.isdigit()))
                atomNumber = int(line[6:11])
                id = line[11:16].strip()
                groupName = line[16:20].strip()
                coordinates = [float(line[27:38]), float(line[38:46]), float(line[46:55])]
                occupancy = float(line[55:60])
                bfactor = float(line[60:67])
                element = line[77:].strip()
                newAtom = config.Atom(number=atomNumber, coordinates=coordinates, id=id, occupancy=occupancy,
                               b_factor=bfactor, element=element, residue=groupName)

                # RNA atom
                if line[0:6] == "HETATM":
                    if chain not in HETATMChains:
                        HETATMChains[chain] = dict()
                    if groupNumber not in HETATMChains[chain]:
                        HETATMChains[chain][groupNumber] = config.HETATM(name=groupName, number=groupNumber)
                    HETATMChains[chain][groupNumber].InsertAtom(newAtom)
                elif len(groupName) == 1:
                    if chain not in RNAChains:
                        RNAChains[chain] = dict()
                    if groupNumber not in RNAChains[chain]:
                        RNAChains[chain][groupNumber] = config.RNA(name=groupName, number=groupNumber)
                    RNAChains[chain][groupNumber].InsertAtom(newAtom)

                elif len(groupName) == 2:
                    if chain not in DNAChains:
                        DNAChains[chain] = dict()
                    if groupNumber not in DNAChains[chain]:
                        DNAChains[chain][groupNumber] = config.DNA(name=groupName, number=groupNumber)
                    DNAChains[chain][groupNumber].InsertAtom(newAtom)

                elif len(groupName) == 3 or len(groupName) == 4:
                    if chain not in proteinChains:
                        proteinChains[chain] = dict()
                    if groupNumber not in proteinChains[chain]:
                        proteinChains[chain][groupNumber] = config.AminoAcid(name=groupName, number=groupNumber)
                    proteinChains[chain][groupNumber].InsertAtom(newAtom)

        # Postparsing functions
        self.container.SetProteinChains(proteinChains)
        self.container.SetDNAChains(DNAChains)
        self.container.SetRNAChains(RNAChains)
        self.container.SetHETATMChains(HETATMChains)

        for chain in self.container.GetPeptideChains():
            for index in self.container.GetPeptideChains()[chain]:
                self.container.GetPeptideChains()[chain][index].CalculateCentroid(self.container.GetPeptideChains()[chain][index].atoms)

    # def CountResidues(self, **kwargs):
    #     for key in kwargs:
    #         if key != 'find' or (key == 'find' and not isinstance(kwargs['find'], list)):
    #             raise apalib.apalibExceptions.BadKwarg('find=[residue_name1, residue_name2, ...]')
    #
    #     # If a specific residue is wanted
    #     if 'find' in kwargs:
    #
    #     else:
    #
    # #TODO GetMass() of a current fetch
    #
    #
    # def __StandardizeResidue(self, res, **kwargs):
    #     accepted_kwargs = ['']
    #


    def Validate(self, **kwargs):
        for key in kwargs:
            if key != 'pdb' or (key == 'pdb' and not isinstance(kwargs['pdb'], str)):
                raise apalib.apalibExceptions.BadKwarg('pdb=<pdb_to_validate>')