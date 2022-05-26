"""## Directories
* [data](/data) - Directbeam files and experimentally-measured data for a selection of samples of varying complexity.
* [models](/models) - Model definitions and fits for the aforementioned samples.

## Modules
* [angles.py](/angles.py) - Optimises and visualises the choice of measurement angle(s) for a collection of samples of varying complexity.
* [contrasts.py](/contrasts.py) - Optimises and visualises the choice of contrast for the DMPC and DPPC/RaLPS bilayer models.
* [kinetics.py](/kinetics.py) - Optimises and visualises the choice of measurement angle and contrast for the DPPG monolayer model degrading over time.
* [magnetism.py](/magnetism.py) - Optimises and visualises the sample design of the magnetic [YIG](/experimental-design/results/YIG_sample) sample.
* [optimise.py](/optimise.py) - Contains code for optimising the choice of measurement angle(s), counting time(s), contrast(s) and underlayer(s).
* [simulate.py](/simulate.py) - Contains code for simulating experiments using a [directbeam](/experimental-design/data/directbeams) file of incident neutron flux as a function of wavelength.
* [underlayers.py](/underlayers.py) - Optimises and visualises the choice of underlayer thickness(es) and SLD(s) for the DMPC and DPPC/RaLPS bilayer models.
* [utils.py](/utils.py) - Contains miscellaneous code for calculating the Fisher information, nested sampling, and saving plots.
* [visualise.py](/visualise.py) - Contains code for visualising the choice of measurement angle(s), counting time(s), contrast(s) and underlayer(s).
"""

from . import angles
from . import contrasts
from . import kinetics
from . import magnetism
from . import optimise
from . import simulate
from . import underlayers
from . import utils
from . import visualise
from . import data
from . import models
