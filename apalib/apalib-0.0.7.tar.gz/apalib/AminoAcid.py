import sys
# global ONE_LETTER
# global THREE_LETTER
# global FULL_NAME
from types import FunctionType
from apalib.config import *
global FLAGS
FLAGS = {}


class AminoAcid:
    def __init__(self, **kwargs):
        self.number = None
        self.atoms = None
        self.name = None
        self.rotamer = None
        self.vector = None
        self.heptad = None
        self.centroid = None
        set_name = True
        if 'set_name' in kwargs:
            set_name = kwargs['set_name']
        if 'name' in kwargs:
            self.SetName(kwargs['name'], set_name)
        if 'number' in kwargs:
            self.SetNumber(kwargs['number'])
        if 'atoms' in kwargs:
            self.SetAtoms(kwargs['atoms'])

    def AddAttribute(self, attr, var):
        self.__dict__[attr] = var

    def SetNumber(self, num):
        self.number = num

    def SetAtoms(self, atoms):
        self.atoms = atoms
        self.CalculateCentroid(atoms)

    def InsertAtom(self, atom):
        if self.atoms is None:
            self.atoms = list()
        self.atoms.append(atom)

    def GetAtoms(self):
        return self.atoms

    def GetRotamers(self, **kwargs):
        accepted = ['unique']
        for key in kwargs.keys():
            if key not in accepted:
                raise apalib.apalibExceptions.BadKwarg(accepted)

        if self.rotamer is not None:
            return self.rotamer

        if 'unique' in kwargs.keys() and isinstance(kwargs['unique'], (bool)):
            unique = kwargs['unique']
        else:
            unique = False

        retDict = {'Common':[]}
        if self.atoms is not None:
            for atom in self.atoms:
                if atom.rotation is None or atom.rotation == '':
                    retDict['Common'].append(atom)
                    continue
                if atom.rotation not in retDict.keys():
                    retDict[atom.rotation] = []
                retDict[atom.rotation].append(atom)
        if unique is False:
            for lst in [retDict[key] for key in retDict.keys() if key != 'Common']:
                lst += retDict['Common']
        return retDict






    def GetCA(self):
        if self.atoms is None:
            return None
        for atom in self.atoms:
            if atom.GetID() == 'CA':
                return atom
        return None

    def SetName(self, name, set_name):
        if not set_name:
            self.name = name
            self.RaiseFlag('NO_NAME_CHECK')
            return
        else:
            self.ClearFlag('NO_NAME_CHECK')
        if len(name) == 3 and name in THREE_LETTER:
            self.name = name
        elif len(name) == 3 and name not in THREE_LETTER:
            self.name = None
        elif len(name) == 1:
            self.name = self.OneToThree(name)
        elif len(name) <= 4:
            if name[-3:] in THREE_LETTER:
                self.name = name[-3:]
                self.rotamer = name[:-3]
            else:
                self.name = None
        elif len(name) == 2:
            self.name = None
        if self.name is not None:
            self.RaiseFlag('BAD_NAME')
        else:
            self.RaiseFlag('BAD_NAME')
        if self.name is not None and self.rotamer is not None:
            self.RaiseFlag('MARKED')
        elif self.name is not None and self.rotamer is None:
            self.ClearFlag('MARKED')

    def SetHeptad(self, heptad):
        self.heptad = heptad

    def CalculateCentroid(self, atoms):
        # *For Glycine, only the alpha carbon is considered
        # *For Alanine, only the beta carbon is considered
        AAs = {
            "SER": ['OG'],
            "CYS": ['SG'],
            "SEC": ['SE'],
            "GLY": ['CA'],
            "ALA": ['CB'],
            "THR": ['OG1', 'CG2'],
            "PRO": ['CG', 'CD'],
            "VAL": ['CG1', 'CG2'],
            "ASP": ['CG', 'OD1', 'OD2'],
            "ASN": ['CG', 'OD1', 'ND2'],
            "ILE": ['CG1', 'CG2', 'CD1'],
            "LEU": ['CG', 'CD1', 'CD2'],
            "MET": ['CG', 'SD', 'CE'],
            "LYS": ['CG', 'CD', 'CE', 'NZ'],
            "GLU": ['CG', 'CD', 'OE1', 'OE2'],
            "GLN": ['CG', 'CD', 'OE1', 'NE2'],
            "HIS": ['CG', 'ND1', 'CD2', 'CE1', 'NE2'],
            "ARG": ['CG', 'CD', 'NE', 'CZ', 'NH1', 'NH2'],
            "PHE": ['CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ'],
            "TYR": ['CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ', 'OH'],
            "TRP": ['CG', 'CD1', 'CD2', 'NE1', 'CE2', 'CE3', 'CZ2', 'CZ3', 'CH2']
        }
        # TODO Deal with non-1 occupancy
        if len(self.name) == 3 and self.name in AAs:
            # If residue is not specified
            x_coord = 0
            y_coord = 0
            z_coord = 0
            num_atoms = 0
            for atom in [atom for atom in atoms if atom.id in AAs[self.name]]:
                if atom.element == 'H':
                    continue
                x_coord += atom.GetCoordinates()[0]
                y_coord += atom.GetCoordinates()[1]
                z_coord += atom.GetCoordinates()[2]
                num_atoms += 1
            self.centroid = list()
            try:
                self.centroid.append(x_coord / num_atoms)
                self.centroid.append(y_coord / num_atoms)
                self.centroid.append(z_coord / num_atoms)
            except ZeroDivisionError:
                self.centroid.clear()
                beta = [atom for atom in atoms if atom.id == 'CB']
                alpha = [atom for atom in atoms if atom.id == 'CA']
                if len(beta) != 0:
                    self.centroid.append(beta[0].coordinates[0])
                    self.centroid.append(beta[0].coordinates[1])
                    self.centroid.append(beta[0].coordinates[2])
                    self.RaiseFlag('B_CENTROID')
                elif len(alpha) != 0:
                    self.centroid.append(alpha[0].coordinates[0])
                    self.centroid.append(alpha[0].coordinates[1])
                    self.centroid.append(alpha[0].coordinates[2])
                    self.RaiseFlag('A_CENTROID')
                else:
                    self.centroid = None
                    self.vector = None
                    self.RaiseFlag('BAD_CENTROID')
                    return
            # After all that, set the centroidal vector
            self.vector = [self.centroid[0] - self.GetCA().GetCoordinates()[0],
                           self.centroid[1] - self.GetCA().GetCoordinates()[1],
                           self.centroid[2] - self.GetCA().GetCoordinates()[2]]

        elif len(self.name) == 4 and self.name[1:] in AAs:
            sys.stderr.write("ROTAMER!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        else:
            sys.exit("UNKNOWN AMINO ACID YO. DO SOMETHING ABOUT THIS!!!!!")

    def GetCentroid(self):
        return self.centroid

    @staticmethod
    def OneToThree(oln):
        if oln in ONE_LETTER:
            try:
                return ONE_LETTER[oln]
            except KeyError:
                return None

    @staticmethod
    def NameToThree(name):
        if name in FULL_NAME:
            try:
                return FULL_NAME[name]
            except KeyError:
                return None

    @staticmethod
    def CheckFlag(f):
        global FLAGS
        if f in FLAGS:
            return FLAGS[f]
        return False

    @staticmethod
    def RaiseFlag(flag):
        global FLAGS
        FLAGS[flag] = True

    @staticmethod
    def ClearFlag(flag):
        global FLAGS
        FLAGS[flag] = False

    # TODO These would be pretty cool to implement if possible. Open and write to a new python file that these access?
    @staticmethod
    def Set_lt(str):
        print('stub')

    @staticmethod
    def Set_repr(str):
        print('stub')


    def Set_str(self, str):
        return

    def __lt__(self, other):
        return self.number < other.number

    def __repr__(self):
        return f"RESIDUE: {self.name}, NUMBER: {self.number}"

    def __str__(self):
        return f"{self.name} {self.number}"


# Shoved down here for cleanliness
global ONE_LETTER
ONE_LETTER = {
    "R": 'ARG',
    "H": 'HIS',
    "K": 'LYS',
    "D": 'ASP',
    "E": 'GLU',
    "S": 'SER',
    "T": 'THR',
    "N": 'ASN',
    "Q": 'GLN',
    "C": 'CYS',
    "U": 'SEC',
    "G": 'GLY',
    "P": 'PRO',
    "A": 'ALA',
    "V": 'VAL',
    "I": 'ILE',
    "L": 'LEU',
    "M": 'MET',
    "F": 'PHE',
    "Y": 'TYR',
    "W": 'TRP',
    "O": 'PYL'
}

global THREE_LETTER
THREE_LETTER = {
    "ARG": 'R',
    "HIS": 'H',
    "LYS": 'K',
    "ASP": 'D',
    "GLU": 'E',
    "SER": 'S',
    "THR": 'T',
    "ASN": 'N',
    "GLN": 'G',
    "CYS": 'C',
    "SEC": 'U',
    "GLY": 'G',
    "PRO": 'P',
    "ALA": 'A',
    "VAL": 'V',
    "ILE": 'I',
    "LEU": 'L',
    "MET": 'M',
    "PHE": 'F',
    "TYR": 'Y',
    "TRP": 'W',
    "PYL": 'O'
}

global FULL_NAME
FULL_NAME = {
    "ALANINE": 'ALA',
    "CYSTEINE": 'CYS',
    "ASPARTIC ACID": 'ASP',
    "ASPARTATE": 'ASP',
    "GLUTAMIC ACID": 'GLU',
    "GLUTAMATE": 'GLU',
    "PHENYLALANINE": 'PHE',
    "GLYCINE": 'GLY',
    "HISTIDINE": 'HIS',
    "ISOLEUCINE": 'ILE',
    "LYSINE": 'LYS',
    "LEUCINE": 'LEU',
    "METHIONINE": 'MET',
    "ASPARAGINE": 'ASN',
    "PYRROLYSINE": 'PYL',
    "PROLINE": 'PRO',
    "GLUTAMINE": 'GLN',
    "ARGININE": 'ARG',
    "SERINE": 'SER',
    "THREONINE": 'THR',
    "SELENOCYSTEINE": 'SEC',
    "VALINE": 'VAL',
    "TRYPTOPHAN": 'TRP',
    "TYROSINE": 'TYR',
}
