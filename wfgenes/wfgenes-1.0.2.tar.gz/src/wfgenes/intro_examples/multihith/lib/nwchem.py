__author__ = 'Ivan Kondov'
__email__ = 'ivan.kondov@kit.edu'
__copyright__ = 'Copyright 2016, Karlsruhe Institute of Technology'


import re
import numpy as np
try: 
    from StringIO import StringIO 
except ImportError: 
    from io import StringIO 
from ase.io import read
from ase.units import Hartree
from ase.calculators.nwchem import NWChem

class KITnwchem(NWChem):
    def __init__(self, **parameters):

        self.set_parameters(parameters)
        assert self.verify_parameters() # need some handling

        NWChem.__init__(self,
            label=self.title,
            geometry=self.geometry,
            basis=self.basis_set,
            charge=self.charge,
            mult=self.multiplicity,
            xc=self.func,
            convergence=self.convergence,
            task=self.task
            )
        self.reset()

    def set_parameters(self, parameters):

        self.geometry = 'nocenter noautosym noautoz units angstroms'

        if 'command' in parameters.keys(): # e.g. "mpirun -np 4 nwchem PREFIX.nw > PREFIX.out"
            self.command = parameters['command']

        if 'title' in parameters.keys():
            self.title = parameters['title'].replace (" ", "_")
        else:
            self.title = 'notitle'
        if 'basis set' in parameters.keys():
            self.basis_set = parameters['basis set']
        if 'charge' in parameters.keys():
            self.charge = parameters['charge']
        else:
            self.charge = 0
        if 'multiplicity' in parameters.keys():
            self.multiplicity = parameters['multiplicity']
        if 'dft' in parameters.keys():
            self.dft = parameters['dft']
        if 'density functional' in parameters.keys():
            self.func = parameters['density functional']
        else:
            self.func = 'lda'
            print("Density functional set to default: "), self.func
        if 'ri' in parameters.keys():
            self.ri = parameters['ri']
        if 'internals' in parameters.keys():
            self.internals = parameters['internals']
        else:
            self.internals = False
        if 'scfiterlimit' in parameters.keys():
            self.scfiterlimit = parameters['scfiterlimit']
        else:
            self.scfiterlimit = 60
        if 'force convergence' in parameters.keys():
            self.force_conv = parameters['force convergence']
        else:
            self.force_conv = None
        if 'energy convergence' in parameters.keys():
            self.energy_conv = parameters['energy convergence']
        else:
            self.energy_conv = None
        self.convergence= {'energy': self.energy_conv, 'density': None, 'gradient': self.force_conv, 'lshift': None, 'damp': None}
        if 'task' in parameters.keys():
            self.task = parameters['task']
        else:
            self.task = 'energy' # note that 'gradient' is the default of the base class
        if 'geometry iterations' in parameters.keys():
            self.maxiter = parameters['geometry iterations']
        else:
            self.maxiter = None


    def verify_parameters(self):
        available_functionals = [ # only "parameter-free" funcionals from all supported fnctionals
            'acm', 'b3lyp', 'beckehandh',  'pbe0', 'becke97',   'becke97-1', 'becke97-2', 
            'becke97-3', 'becke97-d', 'becke98', 'hcth', 'hcth120', 'hcth147', 'hcth407', 
            'becke97gga1',  'hcth407p', 'mpw91', 'mpw1k', 'xft97', 'cft97', 'ft97', 'op', 
            'bop', 'pbeop', 'xpkzb99', 'cpkzb99', 'xtpss03', 'ctpss03', 'xctpssh', 'b1b95', 
            'bb1k', 'mpw1b95', 'mpwb1k', 'pw6b95', 'pwb6k', 'm05', 'm05-2x', 'vs98', 'm06',
            'm06-hf', 'm06-L', 'm06-2x'
            ]
        available_basis_sets = [ # no ECP, no check for availability for given elements
            '3-21++G', '3-21++G*', '3-21G', '3-21G*', '3-21GSP', '4-22GSP', '4-31G', '6-31++G', '6-31++G*', '6-31++G**', '6-31+G*', '6-311++G(2d,2p)', '6-311++G(3df,3pd)', '6-311++G**', '6-311+G*', '6-311G', '6-311G(2df,2pd)', '6-311G*', '6-311G**', '6-31G', '6-31G-Blaudeau', '6-31G(3df,3pd)', '6-31G*', '6-31G*-Blaudeau', '6-31G**', 'Ahlrichs pVDZ', 'Ahlrichs TZV', 'Ahlrichs VDZ', 'Ahlrichs VTZ', 'ANO-RCC', 'apr-cc-pV(Q+d)Z', 'aug-cc-pCV5Z', 'aug-cc-pCVDZ', 'aug-cc-pCVQZ', 'aug-cc-pCV(T+d)Z', 'aug-cc-pCVTZ', 'aug-cc-pV(5+d)Z', 'aug-cc-pV5Z', 'aug-cc-pV(6+d)Z', 'aug-cc-pV6Z', 'aug-cc-pV(D+d)Z', 'aug-cc-pVDZ', 'aug-cc-pV(Q+d)Z', 'aug-cc-pVQZ', 'aug-cc-pV(T+d)Z', 'aug-cc-pVTZ', 'aug-cc-pVTZ-J', 'aug-cc-pwCV5Z', 'aug-cc-pwCV5Z-NR', 'aug-cc-pwCVDZ', 'aug-cc-pwCVQZ', 'aug-cc-pwCVQZ-NR', 'aug-cc-pwCVTZ', 'aug-cc-pwCVTZ-NR', 'aug-mcc-pV5Z', 'aug-mcc-pV6Z', 'aug-mcc-pV7Z', 'aug-mcc-pV8Z', 'aug-mcc-pVQZ', 'aug-mcc-pVTZ', 'aug-pc-0', 'aug-pc-1', 'aug-pc-2', 'aug-pc-3', 'aug-pc-4', 'aug-pcJ-0', 'aug-pcJ-0_2006', 'aug-pcJ-1', 'aug-pcJ-1_2006', 'aug-pcJ-2', 'aug-pcJ-2_2006', 'aug-pcJ-3', 'aug-pcJ-3_2006', 'aug-pcJ-4', 'aug-pcJ-4_2006', 'aug-pcS-0', 'aug-pcS-1', 'aug-pcS-2', 'aug-pcS-3', 'aug-pcS-4', 'aug-pV7Z', 'B2 basis set for Zn', 'Bauschlicher ANO', 'Binning/Curtiss SV', 'Binning/Curtiss SVP', 'Binning/Curtiss VTZ', 'Binning/Curtiss VTZP', 'cc-pCV5Z', 'cc-pCV6Z', 'cc-pCV6Z(old)', 'cc-pCVDZ', 'cc-pCVDZ(old)', 'cc-pCVQZ', 'cc-pCVQZ(old)', 'cc-pCVTZ', 'cc-pCVTZ(old)', 'cc-pV(5+d)Z', 'cc-pV5Z', 'cc-pV(6+d)Z', 'cc-pV6Z', 'cc-pV8Z', 'cc-pV9Z', 'cc-pV(D+d)Z', 'cc-pVDZ', 'cc-pVDZ(seg-opt)', 'cc-pV(Q+d)Z', 'cc-pVQZ', 'cc-pVQZ(seg-opt)', 'cc-pV(T+d)Z', 'cc-pVTZ', 'cc-pVTZ(seg-opt)', 'cc-pwCV5Z', 'cc-pwCV5Z Core Set', 'cc-pwCV5Z-NR', 'cc-pwCVDZ', 'cc-pwCVQZ', 'cc-pwCVQZ-NR', 'cc-pwCVTZ', 'cc-pwCVTZ-NR', 'ccemd-2', 'ccemd-3', 'ccJ-pV5Z', 'ccJ-pVDZ', 'ccJ-pVQZ', 'ccJ-pVTZ', 'coemd-2', 'coemd-3', 'coemd-4', 'coemd-ref', 'CVTZ', 'd-aug-cc-pV5Z', 'd-aug-cc-pV6Z', 'd-aug-cc-pVDZ', 'd-aug-cc-pVQZ', 'd-aug-cc-pVTZ', 'Def2-QZVP', 'Def2-QZVPD', 'Def2-SVP', 'def2-SV(P)', 'Def2-SVPD', 'Def2-TZVP', 'Def2-TZVPD', 'dhf-QZVP', 'dhf-SV(P)', 'dhf-TZVP', 'Dunning-Hay Double Rydberg', 'Dunning-Hay Rydberg', 'DZ + Double Rydberg (Dunning-Hay)', 'DZ + Rydberg (Dunning)', 'DZ (Dunning)', 'DZP + Rydberg (Dunning)', 'DZP (Dunning)', 'DZQ', 'DZVP2 (DFT Orbital)', 'DZVP (DFT Orbital)', 'Feller Misc. CVDZ', 'Feller Misc. CVQZ', 'Feller Misc. CVTZ', 'GAMESS PVTZ', 'GAMESS VTZ', 'IGLO-II', 'IGLO-III', 'jul-cc-pV(D+d)Z', 'jul-cc-pV(Q+d)Z', 'jul-cc-pV(T+d)Z', 'jun-cc-pV(D+d)Z', 'jun-cc-pV(Q+d)Z', 'jun-cc-pV(T+d)Z', 'LANL08', 'LANL08+', 'LANL08d', 'LANL08(f)', 'Lanl2-\[10s8p7d3f2g\]', 'Lanl2-\[5s4p4d2f\]', 'Lanl2-\[6s4p4d2f\]', 'Lanl2DZ+1d1f', 'Lanl2DZ+2s2p2d2f', 'LANL2TZ', 'LANL2TZ+', 'LANL2TZ(f)', 'm6-31G', 'm6-31G*', 'maug-cc-pV(D+d)Z', 'maug-cc-pVDZ', 'maug-cc-pV(Q+d)Z', 'maug-cc-pVQZ', 'maug-cc-pV(T+d)Z', 'maug-cc-pVTZ', 'may-cc-pV(Q+d)Z', 'may-cc-pV(T+d)Z', 'McLean/Chandler VTZ', 'MG3S', 'MIDI!', 'MIDI (Huzinaga)', 'MINI (Huzinaga)', 'MINI (Scaled)', 'modified LANL2DZ', 'NASA Ames ANO', 'NASA Ames ANO2', 'NASA Ames cc-pCV5Z', 'NASA Ames cc-pCVQZ', 'NASA Ames cc-pCVTZ', 'NASA Ames cc-pV5Z', 'NASA Ames cc-pVQZ', 'NASA Ames cc-pVTZ', 'Partridge Uncontracted 1', 'Partridge Uncontracted 2', 'Partridge Uncontracted 3', 'Partridge Uncontracted 4', 'pc-0', 'pc-1', 'pc-2', 'pc-3', 'pc-4', 'pcemd-2', 'pcemd-3', 'pcemd-4', 'pcJ-0', 'pcJ-0_2006', 'pcJ-1', 'pcJ-1_2006', 'pcJ-2', 'pcJ-2_2006', 'pcJ-3', 'pcJ-3_2006', 'pcJ-4', 'pcJ-4_2006', 'pcS-0', 'pcS-1', 'pcS-2', 'pcS-3', 'pcS-4', 'pSBKJC', 'Pt - mDZP', 'pV6Z', 'pV7Z', 'Roos_ANO_DZ', 'Roos_ANO_TZ', 'Roos Augmented Double Zeta ANO', 'Roos Augmented Triple Zeta ANO', 's3-21G', 's3-21G*', 's6-31G', 's6-31G*', 'Sadlej pVTZ', 'SDB-aug-cc-pVQZ', 'SDB-aug-cc-pVTZ', 'SDB-cc-pVQZ', 'SDB-cc-pVTZ', 'STO-2G', 'STO-3G', 'STO-3G*', 'STO-6G', 'SV + Double Rydberg (Dunning-Hay)', 'SV + Rydberg (Dunning-Hay)', 'SV (Dunning-Hay)', 'SVP + Rydberg (Dunning-Hay)', 'SVP (Dunning-Hay)', 'TZ (Dunning)', 'TZVP (DFT Orbital)', 'UGBS', 'un-ccemd-ref', 'un-pcemd-ref', 'Wachters+f', 'WTBS', 'Z3Pol' ]

        if self.basis_set.lower() not in [x.lower() for x in available_basis_sets]:
            print("basis set ", self.basis_set, " not available / not supported")
            return None
        if self.func.lower() not in [x.lower() for x in available_functionals]:
            print("density functional ", self.func, " not available / not supported")
            return None
        return True


    def reset(self):
        NWChem.reset(self)
        self.atoms = None
        self.results = {}
        self.initialized = False
        self.orbitals = []


    def initialize(self, atoms=None):
        return


    def write_input(self, atoms, properties=None, system_changes=None):
        NWChem.write_input(self, atoms, properties=properties, system_changes=system_changes)
        filename = self.title+'.nw'
        buf = []
        drvset = False
        for line in open(filename,'r'):
            buf.append(line)
            if re.search('^dft\s*$',line):
                buf.append('  print \"final vectors analysis\" \"final vectors\"\n')
                buf.append('  direct\n')
                buf.append('  noio\n')
                buf.append('  iterations ' + str(self.scfiterlimit) + '\n')
            if re.search('^end\s*$',line) and self.task == 'optimize' and not drvset:
                buf.append('\ndriver\n')
                if self.force_conv > 0.000450:
                    buf.append('  loose\n')
                if self.maxiter:
                    buf.append('  maxiter ' + str(self.maxiter) + '\n')
                buf.append('end\n\n')
                drvset = True

        outfile = open(filename,'w')
        outfile.write("".join(buf))
        outfile.close()


    def get_potential_energy(self,atoms):
        if self.task == 'optimize':
            energy = NWChem.get_potential_energy(self,atoms)
            self.read_geometry()
            atoms.set_positions(self.atoms.get_positions())
            return energy
        else:
            return NWChem.get_potential_energy(self,atoms)


    def get_mo(self,mo_type,atoms):
        if not self.orbitals:
            self.energy = atoms.get_potential_energy()
        assert mo_type in ['HOMO', 'LUMO']
        if mo_type == 'HOMO':
            orb_energy = None
            orb_number = None
            for orbital in self.orbitals:
                if orbital['occupation'] > 0:
                    if orbital['energy'] > orb_energy:
                        orb_energy = orbital['energy']
                        orb_number = orbital['number']
        if mo_type == 'LUMO':
            orb_energy = None
            orb_number = None
            for orbital in self.orbitals:
                if orbital['occupation'] < 1:
                    if orbital['energy'] < orb_energy or not orb_energy:
                        orb_energy = orbital['energy']
                        orb_number = orbital['number']
        return [orb_number, orb_energy*Hartree]


    def get_mos(self, atoms):
        if not self.orbitals:
            self.energy = atoms.get_potential_energy()
        orbital_coefficients = []
        eigen_energies = []
        for orbital in self.orbitals:
            orbital_coefficients.append(orbital['coefficients'])
            eigen_energies.append(orbital['energy'])
        return [np.array(orbital_coefficients), np.diag(np.array(eigen_energies)*Hartree)]


    def read_results(self):
        NWChem.read_results(self)
        self.read_mos()


    def read_energy(self): # reads the last energy from geometry optimization output
        NWChem.read_energy(self)
        text = open(self.label + '.out', 'r').read()
        lines = iter(text.split('\n'))

        # Energy:
        estring = 'Total '
        if self.parameters.xc == 'RHF':
            estring += 'SCF'
        elif self.parameters.xc == 'MP2':
            estring += 'MP2'
        else:
            estring += 'DFT'
        estring += ' energy'
        for line in lines:
            if line.find(estring) >= 0:
                energy = float(line.split()[-1])
                continue
        self.results['energy'] = energy*Hartree


    def read_geometry(self):
        text = open(self.label + '.out', 'r').read()
        lines = iter(text.split('\n'))
        natoms = len(self.atoms)
        read_flag = False
        atoms_read = 0
        xyz_string = str(natoms)+'\n\n'
        for line in lines:
            if 'Output coordinates in angstroms' in line:
                read_flag = True
                xyz_string = str(natoms)+'\n\n'
                continue
            if read_flag:
                match = re.search('(\d+)\s+(\w+)\s+([+-]?\d+\.\d+)\s+([+-]?\d+\.\d+)\s+([+-]?\d+\.\d+)\s+([+-]?\d+\.\d+)',line) 
                if match:
                    string = match.group(2) + ' ' + match.group(4) + ' ' + match.group(5) + ' ' + match.group(6) + '\n'
                    xyz_string += string
                    atoms_read += 1
                    assert int(match.group(1)) == natoms, 'number of xyz lines more than expected number of atoms'
            if atoms_read == natoms:
                read_flag = False
                atoms_read = 0
        new_atoms = read(StringIO(xyz_string), format='xyz')
        self.atoms.set_positions(new_atoms.get_positions())

# end of class KITnwchem
