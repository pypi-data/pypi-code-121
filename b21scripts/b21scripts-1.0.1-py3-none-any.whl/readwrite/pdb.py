import sys
import logging
import numpy
import os
import re
from .interface import Interface

class PDB(Interface):
    """Read and write pdb files
    
    The pdb class contains functions for reading pdb files to
    a dictionary object where various calculations can be
    performed on it and then writing it back out again.
    """
    def __init__(self, pdbfile=None):
        ###start a log file
        self.logger = logging.getLogger('readwrite.PDB')
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s: %(levelname)s: %(name)s: %(message)s',"[%Y-%m-%d %H:%M:%S]")
        streamhandler = logging.StreamHandler()
        streamhandler.setFormatter(formatter)
        if len(self.logger.handlers) == 0:
            self.logger.addHandler(streamhandler)
            self.logger.info(f'Starting a new readwrite.PDB job')        
        ###DEFINE SOME PARAMETERS
        self.type = 'pdb'
        self.converter = {
            'GLY': ('Glycine','G', 57.05),
            'PRO': ('Proline','P', 97.12),
            'ALA': ('Alanine','A', 71.09),
            'VAL': ('Valine','V', 99.14),
            'LEU': ('Leucine','L', 113.16),
            'ILE': ('Isoleucine','I', 113.16),
            'MET': ('Methionine','M', 131.19),
            'CYS': ('Cysteine','C', 103.15),
            'PHE': ('Phenylalanine', 'F', 147.18),
            'TYR': ('Tyrosine','Y', 163.18),
            'TRP': ('Tryptophan','W', 186.12),
            'HIS': ('Histidine','H', 137.14),
            'LYS': ('Lysine','K', 128.17),
            'ARG': ('Arginine','R', 156.19),
            'GLN': ('Glutamine','Q', 128.14),
            'ASN': ('Asparagine','N', 115.09),
            'GLU': ('Glutamic Acid','E', 129.12),
            'ASP': ('Aspartic Acid','D', 114.11),
            'SER': ('Serine','S', 87.08),
            'THR': ('Threonine','T', 101.11)
        }

        self.hashdata = {}

        ###Check file exists and is of right type
        if pdbfile == None:
            self.pdbfile = None
            self.logger.info('Will create an empty pdb dictionary')

        elif os.path.isfile(pdbfile) and pdbfile[-4:] == '.pdb':
            self.pdbfile = pdbfile
        else:
            sys.exit(str(pdbfile)+' either does not exist or is not of type ".pdb"')
    def input_dict(self, input_dict):
        self.logger.info('Reading in PDB data as a dictionary')
        if type(input_dict) == type({}):
            self.hashdata = input_dict

    def return_dict(self):
        self.logger.info('Returning PDB data as a dictionary')
        return self.hashdata

    def ReturnSeq(self, code=1):
        seq = []

        for index in self.hashdata.keys():
            if self.hashdata[index]['record_type'] == 'ATOM' and self.hashdata[index]['atom_name'] == 'CA':
                if self.hashdata[index]['residue'] in self.converter.keys():
                    if code == 1:
                        seq.append(self.converter[self.hashdata[index]['residue']][1])
                    else:
                        seq.append(self.hashdata[index]['residue'])
                else:
                    if code == 1:
                        seq.append('X')
                    else:
                        seq.append('XXX')
        if 'X' in seq:
            self.logger.info('There are unknown residue types in the structure')
        return seq

    def ReturnPdbFileName(self):
        if self.pdbfile[-4:] == '.pdb':
            return self.pdbfile[:-4]
        else:
            return 'None'
        
    def ReturnMolecularWeight(self, unit='Kd'):
        self.logger.info('Calculating molecular weight')
        mw = 0
        for aa in self.ReturnSeq(3):
            if aa in self.converter.keys():
                mw += self.converter[aa][2]
            else:
                mw += 110
        if unit == 'Kd':
            return round(mw / 1000, 1)
        elif unit == 'Da':
            return mw
        else:
            self.logger.error("ReturnMolecularWeight accepts units 'Kd' or 'Da'")
            return 0
    def ReturnExtinctionCoefficient(self, unit='absorbance'):
        self.logger.info('Calculating extinction coefficient')
        myseq = self.ReturnSeq(1)
        ec = myseq.count('W') * 5500.0 + myseq.count('Y') * 1490.0 + myseq.count('C') * 125.0
        if unit == 'absorbance':
            return ec / self.ReturnMolecularWeight('Da')
        elif unit == 'extinction':
            return ec
        else:
            self.logger.error("ReturnExtinctionCoefficient accepts units 'absorbance' or 'extinction'")
            return 0


    def Invert(self):
        self.logger.info('Inverting the structure')
        for index in self.hashdata.keys():
            if self.hashdata[index]['record_type'] == 'ATOM' or self.hashdata[index]['record_type'] == 'HETATM':
                self.hashdata[index]['z'] = self.hashdata[index]['z'] * -1
        
    def Rotate(self, option):
        mytype = None
        if type(option) == type('string'):
            try:
                if not re.search('[xyzXYZ]', option[0]):
                    raise IOError('Wrong format input string for Rotate')
                axis = option[0].upper()
                theta = float(option[1:])
                mytype = 'string'
            except:
                self.logger.error("Rotation axis and angle must be in form 'x10' or 'Z2.5'")
                sys.exit()
        elif type(option) == type([]):
            try:
                for i1 in range(0,3):
                    for i2 in range(0,3):
                        float(option[i1][i2])
                option = numpy.array(option)
                mytype = 'matrix'
            except:
                self.logger.error("Rotation matrix must be a 3x3 nested array of floats")
                sys.exit()
        else:
            self.logger.error("Rotation axis and angle must be in form 'x10' or 'Z2.5'")
            sys.exit()

        def rotation_matrix(axis,theta):
            theta = numpy.radians(theta)
            if axis == 'X':
                return numpy.array([[1,0,0],[0,numpy.cos(theta),-numpy.sin(theta)],[0,numpy.sin(theta),numpy.cos(theta)]])
            elif axis == 'Y':
                return numpy.array([[numpy.cos(theta),0,numpy.sin(theta)],[0,1,0],[-numpy.sin(theta),0,numpy.cos(theta)]])
            elif axis == 'Z':
                return numpy.array([[numpy.cos(theta),-numpy.sin(theta),0],[numpy.sin(theta),numpy.cos(theta),0],[0,0,1]])
            else:
                sys.exit('error matrix function, required axis is neither x,y or z!')
        
        if mytype == 'string':
            self.logger.info(f'Rotating around {axis} by {theta} degrees')
        if mytype == 'matrix':
            self.logger.info('Rotating by a user input matrix')
        
        for index in self.hashdata.keys():
            if self.hashdata[index]['record_type'] == 'ATOM' or self.hashdata[index]['record_type'] == 'HETATM':
                v = numpy.array([self.hashdata[index]['x'],self.hashdata[index]['y'],self.hashdata[index]['z']])
                if mytype == 'string':
                    newcoords = (numpy.dot(rotation_matrix(axis, theta),v))
                else:
                    newcoords = (numpy.dot(option,v))
                self.hashdata[index]['x'] = float(newcoords[0])
                self.hashdata[index]['y'] = float(newcoords[1])
                self.hashdata[index]['z'] = float(newcoords[2])

    def RenameChain(self, old, new):
        if not len(str(new)) == 1:
            self.logger.error('Chain names should be a single character')
        else:
            number_renamed = 0
            for index in self.hashdata.keys():
                if self.hashdata[index]['record_type'] == 'ATOM' or self.hashdata[index]['record_type'] == 'HETATM':
                    if self.hashdata[index]['chain'] == str(old):
                        self.hashdata[index]['chain'] = str(new)
                        number_renamed += 1
            self.logger.info(f'Renamed chain on {number_renamed} residues')
                    
    def Translate(self, option):
        translation = []
        for item in re.split('[,x ]', option):
            try:
                translation.append(float(item))
            except:
                pass
        if len(translation) != 3:
            self.logger.error("The translation matrix should be in the form i.e. '10.2,9.6,0.0'")
            sys.exit()
        self.logger.info(f'Translating by {translation[0]}x{translation[1]}x{translation[2]}')
        for index in self.hashdata.keys():
            if self.hashdata[index]['record_type'] == 'ATOM' or self.hashdata[index]['record_type'] == 'HETATM':
                self.hashdata[index]['x'] = self.hashdata[index]['x'] + translation[0]
                self.hashdata[index]['y'] = self.hashdata[index]['y'] + translation[1]
                self.hashdata[index]['z'] = self.hashdata[index]['z'] + translation[2]

    def parse_file(self):
        self.logger.info(f'Reading and parsing pdb file: {self.pdbfile}')

        ######################################
        #PDB DEFINITION FROM wwPDB GUIDLINES #
        # VERSION 3.30 31/07/14              #
        ######################################
        self.pdb_definition = {
            'record_type': ( 0 , 6 ),
            'serial_no': ( 6 , 11 ),
            'atom_name': ( 12 , 16 ),
            'alternate': ( 16 , 17 ),
            'residue': ( 17 , 20 ),
            'chain': ( 21 , 22 ),
            'residue_no': ( 22 , 26 ),
            'icode': ( 26 , 27 ),
            'x': ( 30 , 38 ),
            'y': ( 38 , 46 ),
            'z': ( 46 , 54 ),
            'occupancy': ( 54 , 60 ),
            'bfactor': ( 60 , 66 ),
            'element': ( 76 , 78 ),
            'charge': ( 78 , 80 ),
            'string': ( 6 , '' )}
        self.integer_records = ['serial_no', 'residue_no']
        self.float_records = {'bfactor': 2, 'occupancy': 2, 'x': 3, 'y': 3, 'z': 3}
        if self.pdbfile == None:
            pdblines = []
        else:
            file = open(self.pdbfile, 'r')
            pdblines = file.readlines()

        for line in pdblines:
            index = pdblines.index(line)
            self.hashdata[index] = {}
            record_type = line[self.pdb_definition['record_type'][0]:self.pdb_definition['record_type'][1]].rstrip()
            if record_type == 'ATOM' or record_type == 'HETATM':
                for record in self.pdb_definition.keys():
                    try:
                        if record in self.integer_records:
                            self.hashdata[index][record] = int(line[self.pdb_definition[record][0]:self.pdb_definition[record][1]].strip())
                        elif record in self.float_records.keys():
                            self.hashdata[index][record] = float(line[self.pdb_definition[record][0]:self.pdb_definition[record][1]].strip())
                        else:
                            self.hashdata[index][record] = line[self.pdb_definition[record][0]:self.pdb_definition[record][1]].strip()
                    except:
                        pass
            else:
                self.hashdata[index]['record_type'] = line[self.pdb_definition['record_type'][0]:self.pdb_definition['record_type'][1]].rstrip()
                self.hashdata[index]['string'] = line[self.pdb_definition['string'][0]:-1]+line[-1]


    def return_file(self, justatoms=False):
        self.logger.info('Writing out a formatted PDB file')
        if justatoms:
            justatoms = True
            self.logger.info('Will only return the atom lines')

        output_lines = []
        #ljust_records = [ 'record_type', 'atom_name', 'string' ]
        ljust_records = [ 'record_type', 'string' ]
        
        for index in sorted(self.hashdata.keys()):
            try:
                if len(self.hashdata[index]['atom_name']) < 4:
                    self.hashdata[index]['atom_name'] = ' '+self.hashdata[option][index]['atom_name']
            except:
                pass
            line = list(' '*80)
            for record in self.hashdata[index]:
                try:
                    length = self.pdb_definition[record][1] - self.pdb_definition[record][0]
                except:
                    length = 80 - self.pdb_definition[record][0]
                if record in self.float_records:
                    if record in ljust_records:
                        content = list((('%.'+str(self.float_records[record])+'f') % self.hashdata[index][record]).ljust(length))
                    else:
                        content = list((('%.'+str(self.float_records[record])+'f') % self.hashdata[index][record]).rjust(length))
                        
                else:
                    if record in ljust_records:
                        content = list(str(self.hashdata[index][record]).ljust(length))
                    else:
                        if record == 'atom_name':
                            temp_string = str(self.hashdata[index][record]).ljust(3)
                        else:
                            temp_string = str(self.hashdata[index][record])
                        content = list(temp_string.rjust(length))
            
                try:
                    line[self.pdb_definition[record][0]:self.pdb_definition[record][1]] = content[0:]
                except:
                    line[self.pdb_definition[record][0]:80] = content[0:]
            if justatoms:
                if self.hashdata[index]['record_type'] == 'ATOM' or self.hashdata[index]['record_type'] == 'HETATM':
                    output_lines.append(''.join(line))
            else:
                output_lines.append(''.join(line))


        return '\n'.join(output_lines)+'\n'

