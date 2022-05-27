from typing import Iterable
from . import LAMMPSDataImporter, LAMMPSDataExporter

# Implementation of the LAMMPSDataImporter.atom_style property:
def _get_LAMMPSDataImporter_atom_style(self):
    """ The LAMMPS atom style used by the data file. """
    s = str(self._atom_style)
    assert(s.startswith('LAMMPSAtomStyle.'))
    return s[len('LAMMPSAtomStyle.'):]
def _set_LAMMPSDataImporter_atom_style(self, style):
    if str(style) not in LAMMPSDataImporter.LAMMPSAtomStyle.__dict__:
        raise KeyError("'%s' is not a valid LAMMPS atom style supported by OVITO. Must be one of %s." %
            (style, [s for s in dir(LAMMPSDataImporter.LAMMPSAtomStyle) if not s.startswith('_')]))
    self._atom_style = LAMMPSDataImporter.LAMMPSAtomStyle.__dict__[str(style)]
LAMMPSDataImporter.atom_style = property(_get_LAMMPSDataImporter_atom_style, _set_LAMMPSDataImporter_atom_style)

# Implementation of the LAMMPSDataImporter.atom_substyles property:
def _get_LAMMPSDataImporter_atom_substyles(self):
    """ The sub-styles of the LAMMPS atom style 'hybrid'. """
    substyles = []
    for s in self._atom_substyles:
        s = str(s)
        assert(s.startswith('LAMMPSAtomStyle.'))
        substyles.append(s[len('LAMMPSAtomStyle.'):])
    return tuple(substyles)
def _set_LAMMPSDataImporter_atom_substyles(self, substyles_names):
    if isinstance(substyles_names, str) or not isinstance(substyles_names, Iterable):
        raise ValueError("Sequence of atom style names expected")
    substyles = []
    for name in substyles_names:
        if name not in LAMMPSDataImporter.LAMMPSAtomStyle.__dict__:
            raise KeyError("'%s' is not a valid LAMMPS atom style supported by OVITO. Must be one of %s." %
                (name, [s for s in dir(LAMMPSDataImporter.LAMMPSAtomStyle) if not s.startswith('_')]))
        substyles.append(LAMMPSDataImporter.LAMMPSAtomStyle.__dict__[str(name)])
    self._atom_substyles = substyles
LAMMPSDataImporter.atom_substyles = property(_get_LAMMPSDataImporter_atom_substyles, _set_LAMMPSDataImporter_atom_substyles)

# Implementation of the LAMMPSDataExporter.atom_style property:
def _get_LAMMPSDataExporter_atom_style(self):
    s = str(self._atom_style)
    assert(s.startswith('LAMMPSAtomStyle.'))
    return s[len('LAMMPSAtomStyle.'):]
def _set_LAMMPSDataExporter_atom_style(self, style):
    if str(style) not in LAMMPSDataImporter.LAMMPSAtomStyle.__dict__:
        raise KeyError("'%s' is not a valid LAMMPS atom style supported by OVITO. Must be one of %s." %
            (style, [s for s in dir(LAMMPSDataImporter.LAMMPSAtomStyle) if not s.startswith('_')]))
    self._atom_style = LAMMPSDataImporter.LAMMPSAtomStyle.__dict__[str(style)]
LAMMPSDataExporter.atom_style = property(_get_LAMMPSDataExporter_atom_style, _set_LAMMPSDataExporter_atom_style)

# Implementation of the LAMMPSDataExporter.atom_substyles property:
def _get_LAMMPSDataExporter_atom_substyles(self):
    """ The sub-styles of the LAMMPS atom style 'hybrid'. """
    substyles = []
    for s in self._atom_substyles:
        s = str(s)
        assert(s.startswith('LAMMPSAtomStyle.'))
        substyles.append(s[len('LAMMPSAtomStyle.'):])
    return tuple(substyles)
def _set_LAMMPSDataExporter_atom_substyles(self, substyles_names):
    if isinstance(substyles_names, str) or not isinstance(substyles_names, Iterable):
        raise ValueError("Sequence of atom style names expected")
    substyles = []
    for name in substyles_names:
        if name not in LAMMPSDataImporter.LAMMPSAtomStyle.__dict__:
            raise KeyError("'%s' is not a valid LAMMPS atom style supported by OVITO. Must be one of %s." %
                (name, [s for s in dir(LAMMPSDataImporter.LAMMPSAtomStyle) if not s.startswith('_')]))
        substyles.append(LAMMPSDataImporter.LAMMPSAtomStyle.__dict__[str(name)])
    self._atom_substyles = substyles
LAMMPSDataExporter.atom_substyles = property(_get_LAMMPSDataExporter_atom_substyles, _set_LAMMPSDataExporter_atom_substyles)
