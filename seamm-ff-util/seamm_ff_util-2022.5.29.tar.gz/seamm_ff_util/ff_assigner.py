# -*- coding: utf-8 -*-

"""Main class for handling forcefields"""

import logging
import rdkit
import rdkit.Chem
import rdkit.Chem.Draw
import rdkit.Chem.AllChem

logger = logging.getLogger(__name__)
# logger.setLevel("DEBUG")


class FFAssigner(object):
    def __init__(self, forcefield):
        """Handle the assignment of the forcefield to the structure

        This class is closely related to the Forcefield class, but
        separated from it due to the dependencies it carries along,
        coupled with the fact that it is not needed in some
        computations where the forcefield itself is.
        """

        self.forcefield = forcefield

    def assign(self, configuration):
        """Assign the atom types to the structure using SMARTS templates"""
        molecule = configuration.to_RDKMol()

        n_atoms = configuration.n_atoms

        atom_types = ["?"] * n_atoms
        templates = self.forcefield.get_templates()
        for atom_type in templates:
            template = templates[atom_type]
            for smarts in template["smarts"]:
                pattern = rdkit.Chem.MolFromSmarts(smarts)

                ind_map = {}
                for atom in pattern.GetAtoms():
                    map_num = atom.GetAtomMapNum()
                    if map_num:
                        ind_map[map_num - 1] = atom.GetIdx()
                map_list = [ind_map[x] for x in sorted(ind_map)]

                matches = molecule.GetSubstructMatches(pattern, maxMatches=6 * n_atoms)
                logger.debug(atom_type + ": ")
                if len(matches) > 0:
                    for match in matches:
                        atom_ids = [match[x] for x in map_list]
                        for x in atom_ids:
                            atom_types[x] = atom_type
                        tmp = [str(x) for x in atom_ids]
                        logger.debug("\t" + ", ".join(tmp))

        i = 0
        untyped = []
        for atom, atom_type in zip(molecule.GetAtoms(), atom_types):
            if atom_type == "?":
                untyped.append(i)
            logger.debug("{}: {}".format(atom.GetSymbol(), atom_type))
            i += 1

        if len(untyped) > 0:
            logger.warning(
                "The forcefield does not have atom types for"
                " the molecule!. See missing_atom_types.png"
                " for more detail."
            )
            rdkit.Chem.AllChem.Compute2DCoords(molecule)
            img = rdkit.Chem.Draw.MolToImage(
                molecule,
                size=(1000, 1000),
                highlightAtoms=untyped,
                highlightColor=(0, 1, 0),
            )
            img.save("missing_atom_types.png")
        else:
            logger.info("The molecule was successfully atom-typed")

        return atom_types
