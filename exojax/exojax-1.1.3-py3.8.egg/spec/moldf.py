"""Molecular DataFrabe (MDF) class.

"""
import os
import numpy as np
import jax.numpy as jnp
from jax import jit, vmap
import pathlib
import vaex
from exojax.spec import hapi, exomolapi, exomol, atomllapi, atomll, hitranapi
from exojax.spec.hitran import gamma_natural as gn
from exojax.utils.constants import hcperk

from radis.io.exomol import fetch_exomol


class MdbExomol(object):
    def __init__(self, path, nurange=[-np.inf, np.inf], margin=0.0, crit=0., Ttyp=1000., bkgdatm='H2', broadf=True, remove_original_hdf=True):
        self.path = pathlib.Path(path).expanduser()
        df = fetch_exomol("CH4", database="YT10to10", isotope="1", load_wavenum_max=5000, output="jax")
        print(df)
if __name__ == "__main__":
    mdbCH4 = moldb.MdbExomol('.database/CH4/12C-1H4/YT10to10/', nus, crit=1.e-30)
