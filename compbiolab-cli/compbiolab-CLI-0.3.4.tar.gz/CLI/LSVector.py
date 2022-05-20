import numpy as np
from .load_files import load_family, load_ls_file, is_pf


class LSVector:
    ls_name: str
    ls_data: np.ndarray

    def __init__(self, ls_name: str, ls_data: np.ndarray = None):
        """

        Parameters
        ----------
        ls_name : str
            Name of latent space
        ls_data : numpy.ndarray
            Latent space data
        """
        self.ls_name = ls_name
        if ls_data is None:
            self.ls_data = self.load_vector()
        else:
            self.ls_data = ls_data

    def load_vector(self) -> np.ndarray:
        """ Load data if only ls_name was given

        Load latent space data from protein family if one matches name, otherwise treat it as filename

        Returns
        -------
        numpy.ndarray
        """
        if is_pf(self.ls_name):
            return load_family(self.ls_name + '.txt')
        else:
            return load_ls_file(self.ls_name)
