import apalib.config
import apalib.apalibExceptions
from apalib.Container import Container
from apalib.AminoAcid import AminoAcid
from apalib.Atom import Atom
from apalib.DNA import DNA
from apalib.RNA import RNA
from apalib.HETATM import HETATM
from apalib.pdb import PDB



# TODO work on error messages
# try:
#     requests.get(r"http://www.google.com", timeout=5)
# except :
#     sys.stderr.write(apalib.apalibExceptions.BadInternet())


# TODO Move **ALL HARDCODED DATA** into a json
# TODO Make error messages a full string (functional with stderr.write())
# TODO get this to work with DNA and RNA domains https://pdb101.rcsb.org/learn/guide-to-understanding-pdb-data/primary-sequences-and-the-pdb-format
# Parsing DNA/RNA should be essentially the same as an amino acid atom-group, with some intricacies. 1pyi is a good example
# TODO Check other PDB standards
# TODO Ensure functionality with symmetry pairs
# TODO Make set_name a thing everywhere


#  Naive approach to calculating isoelectric point at a specific pH

def getIEP(pHofInterest):
    global CONTAINER
    curr_protein_chains = CONTAINER.PeptideChains

    # initialize dict of counts
    total_counts = {'NTERM': 0, 'CTERM': 0, 'CYS': 0, 'ASP': 0, 'GLU': 0, 'HIS': 0, 'LYS': 0, 'ARG': 0, 'TYR': 0}
    import copy
    for key, value in curr_protein_chains.items():
        current_chain = value
        #TODO Add check for termini (in case section of a protein is checked instead of a full protein)
        #TODO Are there pKas for nucleic acids?

        total_counts['NTERM'] += 1
        total_counts['CTERM'] += 1

        for key, value in current_chain.items():
            if value.name == "CYS":
                total_counts['CYS'] += 1
            elif value.name == "ASP":
                total_counts['ASP'] += 1
            elif value.name == "GLU":
                total_counts['GLU'] += 1
            elif value.name == "HIS":
                total_counts['HIS'] += 1
            elif value.name == "LYS":
                total_counts['LYS'] += 1
            elif value.name == "ARG":
                total_counts['ARG'] += 1
            elif value.name == "TYR":
                total_counts['TYR'] += 1



    print(total_counts)

    # TODO Add pKa values to JSON file
    # using "EMBOSS" pKa's

    sum_charges = 0

    if pHofInterest < 8.6:
        sum_charges += total_counts['NTERM']
    if pHofInterest > 3.6:
        sum_charges -= total_counts['CTERM']
    if pHofInterest > 8.5:
        sum_charges -= total_counts['CYS']
    if pHofInterest > 3.9:
        sum_charges -= total_counts['ASP']
    if pHofInterest > 4.1:
        sum_charges -= total_counts['GLU']
    if pHofInterest < 6.5:
        sum_charges += total_counts['HIS']
    if pHofInterest < 10.8:
        sum_charges += total_counts['LYS']
    if pHofInterest < 12.5:
        sum_charges += total_counts['ARG']
    if pHofInterest > 10.1:
        sum_charges -= total_counts['TYR']

    return sum_charges










# TODO in all GETTERS in each class, add a check to see if variable exists
# if var in self.__dict__:
#   return var
# return None


# TODO Complete the below functions before pushing version 1.0.0

# def SurfaceArea(**kwargs):
#     if 'domain' not in kwargs:
#         sys.stderr.write("No domain provided. Specify using SurfaceArea(domain=val)\n")
#     if 'num_dots' not in kwargs:
#         sys.stderr.write("Number of dots not provided. Specify using SurfaceArea(num_dots=val)\n")
#     if 'solvent_radius' not in kwargs:
#         sys.stderr.write("Solvent radius not provided. Specify using SurfaceArea(solvent_radius=val)\n")
#     print("stub")
#
# def GetDistance(coor1, coor2):
#     return ((coor1[0] - coor2[0])**2 + (coor1[1] - coor2[1])**2 + (coor1[2] - coor2[2])**2)**.5
#
# def VectorPair(self, AA1, AA2):
#     # Slope of line made from CA --> CENTROID
#     CA1 = AA1.GetCA()
#     CA2 = AA2.GetCA()
#     # XY orthogonal projection
#     m1 = (AA1.GetCentroid()[1] - CA1.GetCoordinates()[1]) / (AA1.GetCentroid()[0] - CA1.GetCoordinates()[0])
#     m2 = (AA2.GetCentroid()[1] - CA2.GetCoordinates()[1]) / (AA2.GetCentroid()[0] - CA2.GetCoordinates()[0])
#     # Intersection point
#     #
#     #               y_2 - y_1 + m_1x_1 - m_2x_2
#     #   x_int =    ------------------------------
#     #                       m_1 - m_2
#
#     x_int = (AA2.GetCentroid()[1] - AA1.GetCentroid()[1] + m1 * AA1.GetCentroid()[0] - m2 * AA2.GetCentroid()[0])
#     #/ (m1 - m2)
#     # Cast back into 3D
#     #
#     #        x - x_1
#     #   z = --------- * c + z_1
#     #           a
#
#     y1 = (x_int - AA1.GetCentroid()[0]) / AA1.vector[0] * AA1.vector[1] + AA1.GetCentroid()[1]
#     y2 = (x_int - AA2.GetCentroid()[0]) / AA2.vector[0] * AA2.vector[1] + AA2.centroid[1]
#
#     z1 = (x_int - AA1.GetCentroid()[0]) / AA1.vector[0] * AA1.vector[2] + AA1.GetCentroid()[2]
#     z2 = (x_int - AA2.GetCentroid()[0]) / AA2.vector[0] * AA2.vector[2] + AA2.GetCentroid()[2]
#     return abs(z1 - z2), [x_int, y1, z1], [x_int, y2, z2]
#
# def CheckBridge(object1, object2):
#     print("stub")

# TODO Make sure ALL flags are properly cleared automatically

