import os
import unittest

from ralf import get_rotation_limit


class Test_ralf(unittest.TestCase):
    """
    Test the various functionalities of ralf.
    """

    @classmethod
    def setUpClass(self):
        self._knipholone_pdb = os.path.join(
            os.getcwd(),
            "test",
            "data",
            "knipholone.pdb",
        )
        self._binap_pdb = os.path.join(
            os.getcwd(),
            "test",
            "data",
            "binap.pdb",
        )
        self._segphos_pdb = os.path.join(
            os.getcwd(),
            "test",
            "data",
            "segphos.pdb",
        )
        self._tolbinap_pdb = os.path.join(
            os.getcwd(),
            "test",
            "data",
            "tolbinap.pdb",
        )
        self._ethane_pdb = os.path.join(
            os.getcwd(),
            "test",
            "data",
            "ethane.pdb",
        )

    def test_knipholone(self):
        """knipholone natrual product"""
        get_rotation_limit(
            self._knipholone_pdb,
            14,
            7,
        )

    def test_binap(self):
        """binap ligand"""
        get_rotation_limit(
            self._binap_pdb,
            23,
            24,
        )

    def test_segphos(self):
        """segphos ligand"""
        get_rotation_limit(
            self._segphos_pdb,
            23,
            6,
        )

    def test_tolbinap(self):
        """tolbinap ligand"""
        get_rotation_limit(
            self._tolbinap_pdb,
            25,
            26,
        )

    def test_custom_cutoff(self):
        """run with custom cutoff distance"""
        get_rotation_limit(
            self._segphos_pdb,
            23,
            6,
            cutoff_distance=2.2,
        )

    def test_unrestricted_mol(self):
        """non-atropisomer should raise an error"""
        with self.assertRaises(RuntimeError):
            get_rotation_limit(
                self._ethane_pdb,
                1,
                2,
            )

    def test_nonexistent_atom_1_id(self):
        """Bad ID for atom 1 error"""
        with self.assertRaises(RuntimeError):
            get_rotation_limit(
                self._tolbinap_pdb,
                1001,
                26,
            )

    def test_nonexistent_atom_2_id(self):
        """Bad ID for atom 2 error"""
        with self.assertRaises(RuntimeError):
            get_rotation_limit(
                self._tolbinap_pdb,
                10,
                260,
            )

    def test_unbonded_atom_ids(self):
        """wrong atoms for tolbinap ligand"""
        with self.assertRaises(RuntimeError):
            get_rotation_limit(
                self._tolbinap_pdb,
                16,
                26,
            )


if __name__ == "__main__":
    unittest.main()
