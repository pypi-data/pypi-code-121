global FLAGS
FLAGS = {}

class HETATM:
    def __init__(self, **kwargs):
        self.number = None
        self.atoms = None
        self.name = None

        if 'name' in kwargs:
            self.SetName(kwargs['name'])
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

    def SetName(self, name):
        self.name = name

    def ClearFlags(self):
        self.flags.clear()

    def CalculateCentroid(self, atoms):
        n = 0
        x = 0
        y = 0
        z = 0
        for atom in atoms:
            n += 1
            x += atom.GetCoordinates()[0]
            y += atom.GetCoordinates()[1]
            z += atom.GetCoordinates()[2]
        self.centroid = [x/n, y/n, z/n]

    def GetCentroid(self):
        if 'centroid' in self.__dict:
            return self.centroid
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

    def __lt__(self, other):
        return self.number < other.number

    def __repr__(self):
        return f"RESIDUE: {self.name}, NUMBER: {self.number}"

    def __str__(self):
        return f"{self.name} {self.number}"
